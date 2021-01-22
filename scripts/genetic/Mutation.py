import json
import random
import typing
import copy

############################
# Basic Mutation Operators #
############################

# Random #
from genetic import OrganismValidation


def MutateFloat(mutationChance: float, originalValue: float, min: float, max: float) -> float:
    """
    Mutate a floating point value between a minimum and maximum value
    :param mutationChance: Chance to mutate the value, should be between 0-1
    :param originalValue: Original value of the gene
    :param min: Minimum result
    :param max: Maximum result
    :return: A mutated value
    """
    if mutationChance < 0 or mutationChance > 1:
        raise ValueError(f"Mutation chance must be between 0 and 1, given {mutationChance}")

    mutation = random.random()

    if mutation <= mutationChance:
        return random.uniform(min, max)

    return originalValue


def MutateInt(mutationChance: float, originalValue: int, min: int, max: int) -> int:
    """
    Mutate an int value in a range
    :param mutationChance: Chance to mutate value, should be between 0-1
    :param originalValue: Original gene value
    :param min: Minimum value in the range
    :param max: Maximum value in the range
    :return: A mutated value
    """
    if mutationChance < 0 or mutationChance > 1:
        raise ValueError(f"Mutation chance must be between 0 and 1, given {mutationChance}")
    mutation = random.random()

    if mutation <= mutationChance:
        return random.randrange(min, max)

    return originalValue

def MutateList(mutationChance: float, originalValue, valueList: list):
    """
    Mutate a value by selecting from a list
    :param mutationChance: Chance to mutate, should be between 0-1
    :param originalValue: Original gene value
    :param valueList: List to choose from, should contain original value
    :return: A mutated value
    """
    if mutationChance < 0 or mutationChance > 1:
        raise ValueError(f"Mutation chance must be between 0 and 1, given {mutationChance}")

    if originalValue not in valueList:
        raise ValueError(f"Original value should be in list Original: {originalValue} List: {valueList}")

    mutation = random.random()

    if mutation <= mutationChance:
        return random.choice(valueList)

    return originalValue

# Normal Distribution #
def MutateAbsNormal(mutationProbability: float, originalValue: float, sigma=0.2) -> float:
    """
    Mutate a gene relative to an absolute normal distribution
    :param mutationProbability: Probability of mutation, should be between 0 and 1, values >= 1 means always mutate values <= 0 means never mutate
    :param originalValue: Original gene value
    :param sigma: Sigma value for normal distribution
    :return: Mutated gene value
    """
    newValue = copy.deepcopy(originalValue)

    if mutationProbability >= random.random():
        return newValue + random.gauss(0, sigma)

    return newValue

# Relative Normal Distribution #
def MutateRelNormal(mutationProbability: float, originalValue: float, sigma=0.2) -> float:
    """
    Mutate a gene relative to a relative normal distribution
    :param mutationProbability: Probability of mutation, should be between 0 and 1, values >= 1 means always mutate values <= 0 means never mutate
    :param originalValue: Original gene value
    :param sigma: Sigma value for normal distribution
    :return: Mutated gene value
    """
    newValue = copy.deepcopy(originalValue)

    if mutationProbability >= random.random():
        return newValue * (1 + random.gauss(0, sigma))

    return newValue

###################
# Mutate Organism #
###################

def MutateOrganisms(organisms: list, mutationProbability: float, constraints, mutationOperator: typing.Callable, *extraMutationOperatorArgs):
    result = []

    for o in organisms:
        result.append(MutateOrganism(o, mutationProbability, constraints, mutationOperator, *extraMutationOperatorArgs))

    return result

def MutateOrganism(organism, mutationProbability: float, constraints, mutationOperator: typing.Callable, *extraMutationOperatorArgs):
    while True:
        org = copy.deepcopy(organism)
        result = {}
        for k, v in org.items():
            result[k] = mutationOperator(mutationProbability, v, *extraMutationOperatorArgs)

        if OrganismValidation.CheckOrganismConstraints(result, constraints):
            break

    return result

def MutateOrganismSimple(organisms, mutationChance: float, min, max, mutationOperator=MutateFloat):
    """
    Applies the same basic mutation operator to all genes in an organism
    :param organism: Organism to mutate
    :param mutationChance: Probability of mutation, should be in the range 0-1
    :param min: Minimum range of values
    :param max: Maximum range of values
    :param mutationOperator: Mutation operator to apply, should be a basic mutation operator
    :return:
    """
    result = []

    for organism in organisms:
        res = {}
        org = copy.deepcopy(organism)
        for k in organism.keys():
            res[k] = mutationOperator(mutationChance, org[k], min, max)
        result.append(res)

    return result

def MutateOrganismSimpleList(organisms, mutationChance: list, range: list[list], mutationOperator: list):
    result = []

    for organism in organisms:
        i = 0
        res = {}
        org = copy.deepcopy(organism)
        for k in organisms.keys():
            res[k] = mutationOperator[i](mutationChance[i], org[k], range[i][0], range[i][1])
            i += 1
        result.append(res)

    return result
