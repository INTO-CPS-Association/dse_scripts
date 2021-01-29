import argparse
import csv

from libs.Common import *

# Setup argument parser so that the script is more user friendly
parser = argparse.ArgumentParser(description="Compare simulation results with a simple objective",
                                 prog="Objective Simple")

# required params
parser.add_argument("simFolder", type=str, help="Full path to the simulation folder")
parser.add_argument("colId", type=str, help="Name of the column")
parser.add_argument("objType", type=str, help="Type of objective")
parser.add_argument("objName", type=str, help="Name of objective")

# optional params
parser.add_argument("-d", type=strToBool, default=False, help="Show debug output (default: False)")

args = parser.parse_args()

# See what we have been given
debugOutput = args.d
resultsFile = os.path.join(args.simFolder, RESULTS_FILE)
objectivesFile = os.path.join(args.simFolder, OBJECTIVES_FILE)
colName = args.colId
objectiveType = args.objType
objectiveId = args.objName

firstVal = True
firstRow = True
resultVal = 0
sum = 0
count = 0

colToRead = 0


def writeObjectiveToOutfile(key, val):
    parsedJson = {}

    if os.path.isfile(objectivesFile):
        with open(objectivesFile) as f:
            parsedJson = json.load(f)

    parsedJson[key] = val

    dataString = json.dumps(parsedJson, sort_keys=True, indent=4, separators=(',', ': '))

    with io.open(objectivesFile, 'w', encoding='utf-8') as f:
        f.write(str(dataString))


def getColumnFor(colName, row):
    index = 0
    for thisName in row:
        if thisName.strip() == colName.strip():
            return index
        else:
            index += 1
    return index


def updateMax(val):
    global firstVal
    global resultVal
    if firstVal:
        resultVal = val
        firstVal = False
    elif val > resultVal:
        resultVal = val


def updateMin(val):
    global firstVal
    global resultVal
    if firstVal:
        resultVal = val
        firstVal = False
    elif val < resultVal:
        resultVal = val


def updateMean(val):
    global sum
    global count
    global resultVal
    sum += val
    count += 1
    resultVal = sum / count


with open(resultsFile) as f:
    csvData = csv.reader(f, delimiter=",")
    for row in csvData:
        if firstRow:
            colToRead = getColumnFor(colName, row)
            firstRow = False
        else:
            if objectiveType == "max":
                updateMax(float(row[colToRead]))
            elif objectiveType == "min":
                updateMin(float(row[colToRead]))
            elif objectiveType == "mean":
                updateMean(float(row[colToRead]))

writeObjectiveToOutfile(objectiveId, resultVal)

