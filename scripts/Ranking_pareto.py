import argparse
import os, sys, json, io, matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from libs.Common import *

#Objective Script Fault Codes
FAULT_NO_RESULTS = 'noResultsFound'
FAULT_COLUMN_NOT_FOUND = 'columnNotFound'
FAULT_SIMULATION_DID_NOT_END = 'simulationDidNotEnd'
FAULT_VALUE_COULD_NOT_BE_COMPUTED = 'valueCouldNotBeComputed'
FAULT_OBJECTIVE_ARGUMENT_MISSING = 'objectiveArgumentMissing'
FAULT_EMPTY_RESULTS_FOUND = 'emptyResultsFound'
FAULT_GENERAL = 'fault'


# Read the data from each simulation folder
def readInObjectivesFromFile(simulationList):
    for folder in simulationList:
        processFolder(folder)

# Read the data from a single sim folder
def processFolder(folder):
    filePath = os.path.join(resultsPath, folder, OBJECTIVES_FILE)
    fault = False

    thisRow = []

    if os.path.exists(filePath):
        with open(filePath) as f:
            resultsJson = json.load(f)

        # check for any errors in the json that could mean bad things
        for objective in objectiveOrder:
            if debugOutput:
                print(objective)

            if resultsJson[objective] == FAULT_NO_RESULTS:
                fault = True
            if resultsJson[objective] == FAULT_COLUMN_NOT_FOUND:
                fault = True
            if resultsJson[objective] == FAULT_SIMULATION_DID_NOT_END:
                fault = True
            if resultsJson[objective] == FAULT_VALUE_COULD_NOT_BE_COMPUTED:
                fault = True
            if resultsJson[objective] == FAULT_OBJECTIVE_ARGUMENT_MISSING:
                fault = True
            if resultsJson[objective] == FAULT_EMPTY_RESULTS_FOUND:
                fault = True
            if resultsJson[objective] == FAULT_GENERAL:
                fault = True

            # final check is to ensure that it is a number
            try:
                float(resultsJson[objective])
                thisRow.append(resultsJson[objective])
            except:
                fault = True
    else:
        fault = True

    thisRow.append(folder)

    if fault:
        rowsWithFaults.append(thisRow)
    else:
        rows.append(thisRow)

# Get the objectives to be ranked from the DSE
def getObjectiveOrder():
    objectiveOrder = []
    for objective in paretoDetails:
        objectiveOrder.append(objective)

    for objective in dseConfigJson['objectiveDefinitions']['internalFunctions']:
        if not objective in objectiveOrder:
            objectiveOrder.append(objective)

    for objective in dseConfigJson['objectiveDefinitions']['externalScripts']:
        if not objective in objectiveOrder:
            objectiveOrder.append(objective)

    return objectiveOrder

def getObjectiveDirections(paretoDetails):
    objectiveDirections = []
    for objective in paretoDetails:
        objectiveDirections.append(paretoDetails[objective])
    return objectiveDirections

# sort the results
def multiOrderSort(toBeSorted, sortingPosition, sortingDirection):
    if sortingPosition >= 0:
        newSortedList = sortList(toBeSorted, sortingPosition, sortingDirection[sortingPosition])
        sortingPosition -= 1
        return multiOrderSort(newSortedList, sortingPosition, sortingDirection)
    else:
        return toBeSorted

def sortList(toBeSorted, sortingPostion, sortingDirection):
    if sortingDirection == '-':
        if debugOutput:
            print(f"Sorting for a- {sortingPostion}")

        return sorted(toBeSorted, key=lambda designTuple: designTuple[sortingPostion], reverse=False)
    else:
        if debugOutput:
            print(f"Sorting for a+ {sortingPostion}")

        return sorted(toBeSorted, key=lambda designTuple: designTuple[sortingPostion], reverse=True)

# process the results
def compareTwoResults(thisResult, sortingDirection, currentRank):
    if sortingDirection == '-':
        return thisResult[1] < currentRank[-1][1]
    else:
        return thisResult[1] > currentRank[-1][1]


