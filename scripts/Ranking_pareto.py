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


absoluteExperimentDir = sys.argv[1]
absoluteExperimentConfigPath = sys.argv[2]
absoluteResultsPath = sys.argv[3]




class DSEResult:

	COMPARISON_DOMINATES = 0
	COMPARISON_PEER = 1
	COMPARISON_DOMINATEDBY = 2

	objectives = {}
	#scoreDirections = {} # + = higher, - = lower, any other char = not used
	id = ''
	
	def __init__(self, objectives, id):
		self.objectives = objectives
		#self.scoreDirections = scoreDirections
		self.id = id

		#print 'constructor'
		#print self.id
		#print self.objectives
		#print 'constructor ends'


	def compareTo (self, otherResult):
		selfHasABetterValue = False
		otherHasABetterValue = False

		for objective in objectiveDirections:

			direction = objectiveDirections[objective]

			

			#print index, len(self.scores), len(self.scoreDirections)
			if direction == '-':
				if self.objectives[objective] < otherResult.objectives[objective]:
					selfHasABetterValue = True
				if self.objectives[objective] > otherResult.objectives[objective]:
					otherHasABetterValue = True
			if direction == '+':
				if self.objectives[objective] > otherResult.objectives[objective]:
					selfHasABetterValue = True
				if self.objectives[objective] < otherResult.objectives[objective]:
					otherHasABetterValue = True

			#print '        ', objective, direction, selfHasABetterValue, otherHasABetterValue
		
		if selfHasABetterValue and not otherHasABetterValue:
			#print self.id, 'dominates', otherResult.id
			return self.COMPARISON_DOMINATES
	
		if not selfHasABetterValue and otherHasABetterValue:
			#print self.id, 'dominated by', otherResult.id
			return self.COMPARISON_DOMINATEDBY

		if selfHasABetterValue and otherHasABetterValue:
			#print self.id, 'peer', otherResult.id
			return self.COMPARISON_PEER

		if not selfHasABetterValue and not otherHasABetterValue:
			#print self.id, 'peer', otherResult.id
			return self.COMPARISON_PEER


	
def readInObjectivesFromSimResults(simulation_list):
	#rows = []
	#rowsWithFaults = []
	for folder in simulation_list:
		#rows.append(processFolder(folder))
		processFolder(folder)
	#return rows
			
def processFolder(simFolder):

	file_path = absoluteResultsPath + os.path.sep + simFolder + os.path.sep + OBJECTIVES_FILE
	fault_detected = False
	#thisRow = []

	thisResultObjectives = {}
	
	if os.path.exists(file_path):
	
		results_data_file =  open(absoluteResultsPath + os.path.sep + simFolder + os.path.sep + OBJECTIVES_FILE) 
		results_json = json.load(results_data_file)	

		#for objective in results_json:
			#ranking_json[simFolder][objective] = results_json[objective] <- commented out so we don't copy objective values into ranking json for now
			#thisRow.append(results_json[objective])
	
		for objective in objectiveDirections:
			#print(objective)
			#ranking_json[simFolder][objective] = results_json[objective] <- commented out so we don't copy objective values into ranking json for now
		
			if results_json[objective] == FAULT_NO_RESULTS:
				fault_detected = True
				
			if results_json[objective] == FAULT_COLUMN_NOT_FOUND:
				fault_detected = True
			
			if results_json[objective] == FAULT_SIMULATION_DID_NOT_END:
				fault_detected = True
				
			if results_json[objective] == FAULT_VALUE_COULD_NOT_BE_COMPUTED:
				fault_detected = True
				
			if results_json[objective] == FAULT_OBJECTIVE_ARGUMENT_MISSING:
				fault_detected = True
				
			if results_json[objective] == FAULT_EMPTY_RESULTS_FOUND:
				fault_detected = True
				
			if results_json[objective] == FAULT_GENERAL:
				fault_detected = True
				
			# finally check that the objective is numeric to catch any mistype fault identifiers
			try:
				float(results_json[objective])
				thisResultObjectives[objective] = results_json[objective]
				#thisRow.append(results_json[objective])
			except ValueError:
				fault_detected = True
	
	else:
		fault_detected = True

	this_dse_result = DSEResult(thisResultObjectives, simFolder)
		
	#thisRow.append(simFolder)
	
	if fault_detected:
		#rowsWithFaults.append(thisRow)
		resultsWithFaultsMap[this_dse_result] = 0
	else:
		#rows.append(thisRow)
		resultsMap[this_dse_result] = 0
	#return thisRow


