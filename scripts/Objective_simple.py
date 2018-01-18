import csv,os, sys, json, io
from libs.Common import *

resultsFile = sys.argv[1] + os.path.sep + RESULTS_FILE
objectivesFile = sys.argv[1] + os.path.sep + OBJECTIVES_FILE
columnName = sys.argv[2]
objectiveType = sys.argv[3]
objectiveID = sys.argv[4]
 
csvfile = open(resultsFile)
csvdata = csv.reader(csvfile, delimiter=',')

firstVal = True
firstRow = True
resultVal = 0
sum=0
count = 0

columnToRead = 0 

def writeObjectiveToOutfile(key, val):
	parsed_json = {}

	if os.path.isfile(objectivesFile):
		json_data = open(objectivesFile)
		parsed_json = json.load(json_data)

	parsed_json[key] = val

	dataString = json.dumps(parsed_json, sort_keys=True,indent=4, separators=(',', ': '))

	with io.open(objectivesFile, 'w', encoding='utf-8') as f:
   		f.write(unicode(dataString))

def getColumnFor(colName, row):
	index = 0
	for thisName in row:
		if thisName.strip() == colName.strip():
			return index
		else:
			index +=1		
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
	resultVal = sum/count
	

for row in csvdata:
	if firstRow:
		columnToRead = getColumnFor(columnName, row)
		firstRow = False
	else:
		if objectiveType == 'max':
			updateMax(float(row[columnToRead]))
		elif objectiveType == 'min':
			updateMin(float(row[columnToRead]))
		elif objectiveType == 'mean':
			updateMean(float(row[columnToRead]))
			
writeObjectiveToOutfile(objectiveID, resultVal)