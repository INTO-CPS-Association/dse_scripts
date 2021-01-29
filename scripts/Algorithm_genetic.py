import argparse
import random
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from distutils.dir_util import copy_tree
from inspect import isfunction, getmembers

from genetic import Selection, Crossings, Mutation, World, DiversityControl
from genetic.OrganismValidation import CheckOrganismConstraints

from libs.Common import *

debugOutput = False

scenario = ""
baseResultPath = ""
basePath = ""
parsedMMJson = ""
dseConfig = ""
threads = 1
coeConfig = None
currentGen = 0

def runScript():
    args = ScriptArguments().parse_args()
    global basePath, threads, coeConfig
    basePath, dseRelativePath, coeRelativePath, threads, coeConfig = GetScriptArguments(args)

    try:
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    except (WindowsError, OSError) as e:
        print("Error changing path, exiting")
        exit(1)

    if debugOutput:
        print(f"Starting GA with: {basePath}, {dseRelativePath}, {coeRelativePath}")
    else:
        print("Starting GA DSE")

    coePath = os.path.join(basePath, coeRelativePath)
    dsePathConfig = os.path.join(basePath, dseRelativePath)
    dsePath = dsePathConfig[:dsePathConfig.rfind(os.path.sep)] + os.path.sep

    global dseConfig
    with open(dsePathConfig) as f:
        dseConfig = json.load(f)

    constraints = dseConfig["parameterConstraints"]
    dseParams = dseConfig["parameters"]
    global parsedMMJson
    parsedMMJson = combineModelFiles(coePath, dseConfig, basePath, debugOutput)

    if "geneticArguments" not in dseConfig.keys():
        raise ValueError("geneticArguments is not found in DSE config exiting")

    if "popSize" not in dseConfig["geneticArguments"].keys():
        raise ValueError("popSize is not found in DSE config exiting")

    initialOrganisms = createInitialPopulation(dseConfig["geneticArguments"]["popSize"], dseParams, constraints)

    dateTimeFolder = dateTimeFolderName()
    makeDateTimeFolder(dsePath, dateTimeFolder)
    global baseResultPath
    baseResultPath = os.path.join(dsePath, dateTimeFolder)

    scenarioSettings, maxGenerations, useRawRanking, selectionFunction, selectionFunctionArgs, crossingFunction, crossingFunctionArgs, mutationFunction, mutateChance, scaleMutation, mutationFunctionArgs, rankingFunctionArgs, elitismKeep, diversityFunction, diverstiyArgs = GetGAArgsFromDSE(dseConfig)
    World.debugOutput = debugOutput

    dseScenarios = dseConfig["scenarios"] if "scenarios" in dseConfig.keys() and len(dseConfig["scenarios"]) >= 1 else [""]

    for dseScenario in dseScenarios:
        global scenario
        scenario = dseScenario

        w = scenarioSettings[0]

        if len(scenarioSettings) == 1:
            w(maxGenerations, initialOrganisms, constraints, OrganismFitness, rankingFunctionArgs=rankingFunctionArgs,
                     useRawRanking=useRawRanking, selectionFunction=selectionFunction,
                     selectionFunctionArgs=selectionFunctionArgs, crossingFunction=crossingFunction,
                     crossingFunctionArgs=crossingFunctionArgs, mutationFunction=mutationFunction,
                     mutationProbability=mutateChance, scaleMutationProbability=scaleMutation,
                     mutationFunctionArgs=mutationFunctionArgs, elitismKeepPercent=elitismKeep,
                     preRankFunction=RunCOESim, diversityFunction=diversityFunction, diversityFunctionArgs=diverstiyArgs)
        else:
            w(scenarioSettings[1], scenarioSettings[2],
                     maxGenerations, initialOrganisms, constraints, OrganismFitness, rankingFunctionArgs=rankingFunctionArgs,
                     useRawRanking=useRawRanking, selectionFunction=selectionFunction,
                     selectionFunctionArgs=selectionFunctionArgs, crossingFunction=crossingFunction,
                     crossingFunctionArgs=crossingFunctionArgs, mutationFunction=mutationFunction,
                     mutationProbability=mutateChance, scaleMutationProbability=scaleMutation,
                     mutationFunctionArgs=mutationFunctionArgs, elitismKeepPercent=elitismKeep,
                     preRankFunction=RunCOESim, diversityFunction=diversityFunction, diversityFunctionArgs=diverstiyArgs)

    print("Generating Pareto Ranking")
    GenerateResultsJson(dseScenarios)
    subprocess.call(["python", "Ranking_pareto.py", dsePath, dsePathConfig, baseResultPath, "-d={}".format(debugOutput)])

    if not args.noHTML:
        print("\t\tGenerating HTML results page")
        subprocess.call(["python", "Output_HTML.py", baseResultPath])

    if not args.noCSV:
        print("\t\tGenerating CSV results page")
        subprocess.call(["python", "Output_CSV.py", baseResultPath])


