import runmops
from analyzemops.parameters import Parameters
from analyzemops.tracker import Tracker
from analyzemops.analysis import runAnalysis

parameters = Parameters.fromYaml("/project/moeyensj/jpl/fullDensity_3months/full/parameters.yaml")
tracker = Tracker.fromYaml("/project/moeyensj/jpl/fullDensity_3months/full/tracker.yaml")
parameters, tracker = runmops.runMops(parameters, tracker, enableMultiprocessing=False)

parameters = Parameters.fromYaml("/project/moeyensj/jpl/fullDensity_3months/full/run_01/parameters.yaml")
tracker = Tracker.fromYaml("/project/moeyensj/jpl/fullDensity_3months/full/run_01/tracker.yaml")
runAnalysis(tracker, parameters)