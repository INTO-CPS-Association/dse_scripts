import json, sys, os, platform, subprocess, time, io, random, collections, copy
from libs.Common import *

MULTI_MODEL_FOLDER  = "MultiModels"	
DSE_FOLDER = "DSEs"
USER_METRICS_FOLDER = "userMetricsScripts"
DEFAULT_SIM_CONFIG = 'config.mm.json'
RESULTS_FILE = 'results.csv'

OBJECTIVES_FILE = 'objectives.json'
RANKING_FILE = 'ranking.json'
GRAPHS_FOLDER = 'graphs'
HTML_RESULTS = 'results.html'


## algorithm option constants
INITIAL_POPULATION_DISTRIBUTION_RANDOM = 'random'
INITIAL_POPULATION_DISTRIBUTION_UNIFORM = 'uniform'

PARENT_SELECTION_STRATEGY_RANDOM = 'random'
PARENT_SELECTION_STRATEGY_ALGORITHM_OBJECTIVE_SPACE = 'algorithmObjectiveSpace'
PARENT_SELECTION_STRATEGY_ALGORITHM_DESIGN_SPACE = 'algorithmDesignSpace'


def runInitialSimulations(dse_config, parsed_multimodel_json, initialPopulationSize):
	parameterList = dse_config.get('parameters') ##Retrieving the 'parameters' dictionary in the dse config file after parsing
	simulationNumber = 1 ##Number used to increment whenever a simulation has been completed

	##Loop repeats until the specified initial population size is reached
	while simulationNumber <= initialPopulationSize:
		newSimParams = dict() ##Dictionary declared for new set of parameters for a new simulation
		print("\nLaunching simulation number: " + str(simulationNumber))
		
		##For the values of all parameter variables in the parameters of dse config json file
		for paramKey in parameterList.keys(): 
			paramValues = parameterList[paramKey]			
			paramValIndex = random.randint(0,len(paramValues) - 1) ##Random index chosen to be used for selecting the possibilities for parameter values
			#print("paramValIndex: " + str(paramValIndex))
			newSimParams[paramKey] = paramValues[paramValIndex] ##Adds random value from parameter key's possibilities to a new simulation for its parameters
			#print("Param key: " + str(paramKey) + "\nParam value: " + str(newSimParams[paramKey]))
		
		simDirName = makeDirName("studentMap",newSimParams) #Make directory name for simulation
		
		##Write newSimParams to a new config json file and then launch simulation, then move on to the next simulation
		resultsFolderDir = absoluteResultsPath + os.path.sep + str(simDirName) ##New folder to store simulation results and config files		
		#print("Simulation folder: " + str(resultsFolderDir))
		if not os.path.exists(resultsFolderDir):
			os.makedirs(resultsFolderDir)		
		
		configFilePath = resultsFolderDir + os.path.sep +  DEFAULT_SIM_CONFIG #Create a new config json file
		parsed_multimodel_json['parameters'] = newSimParams #Replace parameters with new random design 
		#print("Simulation " + str(simulationNumber) + " design parameters: " + str(parsed_multimodel_json['parameters']))
		
		config_json = json.dumps(parsed_multimodel_json, sort_keys=True, indent=4, separators=(',',': '))	
		config_json_file = open(configFilePath,'w')	
		
		config_json_file.write(config_json)
		config_json_file.close()
		#print("Start time: " + str(dse_config['simulation']['startTime']))
		#print("End time: " + str(dse_config['simulation']['endTime']))
		#print("resultsFolderDir: " + str(resultsFolderDir))
		
		defineRunAndEvluatieSimulation(parsed_multimodel_json,"studentMap",newSimParams,dse_config, absoluteResultsPath, absoluteProjectPath)		
		print("Simulation number " + str(simulationNumber) + " completed")		
		
		simulationNumber = simulationNumber + 1	##Increments for every simulation completed 
	print("Ranking initial population...")
	subprocess.call(["python", "Ranking_pareto.py",absoluteExperimentPath, absoluteExperimentConfigPath,  absoluteResultsPath])
	print("Ranking complete. Now selecting parents for breeding if needed.")
	
