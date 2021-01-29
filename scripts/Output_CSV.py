import argparse
import csv

from libs.Common import *

# Setup argument parser so that the script is more user friendly
from libs.Common_Output import trimmedParamName, naturalKeys

resultsPath = ""

def runScript():
    global resultsPath

    args = scriptArguments().parse_args()
    resultsPath = args.resultsPath

    # load the json
    with open(os.path.join(resultsPath, RANKING_FILE)) as f:
        rankingJson = json.load(f)

    # CSV stuff
    csvFile = open(os.path.join(resultsPath, ANALYSIS_RESULTS), 'wt')
    csvWriter = csv.writer(csvFile, lineterminator="\n")

    putRankingsIntoCSV('pareto', csvWriter, rankingJson)
    csvFile.close()


# CSV stuff
def putRankingsIntoCSV(rankId, csvWriter, rankingJson):
    addHeadings(csvWriter, rankingJson)
    addRows(rankId, csvWriter, rankingJson)


def addHeadings(csvWriter, rankingJson):
    rowData = ['Rank']
    firstSim = rankingJson['simulations'][0]
    getObjectiveHeadingsForRow(firstSim, rowData)
    getParameterHeadingsForRow(firstSim, rowData)
    csvWriter.writerow(rowData)


def getObjectiveHeadingsForRow(design, currentRow):
    with open(os.path.join(resultsPath, design, OBJECTIVES_FILE)) as f:
        objectivesJson = json.load(f)
    for objective in objectivesJson:
        currentRow.append(objective)


def getParameterHeadingsForRow(design, currentRow):
    with open(os.path.join(resultsPath, design, DEFAULT_SIM_CONFIG)) as f:
        configJson = json.load(f)
    paramsJson = configJson['parameters']
    for param in paramsJson:
        currentRow.append(trimmedParamName(param))

    return currentRow


def addRows(rankId, csvWriter, rankingJson):
    thisRankingRoot = rankingJson[rankId]
    sortedRanks = sorted(thisRankingRoot)
    sortedRanks.sort(key=naturalKeys)
    for rank in sortedRanks:
        for design in thisRankingRoot[rank]:
            addRow(rank, design, csvWriter)


def addRow(rank, design, csvWriter):
    rowData = [rank]
    addObjectiveValuesRow(design, rowData)
    addDesignParametersRow(design, rowData)
    csvWriter.writerow(rowData)


def addDesignParametersRow(design, currentRow):
    with open(os.path.join(resultsPath, design, DEFAULT_SIM_CONFIG)) as f:
        configJson = json.load(f)
    paramsJson = configJson['parameters']
    for param in paramsJson:
        currentRow.append(str(paramsJson[param]))

    return currentRow


def addObjectiveValuesRow(design, currentRow):
    with open(os.path.join(resultsPath, design, OBJECTIVES_FILE)) as f:
        objectivesJson = json.load(f)
    for objective in objectivesJson:
        currentRow.append(str(objectivesJson[objective]))


def scriptArguments() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DSE CSV output", prog="Output CSV")

    # required params
    parser.add_argument("resultsPath", type=str, help="Full path to the results")

    return parser

runScript()
