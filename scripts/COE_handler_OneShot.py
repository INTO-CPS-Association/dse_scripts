import argparse
import urllib.request, urllib.error, urllib.parse

from libs.Common import *

debugOutput = False

def runSimulation():
    global debugOutput

    args = scriptArguments().parse_args()
    debugOutput = args.d

    startTime = args.startTime
    endTime = args.endTime
    simulationPath = args.simulationPath

    if aResultsFileAlreadyExists(simulationPath):
        print("\t\tResults File Already Exists Skipping Simulation")
    else:
        runSimulationAndGetResults(startTime, endTime, simulationPath)


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

def runSimulationAndGetResults(startTime, endTime, simulationPath):
    configPath = os.path.join(simulationPath, DEFAULT_SIM_CONFIG)
    resultsPath = os.path.join(simulationPath, RESULTS_FILE)

    with open(resultsPath, "w+"):
        pass

    coe = ["java", "-jar", r"C:\Users\max\Documents\into-cps-projects\install_downloads\coe.jar", "--oneshot", "-configuration", f"{configPath}", "-starttime", f"{startTime}", "-endtime", f"{endTime}", "-r", f"{resultsPath}"]

    subprocess.call(coe)

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
