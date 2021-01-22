def Rank(organisms, fitnessFunction, diversityFunction=None, highToLow=True, **kwargs) -> (list[(any, float, float)], list[(any, float, float)]):
    """
    Will rank a given list of organisms by a given fitness function
    :param organisms: List of organisms to rank
    :param fitnessFunction: Fitness function with the signature f(organism, *extraFitnessArgs)
    :param highToLow: Higher values are more fit?
    :param kwargs: Extra arguments to pass to the fitness & diversity functions if required
    :return:
    """
    rawRank = FitnessBasedRanking(organisms, fitnessFunction, *kwargs["fitnessArgs"])
    if diversityFunction is not None:
        rawRank = diversityFunction(rawRank, highToLow, *kwargs["diversityArgs"])
    normalRank = NormalisedRanking(rawRank, highToLow)
    return normalRank, rawRank

def FitnessBasedRanking(organisms, fitnessFunction, *extraFitnessArgs) -> list[(any, float, float)]:
    """
    Will rank a given list of organisms by a given fitness function
    :param organisms: List of organisms to rank
    :param fitnessFunction: Fitness function with the signature f(organism, *extraFitnessArgs)
    :param extraFitnessArgs: Extra arguments to pass to the fitness function if required
    :return:
    """
    temp = [(org, fitnessFunction(org, *extraFitnessArgs)) for org in organisms]
    return [(org, f, f) for org, f in temp]

def NormalisedRanking(fitnessRankedOrganisms: list, highToLow=True) -> list[(any, float, float)]:
    """
    Will normalise ranking between 1 and N where N is the number of organisms, each organism wil have a unique ranking
    :param fitnessRankedOrganisms: Organisms ranked with fitness function
    :param highToLow: Higher values are more fit?
    :return:
    """
    rank = 0
    sortedRanking = sorted(fitnessRankedOrganisms, key=lambda x: x[1], reverse=highToLow)
    ranked = []

    for organism in sortedRanking:
        ranked.append((organism[0], rank, organism[2]))
        rank += 1

    return ranked

def ReverseRanking(rankedOrganisms: list[(any, float, ...)]) -> list[(any, float)]:
    """
    Reverses ranking such that the highest ranking value becomes the fittest organism
    :param rankedOrganisms: Organisms ranked using NormalisedRanking
    :return:
    """
    s = sorted(rankedOrganisms, key=lambda x: x[1])
    rs = sorted(rankedOrganisms, key=lambda x: x[1], reverse=True)

    result = []

    for i in range(len(s)):
        result.append((s[i][0], rs[i][1]))

    return result

