from analyzemops.parameters import Parameters
from analyzemops.tracker import Tracker
from analyzemops.analysis import runAnalysis

parameters = Parameters.fromYaml("/project/moeyensj/jpl/fullDensity_3months/singlewindow/run_singlewindow/parameters.yaml")
tracker = Tracker.fromYaml("/project/moeyensj/jpl/fullDensity_3months/singlewindow/run_singlewindow/tracker.yaml")
runAnalysis(tracker, parameters)