def createChildren(dseConfig, parent1,parent2,rankings):
	child1_duplicateCounter = 0
	child2_duplicateCounter = 0
	childrenCreated = False
	progressCheck = 0
	while childrenCreated == False:
		##Obtaining the dictionary of parameter name-value pairs within the parent designs and ensuring they are ordered, since dictionaries in Python are unordered
		parent1_params = parent1.get('parameters')
		parent2_params = parent2.get('parameters')

		if cmp(parent1_params,parent2_params) == 0:
			print("Parent designs identical. Reselecting parents!")
			childrenCreated = True
		
		##Generate a random integer for the crossover index. Must not be the first item, so range given between 1 and number of items in parameter list
		genesChosen = False
		counter = 0
		while genesChosen == False:		
			index1 = random.randint(1,len(parent1_params.keys()) - 1)
			print("Index1: " + str(index1))		
			##Obtaining the 'genes' (i.e the parameter value) to be inserted into the chromosomes of the children designs
			keyList = parent1_params.keys()
			parameter = keyList[index1]
			print("Parameter to cross: " + str(parameter))		
			
			gene1 = parent1_params.get(parameter) ##gets the name-value pair from the list at the random index chosen above
			gene2 = parent2_params.get(parameter)		
			
			if gene1 != gene2:			
				genesChosen = True
				print("Genes unique. No need to reselect. Creating children...")
			else:
				counter = counter + 1
				
				if counter == len(parent1_params.values()):
					print("Unable to create unique child")					
					progressCheck = progressCheck + 1
					print("PROGRESS CHECK: " + str(progressCheck))
					if progressCheck == 3:
						print("Checking progress...")
						childrenCreated = True
					genesChosen = True
					
				print("Genes identical. Need to reselect gene")
				
		##Genes crossed over in chromosomes for children designs
		parent1_copy = parent1_params.copy() ##copies the parameters of the first parent
		parent2_copy = parent2_params.copy() ##copies the parameters of the second parent

		#Genes are crossed over from both parents to form designs with new parameters
		parent1_copy[parameter] = gene2
		parent2_copy[parameter] = gene1
		
		#MUTATION
		#mutationProbability = random.randint(1,100) #Probability for mutation in child designs
		#if mutationProbability % 30 == 0: #There is a 3% chance of a mutation happening
		#print("mutationProbability " + str(mutationProbability) + "   " + str(mutationProbability > 1))
		if random.randint(1,100) <= mutationProbability : #There is a 3% chance of a mutation happening
			print("Child designs have undergone mutation")
			
			parentToMutate = random.randint(1,2) #Decides which of the offspring designs to mutate- either parent 1 or parent 2
			print("parentToMutate: " + str(parentToMutate))
			if parentToMutate == 1: 
				mutationIndex = random.randint(0,len(parent1_copy.keys()) -1) ##Decides which gene in the child's chromosome to mutate
				parent1_keys = parent1_params.keys()
				parameterToMutate = parent1_keys[mutationIndex] #Determines which parameter in parent dse config to mutate
				dse_parameterKeys = dseConfig.get('parameters').keys() #Retrieves the keys of the paramters in the DSE file
				for key in dse_parameterKeys:
					if key == parameterToMutate:
						mutantValueIndex = random.randint(0,len(dseConfig.get('parameters').get(key)) - 1) #Used to choose random value from the parameter values in the chosen key to replace with
						print("Value from DSE config at index: " + str(mutantValueIndex) + " for key:  " + str(key) + " -->" +  str(dseConfig.get('parameters').get(key)[mutantValueIndex]))
						parent1_copy[parameterToMutate] = dseConfig.get('parameters').get(key)[mutantValueIndex] #Value in the parameters of the child design is replaced with a new value from dse config file
			else:			
				mutationIndex = random.randint(0,len(parent2_copy.keys()) - 1) ##Decides which gene in the child's chromosome to mutate
				parent2_keys = parent2_params.keys()
				parameterToMutate = parent2_keys[mutationIndex] #Determines which parameter in parent dse config to mutate
				dse_parameterKeys = dseConfig.get('parameters').keys() #Retrieves the keys of the paramters in the DSE file
				for key in dse_parameterKeys:
					if key == parameterToMutate:
						
						mutantValueIndex = random.randint(0,len(dseConfig.get('parameters').get(key)) - 1) #Used to choose random value from the parameter values in the chosen key to replace with
						print("Value from DSE config at index " + str(mutantValueIndex) + " for key:  " + str(key) + " -->" +  str(dseConfig.get('parameters').get(key)[mutantValueIndex]))
						parent2_copy[parameterToMutate] = dseConfig.get('parameters').get(key)[mutantValueIndex] #Value in the parameters of the child design is replaced with a new value from dse config file
				
		##List of key-value pairs transformed to dictionary
		child1_params = dict(parent1_copy)
		child2_params = dict(parent2_copy)	
		child1_dirName = makeDirName('studentMap',child1_params)
		child2_dirName = makeDirName('studentMap',child2_params)
		print("Child 1 dir name: " + str(child1_dirName))
		print("Child 2 dir name: " + str(child2_dirName))
		print("Parent 1 params: " + str(parent1_params.values()))
		print("Parent 2 params: " + str(parent2_params.values()))
		print("Child 1 params: " + str(child1_params.values()))
		print("Child 2 params: " + str(child2_params.values()))	
		
		if child1_dirName in rankings.get('simulations'):
			print("Child 1 dir name is in ranking simulations")
		if child2_dirName in rankings.get('simulations'):
			print("Child 2 dir name is in ranking simulations")
		
		if child1_dirName not in rankings.get('simulations')  :
			print("Children created. Now running...")
			childrenCreated = True
			##Creating the config json file for child design 1
			child1_directoryPath = absoluteResultsPath + os.path.sep + child1_dirName
			if not os.path.exists(child1_directoryPath):
				os.makedirs(child1_directoryPath)
			child1_filepath	= child1_directoryPath + os.path.sep + DEFAULT_SIM_CONFIG
			child1_configParams = parent1_params
			child1_configParams = child1_params ##parameters section replaced with new parameters of child design
			
			child1_jsonOutput = json.dumps(parent1, sort_keys=True, indent=4, separators=(',',': '))	
			print("Child 1 filepath: " + str(child1_filepath))
			child1_json_output_file = open(child1_filepath,'w')	
			child1_json_output_file.write(child1_jsonOutput)
			child1_json_output_file.close()
			print("Running and evaluating child design 1: ")
			defineRunAndEvluatieSimulation(parsed_multimodel_json, "studentMap", child1_configParams, dseConfig, absoluteResultsPath, absoluteProjectPath) #Run and evaluate child design 1
			print("Child design 1 simulation completed")
		if  child2_dirName not in rankings.get('simulations') :	
			##Creating the config json file for child design 2
			child2_directoryPath = absoluteResultsPath + os.path.sep + child2_dirName
			if not os.path.exists(child2_directoryPath):
				os.makedirs(child2_directoryPath)
			child2_filepath	= child2_directoryPath + os.path.sep + DEFAULT_SIM_CONFIG
			print("Child 2 filepath: " + str(child2_filepath))
			child2_configParams = parent2_params
			child2_configParams = child2_params ##parameters section replaced with new parameters of child design
			
			child2_jsonOutput = json.dumps(parent2, sort_keys=True, indent=4, separators=(',',': '))	
			child2_json_output_file = open(child2_filepath,'w')	
			child2_json_output_file.write(child2_jsonOutput)
			child2_json_output_file.close()
			print("Running and evaluating child design 2: ")
			defineRunAndEvluatieSimulation(parsed_multimodel_json, "studentMap", child2_configParams, dseConfig, absoluteResultsPath, absoluteProjectPath) #Run and evaluate child design 2
			print("Child design 2 simulation completed")
		if child1_dirName in rankings.get('simulations') and child2_dirName in rankings.get('simulations') :
			print("Children already exist in rankings, now re-creating children...")
			child1_duplicateCounter = child1_duplicateCounter + 1
			child2_duplicateCounter = child2_duplicateCounter + 1
			if child1_duplicateCounter == 5 or child2_duplicateCounter == 5:	
				print("Unique children cannot be created. Reselecting parents")
				
				childrenCreated = True
	
