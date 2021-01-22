import io
import json
import os
import subprocess
import time
from argparse import ArgumentTypeError
import re

###################
# Constant Values #
###################
from typing import Union

MULTI_MODEL_FOLDER = "Multi-Models"
MULTI_MODEL_EXTENSION = ".mm.json"
FMUS_FOLDER = 'FMUs'
COE_SETTINGS_EXTENSION = ".coe.json"
DSE_FOLDER = "DSEs"
DSE_CONFIG_EXTENSION = ".dse.json"
USER_METRICS_FOLDER = "userMetricScripts"
DEFAULT_SIM_CONFIG = 'config.mm.json'
RESULTS_FILE = 'results.csv'

OBJECTIVES_FILE = 'objectives.json'
RANKING_FILE = 'ranking.json'
GRAPHS_FOLDER = 'graphs'
HTML_RESULTS = 'results.html'
ANALYSIS_RESULTS = 'dseResults.csv'

###############################
# Script Parameter validation #
###############################
def validThreadCount(value: Union[str, int]) -> int:
    ival = int(value)
    if ival <= 0:
        raise ArgumentTypeError(
            f"{value} is an invalid thread count please select a thread count greater than or equal to 1")
    return ival


def validPortNumber(value: str) -> str:
    if not re.match(r"^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$",
                    value.strip()):
        raise ArgumentTypeError(f"{value} is not a valid port number")
    return value.strip()


def strToBool(value: Union[str, bool]) -> bool:
    if isinstance(value, bool):
        return value

    value = value.strip()

    if value.lower() in ("yes", "y", "true", "t", "1"):
        return True
    elif value.lower() in ("no", "n", "false", "f", "0"):
        return False
    else:
        raise ArgumentTypeError(f"{value} is not a valid repersentaiton of a boolean")


def validProjectPath(value: str) -> str:
    """
    Check if path is a valid project path
    :param value: Full path to the project folder
    """
    ival = os.path.exists(value)
    if not ival:
        raise IOError(f"{value} value is not a valid project path")
    return value


def __canReadFile__(path: str):
    """
    Checks if we have read perms for a given file path
    :param path: Full path to the file
    :except IOException if the file cannot be read
    """
    file = open(path, 'r')
    file.close()


def validConfigPath(value: str) -> str:
    """
    Checks if a full path is a valid path for a DSE or COE
    Will also check that the specified file can be opened for read
    :param value: Full path to the file
    """
    ival = os.path.exists(value)
    if not ival:
        raise IOError(f"{value} is not a valid path")

    __canReadFile__(value)

    return value


#########################
# DSE Param Constraints #
#########################
def checkParamConstraints(paramValues, constraints):
    for constraint in constraints:
        if not eval(replaceNamesWithQualifiedNames(paramValues, constraint)):
            return False

    return True


def replaceNamesWithQualifiedNames(paramValues, constraint):
    newConstraint = constraint

    for name in paramValues.keys():
        escapedName = re.escape(name) # we need to escape for regex searching to avoid any issues
        reString = f"(\\b({escapedName})\\b)|((?!\w)({escapedName})(?!\w))"
        # reString = f"\\b{name}\\b"
        newConstraint = re.sub(reString, f"paramValues['{name}']", newConstraint)

    return newConstraint


###########################
# Common Helper Functions #
###########################

# File Functions #

def dateTimeFolderName() -> str:
    return time.strftime("%Y_%m_%d_%H.%M.%S")


def makeDateTimeFolder(experimentPath: str, folderName: str) -> None:
    if not os.path.exists(experimentPath + folderName):
        os.makedirs(experimentPath + folderName)


