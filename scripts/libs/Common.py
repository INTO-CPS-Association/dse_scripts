import os, time, json, platform, subprocess, io, sys
##################################
# folders and files
##################################

MULTI_MODEL_FOLDER  = "Multi-Models"	
MULTI_MODEL_EXTENSION = ".mm.json"
FMUS_FOLDER = 'FMUs'
COE_SETTINGS_EXTENSION = ".coe.json"
DSE_FOLDER = "DSEs"
DSE_CONFIG_EXTENSION = ".dse.json"
USER_METRICS_FOLDER = "userMetricsScripts"
DEFAULT_SIM_CONFIG = 'config.mm.json'
RESULTS_FILE = 'results.csv'

OBJECTIVES_FILE = 'objectives.json'
RANKING_FILE = 'ranking.json'
GRAPHS_FOLDER = 'graphs'
HTML_RESULTS = 'results.html'
ANALYSIS_RESULTS = 'dseResults.csv'


##################################
# dse config sections
##################################

#DSE_CONFIG_SEC_START_TIME = 


##################################
# coe config sections
##################################

#COE_CONFIG_SEC_ALGORITHM = 'algorithm'


##################################
# mm config sections
##################################




###################################
# common functions
###################################

def dateTimeFolderName():
    return time.strftime("%Y_%m_%d_%H.%M.%S")

def makeDateTimeFolder(absoluteExperimentPath, dateTimeFolder):
	
	if not os.path.exists(absoluteExperimentPath + dateTimeFolder):
		os.makedirs(absoluteExperimentPath + dateTimeFolder)


def combineModelFiles(absoluteCoeConfigPath, dseConfig, absoluteProjectPath):
	# load and process coe config
	coeConfig_data = open(absoluteCoeConfigPath)
	coeConfig = json.load(coeConfig_data)

	#open and process multimodel
	absMultiModelPath = absoluteProjectPath + os.path.sep + MultiModelPathURIToNormalPath(coeConfig['multimodel_path'])

	sourceMultiModel_data = open(absMultiModelPath)
	sourceMultiModel = json.load(sourceMultiModel_data)

	makeFMUPathsURIs(sourceMultiModel['fmus'], absoluteProjectPath)

	#parsed_multimodel_json = []
	#sourceMultiModel = ['algorithm'] = []
	sourceMultiModel['algorithm'] = coeConfig['algorithm']

	dseConfig['simulation'] = {}
	dseConfig['simulation']['startTime'] = str(coeConfig['startTime'])
	dseConfig['simulation']['endTime'] = str(coeConfig['endTime'])

	return sourceMultiModel
	
def MultiModelPathURIToNormalPath(multi_model_path):
	return multi_model_path.replace('\\', os.path.sep)

def makeFMUPathsAbsolute(fmusSection, absoluteProjectPath):
	for fmu in fmusSection:
		fmusSection[fmu] = absoluteProjectPath + os.path.sep + FMUS_FOLDER + os.path.sep + fmusSection[fmu]

def makeFMUPathsURIs(fmusSection, absoluteProjectPath):
	for fmu in fmusSection:
		tempPath = os.path.join(absoluteProjectPath, FMUS_FOLDER, fmusSection[fmu])
		fmusSection[fmu] = "file:///" + tempPath.replace(os.path.sep, '/')


def defineRunAndEvluatieSimulation(parsed_multimodel_json, scenarioID, simParamVals, dseConfig, absoluteResultsPath, absoluteProjectPath):
	
	newpath = makeDirName(scenarioID, simParamVals)
	print("    using params " + newpath)
	if not os.path.exists(absoluteResultsPath + os.path.sep + newpath):
		os.makedirs(absoluteResultsPath + os.path.sep + newpath)
		
	print("        results directory created")
	
	filepath = absoluteResultsPath + os.path.sep + newpath + os.path.sep + DEFAULT_SIM_CONFIG
	
	configParams = parsed_multimodel_json['parameters']
	for key in simParamVals.keys():
		configParams[key] = simParamVals[key]
		
	json_output = json.dumps(parsed_multimodel_json, sort_keys=True, indent=4, separators=(',',': '))
	json_output_file = open(filepath,'w')
	
	json_output_file.write(json_output)
	json_output_file.close()
	print("        config created")
	#print simParamVals
	time.sleep(1)

	launchSimulation(newpath, dseConfig, absoluteResultsPath)
	createObjectivesFile(newpath, dseConfig, absoluteResultsPath)
	processObjectives(newpath, dseConfig, absoluteResultsPath)
	processObjectiveExternalScripts(newpath, dseConfig, absoluteResultsPath, absoluteProjectPath, scenarioID)
	addSimulationDirToRankingFile(newpath, absoluteResultsPath, scenarioID)
	return


