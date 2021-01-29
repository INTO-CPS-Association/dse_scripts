import random
from genetic.Ranking import ReverseRanking

def CreatePairs(organisms, selectionFunction, nPairs=0, *args) -> list[list[any]]:
    return selectionFunction(organisms, nPairs, *args)

def RandomSelection(organisms: list[(any, float, float)], nPairs=0) -> list[list[any]]:
    """
    Randomly selects mating pairs until nPairs is reached
    :param organisms: List of organisms to select from
    :param nPairs: Number of pairs to create, if nPairs is <= 0 then nPairs = len(organisms)
    :return: List of mating pairs
    """
    pairs = []
    nPairs = len(organisms) if nPairs <= 0 else nPairs

    while len(pairs) < nPairs:
        pairs.append([random.choice(organisms)[0], random.choice(organisms)[0]])

    return pairs

def RouletteWheel(rankedOrganisms: list[(any, float, float)], nPairs=0, minimiseFitness=False) -> list[list[any]]:
    """
    Selects mating pairs based on the roulette wheel algorithm
    :param rankedOrganisms: Dictionary of ranked organisms to choose from
    :param nPairs: Number of pairs to create, if nPairs is <= 0 then nPairs = len(rankedOrganism)
    :param minimiseFitness: Is the fitness value being minimised?
    :return: List of mating pairs
    """
    pairs = []
    nPairs = len(rankedOrganisms) if nPairs <= 0 else nPairs

    transformedRanking = rankedOrganisms
    if minimiseFitness:
        transformedRanking = ReverseRanking(rankedOrganisms)

    random.shuffle(transformedRanking)
    sumKeys = sum([k for _, k, _ in transformedRanking])

    while len(pairs) < nPairs:
        pair = []

        for i in range(2):
            picked = random.random() * sumKeys

            current = 0

            for v, k in transformedRanking:
                current += k
                if current > picked:
                    o = random.choice(v) if type(v) is list else v
                    pair.append(o)
                    break

        pairs.append(pair)

    return pairs

def Ranked(rankedOrganisms: list[(any, float, float)], nPairs=0) -> list[list[any]]:
    """
    Use ranked selection to create mating pairs
    :param rankedOrganisms: Organisms ranked via normalised ranking
    :param nPairs: Number of pairs to create, if nPairs is <= 0 then nPairs = len(rankedOrganism)
    :return:
    """
    if not set(range(0, len(rankedOrganisms))) == set([k for _, k, _ in rankedOrganisms]):
        raise ValueError("Organisms should use normalised ranking")

    return RouletteWheel(rankedOrganisms, nPairs, True)

def TournamentMin(rankedOrganisms: list[(any, float, float)], nPairs=0, tournamentSize=2) -> list[list[any, any]]:
    """
    Use tournament selection to create mating paris
    :param rankedOrganisms: Organisms ranked
    :param nPairs: Number of pairs to create, if nPairs is <= 0 then nPairs = len(rankedOrganism)
    :param tournamentSize: number of organisms that should compete per tournament
    :return:
    """
    nPairs = len(rankedOrganisms) if nPairs <= 0 else nPairs
    return Tournament(rankedOrganisms, nPairs, tournamentSize, min)

def TournamentMax(rankedOrganisms: list[(any, float, float)], nPairs=0, tournamentSize=2) -> list[list[any, any]]:
    """
    Use tournament selection to create mating paris
    :param rankedOrganisms: Organisms ranked
    :param nPairs: Number of pairs to create, if nPairs is <= 0 then nPairs = len(rankedOrganism)
    :param tournamentSize: number of organisms that should compete per tournament
    :return:
    """
    nPairs = len(rankedOrganisms) if nPairs <= 0 else nPairs
    return Tournament(rankedOrganisms, nPairs, tournamentSize, max)


def Tournament(rankedOrganisms: list[(any, float, float)], nPairs: float, tournamentSize: int, chooseFunction) -> list[list[any, any]]:
    pairs = []

    while len(pairs) < nPairs:
        pair = [
            chooseFunction(random.sample(rankedOrganisms, tournamentSize), key=lambda x: x[1])[0],
            chooseFunction(random.sample(rankedOrganisms, tournamentSize), key=lambda x: x[1])[0]
        ]

        pairs.append(pair)

    return pairs
