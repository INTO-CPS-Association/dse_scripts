# INTO CPS DSE Scripts

Updated old Python 2 scripts to Python 3 and added a modular GA system among other minor improvements

## Highlights
- Updated to Python 3
- Powerful command line arguements
- Added multi threading to allow for multiple parallel simulations
- Added modular GA system
- FMU parameter names {fmu}.dummy.ab will no longer be incorrectly matched with {fmu}.dummy.a for constraints

## Dependancies
- Python 3
- Numpy
- Matplotlib

## Known Issues
  - Numpy 1.19.4, Python 3.9, and Windows do not play nice and insted requires Numpy 1.19.3

## Command Line Arguments

(Arguments apply to Algroithm Selector, Exhaustive, and Genetic)

- help
- `t` Number of threads to use, default 1
- `noCSV` do not generate CSV result file, default false
- `noHTML` do not generate HTML result file, default false
- `u` URL to COE, default http://localhost
- `p` Port for COE, default 8082

## DSE Config for GA's

An example config for the use of GA's with the COE engine is shown below with explanations of each parameter 

```json
{
  "algorithm": {
    "type": "genetic"
  },
  "parameterConstraints": [
    Constraints on organism parameters
  ],
  "parameters": {
    "parameter name": [min value, max value], Parameters to run the DSE on with a min and max ragne to create the initial population from 
  },
  "geneticArguments": 
  {
    "popSize": 1, The size of the population in each iteration
    "scenario": "nGens", The world to use can be any of nGens, Convergence, or Fitness
    "scenarioArgs": [], Any extra arguemnts that may be required for the GA world specified in scenario
                        nGens - specifying config arguement is optional
                        convergence -  specify as [deviation, convergence generations]
                        fitness - specify as [fitness threashold, percentage]
    "maxGenerations": 10, The maximum number of generations a given would can run for.
                          In the case nGens was specitif this is the number of generations the world will run for
    "rankingFunctionArgs": [], Specify as [Rank high to low (true/false), Result Key to look for in Objectives.json to use as ranking]
    "useRawRanking": false, (Optional default: false) Should the raw ranking be used
    "selectionFunction": "Ranked", (Optional default: Ranked) Selection function to be used choose from Ranked, RandomSelection, RouletteWheel, or TounamentMax/Min
    "selectionFunctionArgs": [], (Optional default: []) Extra arguements to pass to the selection function
                                Ranked - specify as [nPairs] note: requires useRawRaking = false
                                RandomSelection - specify as [nPairs]
                                RouletteWheel - specify as [nPairs, minimise fitness]
                                TournamentMax/TournamentMin - specify as [nPairs, tounament size]
    "crossingFunction": "SBX", (Optional default: SBX) Crossing function to use choose from SBX, BLX, UniformCrossing, or NPointCrossing
    "crossingFunctionArgs": [], (Optional) Extra arguements to pass to the crossing function
                                SBX - [eta] Note: Constraints arguement is automatically added
                                BLX - [sigma] Note: Constraints arguement is automatically added
                                UniformCrossing - [Crossing Points] 
                                NPointCrossing - None
    "mutationFunction": "MutateRelNormal", (Optional default: Rel) Mutation function to use choose from MutateRelNormal, MutateAbsNormal
    "mutationFuncitonArgs": [], (Optional) [sigma] Note: Constraints are automatically added
    "mutationChance": 0.3, (Optional default: 0.2) Probability of mutation
    "scaleMutation": true, (Optional default: true) Reduce mutation probability as GA runs
    "elitismKeep": 0.3, (Optional default: 0.1) Keep % of best organisms from previous generation
    "diveristyFunction": "EulerDistance", (Optinal default: euler) Diversity control function choose from EulerDistance, or None
    "diversityFunctionArgs": [], (Optional) Diversity control function arguments
                                EulerDistance - specify as [high, low]
  }
}
```