import os, sys, json, io, webbrowser, csv, re, matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from libs.Common import *


absoluteExperimentDir = sys.argv[1]
absoluteExperimentConfigPath = sys.argv[2]
absoluteResultsPath = sys.argv[3]


def atof(text):
    try:
        retval = float(text)
    except ValueError:
        retval = text
    return retval

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    float regex comes from https://stackoverflow.com/a/12643073/190597
    '''
    return [ atof(c) for c in re.split(r'[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)', text) ]


########################################################
# generate graphs and add to HTML
########################################################


def loadObjectiveValuesForDesign(design):
	objectives_file = open(os.path.join(absoluteResultsPath,design,OBJECTIVES_FILE))
	objectives_json = json.load(objectives_file)
	return objectives_json


def loadObjectivesData(rank_id):
	objectives_data = {}
	ranking_root = ranking_json[rank_id]
	for rank in ranking_root:
		objectives_data[rank] = {}
		this_rank_root = ranking_root[rank]
		for design in this_rank_root:
			objectives_data[rank][design]=loadObjectiveValuesForDesign(design)
	return objectives_data

def getObjectiveDirections():
	dseConfigData = open(absoluteExperimentConfigPath)
	dseConfigJson = json.load(dseConfigData)
	paretoDetails = dseConfigJson['ranking']['pareto']
	objectiveDirections = {}
	for objective in paretoDetails:
		objectiveDirections[objective] = paretoDetails[objective]
	return objectiveDirections



def createGraphCombinations(objective_directions, objectives_data):
	keys = objective_directions.keys()
	print 'keys', keys
	for firstObjective in range (0, len(keys)):
		print 'firstobjective', keys[firstObjective]
		for secondObjective in range (firstObjective + 1, len(keys)):
			print 'secondobjective', keys[secondObjective]
			generateGraph(keys[firstObjective], keys[secondObjective], objectives_data)
			addGraphToPage(keys[firstObjective], keys[secondObjective])
            

def generateGraph(firstObjective, secondObjective, objectives_data):
	print 'generating graph', firstObjective, secondObjective, objectives_data
	graphFolder = absoluteResultsPath + os.path.sep +  GRAPHS_FOLDER
	if not os.path.exists(graphFolder):
		os.makedirs(graphFolder)
	# plot pareto fron in blue
	fig = Figure()
	ax = fig.add_subplot(1,1,1)
	non_dominated_set = True
	odd = True
	for rank in objectives_data:

		print 'rank', rank
		Xs=[]
		Ys=[]

		unsortedPointsList = []
		for design in objectives_data[rank]:

			print 'design', design

			print 'des first', objectives_data[rank][design][firstObjective]
			print 'des secon', objectives_data[rank][design][secondObjective]
			
			#Xs.append(objectives_data[rank][design][firstObjective])
			#Ys.append(objectives_data[rank][design][secondObjective])
			this_result=[objectives_data[rank][design][firstObjective],objectives_data[rank][design][secondObjective]]
			unsortedPointsList.append(this_result)

		sortedPointList = sorted(unsortedPointsList)
		for result in sortedPointList:
			Xs.append(result[0])
			Ys.append(result[1])			

		if non_dominated_set:
			ax.plot(Xs, Ys, 'g')
			ax.plot(Xs, Ys, 'go')
			non_dominated_set = False
		else:
			if odd:
				odd = False
				ax.plot(Xs, Ys, 'r')
				ax.plot(Xs, Ys, 'ro')
			else:
				odd = True
				ax.plot(Xs, Ys, 'y')
				ax.plot(Xs, Ys, 'yo')
	
	ax.set_xlabel(firstObjective)
	ax.set_ylabel(secondObjective)

	plotFileName = os.path.join(graphFolder, firstObjective + '-' + secondObjective + ".png")
	canvas = FigureCanvas(fig)
	canvas.print_figure(plotFileName, dpi=75)

def addGraphToPage(firstObjective, secondObjective):
	#htmlFile.write('<img src=graphs/' + rank_id + '.png>\n')
	htmlFile.write('<img src=graphs/' + firstObjective + '-' + secondObjective + '.png>\n')


def addGraphsForRanking(rank_id):
	objectives_data = loadObjectivesData(rank_id)
	objectives_directions = getObjectiveDirections()
	createGraphCombinations(objectives_directions, objectives_data)



#Output graphs
#graphFolder = absoluteResultsPath + os.path.sep +  GRAPHS_FOLDER
#if not os.path.exists(graphFolder):
#	os.makedirs(graphFolder)








#####################################################
# add numeric ranking data to HTML
#####################################################


def putRankingsIntoTable(rank_id):
	htmlFile.write('<table>\n')
	addHeadings()
	addRows(rank_id)
	htmlFile.write('</table>\n')
	
def addRows(rank_id):
	this_ranking_root = ranking_json[rank_id]
	sorted_ranks = sorted(this_ranking_root)
	#sorted_ranks = this_ranking_root
	sorted_ranks.sort(key=natural_keys)
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
	#sorted_ranks = this_ranking_root
	sorted_ranks.sort(key=natural_keys)
	for rank in sorted_ranks:
		for design in this_ranking_root[rank]:
			addRowToCSV(rank,design)
			
def addRowToCSV(rank, design):
	rowData = []
	rowData.append(rank)
	addObjectiveValuesToCSVRow(design, rowData)
	addDesignParametersToCSVRow(design, rowData)
	csvWriter.writerow(rowData)
	
def addDesignParametersToCSVRow(design, currentRow):
	configData = open(absoluteResultsPath + os.path.sep + design + os.path.sep + DEFAULT_SIM_CONFIG)
	config_json = json.load(configData)
	params_json = config_json['parameters']
	for param in params_json:
		currentRow.append(str(params_json[param]))

def addObjectiveValuesToCSVRow(design, currentRow):
	objectivesData = open(absoluteResultsPath + os.path.sep + design + os.path.sep + OBJECTIVES_FILE)
	objectives_json = json.load(objectivesData)
	for objective in objectives_json:
		currentRow.append(str(objectives_json[objective]))

	
def addHeadingsToCSV():
	rowData = []
	rowData.append('Rank')
	firstSim = ranking_json['simulations'][0]
	getObjectiveHeadingsForCSVRow(firstSim, rowData)
	getParameterHeadingsForCSVRow(firstSim, rowData)
	csvWriter.writerow(rowData)
	
def getObjectiveHeadingsForCSVRow(design, currentRow):
	objectivesData = open(absoluteResultsPath + os.path.sep + design + os.path.sep + OBJECTIVES_FILE)
	objectives_json = json.load(objectivesData)
	for objective in objectives_json:
		currentRow.append(objective)

	
	
def getParameterHeadingsForCSVRow(design, currentRow):
	configData = open(absoluteResultsPath  + os.path.sep + design + os.path.sep + DEFAULT_SIM_CONFIG)
	config_json = json.load(configData)
	params_json = config_json['parameters']
	for param in params_json:
		currentRow.append(trimmedParamName(param))
	


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

# add graphs
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