def OrganismFitness(organism, resultParam):
    organismName = makeDirName(scenario, organism)
    resultPath = os.path.join(baseResultPath, f"{scenario}-{currentGen}" if not scenario == "" else str(currentGen))
    with open(os.path.join(resultPath, organismName, "objectives.json"), "r") as f:
        j = json.load(f)
        fitness = j[resultParam]

    if not os.path.exists(os.path.join(resultPath, "../GAResults.json")):
        with open(os.path.join(resultPath, "../GAResults.json"), "w", encoding="utf-8") as r:
            pass

    # write everything to a results file
    with open(os.path.join(resultPath, "../GAResults.json"), "r+", encoding="utf-8") as r:
        try:
            rj = json.load(r)
            r.seek(0)
        except json.decoder.JSONDecodeError:
            rj = {}
        gen = resultPath.split("\\")[-1]

        if gen in rj.keys():
            if str(fitness) in rj[gen].keys():
                rj[gen][str(fitness)].append(organism)
            else:
                rj[gen][fitness] = [organism]
        else:
            rj[gen] = {fitness: [organism]}

        json.dump(rj, r, indent=4)
        r.truncate()

    return fitness

def RunCOESim(generation, organisms):
    global currentGen
    currentGen = generation

    resultPath = os.path.join(baseResultPath, f"{scenario}-{generation}" if not scenario == "" else str(generation))

    # get only the distinct organisms to simulate in each generation otherwise we will run into problems eventually
    # has to be done sequentially annoyingly
    orgsToSimulate = []
    for organism in organisms:
        if organism not in orgsToSimulate:
            orgsToSimulate.append(organism)

    # Do some DP stuff so we can potentially cut down on amount of actual simulation
    if not generation == 0:
        with open(os.path.join(resultPath, "../GAResults.json"), "r") as f:
            resJson = json.load(f)

        with ThreadPoolExecutor(max_workers=threads) as executor:
            sims = { executor.submit(FindPreviousOrganisms, organism, generation, resJson, resultPath, scenario, baseResultPath): organism for organism in orgsToSimulate }

            for result in as_completed(sims):
                if debugOutput:
                    print(f"Found match in previous generation: {result.result()}")

    outputQ = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        sims = { executor.submit(defineRunAndEvaluateSimulation, parsedMMJson, scenario, organism, dseConfig, resultPath, basePath, threads > 1, random.random() * 4 if threads > 1 else 0, coeConfig, debugOutput): organism for organism in orgsToSimulate }

        for result in as_completed(sims):
            outputQ.append(result.result())

    addSimulationDirToRankingFileThreaded(outputQ, resultPath)

def FindPreviousOrganisms(organism, generation, resJson, resultPath, scenario, baseResultPath):
    foundGeneration = -1
    # find the organism if it exists
    for gen in resJson.items():
        for genVals in gen[1].values():
            if organism in genVals:
                foundGeneration = gen[0]
                break
        if not foundGeneration == -1:
            break

    if not foundGeneration == -1 and not os.path.exists(os.path.join(resultPath, makeDirName(scenario, organism))):
        foundOrganismPath = os.path.join(baseResultPath, foundGeneration, makeDirName(scenario, organism))
        copy_tree(foundOrganismPath, os.path.join(resultPath, makeDirName(scenario, organism)))

    if not foundGeneration == -1 and debugOutput:
        print(f"\t\t\tFound {organism} from generation {generation} in previous generation {foundGeneration}")

def createInitialPopulation(nOrgs, initialParams, constraints):
    organisms = []

    for i in range(nOrgs):

        while True:
            organism = {}
            for k in initialParams:
                sortedInitialParams = sorted(initialParams[k])
                organism[k] = random.random() * (sortedInitialParams[1] - sortedInitialParams[0]) + sortedInitialParams[0]

            if CheckOrganismConstraints(organism, constraints):
                break

        organisms.append(organism)

    return organisms

def GetScriptArguments(args):
    basePath = args.projectpath
    dseRelativePath = args.dsepath
    coeRelativePath = args.coepath
    threads = args.t

    coeConfig = [f"-u {args.u}", f"-p {args.p}"]

    global debugOutput
    debugOutput = args.d

    return basePath, dseRelativePath, coeRelativePath, threads, coeConfig