#def getObjectiveOrder():
#	objectiveOrder = []
#	for objective in paretoDetails:
#		objectiveOrder.append(objective)
#		
#	for objective in dseConfigJson['objectiveDefinitions']['internalFunctions']:
#		if not objective in objectiveOrder:
#			objectiveOrder.append(objective)
#	
#	for objective in dseConfigJson['objectiveDefinitions']['externalScripts']:
#		if not objective in objectiveOrder:
#			objectiveOrder.append(objective)
#	
#	return objectiveOrder

def getObjectiveDirections():
	objectiveDirections = {}
	for objective in paretoDetails:
		objectiveDirections[objective] = paretoDetails[objective]

	return objectiveDirections
#def multiOrderSort(toBeSorted, sortingposition, sortingdirections):
#	
#	if sortingposition >= 0:
#		newSortedList = sortList(toBeSorted, sortingposition, sortingdirections[sortingposition])
#		sortingposition -= 1
#		return multiOrderSort(newSortedList, sortingposition, sortingdirections)
#	else:
#		return toBeSorted
		
		
#def sortList(toBeSorted, sortingposition, sortingdirection):
#	if sortingdirection == '-':
#		print ('sorting for a -', sortingposition)
#		return sorted(toBeSorted, key=lambda designTuple: designTuple[sortingposition], reverse=False)
#	else:
#		print ('sorting for a +', sortingposition)
#		return sorted(toBeSorted, key=lambda designTuple: designTuple[sortingposition], reverse=True)
	

#def compareTwoResults(thisResult, sortingdirection, current_rank):
#	if sortingdirection == '-':
#		return thisResult[1] < current_rank[-1][1]
#	else:
#		return thisResult[1] > current_rank[-1][1]
	
#def getObjectivesToMaximise(objectiveOrder):
#	objectiveColumnsToMaximise = []
#	for objective in paretoDetails:
#		if paretoDetails[objective] == '+':
#			for position in len(objectiveOrder)
#			objectivesToMaximise.append(objective)

#def getObjectiveDirections(paretoDetails):
#	objectiveDirections = []
#	for objective in paretoDetails:
#		objectiveDirections.append(paretoDetails[objective])
#	return objectiveDirections

print ("Opening ranking.json")
json_data = open(absoluteResultsPath + os.path.sep + RANKING_FILE)
ranking_json = json.load(json_data)
json_data.close()

simulation_list = ranking_json['simulations']

dseConfigData = open(absoluteExperimentConfigPath)
dseConfigJson = json.load(dseConfigData)

paretoDetails = dseConfigJson['ranking']['pareto']
rank_id = 'pareto'

objectiveDirections = getObjectiveDirections()
#objectiveCount = len(paretoDetails)
#objectiveDirections = getObjectiveDirections(paretoDetails)


# rows contain results with valid objective data
# rowsWithFaults contain all results that have invalid data 
#rows = []
#rowsWithFaults = []


#Data structure for new n-parameter ranking
resultsMap = {}
resultsWithFaultsMap = {} 

#rows = readInObjectivesFromSimResults(simulation_list)
readInObjectivesFromSimResults(simulation_list)

#output list of unrankable (faulty) results
unrankableResultsID = 'unrankable'
ranking_json[unrankableResultsID] = []
unrankableR_root = ranking_json[unrankableResultsID]
for unrankable in resultsWithFaultsMap:
	ranking_json[unrankableResultsID].append(unrankable.id)


#resultsSorted = sorted(rows)
#resultsSorted = multiOrderSort(rows, len(objectiveDirections)-1, objectiveDirections)

#ranks = []
#while len(resultsSorted) > 0:
	#p_front = [resultsSorted[0]]
	#dominated_list=[]   
#	current_rank = [resultsSorted[0]]
	# Loop through the sorted list
#	for result in resultsSorted[1:]:
		#if result[1] < current_rank[-1][1]: # Look for higher values of Y
#		if compareTwoResults(result, objectiveDirections[1], current_rank):
#			current_rank.append(result) #  and add them to the Pareto front
	