def selectParents(dse_config, rankings):	
	paretoDesigns = rankings.get('pareto').get('1') ##Obtain the optimal designs on the pareto front
	parent1_index = random.randint(0,len(paretoDesigns) - 1)
	parent1_from_ranking = paretoDesigns[parent1_index] ##Random design chosen from pareto front for parent 1
	print("Parent 1: " + str(parent1_from_ranking))
	print("Parent 1 index: " + str(parent1_index))
	parent2_index = random.randint(0,len(paretoDesigns) - 1)
	print("Parent 2 index: " + str(parent2_index))
	designsChosen = False
	
	if len(paretoDesigns) > 1: #If there are more than one designs on the pareto front, choose designs from pareto front. If not, then choose a non-pareto parent for breeding
		parent2_from_ranking = paretoDesigns[parent2_index]
		print(str(parent2_from_ranking))
	else:
		designsChosen = True
		nonParetoDesigns = rankings.get('pareto').get('2')
		parent2_new_index = random.randint(0,len(nonParetoDesigns) - 1)
		parent2_from_ranking = nonParetoDesigns[parent2_index]
		
	designsUnique = False
	if designsChosen == False:
		while (designsUnique == False): ##Repeat this loop while parent designs chosen is not true		
			print("Design unique: " + str(designsChosen))
			if parent1_index !=  parent2_index: #Providing that the two parent designs are not equal, then designs for breeding have been chosen
				
				parent2_from_ranking = paretoDesigns[parent2_index] ##Random design chosen from pareto front for parent 2
				designsUnique = True ##Now, parent designs have been chosen as both chosen designs are not the same
			else:
				parent2_index = random.randint(0,len(paretoDesigns) - 1) ##Random design chosen again to make sure it is not the same design as for parent 1 and repeats until designs chosen are unique

	print("Parent 1: " + str(parent1_from_ranking))
	print("Parent 2: " + str(parent2_from_ranking))	
	
	##Opening and parsing the json config files for the chosen parent designs
	parent1_filePath = absoluteResultsPath + os.path.sep + str(parent1_from_ranking) + os.path.sep +  DEFAULT_SIM_CONFIG
	parent2_filePath = absoluteResultsPath + os.path.sep + str(parent2_from_ranking) + os.path.sep + DEFAULT_SIM_CONFIG
	parent1_open = open(parent1_filePath)
	parent2_open = open(parent2_filePath)
	parent1 = json.load(parent1_open)
	parent2 = json.load(parent2_open)
	
	non_pareto_probability = random.randint(1,100) ##When a random integer is chosen, this is used to determine when to use a non-pareto design for breeding		
	print("Non-pareto probability: " + str(non_pareto_probability ))
	if len(rankings.get('pareto').keys()) >= 2:
		##Creating different child designs by choosing parents with non-pareto chromosomes
		if len(rankings.get('pareto').keys()) == 2:
			non_pareto_rank = '2'
		else:
			non_pareto_rank = random.randint(2,len(rankings.get('pareto').keys()) - 1)
		non_pareto_designs = rankings.get('pareto').get(str(non_pareto_rank)) ##Obtain the designs which are not on the pareto front
		
		non_pareto_parent1_index = random.randint(0,len(non_pareto_designs) -1)
		non_pareto_parent1_path = absoluteResultsPath + os.path.sep + non_pareto_designs[non_pareto_parent1_index] + os.path.sep + DEFAULT_SIM_CONFIG
		non_pareto_parent1_open = open(non_pareto_parent1_path)
		non_pareto_parent1 = json.load(non_pareto_parent1_open)
		
		non_pareto_parent2_index = random.randint(0,len(non_pareto_designs) -1)
		non_pareto_parent2_path = absoluteResultsPath + os.path.sep + non_pareto_designs[non_pareto_parent2_index] + os.path.sep + DEFAULT_SIM_CONFIG
		non_pareto_parent2_open = open(non_pareto_parent2_path)
		non_pareto_parent2 = json.load(non_pareto_parent2_open)
		
		pareto_parent_index = random.randint(0,len(paretoDesigns) -1)
		pareto_parent_params = paretoDesigns[pareto_parent_index]
		pareto_parent_filepath = absoluteResultsPath + os.path.sep + pareto_parent_params + os.path.sep + DEFAULT_SIM_CONFIG
		pareto_parent_open = open(pareto_parent_filepath)
		pareto_parent = json.load(pareto_parent_open)
		
		print("\nParents selected. Now creating new offspring designs...")
		if non_pareto_probability % 5 == 0: ##There is a 20% chance that a pareto design will undergo breeding with a non-pareto design
			print("Child design created with a pareto parent and a non-pareto parent")
			createChildren(dse_config,non_pareto_parent1,pareto_parent,rankings)			
		elif non_pareto_probability % 10 == 0: ##There is a 10% chance that a pareto design will undergo breeding with both parent designs being non-pareto designs
			print("Child design created with two non-pareto parent designs")
			createChildren(dse_config,non_pareto_parent1,non_pareto_parent2,rankings)
		else:
			print("Child design created with two pareto parents")
			createChildren(dse_config,parent1,parent2,rankings)
	else:
		createChildren(dse_config,parent1,parent2,rankings)

