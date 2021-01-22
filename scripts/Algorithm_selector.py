# Created by Max Rose
import argparse, os, subprocess
import json

from libs.Common import validConfigPath, validThreadCount, validProjectPath, validPortNumber, strToBool

try:
    os.chdir(os.path.dirname(os.path.realpath(__file__))) # cd to this scripts location to execute to make things more consistent
except (WindowsError, OSError) as e:
    print("Error changing directory exiting")
    exit(1)

algorithms = ["exhaustive", "genetic"]

# Setup argument parser so that the script is more user friendly
parser = argparse.ArgumentParser(description="Select a DSE algorithm and run it", prog="Algorithm Selector")

# required params
parser.add_argument("projectpath", type=str, help="Full top level path to the project")
parser.add_argument("dsepath", type=str, help="Path to DSE file (.dse.json) relative to projectpath")
parser.add_argument("coepath", type=str, help="Path to COE settings file (coe.json) relative to projectpath")

# optional params
parser.add_argument("-t", type=validThreadCount, default=1, help="Max thread count (default: 1)")
parser.add_argument("-noCSV", action="store_true", help="Dont generate CSV output")
parser.add_argument("-noHTML", action="store_true", help="Dont generate HTML output")
parser.add_argument("-u", type=str, default="http://localhost", help="URL to COE (default: http://localhost)")
parser.add_argument("-p", type=validPortNumber, default=8082, help="Port for COE (default: 8082)")
parser.add_argument("-d", action="store_true", help="Show debug output")

args = parser.parse_args()

# See what we have been given
debugOutput = args.d
threads = args.t
basePath = args.projectpath
dsePath = args.dsepath
coepath = args.coepath

# Check that the required stuff is there
validProjectPath(basePath)
validConfigPath(os.path.join(basePath, dsePath))
validConfigPath(os.path.join(basePath, coepath))

dseConfig = json.load(open(os.path.join(basePath, dsePath)))

optionalArguments = []
selectedAlgorithm = ""

try:
    if dseConfig['algorithm']['type'] == algorithms[0]:
        selectedAlgorithm = "Algorithm_exhaustive.py"

    elif dseConfig['algorithm']['type'] == algorithms[1]:
        selectedAlgorithm = "Algorithm_genetic.py"
except Exception as e:
    selectedAlgorithm = "Algorithm_exhaustive.py"


if args.noCSV:
    optionalArguments.append("-noCSV")

if args.noHTML:
    optionalArguments.append("-noHTML")

optionalArguments.extend(f"-t {threads},-u {args.u},-p {args.p}".split(','))

if debugOutput:
    print(f"Starting with:\nBase path: {basePath}\nDSE Path: {dsePath}\nCOE Path: {coepath}\nAlgorithm: {selectedAlgorithm}\nThreads: {threads}\n\n")

if args.d:
    optionalArguments.append("-d")

subprocess.call(["python", os.path.join(selectedAlgorithm), basePath, dsePath, coepath, *optionalArguments])