def makeDirName(scenarioID: str, simParamVals: list)-> str:
    """
    Creates as a folder name for the current simulation
    :param scenarioID: Scenario to make a folder name for
    :param simParamVals: Parameters for this simulation
    :return: folder name as scenarioID followed by the param values _ separated sorted by keys
    """
    dirName = ""

    if len(scenarioID) > 0:
        dirName = scenarioID

    # Create a path name with scenarioID followed by the simulation params sorted by key _ separated
    return dirName + "_".join([str(simParamVals[k]) for k in sorted(simParamVals)])


# Simulation #
def defineRunAndEvaluateSimulation(parsedMultiModelJson: str, scenarioID, simParamVals, dseConfig, absoluteResultsPath,
                                   absoluteProjectPath, threaded=False, startDelay=0,
                                   coeEngineParams=["-u http://localhost", "-p 8082"], debugOutput=False) -> str:
    """
    Will create a folder for simulation results, run a simulation, and store the results in the folder
    :param parsedMultiModelJson:
    :param scenarioID: Name of the scenario
    :param simParamVals: Parameters for this simulation
    :param dseConfig: DSE json
    :param absoluteResultsPath: Absolute path to the results directory
    :param absoluteProjectPath: Absolute path to the project directory
    :param threaded: Are mutiple simulations being run in paralle
    :param startDelay: Recommended to use when threading to prevent overloading COE with requests
    :param coeEngineParams: Params used to connect to the COE, default is http://localhost:8082 and should be in the format ["-u [url]", "-p [port]"]
    :return: folder name containing simulation results
    note:: When mutiple simulation threads are being used it is the job of the caller to add simulation result directories to objectives.json
    """
    time.sleep(startDelay)

    # define the simulation
    (simFolder, filePath) = createOutputPath(scenarioID, simParamVals, absoluteResultsPath, debugOutput)
    createSimJson(parsedMultiModelJson, simParamVals, filePath, debugOutput)

    simFolderPath = os.path.join(absoluteResultsPath, simFolder)

    # run the simulation
    launchSimulation(simFolderPath, dseConfig, coeEngineParams, debugOutput)

    # evaluate the simulation
    evaluateSimulation(simFolder, simFolderPath, dseConfig, absoluteResultsPath, absoluteProjectPath, scenarioID, threaded, debugOutput)
    return simFolder


# Simulation - Setup #
def createOutputPath(scenarioID: str, simParamVals: list, absoluteResultsPath: str, debugOutput=True) -> (str, str):
    """
    Will create the output folder and generate the output file path
    :return: Tuple of (simulation Folder path, simulation output path)
    """
    simFolder = makeDirName(scenarioID, simParamVals)
    if debugOutput:
        print(f"\t\t\tOutput folder name: {simFolder}")

    path = os.path.join(absoluteResultsPath, simFolder)
    if not os.path.exists(os.path.join(absoluteResultsPath, simFolder)):
        os.makedirs(path)
        if debugOutput:
            print(f"\t\t\tFolder created at: {path}")

    filePath = os.path.join(path, DEFAULT_SIM_CONFIG)

    return (simFolder, filePath)


def createSimJson(parsedMultiModelJson, simParamVals, filePath: str, debugOutput=True) -> None:
    configParams = parsedMultiModelJson['parameters']
    for key in list(simParamVals.keys()):
        configParams[key] = simParamVals[key]

    jsonOutput = json.dumps(parsedMultiModelJson, sort_keys=True, indent=4, separators=(",", ":"))
    jsonOutputFile = open(filePath, 'w')

    jsonOutputFile.write(jsonOutput)
    jsonOutputFile.close()
    if debugOutput:
        print("\t\t\tConfig created")


# Simulation - Run #
def launchSimulation(simFolder: str, dseConfig, coeEngineParams=["-u http://localhost", "-p 8082"], debugOutput=True) -> None:
    if debugOutput:
        coeEngineParams.append("-d")

    thisPath = os.path.dirname(os.path.realpath(__file__))

    # subprocess.call(["python", os.path.join(thisPath, "..", "COE_handler_OneShot.py"), simFolder, dseConfig['simulation']['startTime'], dseConfig['simulation']['endTime'], *coeEngineParams])
    subprocess.call(["python", os.path.join(thisPath, "..", "COE_handler.py"), simFolder, dseConfig['simulation']['startTime'], dseConfig['simulation']['endTime'], *coeEngineParams])


