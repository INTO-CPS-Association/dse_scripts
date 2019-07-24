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
	thisRow = []
	
	if os.path.exists(file_path):
	
		results_data_file =  open(absoluteResultsPath + os.path.sep + simFolder + os.path.sep + OBJECTIVES_FILE) 
		results_json = json.load(results_data_file)	

		#for objective in results_json:
			#ranking_json[simFolder][objective] = results_json[objective] <- commented out so we don't copy objective values into ranking json for now
			#thisRow.append(results_json[objective])
	
		for objective in objectiveOrder:
			print(objective)
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
				thisRow.append(results_json[objective])
			except ValueError:
				fault_detected = True
	
	else:
		fault_detected = True
		
	thisRow.append(simFolder)
	
	if fault_detected:
		rowsWithFaults.append(thisRow)
	else:
		rows.append(thisRow)
	#return thisRow


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



def multiOrderSort(toBeSorted, sortingposition, sortingdirections):
	
	if sortingposition >= 0:
		newSortedList = sortList(toBeSorted, sortingposition, sortingdirections[sortingposition])
		sortingposition -= 1
		return multiOrderSort(newSortedList, sortingposition, sortingdirections)
	else:
		return toBeSorted
		
		
def sortList(toBeSorted, sortingposition, sortingdirection):
	if sortingdirection == '-':
		print ('sorting for a -', sortingposition)
		return sorted(toBeSorted, key=lambda designTuple: designTuple[sortingposition], reverse=False)
	else:
		print ('sorting for a +', sortingposition)
		return sorted(toBeSorted, key=lambda designTuple: designTuple[sortingposition], reverse=True)
	

def compareTwoResults(thisResult, sortingdirection, current_rank):
	if sortingdirection == '-':
		return thisResult[1] < current_rank[-1][1]
	else:
		return thisResult[1] > current_rank[-1][1]
	
#def getObjectivesToMaximise(objectiveOrder):
#	objectiveColumnsToMaximise = []
#	for objective in paretoDetails:
#		if paretoDetails[objective] == '+':
#			for position in len(objectiveOrder)
#			objectivesToMaximise.append(objective)

def getObjectiveDirections(paretoDetails):
	objectiveDirections = []
	for objective in paretoDetails:
		objectiveDirections.append(paretoDetails[objective])
	return objectiveDirections

print ("Opening ranking.json")
json_data = open(absoluteResultsPath + os.path.sep + RANKING_FILE)
ranking_json = json.load(json_data)
json_data.close()

simulation_list = ranking_json['simulations']

dseConfigData = open(absoluteExperimentConfigPath)
dseConfigJson = json.load(dseConfigData)

paretoDetails = dseConfigJson['ranking']['pareto']
rank_id = 'pareto'

objectiveOrder = getObjectiveOrder()
objectiveCount = len(paretoDetails)
objectiveDirections = getObjectiveDirections(paretoDetails)


# rows contain results with valid objective data
# rowsWithFaults contain all results that have invalid data 
rows = []
rowsWithFaults = []

#rows = readInObjectivesFromSimResults(simulation_list)
readInObjectivesFromSimResults(simulation_list)

#output list of unrankable (faulty) results
unrankableResultsID = 'unrankable'
ranking_json[unrankableResultsID] = []
unrankableR_root = ranking_json[unrankableResultsID]
for unrankable in rowsWithFaults:
	ranking_json[unrankableResultsID].append(unrankable[-1])


#resultsSorted = sorted(rows)
resultsSorted = multiOrderSort(rows, len(objectiveDirections)-1, objectiveDirections)

ranks = []
while len(resultsSorted) > 0:
	#p_front = [resultsSorted[0]]
	#dominated_list=[]   
	current_rank = [resultsSorted[0]]
	# Loop through the sorted list
	for result in resultsSorted[1:]:
		#if result[1] < current_rank[-1][1]: # Look for higher values of Y
		if compareTwoResults(result, objectiveDirections[1], current_rank):
			current_rank.append(result) #  and add them to the Pareto front
	
	ranks.append(current_rank)
	for result in current_rank:
		resultsSorted.remove(result)
	
# add ranking result to ranking json
ranking_json[rank_id] = {}
rank_root = ranking_json[rank_id]
rankNumber = 0
for rank in ranks:
	rankNumber += 1
	rank_root[rankNumber] = []
	for result in rank:
		rank_root[rankNumber].append(result[-1])




#rank = 1

#rank_root[rank] = []
#for result in p_front:
#	rank_root[rank].append(result[-1])

#rank += 1

#rank_root[rank] = []
#for result in dominated_list:
#	rank_root[rank].append(result[-1])

json_output = json.dumps(ranking_json, sort_keys=True, indent=4, separators=(',',': '))
#print json_output
json_output_file = open(absoluteResultsPath + os.path.sep +  RANKING_FILE,'w')
json_output_file.write(json_output)
json_output_file.close()

#Output graphs
graphFolder = absoluteResultsPath + os.path.sep +  GRAPHS_FOLDER
if not os.path.exists(graphFolder):
	os.makedirs(graphFolder)


#Xs = []
#Ys = []
#for result in resultsSorted:
#	Xs.append(result[0])
#	Ys.append(result[1])

#plt.scatter(Xs, Ys)
#plt.plot(Xs, Ys, 'ro')

# plot pareto fron in blue
# non_dominated_set = True
# odd = True
# for rank in ranks:
	# Xs=[]
	# Ys=[]

	# for result in rank:
		# Xs.append(result[0])
		# Ys.append(result[1])
	# if non_dominated_set:
		# plt.plot(Xs, Ys, 'g')
		# plt.plot(Xs, Ys, 'go')
		# non_dominated_set = False
	# else:
		# if odd:
			# odd = False
			# plt.plot(Xs, Ys, 'r')
			# plt.plot(Xs, Ys, 'ro')
		# else:
			# odd = True
			# plt.plot(Xs, Ys, 'y')
			# plt.plot(Xs, Ys, 'yo')


# plt.xlabel(objectiveOrder[0])
# plt.ylabel(objectiveOrder[1])

# plotFileName = graphFolder + os.path.sep + rank_id + ".png"
# plt.savefig(plotFileName, dpi=75)


# plot pareto fron in blue
fig = Figure()
ax = fig.add_subplot(1,1,1)
non_dominated_set = True
odd = True
for rank in ranks:
	Xs=[]
	Ys=[]

	for result in rank:
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

ax.set_xlabel(objectiveOrder[0])
ax.set_ylabel(objectiveOrder[1])

plotFileName = os.path.join(graphFolder, rank_id + ".png")
canvas = FigureCanvas(fig)
canvas.print_figure(plotFileName, dpi=75)