import argparse
import urllib.request, urllib.error, urllib.parse

from libs.Common import *

debugOutput = False

def RunCOE():
    global debugOutput

    args = scriptArguments().parse_args()
    debugOutput = args.d

    url = args.u + ":" + str(args.p).strip()
    startTime = args.startTime
    endTime = args.endTime
    simulationPath = args.simulationPath

    if ResultsFileAlreadyExists(simulationPath):
        print("\t\tResults File Already Exists Skipping Simulation")
    else:
        RunSimulationAndGetResults(url, startTime, endTime, simulationPath)


def ResultsFileAlreadyExists(simPath):
    """
    Checks if a result has already been generated for a given simulation
    :param simPath: Path to the simulation folder where results would be output
    :return: True if results exist
    """
    resultsFilePath = os.path.join(simPath, RESULTS_FILE)

    return os.path.exists(resultsFilePath)

def Get(url: str):
    with urllib.request.urlopen(url) as response:
        return response.read()

def Post(url: str, data):
    request = urllib.request.Request(url)

    request.add_header("Content-Type", "application/json")
    encodedRequestData = data.encode("utf-8")

    with urllib.request.urlopen(request, data=encodedRequestData) as response:
        return response.read()

def GetSessionId(url):
    # create simulation session
    if debugOutput:
        print("\t\tGetting session ID")

    sessionId = json.loads(Get(f"{url}/createSession").decode())['sessionId']

    if debugOutput:
        print(f"\t\t\tSession ID: {sessionId}")

    return sessionId

def PostConfigData(url, sessionId, simPath):
    configPath = os.path.join(simPath, DEFAULT_SIM_CONFIG)
    with open(configPath, 'r') as f:
        configData = f.read()
    initResponse = Post(f"{url}/initialize/{sessionId}", configData)

    if debugOutput:
        print(f"\t\t\tRaw init response: {initResponse}")

def RunSimulation(url, sessionId, startTime, endTime):
    # run the simulation
    if debugOutput:
        print("\t\tStarting simulation")

    time.sleep(0.2)
    runSimResponse = Post(f"{url}/simulate/{sessionId}", f"{{\"startTime\": {startTime}, \"endTime\": {endTime}}}")

    if debugOutput:
        print(f"\t\t\tRun simulation response: {runSimResponse}")

def GetResults(url, sessionId, simPath):
    # get simulation results
    if debugOutput:
        print("\t\tGetting simulation results")

    time.sleep(0.2)
    resultsURL = f"{url}/result/{sessionId}/plain"
    getResultsResponse = Get(resultsURL).decode()

    if debugOutput:
        print(f"\t\t\tResults response: {getResultsResponse}")
        print("\t\t\tWriting results to file")

    with open(os.path.join(simPath, RESULTS_FILE), "w+") as f:
        f.write(getResultsResponse)

def DestroySession(url, sessionId):
    # removed the session
    if debugOutput:
        print("\t\tDestroying session")

    time.sleep(0.2)

    destroyURL = f"{url}/destroy/{sessionId}"

    try:
        urllib.request.urlopen(destroyURL)
    except urllib.error.HTTPError as e:
        while True:
            try:
                time.sleep(0.5)
                urllib.request.urlopen(destroyURL)
                return
            except urllib.error.HTTPError as e:
                pass

    time.sleep(0.2)

def RunSimulationAndGetResults(url, startTime, endTime, simulationPath):
    sessionId = GetSessionId(url)

    PostConfigData(url, sessionId, simulationPath)
    RunSimulation(url, sessionId, startTime, endTime)
    GetResults(url, sessionId, simulationPath)
    DestroySession(url, sessionId)

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
    RunCOE()
