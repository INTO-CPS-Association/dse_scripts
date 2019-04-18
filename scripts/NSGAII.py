from jmetal.algorithm.multiobjective.nsgaii import NSGAII
from  jmetal.util.comparator import RankingAndCrowdingDistanceComparator
from jmetal.operator import SBXCrossover, PolynomialMutation, BinaryTournamentSelection
from jmetal.problem import ZDT1, DTLZ1
from jmetal.util.visualization import InteractivePlot
from jmetal.util.solution_list import print_function_values_to_file, print_variables_to_file, read_solutions
from jmetal.util.termination_criterion import StoppingByEvaluations
from jmetal.util.observer import BasicObserver

problem = ZDT1()  # DTLZ1()
problem.reference_front = read_solutions(filename='{}.pf'.format(problem.get_name()))

algorithm = NSGAII(
    problem=problem,
    population_size=100,
    offspring_population_size=100,
    #mating_pool_size=100,
    termination_criterion=StoppingByEvaluations(2000),
    mutation=PolynomialMutation(probability=1.0 / problem.number_of_variables, distribution_index=20),
    crossover=SBXCrossover(probability=1.0, distribution_index=20),
    selection=BinaryTournamentSelection(comparator=RankingAndCrowdingDistanceComparator())
)

basic = BasicObserver(frequency=1.0)
algorithm.observable.register(observer=basic)

algorithm.run()
front = algorithm.get_result()

pareto_front = InteractivePlot(plot_title='ZDT-NSGAII',  reference_front=problem.reference_front, axis_labels=problem.obj_labels, )
pareto_front.plot(front)
pareto_front.export_to_html(filename='ZDT-NSGAII.html')

print_function_values_to_file(front, 'ZDT-NSGAII.fun')
print_variables_to_file(front, 'ZDT-NSGAII.var')