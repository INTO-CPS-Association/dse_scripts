import os, sys, json, io, webbrowser, csv
from libs.Common import *


absoluteExperimentDir = sys.argv[1]
absoluteResultsPath = sys.argv[2]

def addGraphsForRanking(rank_id):
	htmlFile.write('<img src=graphs/' + rank_id + '.png>\n')

def putRankingsIntoTable(rank_id):
	htmlFile.write('<table>\n')
	addHeadings()
	addRows(rank_id)
	htmlFile.write('</table>\n')
	
def addRows(rank_id):
	this_ranking_root = ranking_json[rank_id]
	sorted_ranks = sorted(this_ranking_root)
	for rank in sorted_ranks:
		for design in this_ranking_root[rank]:
			addRow(rank,design)
			
def addRow(rank, design):
	htmlFile.write('<tr>')
	htmlFile.write('<td>' + rank + '</td>')
	addObjectiveValues(design)
	addDesignParameters(design)
	htmlFile.write('<tr>\n')
	
def addDesignParameters(design):
	configData = open(absoluteResultsPath + os.path.sep + design + os.path.sep + DEFAULT_SIM_CONFIG)
	config_json = json.load(configData)
	params_json = config_json['parameters']
	for param in params_json:
		htmlFile.write('<td>' + str(params_json[param]) + '</td>')

def addObjectiveValues(design):
	objectivesData = open(absoluteResultsPath + os.path.sep + design + os.path.sep + OBJECTIVES_FILE)
	objectives_json = json.load(objectivesData)
	for objective in objectives_json:
		htmlFile.write('<td>' + str(objectives_json[objective]) + '</td>')
	
def addHeadings():
	htmlFile.write('<tr>')
	htmlFile.write('<th>Rank</th>')
	firstSim = ranking_json['simulations'][0]
	getObjectiveHeadings(firstSim)
	getParameterHeadings(firstSim)
	htmlFile.write('</tr>\n')
	
def getObjectiveHeadings(design):
	objectivesData = open(absoluteResultsPath + os.path.sep + design + os.path.sep + OBJECTIVES_FILE)
	objectives_json = json.load(objectivesData)
	for objective in objectives_json:
		htmlFile.write('<th>' + objective + '</th>')
	
	
def getParameterHeadings(design):
	configData = open(absoluteResultsPath  + os.path.sep + design + os.path.sep + DEFAULT_SIM_CONFIG)
	config_json = json.load(configData)
	params_json = config_json['parameters']
	for param in params_json:
		htmlFile.write('<th>' + trimmedParamName(param) + '</th>')
		
def includeStyleSheet(fileName):
	returnString = ""
	if os.path.exists(fileName):
		cssFile = open(fileName)
		return cssFile.read()
	return ""
	
def trimmedParamName(param):
	tokens = param.split("}")
	return tokens[1][1:]

def putRankingsIntoCSV(rank_id):
	addHeadingsToCSV()
	addRowsToCSV(rank_id)
	
def addRowsToCSV(rank_id):
	this_ranking_root = ranking_json[rank_id]
	sorted_ranks = sorted(this_ranking_root)
	for rank in sorted_ranks:
		for design in this_ranking_root[rank]:
			addRowToCSV(rank,design)
			
def addRowToCSV(rank, design):
	rowData = []
	rowData.append(rank)
	print('.', rowData)
	addObjectiveValuesToCSVRow(design, rowData)
	addDesignParametersToCSVRow(design, rowData)
	print('...', rowData)
	csvWriter.writerow(rowData)
	
def addDesignParametersToCSVRow(design, currentRow):
	configData = open(absoluteResultsPath + os.path.sep + design + os.path.sep + DEFAULT_SIM_CONFIG)
	config_json = json.load(configData)
	params_json = config_json['parameters']
	for param in params_json:
		currentRow.append(str(params_json[param]))
		print('..', currentRow)
		#htmlFile.write('<td>' + str(params_json[param]) + '</td>')

def addObjectiveValuesToCSVRow(design, currentRow):
	objectivesData = open(absoluteResultsPath + os.path.sep + design + os.path.sep + OBJECTIVES_FILE)
	objectives_json = json.load(objectivesData)
	for objective in objectives_json:
		currentRow.append(str(objectives_json[objective]))
		print('..', currentRow)
		#htmlFile.write('<td>' + str(objectives_json[objective]) + '</td>')
	
def addHeadingsToCSV():
	rowData = []
	rowData.append('Rank')
	print('.', rowData)
	firstSim = ranking_json['simulations'][0]
	getObjectiveHeadingsForCSVRow(firstSim, rowData)
	getParameterHeadingsForCSVRow(firstSim, rowData)
	print('...', rowData)
	csvWriter.writerow(rowData)
	
def getObjectiveHeadingsForCSVRow(design, currentRow):
	objectivesData = open(absoluteResultsPath + os.path.sep + design + os.path.sep + OBJECTIVES_FILE)
	objectives_json = json.load(objectivesData)
	for objective in objectives_json:
		currentRow.append(objective)
		print('..', currentRow)
		#htmlFile.write('<th>' + objective + '</th>')
	
	
def getParameterHeadingsForCSVRow(design, currentRow):
	configData = open(absoluteResultsPath  + os.path.sep + design + os.path.sep + DEFAULT_SIM_CONFIG)
	config_json = json.load(configData)
	params_json = config_json['parameters']
	for param in params_json:
		currentRow.append(trimmedParamName(param))
		print('..', currentRow)
		#htmlFile.write('<th>' + trimmedParamName(param) + '</th>')
	


htmlFileName = absoluteResultsPath + os.path.sep +  HTML_RESULTS
htmlFile = open(htmlFileName,'w')

# create html header
htmlFile.write ('<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">')
htmlFile.write ('<html xmlns="http://www.w3.org/1999/xhtml">')
htmlFile.write ('<head>\n')
htmlFile.write ('<title>DSE Results Page</title>\n')
htmlFile.write ('<style>')
execdir = os.path.dirname(os.path.realpath(__file__))
htmlFile.write (includeStyleSheet(os.path.join(execdir, 'results.css')))
htmlFile.write ('\n</style>')
htmlFile.write ('</head>\n')
htmlFile.write ('<body>\n')

#csv.register_dialect(lineterminator = "\n")
csvFileName = os.path.join(absoluteResultsPath,ANALYSIS_RESULTS)
csvFile = open(csvFileName,'wt')
csvWriter = csv.writer(csvFile, lineterminator = "\n")


# open ranking.json
json_data = open(absoluteResultsPath + os.path.sep + RANKING_FILE)
ranking_json = json.load(json_data)

# read in rank ids (just pareto for now)
rank_id = 'pareto'

# create section
htmlFile.write('<h1>' + rank_id + '</h1>\n')

# add graph
addGraphsForRanking(rank_id)

# add table of data with id, objective values and parameters
putRankingsIntoTable(rank_id)
putRankingsIntoCSV(rank_id)

# close html
htmlFile.write ('</body>')
htmlFile.write ('</html>')

# close file
htmlFile.close()
csvFile.close()
