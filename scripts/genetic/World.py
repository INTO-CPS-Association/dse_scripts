import typing
import numpy

from genetic import Elitism, Crossings, Mutation, Selection, Ranking, DiversityControl

debugOutput = False

def RunGASteps(generation: int, organisms: list, constraints: list, normalRanking=None, rawRank=None, rankingFunction=None, useRawRanking=False, diversityFunction=None, diversityFunctionArgs=None, selectionFunction=Selection.Ranked, crossingFunction=Crossings.SBX, mutationFunction=Mutation.MutateRelNormal, mutationProbability=0.2, elitismKeepPercent=0.1, selectionFunctionArgs=None, crossingFunctionArgs=None, mutationFunctionArgs=None, rankingFunctionArgs=None):
    """
    Run a single generation of the GA
    """
    # normal ga stuff
    if rankingFunction is not None:
        passed = {}
        if rankingFunctionArgs is None:
            rankingFunctionArgs = [True]
            passed["fitnessArgs"] = []
        else:
            passed["fitnessArgs"] = rankingFunctionArgs[1:]

        if diversityFunctionArgs is None:
            passed["diversityArgs"] = []
        else:
            passed["diversityArgs"] = diversityFunctionArgs

        normalRanking, rawRank = Ranking.Rank(organisms, rankingFunction, diversityFunction=diversityFunction, highToLow=rankingFunctionArgs[0], **passed)

    if useRawRanking:
        ranking = rawRank
    else:
        ranking = normalRanking

    # Fix the parameters so we dont get errors later
    if selectionFunctionArgs is None:
        selectionFunctionArgs = []

    if crossingFunctionArgs is None:
        crossingFunctionArgs = []

    if mutationFunctionArgs is None:
        mutationFunctionArgs = []

    # if selectionFunction is Selection.RandomSelection:
    #     breedingPairs = Selection.CreatePairs(ranking, selectionFunction)
    # else:
    breedingPairs = Selection.CreatePairs(ranking, selectionFunction, *selectionFunctionArgs)

    organisms = Crossings.CreateChildren(breedingPairs, crossingFunction, *crossingFunctionArgs)
    organisms = Mutation.MutateOrganisms(organisms, mutationProbability, constraints, mutationFunction, *mutationFunctionArgs)

    organisms = Elitism.KeepBest(rawRank, organisms, elitismKeepPercent, *rankingFunctionArgs)

    return organisms

def nGenerations(nGenerations: int, initialGeneration: list, constraints: list, rankingFunction: typing.Callable, useRawRanking=False, diversityFunction=DiversityControl.EulerDistance, diversityFunctionArgs=None, selectionFunction=Selection.Ranked, crossingFunction=Crossings.SBX, mutationFunction=Mutation.MutateRelNormal, mutationProbability=0.2, scaleMutationProbability=True, elitismKeepPercent=0.1, selectionFunctionArgs=None, crossingFunctionArgs=None, mutationFunctionArgs=None, rankingFunctionArgs=None, preRankFunction=None):
    """
    Run the GA for nGenerations
    :param diversityFunction: Diversity Function to use
    :param diversityFunctionArgs: Arguments to pass to diversity function
    :param nGenerations: Number of generations to run the algorithm for
    :param initialGeneration: Initial population for the GA
    :param constraints: Constraints on GA organisms
    :param rankingFunction: Ranking function to use
    :param useRawRanking: Should the raw ranking be used?
    :param selectionFunction: Selection function to use
    :param crossingFunction: Crossing function to use
    :param mutationFunction: Mutation function to use
    :param mutationProbability: Mutation probability between 0 and 1 inclusive
    :param scaleMutationProbability: Scale mutation probability?
    :param elitismKeepPercent: Keep % of best organisms from previous generation between 0 and 1 inclusive
    :param selectionFunctionArgs: Selection function arguments
    :param crossingFunctionArgs: Crossing function arguments
    :param mutationFunctionArgs: Mutation function arguments
    :param rankingFunctionArgs: Ranking function arguments
    :param preRankFunction: Any function that should be run before ranking, passed the generation and current organism list
    :return: Ranked final generation
    """
    if rankingFunctionArgs is None:
        rankingFunctionArgs = [True]

    organisms = initialGeneration
    originalMutationProbability = mutationProbability

    for i in range(nGenerations):
        print(f"\tStarting generation {i}")

        if scaleMutationProbability:
            mutationProbability = (1-(float(i)/float(nGenerations))) * originalMutationProbability

        if preRankFunction is not None:
            preRankFunction(i, organisms)

            if i == nGenerations - 1:
                break

        organisms = RunGASteps(i, organisms, constraints, diversityFunction=diversityFunction, diversityFunctionArgs=diversityFunctionArgs, rankingFunction=rankingFunction, useRawRanking=useRawRanking, selectionFunction=selectionFunction, crossingFunction=crossingFunction, mutationFunction=mutationFunction, mutationProbability=mutationProbability, elitismKeepPercent=elitismKeepPercent, selectionFunctionArgs=selectionFunctionArgs, crossingFunctionArgs=crossingFunctionArgs, mutationFunctionArgs=mutationFunctionArgs, rankingFunctionArgs=rankingFunctionArgs)

    return PrintResults(organisms, rankingFunction, *rankingFunctionArgs)

