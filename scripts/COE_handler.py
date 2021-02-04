import argparse
import requests
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

def GetSessionID(url: str) -> str:
    if debugOutput:
        print("\t\tGetting session ID")

    createSessionResponse = requests.get(f"{url}/createSession")

    if createSessionResponse.status_code != 200:
        raise Exception(f"Failed to create session: {createSessionResponse.text}")

    sessionId = json.loads(createSessionResponse.text)['sessionId']

    if debugOutput:
        print(f"\t\tCreate session response: {createSessionResponse.text}")
        print(f"\t\tSession ID: {sessionId}")

    return sessionId

def InitSession(url: str, sessionId: str, simulationPath: str):
    if debugOutput:
        print("\t\tInitializing session")

    with open(os.path.join(simulationPath, DEFAULT_SIM_CONFIG), 'r') as f:
        configData = json.load(f)

    initResponse = requests.post(f"{url}/initialize/{sessionId}", json=configData)

    if initResponse.status_code != 200:
        raise Exception(f"Failed to initialize session: {initResponse.text}")

    if debugOutput:
        print(f"\t\tInit response: {initResponse.text}")

def Simulate(url: str, sessionId: str, startTime: float, endTime: float):
    if debugOutput:
        print("Starting simulation")

    simulationResponse = requests.post(f"{url}/simulate/{sessionId}", json=json.loads(f"{{\"startTime\": {startTime}, \"endTime\": {endTime}}}"))

    if simulationResponse.status_code != 200:
        raise Exception(f"Failed to simulate: {simulationResponse.text}")

    if debugOutput:
        print(f"\t\tSimulation response: {simulationResponse.text}")

def GetSimulationResults(url: str, sessionId: str, simulationPath: str):
    if debugOutput:
        print("Getting simulation results")

    zip = requests.get(f"{url}/result/{sessionId}/zip", stream=True)
    with open(os.path.join(simulationPath, "zipResults.zip"), "wb+") as f:
        for chunk in zip.iter_content(chunk_size=128):
            f.write(chunk)

    # using urllib here and not requests because requests adds extra new lines in windows for some reason
    plainResults = urllib.request.urlopen(f"{url}/result/{sessionId}/plain")
    with open(os.path.join(simulationPath, RESULTS_FILE), "w+") as f:
        f.write(plainResults.read())

def DestroySession(url: str, sessionId: str):
    if debugOutput:
        print("\t\tDestroying session")

    time.sleep(0.2)

    times = 0
    while requests.get(f"{url}/destroy/{sessionId}").status_code != 200:
        times += 1

        if times < 5:
            print(f"Failed to destroy session {times} times trying again")
            time.sleep(0.2)
        else:
            raise Exception(f"Failed to destroy session tried {times} times")

    if debugOutput:
        print("\t\tSession destroyed")

def runSimulationAndGetResults(url, startTime, endTime, simulationPath):
    sessionId = GetSessionID(url)

    try:
        time.sleep(0.2)
        InitSession(url, sessionId, simulationPath)

        time.sleep(0.2)
        Simulate(url, sessionId, startTime, endTime)

        time.sleep(0.2)
        GetSimulationResults(url, sessionId, simulationPath)

    finally:
        # always remove the session if we have created one
        DestroySession(url, sessionId)

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