def checkProgress(dseconfig, paretoDesignsBefore,paretoDesignsAfter,absoluteResultsPath,maxGenerationsWithoutImprovement):
	print("Check progress entered!")
	rank1_before = paretoDesignsBefore.get('1') #Retrieve rankings before a generation of the genetic algorithm	
	rank1_after = paretoDesignsAfter.get('1') #Retrieve rankings after a generation of the genetic algorithm
	
	
	#Check whether new designs are added to the pareto front by looking at whether there are any new parameter sets added
	if set(rank1_before) == set(rank1_after):
		global generationsWithoutImprovement
		generationsWithoutImprovement = generationsWithoutImprovement + 1
		print("Generations sampled: " + str(generationsWithoutImprovement))
		print("Generations to sample: " + str(maxGenerationsWithoutImprovement))
		print("There are no better designs being added to non-dominated set")
	else:
		generationsWithoutImprovement = 0 #Reset to 0 if a better design has been added to non-dominated set
		
		print("Better designs being added to non-dominated set. Continue with genetic DSE")
		print("Generations sampled: " + str(generationsWithoutImprovement))
	
	if generationsWithoutImprovement == maxGenerationsWithoutImprovement:
		print("The number of generations sampled is equal to the number of generations to sample, so stop simulations")
		stopSimulations = True #Terminate simulations
					
