from random import random

import numpy


def EulerDistance(rankedOrganisms, highToLow=True, high=0.1, low=0.02):

    if high < low:
        raise ValueError(f"High must be <= low given high: {high} low: {low}")

    if not (high == low and low == 0):
        # get euclidean distance between everything
        dist = numpy.zeros((len(rankedOrganisms), len(rankedOrganisms)))

        for i in range(len(rankedOrganisms) - 1):
            iGenes = numpy.array([v for v in rankedOrganisms[i][0].values()])
            for j in range(i + 1, len(rankedOrganisms)):
                jGenes = numpy.array([v for v in rankedOrganisms[j][0].values()])
                dist[i][j] = numpy.linalg.norm(jGenes - iGenes)
                dist[j][i] = dist[i][j]

        # get threshold
        alpha = (random() * (high - low)) + low
        thresh = numpy.mean(dist) * alpha

        # apply the operator to the ranking
        convertedRanking = []
        for i in range(len(rankedOrganisms)):
            nei = len(list(filter(lambda o: o < thresh, dist[i])))
            if highToLow:
                # fitness should approach infinity
                nei = nei if not nei == 0 else 0.5
                newRank = rankedOrganisms[i][1] / nei
            else:
                # fitness should approach 0
                newRank = rankedOrganisms[i][1] * nei

            convertedRanking.append((rankedOrganisms[i][0], newRank, rankedOrganisms[i][1]))

    # apply scaling to simulate evolution pressure
    operator, f = ("+", max) if not highToLow else ("-", min)
    comp = f([k for _, k, _ in convertedRanking])
    convertedRanking = [(v, eval(f"{k} {operator} {comp}"), o) for v, k, o in convertedRanking]

    return convertedRanking

# TODO: Add more diversity controls?