# Simulation - Evaluation #
def evaluateSimulation(simFolder: str, simFolderPath: str, dseConfig, absoluteResultsPath: str, absoluteProjectPath: str, scenarioID: str, threaded=False, debugOutput=True) -> None:
    createObjectivesFile(simFolderPath, debugOutput)
    processObjectives(simFolderPath, dseConfig, debugOutput)
    processObjectiveExternalScripts(simFolderPath, dseConfig, absoluteProjectPath, scenarioID, debugOutput)
    if not threaded:
        # if we are single threaded then we add the folder ot the objectives json as we go
        # if we are threaded then it is the job of the caller to deal with adding the folders to the objectives.json file
        addSimulationDirToRankingFile(simFolder, absoluteResultsPath)


def createObjectivesFile(simFolder: str, debugOutput=True) -> None:
    emptyJson = {}
    objectivesFile = os.path.join(simFolder, OBJECTIVES_FILE)

    if debugOutput:
        print(f"\t\tCreated Objectives File: {objectivesFile}")

    with io.open(objectivesFile, "w", encoding="utf-8") as f:
        f.write(str(emptyJson))


def processObjectives(simFolder: str, dseConfig, debugOutput=True) -> None:
    if debugOutput:
        print("\t\tProcessing Objectives (default scripts)")

    for objectiveName in list(dseConfig["objectiveDefinitions"]["internalFunctions"].keys()):
        subprocess.call(["python", "Objective_simple", simFolder, dseConfig['objectiveDefinitions']['internalFunctions'][objectiveName]['columnID'], dseConfig['objectiveDefinitions']['internalFunctions'][objectiveName]['objectiveType'], objectiveName])


def processObjectiveExternalScripts(simFolder: str, dseConfig, absoluteProjectPath: str, scenarioId: str, debugOutput=True) -> None:
    """
    Process a simulation using an external script within the userMetricScripts folder
    :param simFolder: Path to the simulation folder
    :param dseConfig: Config of the dse
    :param absoluteProjectPath: Path to the project
    :param scenarioId: Id of this run
    """
    if debugOutput:
        print("\t\tProcessing Objectives (external scripts)")

    for objectiveName in list(dseConfig['objectiveDefinitions']['externalScripts'].keys()):
        # get the path to call the external script
        scriptFile = dseConfig['objectiveDefinitions']['externalScripts'][objectiveName]['scriptFile']
        scriptFilePath = os.path.join(absoluteProjectPath, USER_METRICS_FOLDER, scriptFile)
        scenarioFolderPath = os.path.join(absoluteProjectPath, USER_METRICS_FOLDER, scenarioId)
        callList = ["python", scriptFilePath, simFolder, objectiveName, scenarioFolderPath]

        # add the required params to the external ranking script arguments
        sortedParameterKeys = sorted(dseConfig['objectiveDefinitions']['externalScripts'][objectiveName]['scriptParameters'])
        parametersList = dseConfig['objectiveDefinitions']['externalScripts'][objectiveName]['scriptParameters']
        for parameter in sortedParameterKeys:
            callList.append(parametersList[parameter])

        if debugOutput:
            print(f"\t\t\tProcessing {scriptFile} with params")
            for item in callList:
                print(f"\t\t\t\t{item}")

        subprocess.call(callList)


