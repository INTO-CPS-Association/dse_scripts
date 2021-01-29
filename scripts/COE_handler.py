import argparse
import urllib.request, urllib.error, urllib.parse

from libs.Common import *

debugOutput = False

def runSimulation():
    global debugOutput

    args = scriptArguments().parse_args()
    debugOutput = args.d

    url = args.u + ":" + str(args.p).strip()
    startTime = args.startTime
    endTime = args.endTime
    simulationPath = args.simulationPath

    if aResultsFileAlreadyExists(simulationPath):
        print("\t\tResults File Already Exists Skipping Simulation")
    else:
        runSimulationAndGetResults(url, startTime, endTime, simulationPath)


def aResultsFileAlreadyExists(simPath):
    """
    Checks if a result has already been generated for a given simulation
    :param simPath: Path to the simulation folder where results would be output
    :return: True if results exist
    """
    resultsFilePath = os.path.join(simPath, RESULTS_FILE)

    return os.path.exists(resultsFilePath)

def jsonCall(url, data):
    req = urllib.request.Request(url)
    req.add_header("Content-Type", "application/json")
    jsonDataBytes = data.encode("utf-8")
    return urllib.request.urlopen(req, data=jsonDataBytes)

def readAndDecodeResponse(rawResponse):
    return json.loads(rawResponse.read().decode())

def runSimulationAndGetResults(url, startTime, endTime, simulationPath):
    # create simulation session
    if debugOutput:
        print("\t\tGetting session ID")

    sessionURL = url + "/createSession"

    rawSessionResponse = urllib.request.urlopen(sessionURL)

    decodedResponse = readAndDecodeResponse(rawSessionResponse)
    sessionId = decodedResponse['sessionId']

    if debugOutput:
        print(f"\t\t\tRaw response: {rawSessionResponse}")
        print(f"\t\t\tDecoded response: {decodedResponse}")
        print(f"\t\t\tSession ID: {sessionId}")

    # init the simulation
    if debugOutput:
        print("\t\tInitialising simulation")

    configPath = os.path.join(simulationPath, DEFAULT_SIM_CONFIG)
    with open(configPath, 'r') as f:
        configData = f.read()

    initResponse = jsonCall(url + "/initialize/" + str(sessionId), configData)

    if debugOutput:
        print(f"\t\t\tRaw init response: {initResponse}")
        print(f"\t\t\tDecoded init response: {json.loads(initResponse.read().decode())}")

    # run the simulation
    if debugOutput:
        print("\t\tStarting simulation")

    time.sleep(0.2)
    runSimResponse = jsonCall(url + "/simulate/" + str(sessionId), f"{{\"startTime\": {startTime}, \"endTime\": {endTime}}}")

    if debugOutput:
        print(f"\t\t\tRun simulation response: {runSimResponse}")

    # get simulation results
    if debugOutput:
        print("\t\tGetting simulation results")

    resultsURL = url + "/result/" + str(sessionId) + "/plain"

    time.sleep(0.2)
    getResultsResponse = urllib.request.urlopen(resultsURL)

    if debugOutput:
        print(f"\t\t\tResults response: {getResultsResponse}")
        print("\t\t\tWriting results to file")

    CHUNK = 16 * 1024
    resultsPath = os.path.join(simulationPath, RESULTS_FILE)
    with open(resultsPath, 'wb') as f:
        while True:
            chunk = getResultsResponse.read(CHUNK)
            if not chunk:
                break
            f.write(chunk)

    # removed the session
    if debugOutput:
        print("\t\tDestroying session")

    time.sleep(0.2)

    destroyURL = url + "/destroy/" + str(sessionId)

    try:
        urllib.request.urlopen(destroyURL)
    except urllib.error.HTTPError:
        while True:
            try:
                time.sleep(0.5)
                urllib.request.urlopen(destroyURL)
                return
            except urllib.error.HTTPError as e:
                print(f"Error destroying session: {e}")

    time.sleep(0.2)

def scriptArguments() -> argparse.ArgumentParser:
    # Setup argument parser so that the script is more user friendly
    parser = argparse.ArgumentParser(description="Select a DSE algorithm and run it", prog="COE Handler")

    # required params
    parser.add_argument("simulationPath", type=validProjectPath, help="Path to COE simulation folder")
    parser.add_argument("startTime", type=float, help="Simulation start time")
    parser.add_argument("endTime", type=float, help="Simulation end time")

    # optional params
    parser.add_argument("-d", action="store_true", help="Show debug output (default: False)")
    parser.add_argument("-u", type=str, default="http://localhost", help="URL to COE (default: http://localhost)")
    parser.add_argument("-p", type=validPortNumber, default=8082, help="Port for COE (default: 8082)")

    return parser


if __name__ == "__main__":
    runSimulation()
