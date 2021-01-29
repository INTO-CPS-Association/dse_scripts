import argparse

from libs.Common import *

# Setup argument parser so that the script is more user friendly
from libs.Common_Output import trimmedParamName, naturalKeys

resutsPath = ""

def runScript():
    global resultsPath

    args = scriptArguments().parse_args()
    resultsPath = args.resultsPath

    htmlFileName = os.path.join(resultsPath, HTML_RESULTS)
    htmlFile = open(htmlFileName, 'w')

    # HTML header
    htmlFile.write("<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">")
    htmlFile.write("<html xmlns=\"http://www.w3.org/1999/xhtml\">")
    htmlFile.write("<head>\n")
    htmlFile.write("<title>DSE Results Page</title>\n")
    htmlFile.write("<style>")
    execdir = os.path.dirname(os.path.realpath(__file__))
    htmlFile.write(includeStyleSheet(os.path.join(execdir, "results.css")))
    htmlFile.write("\n</style>")
    htmlFile.write("</head>\n")
    htmlFile.write("<body>\n")

    # open ranking json
    with open(os.path.join(resultsPath, RANKING_FILE)) as f:
        rankingJson = json.load(f)

    rankId = 'pareto'

    htmlFile.write(f"<h1>{rankId}</h1>\n")

    # add the graph to html
    addGraphsForRanking(rankId, htmlFile)

    # add table with data
    putRankingIntoTable(rankId, rankingJson, htmlFile)

    # close files
    htmlFile.write("</body>")
    htmlFile.write("</html>")
    htmlFile.close()

# HTML generation helpers
def addGraphsForRanking(rankId, htmlFile):
    htmlFile.write(f"<img src=graphs/{rankId}.png>\n")
    return htmlFile


def putRankingIntoTable(rankId, rankingJson, htmlFile):
    htmlFile.write("<table>\n")
    addHeadings(htmlFile, rankingJson)
    addRows(rankId, htmlFile, rankingJson)
    htmlFile.write("</table>\n")


def addHeadings(htmlFile, rankingJson):
    htmlFile.write("<tr>")
    htmlFile.write("<th>Rank</th>")
    firstSim = rankingJson['simulations'][0]
    getObjectiveHeadings(firstSim, htmlFile)
    getParameterHeadings(firstSim, htmlFile)
    htmlFile.write("</tr>\n")


def getObjectiveHeadings(design, htmlFile):
    with open(os.path.join(resultsPath, design, OBJECTIVES_FILE)) as f:
        objectivesJson = json.load(f)
    for objective in objectivesJson:
        htmlFile.write(f"<th>{objective}</th>")


def getParameterHeadings(design, htmlFile):
    with open(os.path.join(resultsPath, design, DEFAULT_SIM_CONFIG)) as f:
        configJson = json.load(f)
    paramsJson = configJson['parameters']
    for param in paramsJson:
        htmlFile.write(f"<th>{trimmedParamName(param)}</th>")


def addRows(rankId, htmlFile, rankingJson):
    thisRankingRoot = rankingJson[rankId]
    sortedRanks = sorted(thisRankingRoot)
    sortedRanks.sort(key=naturalKeys)

    for rank in sortedRanks:
        for design in thisRankingRoot[rank]:
            addRow(rank, design, htmlFile)


def addRow(rank, design, htmlFile):
    htmlFile.write("<tr>")
    htmlFile.write(f"<td>{rank}</td>")
    addObjectiveValues(design, htmlFile)
    addDesignParameters(design, htmlFile)
    htmlFile.write("</tr>\n")


def addObjectiveValues(design, htmlFile):
    with open(os.path.join(resultsPath, design, OBJECTIVES_FILE)) as f:
        objectivesJson = json.load(f)

    for objective in objectivesJson:
        htmlFile.write(f"<td>{objectivesJson[objective]}</td>")


def addDesignParameters(design, htmlFile):
    with open(os.path.join(resultsPath, design, DEFAULT_SIM_CONFIG)) as f:
        configJson = json.load(f)

    paramsJson = configJson['parameters']

    for param in paramsJson:
        htmlFile.write(f"<td>{paramsJson[param]}</td>")


def includeStyleSheet(fileName):
    if os.path.exists(fileName):
        with open(fileName) as f:
            cssFile = f.read()
        return cssFile
    return ""


def scriptArguments() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DSE HTML output", prog="Output HTML")

    # required params
    parser.add_argument("resultsPath", type=str, help="Full path to the results")

    return parser

runScript()
