from jmetal.algorithm.multiobjective.nsgaii import NSGAII
from jmetal.util.comparator import RankingAndCrowdingDistanceComparator
from jmetal.operator import SBXCrossover, PolynomialMutation, BinaryTournamentSelection
from jmetal.problem import ZDT1, DTLZ1
from jmetal.util.visualization import InteractivePlot
from jmetal.util.solution_list import print_function_values_to_file, print_variables_to_file, read_solutions
from jmetal.util.termination_criterion import StoppingByEvaluations
from jmetal.util.observer import BasicObserver
from jmetal.core.problem import FloatProblem
from jmetal.core.solution import FloatSolution

# my stuff
import json,sys,pandas,subprocess
from math import sqrt, pow, sin, pi, cos
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

def cosimulate(config):
  # Create session
  try:
      response = urllib.request.urlopen(URL + "/createSession")
      status = json.load(response)
      #if verbose:
      #    print(status)
      sessionId = status['sessionId']
      #print( "\tCreated session: " + str(sessionId))
  except urllib.error.URLError as e:
      print(str(e))
      exit(-1)
      
  # Initialize
  try:
      #config = ""
      #with open(CONFIG, 'r') as f:
      #    config = f.read()
      
      response = jsonCall(URL + "/initialize/" + str(sessionId), json.dumps(config))
      status = json.load(response)
      
      #if verbose:
      #    print( status)
      
      #print( "\tInitialized session status: " + status[0]['status'])
  except urllib.error.URLError as e:
      print( str(e))
      print( e.read())
      exit(-1)
      
  # Simulate
  try:
      simconfig = {'startTime': START_TIME, 'endTime': END_TIME}
      #
      #    #"reportProgress":true,"liveLogInterval":0,"logLevels":{"{G}.GInstance":["logAll","logError","logFmiCall","Protocol","VdmErr","VdmOut"],"{H}.HInstance":["logAll","logError","logFmiCall","Protocol","VdmErr","VdmOut"]}
      #
      #config = {'startTime': START_TIME, 'endTime': END_TIME, "logLevels":{"{G}.GInstance":["logAll","logError","logFmiCall","Protocol","VdmErr","VdmOut"],"{H}.HInstance":["logAll","logError","logFmiCall","Protocol","VdmErr","VdmOut"]}}
      
      response = jsonCall(URL + "/simulate/" + str(sessionId),
                          json.dumps(simconfig))
      status = json.load(response)

      #if verbose:
      #    print( status)
      #
      #print( "\tSimulation " + str(status['status'] + " in " + str(
      #    status['lastExecTime']) + " seconds"))
  except urllib.error.URLError as e:
      print( str(e))
      print( e.read())
      exit(-1)

  # Get result
  try:
      response = urllib.request.urlopen(URL + "/result/" + str(sessionId))
      result = response.read()
      s = str(result, 'utf-8')
      data = StringIO(s) 
      return pandas.read_csv(data)
      #print (df)      
      #CHUNK = 16 * 1024
      #
      #with open(RESULT, 'wb') as f:
      #    while True:
      #        chunk = response.read(CHUNK)
      #        if not chunk:
      #            break
      #        f.write(chunk)
      #print( "\tRead result " + str(file_len(RESULT)) + " lines")
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

  #print( "\tsimulation done") 

class ZDT1Cosim(FloatProblem):
    """ Problem ZDT1 implemented as a co-simulation.

    .. note:: Bi-objective unconstrained problem. The default number of variables is 30.
    .. note:: Continuous problem having a convex Pareto front
    """

    def __init__(self, number_of_variables: int=30):
        """ :param number_of_variables: Number of decision variables of the problem.
        """
        super(ZDT1Cosim, self).__init__()
        self.number_of_variables = number_of_variables
        self.number_of_objectives = 2
        self.number_of_constraints = 0

        self.obj_directions = [self.MINIMIZE, self.MINIMIZE]
        self.obj_labels = ['x', 'y']

        self.lower_bound = self.number_of_variables * [0.0]
        self.upper_bound = self.number_of_variables * [1.0]

        self.config = {}
        with open(CONFIG) as f:
            self.config = json.load(f)
        
    def evaluate(self, solution: FloatSolution) -> FloatSolution:
        # get the value of g and h from the result.csv

        
        self.config["parameters"]["{G}.GInstance.solution_variables"] = str(solution.variables)
        #print(str(solution.variables))
        
        #with open("config.json", "w") as f:
        #    config = json.dump(config, f)
        
        results = cosimulate(self.config)
        
        #results = pandas.read_csv("result.csv")
        
        g_cosim = list(results["{G}.GInstance.g"])[-1]
        h_cosim = list(results["{H}.HInstance.h"])[-1]

        g = g_cosim #self.eval_g(solution)
        h = g_cosim #self.eval_h(solution.variables[0], g)
        
        #print("g_cosim = %s, g = %s" % (g_cosim,g))
        #print("h_cosim = %s, h = %s" % (h_cosim,h))
        #
        #sys.exit(0)
        
        solution.objectives[0] = solution.variables[0]
        solution.objectives[1] = h * g

        return solution

    def eval_g(self, solution: FloatSolution):
        g = sum(solution.variables) - solution.variables[0]

        constant = 9.0 / (solution.number_of_variables - 1)

        print("solution.variables = %s" % (solution.variables))
        print("solution.variables[0] = %s" % (solution.variables[0]))
        print("solution.number_of_variables = %s" % (solution.number_of_variables))
        print("constant = %s" % (constant))
        print("g = %s" % (constant * g + 1.0))
        
        return constant * g + 1.0

    def eval_h(self, f: float, g: float) -> float:
        print("f = %s" % (f))
        print("g = %s" % (g))
        print("sqrt(f/g) = %s" % sqrt(f/g))
        print("h = %s" % (1.0 - sqrt(f/g)))
        
        return 1.0 - sqrt(f / g)

    def get_name(self):
        return 'ZDT1Cosim'

problem = ZDT1Cosim() # ZDT1()  # DTLZ1()
problem.reference_front = read_solutions(filename='{}.pf'.format(problem.get_name()))

algorithm = NSGAII(
    problem=problem,
    population_size=100,
    offspring_population_size=100,
    #mating_pool_size=100,
    termination_criterion=StoppingByEvaluations(2000),#25000
    mutation=PolynomialMutation(probability=1.0 / problem.number_of_variables, distribution_index=20),
    crossover=SBXCrossover(probability=1.0, distribution_index=20),
    selection=BinaryTournamentSelection(comparator=RankingAndCrowdingDistanceComparator())
)

basic = BasicObserver(frequency=1.0)
algorithm.observable.register(observer=basic)

algorithm.run()
front = algorithm.get_result()

pareto_front = InteractivePlot(plot_title='ZDTCosim-NSGAII_online',  reference_front=problem.reference_front, axis_labels=problem.obj_labels)
pareto_front.plot(front)
pareto_front.export_to_html(filename='ZDTCosim-NSGAII_online.html')

print_function_values_to_file(front, 'Cosim-NSGAII_online.fun')
print_variables_to_file(front, 'ZDTCosim-NSGAII_online.var')