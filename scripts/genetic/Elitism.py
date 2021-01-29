from math import floor
from random import random, shuffle


def KeepBest(rankedPreviousGeneration: list[(any, float, float)], newGeneration: list[any], percentToKeep: float, highToLow=True, *_) -> list:
    """
    Will keep the top n% of organisms from the previous generation and insert them into the next generation
    :param rankedPreviousGeneration: Raw ranking of the previous generation
    :param newGeneration: The next generation
    :param percentToKeep: % of organisms to keep (0 - 1)
    :return: newGeneration with top performers inserted
    """

    if percentToKeep > 1 or percentToKeep < 0:
        raise ValueError(f"Percentage of organisms to keep should be between 0 and 1, given {percentToKeep}")

    nToKeep = floor(len(newGeneration) * percentToKeep)

    if nToKeep == 0:
        shuffle(newGeneration)
        return newGeneration # stuff below this is computationally expensive so lets not do it if we dont have to :)

    # sort by raw fitness -> take top % -> map (org, diversity fitness, raw fitness)>org
    kept = list(map(lambda x: x[0], sorted(rankedPreviousGeneration, key=lambda x: x[2], reverse=highToLow)[:nToKeep]))

    for i in range(nToKeep):
        newGeneration.pop(floor(random() * len(newGeneration)))

    newGeneration.extend(kept)
    shuffle(newGeneration)

    return newGeneration