def scriptArguments() -> argparse.ArgumentParser:
    # Setup argument parser so that the script is more user friendly
    parser = argparse.ArgumentParser(description="DSE Pareto ranking", prog="Ranking Pareto")

    # required params
    parser.add_argument("dsePath", type=str, help="Full top level path to the project")
    parser.add_argument("dseConfigPath", type=str, help="Path to DSE file (.dse.json) relative to projectpath")
    parser.add_argument("resultsPath", type=str, help="Path to the results of DSE")

    # optional params
    parser.add_argument("-d", type=strToBool, default=False, help="Show debug output (default: False)")

    return parser


args = scriptArguments().parse_args()

basePath = args.dsePath
dseConfigPath = args.dseConfigPath
resultsPath = args.resultsPath
debugOutput = args.d

if debugOutput:
    print("\t\tOpening ranking JSON")

with open(os.path.join(resultsPath, RANKING_FILE)) as f:
    rankingJson = json.load(f)

simulationList = rankingJson['simulations']

with open(dseConfigPath) as f:
    dseConfigJson = json.load(f)

paretoDetails = dseConfigJson['ranking']['pareto']
rankId = 'pareto'

objectiveOrder = getObjectiveOrder()
objectiveCount = len(paretoDetails)
objectiveDirections = getObjectiveDirections(paretoDetails)

rows = []
rowsWithFaults = []

if debugOutput:
    print("\t\tRanking results")

readInObjectivesFromFile(simulationList)

# output list of unrankable (faulty) results
unrankableResultsId = 'unrankable'
rankingJson[unrankableResultsId] = []
unrankableRRoot = rankingJson[unrankableResultsId]
for unrankable in rowsWithFaults:
    rankingJson[unrankableResultsId].append(unrankable[-1])

resultsSorted = multiOrderSort(rows, len(objectiveDirections) - 1, objectiveDirections)

# rank the rankable results
ranks = []
while len(resultsSorted) > 0:
    currentRank = [resultsSorted[0]]

    for result in resultsSorted[1:]:
        direct = objectiveDirections[-1] # allows for ranking against itself
        if compareTwoResults(result, direct, currentRank):
            currentRank.append(result)

    ranks.append(currentRank)
    for result in currentRank:
        resultsSorted.remove(result)

if debugOutput:
    print("\t\tWriting to JSON")

# put the ranked results into a json
rankingJson[rankId] = {}
rankRoot = rankingJson[rankId]
rankNumber = 0

for rank in ranks:
    rankNumber += 1
    rankRoot[rankNumber] = []

    for result in rank:
        rankRoot[rankNumber].append(result[-1])

jsonOutput = json.dumps(rankingJson, sort_keys=True, indent=4, separators=(",", ":"))
jsonOutputFile = open(os.path.join(resultsPath, RANKING_FILE), 'w')
jsonOutputFile.write(jsonOutput)
jsonOutputFile.close()

if debugOutput:
    print("\t\tCreating graphs")

# output graphs
graphFolder = os.path.join(resultsPath, GRAPHS_FOLDER)
if not os.path.exists(graphFolder):
    os.makedirs(graphFolder)

#plot pareto frount in blue
fig = Figure()
ax = fig.add_subplot(1,1,1)
nonDominatedSet = True
odd = True

for rank in ranks:
    x = []
    y = []

    for result in rank:
        x.append(result[0])
        y.append(result[1])

    if nonDominatedSet:
        ax.plot(x, y, 'g')
        ax.plot(x, y, 'go')
        nonDominatedSet = False
    else:
        if odd:
            odd = False
            ax.plot(x, y, 'r')
            ax.plot(x, y, 'ro')
        else:
            odd = True
            ax.plot(x, y, 'y')
            ax.plot(x, y, 'yo')

ax.set_xlabel(objectiveOrder[0])
ax.set_ylabel(objectiveOrder[-1])

plotFileName = os.path.join(graphFolder, rankId + ".png")
canvas = FigureCanvas(fig)
canvas.print_figure(plotFileName, dpi=75)
