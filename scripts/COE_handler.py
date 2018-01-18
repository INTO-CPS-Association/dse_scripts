import sys, os, subprocess, platform, time, json, urllib2
from libs.Common import *


absoluteSimulationPath = sys.argv[1]
start_time = sys.argv[2]
end_time = sys.argv[3]

pt = platform.system()

url = "http://localhost:8082"

def jsonCall(url, data):
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    return urllib2.urlopen(req, data)

def aResultsFileAlreadyExists(absoluteSimulationPath):
	resultsFilePath = os.path.join(absoluteSimulationPath,RESULTS_FILE)
	if os.path.exists(resultsFilePath):
		if os.path.getsize(resultsFilePath) > 200:
			return True
		else:
			os.remove(resultsFilePath)
	return False


def getSessionKeyFromInitialisationResponse(rawInitResponse):
	parsedInitResponse = json.loads(rawInitResponse)[0]
	#print json.dumps(parsedInitResponse, sort_keys=True, indent=4, separators=(',',': '))
	sessionKey = parsedInitResponse['sessionId']	
	return sessionKey

def getSessionKeyFromSessionResponse(rawSessionResponse):
	#parsedSessionResponse = json.loads(rawSessionResponse)
	parsedSessionResponse = json.load(rawSessionResponse)
	#print json.dumps(parsedInitResponse, sort_keys=True, indent=4, separators=(',',': '))
	sessionKey = parsedSessionResponse['sessionId']	
	return sessionKey


def runSimulationAndGetResults():
	print("        get session id")

	#sessionCmd = 'curl -s http://localhost:8082/createSession'
	sessionURL = url + "/createSession"
	#rawSessionResponse = subprocess.check_output(sessionCmd, shell=True)
	rawSessionResponse = urllib2.urlopen(sessionURL)
	print ""
	print "raw response"
	print(rawSessionResponse)

	sessionKey = getSessionKeyFromSessionResponse(rawSessionResponse)
	print "            session id: " + str(sessionKey)


	time.sleep(1)


	print("        initiliasing simulation")

	#initilise the coe and get session id
	configPath = absoluteSimulationPath + os.path.sep + DEFAULT_SIM_CONFIG
	#initialiseCmd = 'curl -s -H "Content-Type: application/json" --data @' + configPath + ' http://localhost:8082/initialize/' + str(sessionKey)
	
	#print ""
	#print "intialisation cmd"
	#print(initialiseCmd)
	
	configData = ""
	with open(configPath, 'r') as f:
		configData = f.read()

	initialisationresponse = jsonCall(url + "/initialize/" + str(sessionKey), configData)
	#initialisationResponse = subprocess.check_output(initialiseCmd, shell=True)
	#print ""
	#print "intialisation response"
	#print(initialisationResponse)
	#sessionKey = getSessionKeyFromInitialisationResponse(initialisationResponse)
	time.sleep(1)


	print("        launching simulation")
	#if pt == 'Darwin':
	#	#print("Darwin detected")
	#	runSimulationCmd = 'curl -s -H "Content-Type: application/json" --data \'{"startTime":' + start_time + ', "endTime":' + end_time +'}\' http://localhost:8082/simulate/' + str(sessionKey)
	
	#if pt == 'Linux':
	#	print("Linux detected - but not yet supported")
	
	#if pt == 'Windows':
		#print("Windows detected")
	#	runSimulationCmd = 'curl -s -H "Content-Type: application/json" --data "{\\"startTime\\":' + start_time + ', \\"endTime\\":' + end_time +'}" http://localhost:8082/simulate/' + str(sessionKey)
	#print ""
	#print "simulation cmd"
	#print runSimulationCmd
	
	config = {'startTime': start_time, 'endTime': end_time}
	runSimulationResponse = jsonCall(url + "/simulate/" + str(sessionKey), json.dumps(config))
    #status = json.load(response)
	
	#runSimulationResponse = subprocess.check_output(runSimulationCmd, shell=True)
	#print ""
	#print "simulation response"
	#print runSimulationResponse

	time.sleep(1)

	print("        fetching results")
	#getResultsCmd = 'curl -s http://localhost:8082/result/' + str(sessionKey)
	getResultsURL = url + "/result/" + str(sessionKey)
	#print ""
	#print "get results cmd"
	#print getResultsCmd

	#getResultsResponse = subprocess.check_output(getResultsCmd, shell=True)
	getResultsResponse = urllib2.urlopen(getResultsURL)
	#print ""
	print "get results response"
	print getResultsResponse

	CHUNK = 16 * 1024

	

#	if args.repeat is not None:
#       resultPath = resultPath[:resultPath.rfind('.')] + "-%06d.csv" % (simIndex,)

	resultPath = absoluteSimulationPath + os.path.sep + RESULTS_FILE

	with open(resultPath, 'wb') as f:
		while True:
			chunk = getResultsResponse.read(CHUNK)
			if not chunk:
				break
			f.write(chunk)

	#resultsFile = open(absoluteSimulationPath + os.path.sep + RESULTS_FILE,'w')
	#resultsFile.write(getResultsResponse)
	#print 'Results Printed'

	print("        destroying session")
	#destroySessionCmd = 'curl -s http://localhost:8082/destroy/' + str(sessionKey)
	destroyURL = url + "/destroy/" + str(sessionKey)
	#getDestroyResponse = subprocess.check_output(getResultsCmd, shell=True)
	getDestroyResponse = urllib2.urlopen(destroyURL)
	
if aResultsFileAlreadyExists(absoluteSimulationPath):
	print "        Results file already exists, skipping this simulation"
else:
	runSimulationAndGetResults()
	