def GetGAArgsFromDSE(dseJson):
    """
    Gets the arguments from the DSE config and returns the formatted values ready to input into a GA
    :param dseJson: DSE Config as JSON
    :return:
    """
    geneticArgs = dseJson["geneticArguments"]

    if "scenario" not in geneticArgs.keys():
        raise ValueError("You must choose a scenario from nGens, Convergence, or Fitness")

    maxGenerations = geneticArgs["maxGenerations"]

    if geneticArgs["scenario"].lower() == "ngens":
        worldSettings = [World.nGenerations]
    elif geneticArgs["scenario"].lower() in ["convergence", "fitness"]:
        world = World.ConvergenceStopping

        if "scenarioArgs" not in geneticArgs.keys():
            raise ValueError("Please provide world specific arguments in \"scenarioArgs\": [deviation, convergence generation]")

        if not len(geneticArgs["scenarioArgs"]) == 2:
            raise ValueError(f"Incorrect number of scenario arguments given expected 2 got {len(geneticArgs['scenarioArgs'])}")

        arg1 = geneticArgs["scenarioArgs"][0]
        arg2 = geneticArgs["scenarioArgs"][1]

        if geneticArgs["scenario"].lower() == "convergence" and maxGenerations < arg2:
            raise ValueError(f"Convergence generations greater than maximum generations, max generations: {maxGenerations}, convergence: {arg2}")
        elif geneticArgs["scenario"].lower() == "fitness" and arg2 > 1 or arg2 < 0:
            raise ValueError(f"Fitness threshold not possible given {arg2} expected a number between 0 and 1 inclusive")

        worldSettings = [world, arg1, arg2]
    else:
        raise ValueError(f"{geneticArgs['scenario']} is not a recognised scenario. Please choose from nGens, Convergence, or Fitness")

    useRawRanking = geneticArgs["useRawRanking"] if "useRawRanking" in geneticArgs.keys() else False

    selectionFunctions = { name.lower():f for name, f in getmembers(Selection, isfunction) }
    # selectionFunctions = { "ranked": Selection.Ranked, "random": Selection.RandomSelection, "roulette": Selection.RouletteWheel, "tournamentmin": Selection.TournamentMin, "tournamentmax": Selection.TournamentMax}
    selectionFunction = selectionFunctions[geneticArgs["selectionFunction"].lower()] if "selectionFunction" in geneticArgs.keys() else Selection.Ranked
    selectionFunctionArgs = geneticArgs["selectionFunctionArgs"] if "selectionFunctionArgs" in geneticArgs.keys() else None

    crossingFunctions = {name.lower(): f for name, f in getmembers(Crossings, isfunction)}
    # crossingFunctions = { "sbx": Crossings.SBX, "blx": Crossings.BLX, "uniform": Crossings.UniformCrossing, "npoint": Crossings.NPointCrossing }
    crossingFunction = crossingFunctions[geneticArgs["crossingFunction"].lower()] if "crossingFunction" in geneticArgs.keys() else Crossings.SBX
    crossingFunctionArgs = geneticArgs["crossingFunctionArgs"] if "crossingFunctionArgs" in geneticArgs.keys() else []

    if crossingFunction is Crossings.SBX or crossingFunction is Crossings.BLX:
        crossingFunctionArgs.insert(0, dseJson["parameterConstraints"])

    mutationFunctions = {name.lower(): f for name, f in getmembers(Mutation, isfunction)}
    # mutationFunctions = { "abs": Mutation.MutateAbsNormal, "rel": Mutation.MutateRelNormal }
    mutationFunction = mutationFunctions[geneticArgs["mutationFunction"].lower()] if "mutationFunction" in geneticArgs.keys() else Mutation.MutateRelNormal
    mutateChance = geneticArgs["mutationChance"] if "mutationChance" in geneticArgs.keys() else 0.2
    scaleMutation = geneticArgs["scaleMutation"] if "scaleMutation" in geneticArgs.keys() else True
    mutationFunctionArgs = geneticArgs["mutationFunctionArgs"] if "mutationFunctionArgs" in geneticArgs.keys() else None

    rankingFunctionArgs = geneticArgs["rankingFunctionArgs"] if "rankingFunctionArgs" in geneticArgs.keys() else [True]

    elitismKeep = geneticArgs["elitismKeep"] if "elitismKeep" in geneticArgs.keys() else 0.1

    diversityFunctions = {name.lower(): f for name, f in getmembers(DiversityControl, isfunction)}
    diversityFunctions["none"] = None
    # diversityFunctions = {"euler": DiversityControl.EulerDistance, "none": None}
    diversityFunction = diversityFunctions[geneticArgs["diversityFunction"].lower()] if "diversityFunction" in geneticArgs.keys() else DiversityControl.EulerDistance
    diverstiyArgs = geneticArgs["diversityFunctionArgs"] if "diversityFunctionArgs" in geneticArgs.keys() else []

    return worldSettings, maxGenerations, useRawRanking, selectionFunction, selectionFunctionArgs, crossingFunction, crossingFunctionArgs, mutationFunction, mutateChance, scaleMutation, mutationFunctionArgs, rankingFunctionArgs, elitismKeep, diversityFunction, diverstiyArgs

def GenerateResultsJson(scenarios):
    rankingJson = {"simulations": []}
    for s in scenarios:
        for g in range(currentGen):
            genrationName = f"{s}-{g}" if not s == "" else str(g)

            with open(os.path.join(baseResultPath, genrationName, "ranking.json"), "r") as f:
                rankingJson["simulations"].extend([os.path.join(genrationName, sim) for sim in json.load(f)["simulations"]])

    rankingJson["simulations"] = list(set(rankingJson["simulations"]))

    with open(os.path.join(baseResultPath, "ranking.json"), "w+") as f:
        json.dump(rankingJson, f)


def ScriptArguments():
    # Setup argument parser so that the script is more user friendly
    parser = argparse.ArgumentParser(description="DSE using a genetic algorithm", prog="Algorithm Genetic")

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
    parser.add_argument("-d", action="store_true", help="Show debug output")

    return parser


runScript()