#######################################################################################################################################################################################
print("\n\nAUTOMATED DESIGN SPACE EXPLORATION (DSE) USING A GENETIC ALGORITHM APPROACH")
print("\nProcessing command line arguments: ")
absoluteProjectPath  = sys.argv[1] ##Project folder 	
relativeExperimentConfigFile = sys.argv[2] ##DSE file 			lfr-1.dse.json
#multiModelConfigFile = sys.argv[3] ##MultiModel file 	lfr-1.mm.json
relativeCoeConfigFile = sys.argv[3]
#initialPopulationSizeStr = sys.argv[4] ##Specifies the initial population of designs to simulate
#initialPopulationSize = int(initialPopulationSizeStr)
#maxGenerationsWithoutImprovementStr = sys.argv[5]#How many generations to iterate before stopping after no better designs are found
#maxGenerationsWithoutImprovement = int(maxGenerationsWithoutImprovementStr)
#phaseChoice = int(sys.argv[6])  
#absoluteExperimentPath = absoluteProjectPath + os.path.sep + DSE_FOLDER + os.path.sep ##Where DSE folder is located
absoluteExperimentConfigPath = os.path.join(absoluteProjectPath, relativeExperimentConfigFile) ##Where the json config file is located
trimLocation = absoluteExperimentConfigPath.rfind(os.path.sep)
absoluteExperimentPath = absoluteExperimentConfigPath[:trimLocation] + os.path.sep

#absoluteBaseMultiModelPath = absoluteProjectPath + os.path.sep + MULTI_MODEL_FOLDER + os.path.sep + multiModelConfigFile ##Where the multimodel file is located

absoluteCoeConfigFile = absoluteProjectPath + os.path.sep + relativeCoeConfigFile

absoluteUserScriptPath = absoluteProjectPath + os.path.sep + USER_METRICS_FOLDER + os.path.sep ##Where user scripts are loated
dateTimeFolder = dateTimeFolderName()
absoluteResultsPath = absoluteExperimentPath + dateTimeFolder ##Where results are to be stored

stopSimulations = False
generationsWithoutImprovement = 0

print ("Opening DSE config: " + relativeExperimentConfigFile)
dseConfig_data = open(absoluteExperimentConfigPath)
dseConfig = json.load(dseConfig_data)

initialPopulationSize = dseConfig['algorithm']['initialPopulation']
initialPopulationDistribution  = dseConfig['algorithm']['initialPopulationDistribution']
parentSelectionStrategy = dseConfig['algorithm']['parentSelectionStrategy']
mutationProbability = dseConfig['algorithm']['mutationProbability']
maxGenerationsWithoutImprovement = dseConfig['algorithm']['maxGenerationsWithoutImprovement']

initialPopulationDistribution == dseConfig['algorithm']['initialPopulationDistribution']
parentSelectionStrategy == dseConfig['algorithm']['parentSelectionStrategy']

	
print ("Opening multi model: " + relativeCoeConfigFile)
#multimodel_json_data = open(absoluteBaseMultiModelPath)
#parsed_multimodel_json = json.load(multimodel_json_data)
parsed_multimodel_json = combineModelFiles(absoluteCoeConfigFile, dseConfig, absoluteProjectPath)

print ("Creating Date Time folder")
makeDateTimeFolder(absoluteExperimentPath, dateTimeFolder)