def addSimulationDirToRankingFile(simFolder: str, absoluteResultsPath: str) -> None:
    """
    Adds simulation folder to the results json
    """
    rankingJson = {'simulations': []}

    # load the ranking.json file
    if os.path.isfile(os.path.join(absoluteResultsPath, RANKING_FILE)):
        jsonData = open(os.path.join(absoluteResultsPath, RANKING_FILE))
        rankingJson = json.load(jsonData)
        jsonData.close()

    # add the new folder to the json
    simulationsFolder = rankingJson['simulations']
    if simFolder not in simulationsFolder:
        simulationsFolder.append(simFolder)

    # write the data to the json file
    rankingString = json.dumps(rankingJson, sort_keys=True, indent=4, separators=(",", ":"))
    with io.open(os.path.join(absoluteResultsPath, RANKING_FILE), 'w', encoding="utf-8") as f:
        f.write(str(rankingString))


def addSimulationDirToRankingFileThreaded(folderNames, absoluteResutsPath: str) -> None:
    rankingJson = {"simulations": []}

    # load rankings.json file if it exists
    if os.path.isfile(os.path.join(absoluteResutsPath, RANKING_FILE)):
        jsonData = open(os.path.join(absoluteResutsPath, RANKING_FILE))
        rankingJson = json.load(jsonData)
        jsonData.close()

    # append the new folders
    simulationsFolder = rankingJson["simulations"]
    for simFolder in folderNames:
        if simFolder not in simulationsFolder:
            simulationsFolder.append(simFolder)  # should not be possible to get duplicate folder names

    # write to file
    rankingString = json.dumps(rankingJson, sort_keys=True, indent=4, separators=(",", ":"))
    with io.open(os.path.join(absoluteResutsPath, RANKING_FILE), "w", encoding="utf-8") as f:
        f.write(str(rankingString))


# Model Functions
def combineModelFiles(absoludeCOEConfigPath: str, dseConfig, absoluteProjectPath: str, debugOutput=True):
    if debugOutput:
        print("\t\t\tLoading and processing COE & MM's")

    # load and process COE
    with open(absoludeCOEConfigPath) as f:
        coeConfig = json.load(f)

    # open and process multimodel
    absMultiModelPath = os.path.join(absoluteProjectPath, multiModelPathURIToNormalPath(coeConfig['multimodel_path']))

    with open(absMultiModelPath) as f:
        multiModel = json.load(f)

    if debugOutput:
        print("\t\t\tConverting FMU's to URI's")

    makeFMUPathsURIs(multiModel['fmus'], absoluteProjectPath)

    if debugOutput:
        print("\t\t\tCombining")

    multiModel['algorithm'] = coeConfig['algorithm']

    dseConfig['simulation'] = {}
    dseConfig['simulation']['startTime'] = str(coeConfig['startTime'])
    dseConfig['simulation']['endTime'] = str(coeConfig['endTime'])

    return multiModel


def multiModelPathURIToNormalPath(multi_model_path: str) -> str:
    return multi_model_path.replace('\\', os.path.sep)


def makeFMUPathsAbsolute(fmusSection, absoluteProjectPath: str) -> None:
    for fmu in fmusSection:
        fmusSection[fmu] = absoluteProjectPath + os.path.sep + FMUS_FOLDER + os.path.sep + fmusSection[fmu]


def makeFMUPathsURIs(fmusSection, absoluteProjectPath: str) -> None:
    for fmu in fmusSection:
        tempPath = os.path.join(absoluteProjectPath, FMUS_FOLDER, fmusSection[fmu])
        fmusSection[fmu] = "file:///" + tempPath.replace(os.path.sep, '/')

#######################
# User output Helpers #
#######################

def printProgressBar(current: float, total: float, prefix="", suffix="", decimals=1, length=100, noFill='-', fill='#', printEnd="\r"):
    # https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    # f"{{0:.{decimals}f}}" makes the number of decimals shown variable as it will become "{:.2f}" for example
    percent = f"{{:.{decimals}f}}".format(100 * (current / float(total)))
    fillLength = int(length * current // total)
    bar = fill * fillLength + noFill * (length - fillLength)

    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=printEnd)

    if current == total:
        print()
