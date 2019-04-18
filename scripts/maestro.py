import os,sys,json,pandas
import urllib.request
import urllib.error
from io import StringIO

def jsonCall(url, data):
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    return urllib.request.urlopen(req, data.encode('ascii'))
    
def file_len(fname):
    i = 0
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1    
    
URL = "http://localhost:8082"

START_TIME = 0
END_TIME = 3
CONFIG = "config.json"
RESULT = "result.csv"
verbose = False

config = ""
with open(CONFIG, 'r') as f:
    config = f.read()

# Create session
try:
    response = urllib.request.urlopen(URL + "/createSession")
    status = json.load(response)
    if verbose:
        print(status)
    sessionId = status['sessionId']
    print( "\tCreated session: " + str(sessionId))
except urllib.error.URLError as e:
    print( str(e))
    exit(-1)
    
# Initialize
try:
    response = jsonCall(URL + "/initialize/" + str(sessionId), config)
    status = json.load(response)
    if verbose:
        print( status)

    print( "\tInitialized session status: " + status[0]['status'])
except urllib.error.URLError as e:
    print( str(e))
    print( e.read())
    exit(-1)
    
# Simulate
try:
    #config = {'startTime': START_TIME, 'endTime': END_TIME}
    #
    #    #"reportProgress":true,"liveLogInterval":0,"logLevels":{"{G}.GInstance":["logAll","logError","logFmiCall","Protocol","VdmErr","VdmOut"],"{H}.HInstance":["logAll","logError","logFmiCall","Protocol","VdmErr","VdmOut"]}
    
    config = {'startTime': START_TIME, 'endTime': END_TIME, "logLevels":{"{G}.GInstance":["logAll","logError","logFmiCall","Protocol","VdmErr","VdmOut"],"{H}.HInstance":["logAll","logError","logFmiCall","Protocol","VdmErr","VdmOut"]}}
    
    response = jsonCall(URL + "/simulate/" + str(sessionId),
                        json.dumps(config))
    status = json.load(response)

    if verbose:
        print( status)

    print( "\tSimulation " + str(status['status'] + " in " + str(
        status['lastExecTime']) + " seconds"))
except urllib.error.URLError as e:
    print( str(e))
    print( e.read())
    exit(-1)

# Get result
try:
    response = urllib.request.urlopen(URL + "/result/" + str(sessionId))
    result = response.read()
    #CHUNK = 16 * 1024
    #
    #with open(RESULT, 'wb') as f:
    #    while True:
    #        chunk = response.read(CHUNK)
    #        if not chunk:
    #            break
    #        f.write(chunk)
    #print( "\tRead result " + str(file_len(RESULT)) + " lines")
    s = str(result, 'utf-8')
    data = StringIO(s) 
    df = pandas.read_csv(data)
    print (df)
except urllib.error.URLError as e:
    print( str(e))
    print( e.read())
    exit(-1)    
    
# Destroy
try:
    response =  urllib.request.urlopen(URL + "/destroy/" + str(sessionId))
except urllib.error.URLError as e:
    print( str(e))
    print( e.read())
    exit(-1)

print( "\tsimulation done")    