def makeDirName(scenarioID, simParamVals):
	first = True;
	dirName = ''
	
	if len(scenarioID) >0:
		dirName = scenarioID
		first = False
	
	sortedKeys = sorted(simParamVals.keys())

	for key in sortedKeys:
		if not first:
			dirName += '_'
		dirName += str(simParamVals[key]) 
		first = False
	return dirName
	
#def shortName(fullName):
#	tokens = fullName.split("}")
#	return tokens[1]
	
def launchSimulation(simFolder, dseConfig, absoluteResultsPath):
	execdir = os.path.dirname(os.path.realpath(__file__))
	print execdir
	subprocess.call(["python", os.path.join(execdir, "..", "COE_handler.py"), absoluteResultsPath + os.path.sep + simFolder, dseConfig['simulation']['startTime'], dseConfig['simulation']['endTime']])

def createObjectivesFile(simFolder, dseConfig, absoluteResultsPath):
	empty_json = {}
	empty_json_string = json.dumps(empty_json, sort_keys=True,indent=4, separators=(',', ': '))
	objectivesFile = absoluteResultsPath + os.path.sep + simFolder + os.path.sep + OBJECTIVES_FILE
	with io.open(objectivesFile, 'w', encoding='utf-8') as f:
   		f.write(unicode(empty_json_string))
	
def processObjectives(simFolder, dseConfig, absoluteResultsPath):
	print("        processing objectives")
	for objectiveName in dseConfig['objectiveDefinitions']['internalFunctions'].keys():
		processObjective(absoluteResultsPath + os.path.sep + simFolder, dseConfig['objectiveDefinitions']['internalFunctions'][objectiveName]['columnID'], dseConfig['objectiveDefinitions']['internalFunctions'][objectiveName]['objectiveType'], objectiveName)

def processObjective(simFolder, colID, objType, objName):
	subprocess.call(["python", "Objective_simple.py", simFolder, colID, objType, objName])
	

def processObjectiveExternalScripts(simFolder, dseConfig, absoluteResultsPath, absoluteProjectPath, scenarioID):	
	print("        processing objectives (external scripts)")
	for objectiveName in dseConfig['objectiveDefinitions']['externalScripts'].keys():
		scriptFile = dseConfig['objectiveDefinitions']['externalScripts'][objectiveName]['scriptFile']
		parametersList = dseConfig['objectiveDefinitions']['externalScripts'][objectiveName]['scriptParameters']
		sortedParameterKeys = sorted(dseConfig['objectiveDefinitions']['externalScripts'][objectiveName]['scriptParameters'])
		scriptFilePath = absoluteProjectPath + os.path.sep + 'userMetricScripts' + os.path.sep + scriptFile
		resultsFolderPath = absoluteResultsPath + os.path.sep + simFolder
		scenarioFolderPath = absoluteProjectPath + os.path.sep + 'userMetricScripts' + os.path.sep + scenarioID
		callList = ["python", scriptFilePath, resultsFolderPath, objectiveName, scenarioFolderPath]
		for parameter in sortedParameterKeys:
			callList.append(parametersList[parameter])
		print ("processing " + scriptFile + " with params ")
		for item in callList:
			print(item)
		subprocess.call(callList)

	
def addSimulationDirToRankingFile(simFolder, absoluteResultsPath, scenarioID):
	ranking_json = {}
	ranking_json['simulations'] = []
	if os.path.isfile(absoluteResultsPath + os.path.sep + RANKING_FILE):
		json_data = open(absoluteResultsPath + os.path.sep + RANKING_FILE)
		ranking_json = json.load(json_data)
		
		
	simulations_folder = ranking_json['simulations']
	if simFolder not in simulations_folder:
		simulations_folder.append(simFolder)
	ranking_string = json.dumps(ranking_json, sort_keys=True,indent=4, separators=(',', ': '))

	with io.open(absoluteResultsPath + os.path.sep + RANKING_FILE, 'w', encoding='utf-8') as f:
   		f.write(unicode(ranking_string))
		

###################################
# parameter contraints
###################################


def checkParameterContraints(parameterValues, contraints):
	for constraint in contraints:
		if not eval(replaceNamesWithQualifiedNames(constraint, parameterValues)):
			return False
			
	return True

def replaceNamesWithQualifiedNames(originalConstraint, parameterValues):
	newConstraint = originalConstraint
	for name in parameterValues.keys():
		newConstraint = newConstraint.replace(name, "parameterValues['" + name + "']")
		
	return newConstraint
		

###################################
# objective contraints
###################################

    