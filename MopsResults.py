__all__ = ["MopsResults"]

class MopsResults(object):

    def __init__(self, parameters, tracker):
        self._parameters = parameters
        self._tracker = tracker

        # General run overview
        self._nights = []
        self._windows = []
        self._uniqueObjects = {}
        self._findableObjects = {}
        self._foundObjects = {}
        self._missedObjects = {}
        self._performanceRatio = {}
        self._nightlyDetectionFileSizes = {}
        self._windowDetectionFileSizes = {}

        # Tracks
        self._totalTracks = {}
        self._trueTracks = {}
        self._falseTracks = {}
        self._subsetTracks = {}
        self._longestTracks = {}
        self._trackIdFileSizes = {}
        self._trackFileSizes = {}

        # Final tracks
        self._totalFinalTracks = {}
        self._trueFinalTracks = {}
        self._falseFinalTracks = {}
        self._subsetFinalTracks = {}
        self._longestFinalTracks = {}
        self._finalTrackIdFileSizes = {}
        self._finalTrackFileSizes = {}

        # Tracklets (post findTracklets)
        self._totalTracklets = {}
        self._trueTracklets = {}
        self._falseTracklets = {}
        self._trackletFileSizes = {}

        # Collapsed tracklets
        self._totalCollapsedTracklets = {}
        self._trueCollapsedTracklets = {}
        self._falseCollapsedTracklets = {}
        self._collapsedTrackletFileSizes = {}

        # Purified tracklets
        self._totalPurifiedTracklets = {}
        self._truePurifiedTracklets = {}
        self._falsePurifiedTracklets = {}
        self._purifiedTrackletFileSizes = {}

        # Final tracklets (post removeSubsets)
        self._totalFinalTracklets = {}
        self._trueFinalTracklets = {}
        self._falseFinalTracklets = {}
        self._finalTrackletFileSizes = {}
        
        # General analysis information
        self._startTime = 0
        self._endTime = 0

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, value):
        self._parameters = value

    @property
    def tracker(self):
        return self._tracker

    @tracker.setter
    def tracker(self, value):
        self._tracker = value

    # General run overview

    @property
    def nights(self):
        return self._nights

    @nights.setter
    def nights(self, value):
        self._nights = value

    @property
    def windows(self):
        return self._windows

    @windows.setter
    def windows(self, value):
        self._windows = value

    @property
    def uniqueObjects(self):
        return self._uniqueObjects

    @uniqueObjects.setter
    def uniqueObjects(self, value):
        self._uniqueObjects = value

    @property
    def findableObjects(self):
        return self._findableObjects

    @findableObjects.setter
    def findableObjects(self, value):
        self._findableObjects = value

    @property
    def foundObjects(self):
        return self._foundObjects

    @foundObjects.setter
    def foundObjects(self, value):
        self._foundObjects = value

    @property
    def missedObjects(self):
        return self._missedObjects

    @missedObjects.setter
    def missedObjects(self, value):
        self._missedObjects = value

    @property
    def missedObjects(self):
        return self._missedObjects

    @missedObjects.setter
    def missedObjects(self, value):
        self._missedObjects = value

    @property
    def performanceRatio(self):
        return self._performanceRatio

    @performanceRatio.setter
    def performanceRatio(self, value):
        self._performanceRatio = value

    @property
    def nightlyDetectionFileSizes(self):
        return self._nightlyDetectionFileSizes

    @nightlyDetectionFileSizes.setter
    def nightlyDetectionFileSizes(self, value):
        self._nightlyDetectionFileSizes = value

    @property
    def windowDetectionFileSizes(self):
        return self._windowDetectionFileSizes

    @windowDetectionFileSizes.setter
    def windowDetectionFileSizes(self, value):
        self._windowDetectionFileSizes = value

    # Tracks

    @property
    def totalTracks(self):
        return self._totalTracks

    @totalTracks.setter
    def totalTracks(self, value):
        self._totalTracks = value

    @property
    def trueTracks(self):
        return self._trueTracks

    @trueTracks.setter
    def trueTracks(self, value):
        self._trueTracks = value

    @property
    def falseTracks(self):
        return self._falseTracks

    @falseTracks.setter
    def falseTracks(self, value):
        self._falseTracks = value

    @property
    def subsetTracks(self):
        return self._subsetTracks

    @subsetTracks.setter
    def subsetTracks(self, value):
        self._subsetTracks = value

    @property
    def longestTracks(self):
        return self._longestTracks

    @longestTracks.setter
    def longestTracks(self, value):
        self._longestTracks = value

    @property
    def trackIdFileSizes(self):
        return self._trackIdFileSizes

    @trackIdFileSizes.setter
    def trackIdFileSizes(self, value):
        self._trackIdFileSizes = value

    @property
    def trackFileSizes(self):
        return self._trackFileSizes

    @trackFileSizes.setter
    def trackFileSizes(self, value):
        self._trackFileSizes = value

    # Final tracks

    @property
    def totalFinalTracks(self):
        return self._totalFinalTracks

    @totalFinalTracks.setter
    def totalFinalTracks(self, value):
        self._totalFinalTracks = value

    @property
    def trueFinalTracks(self):
        return self._trueFinalTracks

    @trueFinalTracks.setter
    def trueFinalTracks(self, value):
        self._trueFinalTracks = value

    @property
    def falseFinalTracks(self):
        return self._falseFinalTracks

    @falseFinalTracks.setter
    def falseFinalTracks(self, value):
        self._falseFinalTracks = value

    @property
    def subsetFinalTracks(self):
        return self._subsetFinalTracks

    @subsetFinalTracks.setter
    def subsetFinalTracks(self, value):
        self._subsetFinalTracks = value

    @property
    def longestFinalTracks(self):
        return self._longestFinalTracks

    @longestFinalTracks.setter
    def longestFinalTracks(self, value):
        self._longestFinalTracks = value

    @property
    def finalTrackIdFileSizes(self):
        return self._finalTrackIdFileSizes

    @finalTrackIdFileSizes.setter
    def finalTrackIdFileSizes(self, value):
        self._finalTrackIdFileSizes = value

    @property
    def finalTrackFileSizes(self):
        return self._finalTrackFileSizes

    @finalTrackFileSizes.setter
    def finalTrackFileSizes(self, value):
        self._finalTrackFileSizes = value

    # Tracklets (post findTracklets)

    @property
    def totalTracklets(self):
        return self._totalTracklets

    @totalTracklets.setter
    def totalTracklets(self, value):
        self._totalTracklets = value

    @property
    def trueTracklets(self):
        return self._trueTracklets

    @trueTracklets.setter
    def trueTracklets(self, value):
        self._trueTracklets = value

    @property
    def falseTracklets(self):
        return self._falseTracklets

    @falseTracklets.setter
    def falseTracklets(self, value):
        self._falseTracklets = value

    @property
    def trackletFileSizes(self):
        return self._trackletFileSizes

    @trackletFileSizes.setter
    def trackletFileSizes(self, value):
        self._trackletFileSizes = value

    # Collapsed tracklets

    @property
    def totalCollapsedTracklets(self):
        return self._totalCollapsedTracklets

    @totalCollapsedTracklets.setter
    def totalCollapsedTracklets(self, value):
        self._totalCollapsedTracklets = value

    @property
    def trueCollapsedTracklets(self):
        return self._trueCollapsedTracklets

    @trueCollapsedTracklets.setter
    def trueCollapsedTracklets(self, value):
        self._trueCollapsedTracklets = value

    @property
    def falseCollapsedTracklets(self):
        return self._falseCollapsedTracklets

    @falseCollapsedTracklets.setter
    def falseCollapsedTracklets(self, value):
        self._falseCollapsedTracklets = value

    @property
    def collapsedTrackletFileSizes(self):
        return self._collapsedTrackletFileSizes

    @collapsedTrackletFileSizes.setter
    def collapsedTrackletFileSizes(self, value):
        self._collapsedTrackletFileSizes = value

    # Purified tracklets

    @property
    def totalPurifiedTracklets(self):
        return self._totalPurifiedTracklets

    @totalPurifiedTracklets.setter
    def totalPurifiedTracklets(self, value):
        self._totalPurifiedTracklets = value

    @property
    def truePurifiedTracklets(self):
        return self._truePurifiedTracklets

    @truePurifiedTracklets.setter
    def truePurifiedTracklets(self, value):
        self._truePurifiedTracklets = value

    @property
    def falsePurifiedTracklets(self):
        return self._falsePurifiedTracklets

    @falsePurifiedTracklets.setter
    def falsePurifiedTracklets(self, value):
        self._falsePurifiedTracklets = value

    @property
    def purifiedTrackletFileSizes(self):
        return self._purifiedTrackletFileSizes

    @purifiedTrackletFileSizes.setter
    def purifiedTrackletFileSizes(self, value):
        self._purifiedTrackletFileSizes = value

    # Final tracklets (post removeSubsets)

    @property
    def totalFinalTracklets(self):
        return self._totalFinalTracklets

    @totalFinalTracklets.setter
    def totalFinalTracklets(self, value):
        self._totalFinalTracklets = value

    @property
    def trueFinalTracklets(self):
        return self._trueFinalTracklets

    @trueFinalTracklets.setter
    def trueFinalTracklets(self, value):
        self._trueFinalTracklets = value

    @property
    def falseFinalTracklets(self):
        return self._falseFinalTracklets

    @falseFinalTracklets.setter
    def falseFinalTracklets(self, value):
        self._falsePurifiedTracklets = value

    @property
    def finalTrackletFileSizes(self):
        return self._finalTrackletFileSizes

    @finalTrackletFileSizes.setter
    def finalTrackletFileSizes(self, value):
        self._finalTrackletFileSizes = value

    # General analysis information

    @property
    def startTime(self):
        return self._startTime

    @startTime.setter
    def startTime(self, value):
        print "Cannot edit analysis start time."

    @property
    def endTime(self):
        return self._endTime

    @endTime.setter
    def endTime(self, value):
        print "Cannot edit analysis end time."

    def toYaml(self, outDir=None):
        import os
        import yaml

        if outDir == None:
            outname = "results.yaml"
        else:
            outname = os.path.join(outDir, "results.yaml")

        print "Saving results to %s" % (outname)

        stream = file(outname, "w")
        yaml.dump(self, stream)   
        stream.close()

        return

    @classmethod
    def fromYaml(cls, yamlFile):
        import yaml
        
        print "Loading results from %s" % (yamlFile)
        
        cls = yaml.load(file(yamlFile, "r"))
        
        return cls