def FitnessStopping(fitnessThreshold: float, percentRequired: float, maxGenerations: int, initialGeneration: list, constraints: list, rankingFunction: typing.Callable, useRawRanking=False, diversityFunction=DiversityControl.EulerDistance, diversityFunctionArgs=None, selectionFunction=Selection.Ranked, crossingFunction=Crossings.SBX, mutationFunction=Mutation.MutateRelNormal, mutationProbability=0.2, scaleMutationProbability=True, elitismKeepPercent=0.1, selectionFunctionArgs=None, crossingFunctionArgs=None, mutationFunctionArgs=None, rankingFunctionArgs=None, preRankFunction=None):
    """
    Run the GA until a specified fitness is reached or until the maximum iterations ahs been reached
    :param fitnessThreshold: Minimum threshold fitness
    :param percentRequired: % Organisms required to pass between 0 and 1 inclusive
    :param maxGenerations: Maximum number of generations to run the algorithm for
    :param diversityFunction: Diversity Function to use
    :param diversityFunctionArgs: Arguments to pass to diversity function
    :param initialGeneration: Initial population for the GA
    :param constraints: Constraints on GA organisms
    :param rankingFunction: Ranking function to use
    :param useRawRanking: Should the raw ranking be used?
    :param selectionFunction: Selection function to use
    :param crossingFunction: Crossing function to use
    :param mutationFunction: Mutation function to use
    :param mutationProbability: Mutation probability between 0 and 1 inclusive
    :param scaleMutationProbability: Scale mutation probability?
    :param elitismKeepPercent: Keep % of best organisms from previous generation between 0 and 1 inclusive
    :param selectionFunctionArgs: Selection function arguments
    :param crossingFunctionArgs: Crossing function arguments
    :param mutationFunctionArgs: Mutation function arguments
    :param rankingFunctionArgs: Ranking function arguments
    :param preRankFunction: Any function that should be run before ranking, passed the generation and current organism list
    :return: Ranked final generation
    """
    organisms = initialGeneration
    originalMutationProbability = mutationProbability

    passed = {}
    if rankingFunctionArgs is None:
        rankingFunctionArgs = [True]
        passed["fitnessArgs"] = []
    else:
        passed["fitnessArgs"] = rankingFunctionArgs[1:]

    if diversityFunctionArgs is None:
        passed["diversityArgs"] = []
    else:
        passed["diversityArgs"] = rankingFunctionArgs

    if rankingFunctionArgs is None:
        rankingFunctionArgs = []

    rankingDirection = rankingFunctionArgs[0] if len(rankingFunctionArgs) != 0 else True
    generations = 0

    while True:
        print(f"\tStarting generation {generations}")

        if preRankFunction is not None:
            preRankFunction(generations, organisms)

            if generations == maxGenerations - 1:
                break

        # we only need to calculate the fitness/ranking once so do it here and pass it to the function
        normalRanking, rawRank = Ranking.Rank(organisms, rankingFunction, diversityFunction=diversityFunction, highToLow=rankingFunctionArgs[0], **passed)

        thresholdOrganisms = 0
        if scaleMutationProbability:
            mutationProbability = (1-(float(generations)/float(maxGenerations))) * originalMutationProbability

        for k in [k for _, _, k in rawRank]:
            if (k >= fitnessThreshold and rankingDirection) or (k <= fitnessThreshold and not rankingDirection):
                thresholdOrganisms += 1

        if thresholdOrganisms >= (len(organisms) * percentRequired) or generations == maxGenerations:
            print(f"Stopped after {generations} generations, {thresholdOrganisms} organisms have passed the threshold out of {len(organisms)} organisms ({(float(thresholdOrganisms)/float(len(organisms))) * 100}%). The mean fitness is {sum([k for _, _, k in rawRank]) / len(rawRank)}")
            break

        organisms = RunGASteps(generations, organisms, constraints, rankingFunction=None, normalRanking=normalRanking, rawRank=rawRank, useRawRanking=useRawRanking, selectionFunction=selectionFunction, crossingFunction=crossingFunction, mutationFunction=mutationFunction, mutationProbability=mutationProbability, elitismKeepPercent=elitismKeepPercent, selectionFunctionArgs=selectionFunctionArgs, crossingFunctionArgs=crossingFunctionArgs, mutationFunctionArgs=mutationFunctionArgs, rankingFunctionArgs=rankingFunctionArgs)
        generations += 1

    return PrintResults(organisms, rankingFunction, *rankingFunctionArgs)

