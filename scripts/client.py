#! /usr/bin/env python
import urllib.request
import urllib.error
import os
import argparse
import json
import time
import asyncio
import websockets
import socket
import pprint
from concurrent.futures import ProcessPoolExecutor

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

async def listen(url, id):
    uri = 'ws://%s/attachSession/%s' % (url.split("://")[1],id)
    print(uri)
    #try:
    async with websockets.connect(uri) as websocket: #websockets.connect('ws://%s/attachSession/%s' % (url.split("://")[1],id)):
        while True:
          print("bar")
          message = await websocket.recv()
          print(message)
    #except socket.gaierror as e:
    #    print(pprint.pprint(e))
        
parser = argparse.ArgumentParser(description='Python COE Client')

parser.add_argument('--config', metavar='PATH', required=True,
                    help='Path to a valid configuration file')

parser.add_argument('--result', metavar='RESULT_PATH', required=True,
                    help='The path of the COE generated result file (CSV)')

parser.add_argument('--starttime', metavar='time', required=False,
                    help='The start time')

parser.add_argument('--endtime', metavar='time', required=True,
                    help='The end time')

parser.add_argument('--url', metavar='url', required=False,
                    help='The COE endpoint url')

parser.add_argument('--repeat', metavar='count', required=False,
                    help='Number of times to repeat the simulation')

parser.add_argument('--verbose', action='store_const', const=True, help='Verbose')

args = parser.parse_args()

# Check required info
verbose = False

if args.verbose is not None:
    verbose = True

url = "http://localhost:8082"

if args.url is not None:
    url = args.url
    if url[-1] == "/":
        url = url[:len(url) - 1]

startTime = 0
if args.starttime is not None:
    startTime = float(args.starttime)

endTime = float(args.endtime)

if startTime >= endTime:
    print("Invalid end time. <start time> " + str(
        +startTime) + " must be less than <end time> " + str(endTime))
    exit(-1)

if not os.path.exists(args.config):
    print("Config path invalid: " + args.config)
    exit(-1)

repeats = 1
print( "Configuration:")
print( "\tStart Time   : " + str(startTime))
print( "\tEnd Time     : " + str(endTime))
print( "\tConfig Path: : " + args.config)
print( "\tResult Path: : " + args.result)
print( "\tCOE end point: " + url)
if args.repeat is not None:
    repeats = int(args.repeat)
    print( "\tRepeats      : " + str(repeats))

exec_start_time = time.time()

for simIndex in range(0, repeats):
    if args.repeat is not None:
        print( "\nSimulating: " + str(simIndex + 1) + " / " + str(repeats))

    #
    # Simulation
    #
    sesstionId = ""

    # Create session
    try:
        response = urllib.request.urlopen(url + "/createSession")
        status = json.load(response)
        if verbose:
            print( status)
        sessionId = status['sessionId']
        print( "\tCreated session: " + str(sessionId))
    except urllib.error.URLError as e:
        print( str(e))
        exit(-1)

    # Initialize
    try:
        config = ""
        with open(args.config, 'r') as f:
            config = f.read()

        response = jsonCall(url + "/initialize/" + str(sessionId), config)
        status = json.load(response)
        if verbose:
            print( status)

        print( "\tInitialized session status: " + status[0]['status'])
    except urllib.error.URLError as e:
        print( str(e))
        print( e.read())
        exit(-1)

    # Subscribe
    #listen(url,sessionId)
    #print("foo")
    #asyncio.get_event_loop().run_until_complete(listen(url,sessionId))   
    #asyncio.run_coroutine_threadsafe(listen(url,sessionId), asyncio.get_event_loop())
    #asyncio.get_event_loop().run_in_executor(ProcessPoolExecutor(1), listen(url, sessionId), 5)
    
    input("Press Enter to continue...")
    
    # Simulate
    try:
        config = {'startTime': startTime, 'endTime': endTime}

        response = jsonCall(url + "/simulate/" + str(sessionId),
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
        response = urllib.request.urlopen(url + "/result/" + str(sessionId))
        CHUNK = 16 * 1024

        resultPath = args.result

        if args.repeat is not None:
            resultPath = resultPath[:resultPath.rfind('.')] + "-%06d.csv" % (simIndex,)

        with open(resultPath, 'wb') as f:
            while True:
                chunk = response.read(CHUNK)
                if not chunk:
                    break
                f.write(chunk)
        print( "\tRead result " + str(file_len(args.result)) + " lines")
    except urllib.error.URLError as e:
        print( str(e))
        print( e.read())
        exit(-1)

    # Destroy
    try:
        response =  urllib.request.urlopen(url + "/destroy/" + str(sessionId))
    except urllib.error.URLError as e:
        print( str(e))
        print( e.read())
        exit(-1)

    print( "\tsimulation done")

m, s = divmod(time.time() - exec_start_time, 60)
h, m = divmod(m, 60)

print( "\nTotal execution time: %02d:%02d:%02d" % (h, m, s))
