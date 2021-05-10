import argparse
import requests

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

def readAndDecodeResponse(rawResponse):
    return json.loads(rawResponse.read().decode())

def runSimulationAndGetResults(url, startTime, endTime, simulationPath):
    # create simulation session
    if debugOutput:
        print("\t\tGetting session ID")

    rawSessionResponse = requests.get(f"{url}/createSession")

    if not rawSessionResponse.status_code == 200:
        raise Exception("Failed to create session")

    sessionId = json.loads(rawSessionResponse.text)['sessionId']

    if debugOutput:
        print(f"\t\t\tRaw response: {rawSessionResponse.text}")
        print(f"\t\t\tSession ID: {sessionId}")

    try:
        # init the simulation
        if debugOutput:
            print("\t\tInitialising simulation")

        configPath = os.path.join(simulationPath, DEFAULT_SIM_CONFIG)
        with open(configPath, 'r') as f:
            # Remove the whitespace from the file so we arnt sending as much data
            configData = f.read().replace("\n", "").replace(" ", "")

        initResponse = requests.post(f"{url}/initialize/{sessionId}", json=json.loads(configData))

        if not initResponse.status_code == 200:
            raise Exception("Could not initialise session")

        if debugOutput:
            print(f"\t\t\tRaw init response: {initResponse}")
            print(f"\t\t\tDecoded init response: {initResponse.text}")

        # run the simulation
        if debugOutput:
            print("\t\tStarting simulation")

        time.sleep(0.2)
        requests.post(f"{url}/executeViaCLI/{sessionId}", json={"executeViaCLI": True})
        runSimResponse = requests.post(f"{url}/simulate/{sessionId}", json=json.loads(f"{{\"startTime\": {startTime}, \"endTime\": {endTime}}}"))

        if not runSimResponse.status_code == 200:
            raise Exception(f"Failed to simulate: {runSimResponse.text}")

        if debugOutput:
            print(f"\t\t\tRun simulation response: {runSimResponse}")

        # get simulation results
        if debugOutput:
            print("\t\tGetting simulation results")

        r = requests.get(f"{url}/result/{sessionId}/zip", stream=True)

        with open(os.path.join(simulationPath, "results zip.zip"), "wb+") as f:
            for chunk in r.iter_content(chunk_size=128):
                f.write(chunk)

        getResultsResponse = requests.get(f"{url}/result/{sessionId}/plain")

        if not getResultsResponse.status_code == 200:
            raise Exception("Failed to get results")

        if debugOutput:
            print(f"\t\t\tResults response: {getResultsResponse}")
            print("\t\t\tWriting results to file")

        # CHUNK = 16 * 1024
        resultsPath = os.path.join(simulationPath, RESULTS_FILE)
        with open(resultsPath, 'w+') as f:
            chunk = getResultsResponse.text.replace("\r\n", "\n")
            f.write(chunk)

    finally:
        # removed the session
        if debugOutput:
            print("\t\tDestroying session")

        time.sleep(0.2)

        while not requests.get(f"{url}/destroy/{sessionId}").status_code == 200:
            print("Failed to destroy session will retry")
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