#	ranks.append(current_rank)
#	for result in current_rank:
#		resultsSorted.remove(result)



def checkDesignsStillInPool(resultsMap):
	for result in resultsMap:
		if resultsMap[result] == 0:
			return True
	return False

currentRank = 0

while (checkDesignsStillInPool(resultsMap)):
	currentRank += 1
	print currentRank
	firstCandidate = True
	for candidate in resultsMap:
		if resultsMap[candidate] == 0:  #in pool to rank
			#print 'candidate is', candidate.id
			if firstCandidate:
				resultsMap[candidate] = currentRank
				#print 'adding first to', currentRank
				firstCandidate = False
			else:
				#print 'rank already populated'
				for inRankDesign in resultsMap:
					
					if resultsMap[inRankDesign] == currentRank and inRankDesign != candidate:
						
						#print '    comparing', candidate.id, 'with', inRankDesign.id
						comparisonResult = candidate.compareTo(inRankDesign)
						
						if comparisonResult == DSEResult.COMPARISON_DOMINATES:
							#print '        dominates'
							resultsMap[candidate] = currentRank
							resultsMap[inRankDesign] = 0
							#print '     ', candidate.id, str(resultsMap[candidate])
							#print '     ', inRankDesign.id, str(resultsMap[inRankDesign])
						if comparisonResult == DSEResult.COMPARISON_PEER:
							#print '        peer'
							resultsMap[candidate] = currentRank
							#print '     ', candidate.id, str(resultsMap[candidate])
						if comparisonResult == DSEResult.COMPARISON_DOMINATEDBY:
							#print '        Dominated by - breaking to outer loop'
							resultsMap[candidate] = 0
							break




# add ranking result to ranking json
ranking_json[rank_id] = {}
rank_root = ranking_json[rank_id]
rankNumber = 0

while True:
	resultFoundInRank = False
	rankNumber += 1
	for result in resultsMap:
		if resultsMap[result] == rankNumber:

			if not resultFoundInRank:
				rank_root[rankNumber] = []
				resultFoundInRank = True
			
			rank_root[rankNumber].append(result.id)

	if not resultFoundInRank:
		break



#for rank in ranks:
#	rankNumber += 1
#	rank_root[rankNumber] = []
#	for result in rank:
#		rank_root[rankNumber].append(result[-1])





#rank = 1

#rank_root[rank] = []
#for result in p_front:
#	rank_root[rank].append(result[-1])

#rank += 1

#rank_root[rank] = []
#for result in dominated_list:
#	rank_root[rank].append(result[-1])

print
print '*****************************************'
print ' printing ranking_json'
print '****************************************'
print ranking_json

print
print '*****************************************'
print ' printing ranking_json... done'
print '****************************************'




json_output = json.dumps(ranking_json, sort_keys=True, indent=4, separators=(',',': '))
#print json_output
json_output_file = open(absoluteResultsPath + os.path.sep +  RANKING_FILE,'w')
json_output_file.write(json_output)
json_output_file.close()

#Output graphs
graphFolder = absoluteResultsPath + os.path.sep +  GRAPHS_FOLDER
if not os.path.exists(graphFolder):
	os.makedirs(graphFolder)




#def plot2AxisGraph(objective1, objective2):

# plot pareto fron in blue
#fig = Figure()
#ax = fig.add_subplot(1,1,1)
#non_dominated_set = True
#odd = True
#for rank in ranks:
#	Xs=[]
#	Ys=[]

#	for result in rank:
#		Xs.append(result[0])
#		Ys.append(result[1])
#	if non_dominated_set:
#		ax.plot(Xs, Ys, 'g')
#		ax.plot(Xs, Ys, 'go')
#		non_dominated_set = False
#	else:
#		if odd:
#			odd = False
#			ax.plot(Xs, Ys, 'r')
#			ax.plot(Xs, Ys, 'ro')
#		else:
#			odd = True
#			ax.plot(Xs, Ys, 'y')
#			ax.plot(Xs, Ys, 'yo')
#
#ax.set_xlabel(objectiveOrder[0])
#ax.set_ylabel(objectiveOrder[1])

#plotFileName = os.path.join(graphFolder, rank_id + ".png")
#canvas = FigureCanvas(fig)
#canvas.print_figure(plotFileName, dpi=75)