phaseChoice = -1

phaseChosen = False
while phaseChosen == False:
	print("Phase choice: " + str(phaseChoice))
	if initialPopulationDistribution == INITIAL_POPULATION_DISTRIBUTION_RANDOM and parentSelectionStrategy == PARENT_SELECTION_STRATEGY_RANDOM:
	#if phaseChoice == 1:
		phaseChosen = True
		print("\nRunning DSE with genetic algorithm using random initial set")
		print("\nStep 1: Generating initial set of simulation results")
		runInitialSimulations(dseConfig, parsed_multimodel_json, initialPopulationSize)

		#Repeat loop of selecting parent designs, breeding children and then evaluating their results. Terminates when no more progress is made in finding designs on the pareto front
		while stopSimulations == False and generationsWithoutImprovement <= maxGenerationsWithoutImprovement:
			
			print("\n\nStep 2: Selecting parents for breeding and creating new child designs")
			rankingFilePath = absoluteResultsPath + os.path.sep + RANKING_FILE
			rankingFilePathOpen = open(rankingFilePath)
			rankingFileDataParsed = json.load(rankingFilePathOpen)
			paretoDesignsBefore = rankingFileDataParsed.get('pareto')
			
			selectParents(dseConfig,rankingFileDataParsed)
			subprocess.call(["python", "Ranking_pareto.py",absoluteExperimentPath, absoluteExperimentConfigPath,  absoluteResultsPath])
			
			print("\n\nStep 3: Evaluate current progress and determine whether to continue")	
			rankingFilePathAfter = absoluteResultsPath + os.path.sep + RANKING_FILE
			rankingFilePathAfterOpen = open(rankingFilePathAfter)
			rankingFileDataAfterParsed = json.load(rankingFilePathAfterOpen) #Parses the ranking data after the genetic algorithm has been run
			paretoDesignsAfter = rankingFileDataAfterParsed.get('pareto')
			checkProgress(dseConfig, paretoDesignsBefore,paretoDesignsAfter, absoluteResultsPath,maxGenerationsWithoutImprovement)
		
		#Rank final designs
		print("Starting the ranking...")
		subprocess.call(["python", "Ranking_pareto.py",absoluteExperimentPath, absoluteExperimentConfigPath,  absoluteResultsPath])
		print("Ranking complete.")

		#Generating HTML output page
		print("Generating results page...")
		subprocess.call(["python", "Output_HTML.py", absoluteExperimentPath, absoluteResultsPath])
		print("Page complete.")
		print("DSE complete.")
		
		
	#elif phaseChoice == 2:
	#elif initialPopulationDistribution == INITIAL_POPULATION_DISTRIBUTION_UNIFORM and parentSelectionStrategy == PARENT_SELECTION_STRATEGY_RANDOM:
	#	phaseChosen = True
	#	print("\nRunning DSE with uniform distribution of initial set")
	#	subprocess.call(["python","genetic_DSE_phase2.py", absoluteProjectPath, experimentConfigFile, multiModelConfigFile, initialPopulationSizeStr, maxGenerationsWithoutImprovementStr])
	
	#elif phaseChoice == 3:
	#elif initialPopulationDistribution == INITIAL_POPULATION_DISTRIBUTION_UNIFORM and parentSelectionStrategy == PARENT_SELECTION_STRATEGY_ALGORITHM_OBJECTIVE_SPACE:
	#	phaseChosen = True
	#	print("\nRunning DSE with uniform distribution of initial set and algorithmic selection of parent designs in objective space")
	#	subprocess.call(["python","genetic_DSE_phase3.py",absoluteProjectPath,experimentConfigFile,multiModelConfigFile,initialPopulationSizeStr, maxGenerationsWithoutImprovementStr])
	
	#elif phaseChoice == 4:
	#elif initialPopulationDistribution == INITIAL_POPULATION_DISTRIBUTION_UNIFORM and parentSelectionStrategy == PARENT_SELECTION_STRATEGY_ALGORITHM_DESIGN_SPACE:
	#	phaseChosen = True
	#	print("\nRunning DSE with uniform distribution of initial set and algorithmic selection of parent designs in design space")
	#	subprocess.call(["python","genetic_DSE_phase4.py",absoluteProjectPath,experimentConfigFile,multiModelConfigFile,initialPopulationSizeStr, maxGenerationsWithoutImprovementStr])
	
	else:
		phaseChosen = False
		phaseChoice = int(raw_input("Phase not recognised. Try again ==> "))