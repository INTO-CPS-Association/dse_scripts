# change to dse directory for calling other scripts
import os,sys, time
try:
  os.chdir(os.path.dirname(os.path.realpath(__file__)))
except WindowsError, OSError:
  print 'Error changing to scripts directory'
  sys.exit(1)
  
import json, platform, subprocess, time, io, math
from subprocess import CalledProcessError 
from libs.Common import *


ALGORITHM_ID_EXHAUSTIVE = 'exhaustive'
ALGORITHM_ID_GENETIC = 'genetic'



print ("Processing command arguments")
absoluteProjectPath  = sys.argv[1]
relativeExperimentConfigPath = sys.argv[2]
relativeCoeConfigFile = sys.argv[3]




#absoluteCoeConfigFile = absoluteProjectPath + os.path.sep + relativeCoeConfigFile


#trimLocation = absoluteExperimentConfigPath.rfind(os.path.sep)
#absoluteExperimentPath = absoluteExperimentConfigPath[:trimLocation] + os.path.sep


absoluteExperimentConfigPath = os.path.join(absoluteProjectPath, relativeExperimentConfigPath)
print ("Selecting algorithm script: ")
dseConfig_data = open(absoluteExperimentConfigPath)
dseConfig = json.load(dseConfig_data)

execdir = os.path.dirname(os.path.realpath(__file__))
try:
  if  dseConfig['algorithm']['type']   ==  ALGORITHM_ID_GENETIC:
      #launch genetic algorithm
      subprocess.call(["python", os.path.join("Algorithm_genetic.py"), absoluteProjectPath, relativeExperimentConfigPath, relativeCoeConfigFile])

  elif dseConfig['algorithm']['type']  ==  ALGORITHM_ID_EXHAUSTIVE :
      #launc exhaustive algorithm
      subprocess.call(["python", os.path.join("Algorithm_exhaustive.py"), absoluteProjectPath, relativeExperimentConfigPath, relativeCoeConfigFile])
except Exception:
      # for bacwards compatibility with older configs just launch exhaustive is type not specified
      subprocess.call(["python", os.path.join("Algorithm_exhaustive.py"), absoluteProjectPath, relativeExperimentConfigPath, relativeCoeConfigFile])


