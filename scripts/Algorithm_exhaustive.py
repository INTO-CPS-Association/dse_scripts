import argparse
import itertools
from concurrent.futures.thread import ThreadPoolExecutor
import concurrent.futures
import random
from libs.Common import *

debugOutput = False

def runScript():
    # Get all the needed arguments
    args = scriptArguments().parse_args()
    basePath = args.projectpath
    dseRelativePath = args.dsepath
    coeRelativePath = args.coepath
    threads = args.t

    global debugOutput
    debugOutput = args.d

    try:
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    except (WindowsError, OSError) as e:
        print("Error changing path, exiting")
        exit(1)

    if debugOutput:
        print(f"Starting Exhaustive with: {basePath}, {dseRelativePath}, {coeRelativePath}")
    else:
        print("Starting Exhaustive DSE")

    timeScriptExecutionStart = time.time()

    # Get the paths to everything
    coePath = os.path.join(basePath, coeRelativePath)

    dsePathConfig = os.path.join(basePath, dseRelativePath)
    trimLocation = dsePathConfig.rfind(os.path.sep)
    dsePath = dsePathConfig[:trimLocation] + os.path.sep

    # load DSE
    if debugOutput:
        print("\t\tOpening DSE config")

    with open(dsePathConfig) as f:
        dseConfig = json.load(f)

    # load the MM's
    parsedMMJson = combineModelFiles(coePath, dseConfig, basePath, debugOutput)

    # output folder
    if debugOutput:
        print("\t\tCreating output folder")

    dateTimeFolder = dateTimeFolderName()
    makeDateTimeFolder(dsePath, dateTimeFolder)
    resultsPath = os.path.join(dsePath, dateTimeFolder)

    print(f"\t\tOutput folder created at {resultsPath}")

    # create combinations
    if debugOutput:
        print("\t\tCreating Combinations")
    viable = getAllViableParametersCombinations(getAllParameterCombinations(dseConfig['parameters']), dseConfig['parameterConstraints'])
    if debugOutput:
        print(f"\t\t\tFound {len(viable)} viable combinations")

    # simulate things
    print("\t\tStarting simulations...")
    timeSimulationsStart = time.time()
    iterateOverScenarios(dseConfig['scenarios'], viable, parsedMMJson, dseConfig, resultsPath, basePath, threads, [f"-u {args.u}", f"-p {args.p}"], debugOutput)
    timeSimulationsEnd = time.time()
    print("\t\tSimulations complete!")

    # rank things
    print("\t\tRanking results...")
    subprocess.call(["python", "Ranking_pareto.py", dsePath, dsePathConfig, resultsPath, "-d={}".format(debugOutput)])
    print("\t\tRanking finished")

    if not args.noHTML:
        print("\t\tGenerating HTML results page...")
        subprocess.call(["python", "Output_HTML.py", resultsPath])
        print("\t\tHTML results page generated")

    if not args.noCSV:
        print("\t\tGenerating CSV results file...")
        subprocess.call(["python", "Output_CSV.py", resultsPath])
        print("\t\tCSV results file generated")

    timeScriptExecutionEnd = time.time()

    print("\t\tTiming:")
    print(f"\t\t\tSimualtion Time: {(timeSimulationsEnd - timeSimulationsStart)}s")
    print(f"\t\t\tTotal Execution Time: {(timeScriptExecutionEnd - timeScriptExecutionStart)}s")


def getAllParameterCombinations(simParamValues):
    """
    Generate all parameter combinations for a given simulation
    :return: Array of parameter dictionary's
    """
    result = []

    for values in itertools.product(*map(simParamValues.get, simParamValues.keys())):
        result.append(dict(zip(simParamValues.keys(), values)))

    return result

def getAllViableParametersCombinations(paramCombinations, dseParamConstraints):
    """
    Finds all viable parameter combinations given combinations and dse constraints, also removed duplicate combinations
    :return: Array of parameter dictionary's
    """
    viableParameters = []

    for combination in paramCombinations:
        if checkParamConstraints(combination, dseParamConstraints) and (combination not in viableParameters):
            viableParameters.append(combination)

    return viableParameters

def iterateOverScenarios(scenarioList, parameterCombinations, multiModelJson, dseConfig, absResultsPath, basePath, threads, coeEngineConfig, debugOutput=False):
    if len(scenarioList) == 0:
        scenarioList = [""]

    for scenario in scenarioList:
        # output queue to ensure thread safety
        outputQ = []

        # print the simulations progress bar if we are not in debug mode
        iterations = 0
        if not debugOutput:
            printProgressBar(iterations, len(parameterCombinations), scenario)
        # threading
        with ThreadPoolExecutor(max_workers=threads) as executor:
            # upping the start of each thread to be 0-4 seconds apart fixed instability on my machine up to 15 concurrent threads
            sims = { executor.submit(defineRunAndEvaluateSimulation, multiModelJson, scenario, params, dseConfig, absResultsPath, basePath, threads > 1, random.random()*4 if threads > 1 else 0, coeEngineConfig, debugOutput): params for params in parameterCombinations }

            for result in concurrent.futures.as_completed(sims): # get the results as they are finished

                if not debugOutput: # move the progress bar once a sim has finished
                    iterations += 1
                    printProgressBar(iterations, len(parameterCombinations), scenario)

                outputQ.append(result.result())

        addSimulationDirToRankingFileThreaded(outputQ, absResultsPath)


def scriptArguments() -> argparse.ArgumentParser:
    # Setup argument parser so that the script is more user friendly
    parser = argparse.ArgumentParser(description="DSE Exhaustive search algorithm", prog="Algorithm Exhaustive")

    # required params
    parser.add_argument("projectpath", type=str, help="Full top level path to the project")
    parser.add_argument("dsepath", type=str, help="Path to DSE file (.dse.json) relative to projectpath")
    parser.add_argument("coepath", type=str, help="Path to COE settings file (coe.json) relative to projectpath")

    # optional params
    parser.add_argument("-t", type=validThreadCount, default=1, help="Max thread count (default: 1)")
    parser.add_argument("-noCSV", action="store_true", help="Dont Generate CSV output")
    parser.add_argument("-noHTML", action="store_true", help="Dont Generate HTML output")
    parser.add_argument("-u", type=str, default="http://localhost", help="URL to COE (default: http://localhost)")
    parser.add_argument("-p", type=validPortNumber, default=8082, help="Port for COE (default: 8082)")
    parser.add_argument("-d", action="store_true", help="Show debug output (default: False)")

    return parser


runScript()
