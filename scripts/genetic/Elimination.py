from math import floor
from random import random


def EliminateOrganisms(organisms, percentToRemove=0.1):
    num = round(len(organisms) * percentToRemove)

    # remove random organisms
    for i in range(num):
        organisms.pop(floor(len(organisms) * random()))

    # replace the removed ones
    for i in range(num):
        organisms.append(organisms[floor(len(organisms) * random())])