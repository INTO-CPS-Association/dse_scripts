import json
import random
import typing
import numpy

from genetic import OrganismValidation

#############
# Accessors #
#############
def CreateChildren(parents: list[list], crossingFunction: typing.Callable, *extraCrossingFunctionArgs) -> list:
    children = []

    for i in range(len(parents)):
        children.append(crossingFunction(parents[i][0], parents[i][1], *extraCrossingFunctionArgs))

    return children

def CreateNChildren(nChildren: int, crossingFunction: typing.Callable, p1, p2, *extraCrossingFunctionArgs) -> list:
    children = []

    for i in range(0, nChildren):
        children.append(crossingFunction(p1, p2, *extraCrossingFunctionArgs))

    return children

###########
# Helpers #
###########
def CheckParents(p1, p2):
    # Must have the same number of genes
    if len(p1.keys()) != len(p2.keys()):
        raise ValueError(f"Parents must have the same number of genes")

    # Must have the same type of genes
    p1Keys = p1.keys()
    p2Keys = p2.keys()

    if p1Keys != p2Keys:
        raise ValueError("Parents must have the same type of genes")

    # check that the gene values are compatible
    p1Values = p1.values()
    p2Values = p2.values()
    paired = zip(p1Values, p2Values)

    if not all([type(g1) is type(g2) for g1, g2 in paired]):
        raise ValueError("Parent genes must be of the same type")


###################
# Basic Operators #
###################

def NPointCrossing(p1, p2, nCrossingPoints=1):

    CheckParents(p1, p2)

    if nCrossingPoints > len(p1.keys()) or nCrossingPoints < 0:
        raise ValueError(f"Number of crossing point must be less than the number of genes and > 0, given {nCrossingPoints}, maximum {len(p1.keys())}")

    result = json.loads("{}")
    keys = sorted(list(p1.keys()))
    crossingPoints = random.sample(keys, nCrossingPoints)

    selectedParent = p1

    for v in keys:
        # swaps between parents at each crossing point
        if v in crossingPoints:
            selectedParent = p2 if selectedParent == p1 else p1

        result[v] = selectedParent[v]

    return result

def UniformCrossing(p1, p2):

    CheckParents(p1, p2)

    result = json.loads("{}")
    keys = list(p1.keys())

    # Generate bitmask in base 2 the same length as the number of keys
    crossingMask = numpy.random.randint(2, size=len(keys))

    for v in crossingMask:
        key = keys.pop(0)
        if v == 0:
            result[key] = p1[key]
        else:
            result[key] = p2[key]

    return result

######################
# Advanced Operators #
######################

def BLX(p1, p2, constraints, alpha=0.5):
    CheckParents(p1, p2)

    if alpha < 0:
        raise ValueError(f"Alpha value must be greater than 0, provided {alpha}")

    keys = list(p1.keys())

    while True:
        result = {}

        for k in keys:
            low = min(p1[k], p2[k])
            high = max(p1[k], p2[k])
            delta = alpha * abs(p1[k] - p2[k])

            result[k] = random.uniform(low - delta, high + delta)

        if OrganismValidation.CheckOrganismConstraints(result, constraints):
            break

    return result


def SBX(p1, p2, constraints, eta=2):
    CheckParents(p1, p2)

    keys = list(p1.keys())

    while True:
        result = {}

        for k in keys:
            mu = random.random()

            if mu <= 0.5:
                beta = (2 * mu)**(1 / (eta + 1))
            else:
                beta = (1 / (2 * (1 - mu)))**(1 / (eta + 1))

            p = random.sample([-1, 1], 1)[0]

            result[k] = 0.5 * ((1 + (beta * p)) * p1[k] + (1 + (beta * p * -1)) * p2[k])

        if OrganismValidation.CheckOrganismConstraints(result, constraints):
            break

    return result