def ConvergenceStopping(convergenceDeviation: float, convergenceGenerations: int, maxGenerations: int, initialGeneration: list, constraints: list, rankingFunction: typing.Callable, useRawRanking=False, diversityFunction=DiversityControl.EulerDistance, diversityFunctionArgs=None, selectionFunction=Selection.Ranked, crossingFunction=Crossings.SBX, mutationFunction=Mutation.MutateRelNormal, mutationProbability=0.2, scaleMutationProbability=True, elitismKeepPercent=0.1, selectionFunctionArgs=None, crossingFunctionArgs=None, mutationFunctionArgs=None, rankingFunctionArgs=None, preRankFunction=None):
    """
    Run the GA until convergence is reached or until the maximum iterations ahs been reached
    :param convergenceDeviation: Deviation required to consider as converged
    :param convergenceGenerations: Number of sequential generations to consider when looking for convergence
    :param maxGenerations: Maximum number of generations to run the algorithm for
    :param initialGeneration: Initial population for the GA
    :param constraints: Constraints on GA organisms
    :param diversityFunction: Diversity Function to use
    :param diversityFunctionArgs: Arguments to pass to diversity function
    :param rankingFunction: Ranking function to use
    :param useRawRanking: Should the raw ranking be used?
    :param selectionFunction: Selection function to use
    :param crossingFunction: Crossing function to use
    :param mutationFunction: Mutation function to use
    :param mutationProbability: Mutation probability between 0 and 1 inclusive
    :param scaleMutationProbability: Scale mutation probability?
    :param elitismKeepPercent: Keep % of best organisms from previous generation between 0 and 1 inclusive
    :param selectionFunctionArgs: Selection function arguments
    :param crossingFunctionArgs: Crossing function arguments
    :param mutationFunctionArgs: Mutation function arguments
    :param rankingFunctionArgs: Ranking function arguments
    :param dseArgs: DSE arguments
    :return: Ranked final generation
    """
    organisms = initialGeneration
    originalMutationProbability = mutationProbability

    if rankingFunctionArgs is None:
        rankingFunctionArgs = []

    passed = { "fitnessArgs": rankingFunctionArgs }

    if diversityFunctionArgs is None:
        passed["diversityArgs"] = []
    else:
        passed["diversityArgs"] = rankingFunctionArgs

    generations = 0
    averageRanks = []

    while True:
        print(f"\tStarting generation {generations}")
        if preRankFunction is not None:
            preRankFunction(generations, organisms)

            if generations == maxGenerations - 1:
                break

        # we only need to calculate the fitness/ranking once so do it here and pass it to the function
        normalRanking, rawRank = Ranking.Rank(organisms, rankingFunction, diversityFunction=diversityFunction, highToLow=rankingFunctionArgs is [], **passed)

        if len(averageRanks) == convergenceGenerations:
            averageRanks.pop(0)

        averageRanks.append(sum([k for _, _, k in rawRank]) / len(rawRank))

        if len(averageRanks) == convergenceGenerations and numpy.std(averageRanks) <= convergenceDeviation or generations == maxGenerations:
            print(f"Stopped after {generations} generations, with a deviation of {numpy.std(averageRanks)} and final generation with an average fitness of {averageRanks[-1]}")
            break

        if scaleMutationProbability:
            mutationProbability = (1-(float(generations)/float(maxGenerations))) * originalMutationProbability

        organisms = RunGASteps(generations, organisms, constraints, rankingFunction=None, normalRanking=normalRanking, rawRank=rawRank, useRawRanking=useRawRanking, selectionFunction=selectionFunction, crossingFunction=crossingFunction, mutationFunction=mutationFunction, mutationProbability=mutationProbability, elitismKeepPercent=elitismKeepPercent, selectionFunctionArgs=selectionFunctionArgs, crossingFunctionArgs=crossingFunctionArgs, mutationFunctionArgs=mutationFunctionArgs, rankingFunctionArgs=rankingFunctionArgs)
        generations += 1

    return PrintResults(organisms, rankingFunction, *rankingFunctionArgs)

def PrintResults(finalOrganisms, rankingFunction, highToLow=True, *rankingFunctionArgs):
    ranked = []
    for org in finalOrganisms:
        ranked.append((org, rankingFunction(org, *rankingFunctionArgs)))

    ranked = sorted(ranked, key=lambda x: x[1], reverse=highToLow)

    print("Results:")
    print(f"\tMean Rank: {numpy.mean([k for _, k in ranked])}")
    print(f"\tStd Dev: {numpy.std([k for _, k in ranked])}")
    print(f"\tBest: {ranked[0]}")
    print(f"\tWorst: {ranked[-1]}")

    return ranked
