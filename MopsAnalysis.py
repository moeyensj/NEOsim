import os
import time
import yaml
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import moMetrics
import MopsPlotter
import MopsReader
from MopsObjects import tracklet
from MopsObjects import track
from MopsParameters import MopsParameters
from MopsTracker import MopsTracker

LSST_MIDNIGHT = 0.166

class runAnalysis(object):

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

        # Tracks
        self._totalTracks = {}
        self._trueTracks = {}
        self._falseTracks = {}
        self._subsetTracks = {}
        self._longestTracks = {}
        self._trackDetFileSizes = {}
        self._trackIdFileSizes = {}
        self._trackFileSizes = {}

        # Final tracks
        self._totalFinalTracks = {}
        self._trueFinalTracks = {}
        self._falseFinalTracks = {}
        self._subsetFinalTracks = {}
        self._longestFinalTracks = {}
        self._finalTrackDetFileSizes = {}
        self._finalTrackIdFileSizes = {}
        self._finalTrackFileSizes = {}

        # Tracklets (post findTracklets)
        self._totalTracklets = {}
        self._trueTracklets = {}
        self._falseTracklets = {}
        self._trackletDetFileSizes = {}
        self._trackletFileSizes = {}

        # Collapsed tracklets
        self._totalCollapsedTracklets = {}
        self._trueCollapsedTracklets = {}
        self._falseCollapsedTracklets = {}
        self._collapsedTrackletDetFileSizes = {}
        self._collapsedTrackletFileSizes = {}

        # Purified tracklets
        self._totalPurifiedTracklets = {}
        self._truePurifiedTracklets = {}
        self._falsePurifiedTracklets = {}
        self._purifiedTrackletDetFileSizes = {}
        self._purifiedTrackletFileSizes = {}

        # Final tracklets (post removeSubsets)
        self._totalFinalTracklets = {}
        self._trueFinalTracklets = {}
        self._falseFinalTracklets = {}
        self._finalTrackletDetFileSizes = {}
        self._finalTrackletFileSizes = {}
        
        # General analysis information
        self._startTime = 0
        self._endTime = 0

        self.findNights()
        self.findWindows()

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
    def trackDetFileSizes(self):
        return self._trackDetFileSizes

    @trackDetFileSizes.setter
    def trackDetFileSizes(self, value):
        self._trackDetFileSizes = value

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
    def finalTrackDetFileSizes(self):
        return self._finalTrackDetFileSizes

    @finalTrackDetFileSizes.setter
    def finalTrackDetFileSizes(self, value):
        self._finalTrackDetFileSizes = value

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
    def trackletDetFileSizes(self):
        return self._trackletDetFileSizes

    @trackletDetFileSizes.setter
    def trackletDetFileSizes(self, value):
        self._trackletDetFileSizes = value

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
    def collapsedTrackletDetFileSizes(self):
        return self._collapsedTrackletDetFileSizes

    @collapsedTrackletDetFileSizes.setter
    def collapsedTrackletDetFileSizes(self, value):
        self._collapsedTrackletDetFileSizes = value

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
    def purifiedTrackletDetFileSizes(self):
        return self._purifiedTrackletDetFileSizes

    @purifiedTrackletDetFileSizes.setter
    def purifiedTrackletDetFileSizes(self, value):
        self._purifiedTrackletDetFileSizes = value

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
    def finalTrackletDetFileSizes(self):
        return self._finalTrackletDetFileSizes

    @finalTrackletDetFileSizes.setter
    def finalTrackletDetFileSizes(self, value):
        self._finalTrackletDetFileSizes = value

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

    # Instance Methods

    def findNights(self):
        for detFile in self.tracker.diasources:
            self._nights.append(MopsReader.readNight(detFile))

    def findWindows(self):
        for trackFile in self.tracker.tracks:
            self._windows.append(MopsReader.readWindow(trackFile))

    def analyze(self, tracklets=True, collapsedTracklets=True, purifiedTracklets=True, finalTracklets=True, tracks=True, finalTracks=True, analyzeSubsets=True, minWindowSize=0):

        self._startTime = time.ctime()

        if tracklets and self.tracker.ranFindTracklets:
            resultFiles = []

            for night, trackletFile, detFile in zip(self.nights, self.tracker.tracklets, self.tracker.diasources):
                [resultsFile, true_tracklets_num, false_tracklets_num, total_tracklets_num, det_file_size, 
                    tracklet_file_size] = analyzeTracklets(trackletFile, detFile)

                resultFiles.append(resultsFile)

                self._totalTracklets[night] = total_tracklets_num
                self._trueTracklets[night] = true_tracklets_num
                self._falseTracklets[night] = false_tracklets_num
                self._trackletFileSizes[night] = tracklet_file_size
                self._trackletDetFileSizes[night] = det_file_size

                print ""

            self.tracker.ranTrackletAnalysis = True
            self.tracker.trackletResults = sorted(resultFiles)
            self.tracker.toYaml(outDir=self.tracker.runDir)
                   
        else:
            print "Skipping tracklet analysis..."
            print ""
        

        if collapsedTracklets and self.tracker.ranCollapseTracklets:
            resultFiles = []

            for night, trackletFile, detFile in zip(self.nights, self.tracker.collapsedTrackletsById, self.tracker.diasources):
                [resultsFile, true_tracklets_num, false_tracklets_num, total_tracklets_num, det_file_size, 
                    tracklet_file_size] = analyzeTracklets(trackletFile, detFile)

                resultFiles.append(resultsFile)

                self._totalCollapsedTracklets[night] = total_tracklets_num
                self._trueCollapsedTracklets[night] = true_tracklets_num
                self._falseCollapsedTracklets[night] = false_tracklets_num
                self._collapsedTrackletFileSizes[night] = tracklet_file_size
                self._collapsedTrackletDetFileSizes[night] = det_file_size

                print ""

            self.tracker.ranCollapsedTrackletAnalysis = True
            self.tracker.collapsedTrackletResults = sorted(resultFiles)
            self.tracker.toYaml(outDir=self.tracker.runDir)
                
        else:
            print "Skipping collapsed tracklet analysis..."
            print ""


        if purifiedTracklets and self.tracker.ranPurifyTracklets:
            resultFiles = []

            for night, trackletFile, detFile in zip(self.nights, self.tracker.purifiedTrackletsById, self.tracker.diasources):
                [resultsFile, true_tracklets_num, false_tracklets_num, total_tracklets_num, det_file_size, 
                    tracklet_file_size] = analyzeTracklets(trackletFile, detFile)

                resultFiles.append(resultsFile)

                self._totalPurifiedTracklets[night] = total_tracklets_num
                self._truePurifiedTracklets[night] = true_tracklets_num
                self._falsePurifiedTracklets[night] = false_tracklets_num
                self._purifiedTrackletFileSizes[night] = tracklet_file_size
                self._purifiedTrackletDetFileSizes[night] = det_file_size

                print ""

            self.tracker.ranPurifiedTrackletAnalysis = True
            self.tracker.purifiedTrackletResults = sorted(resultFiles)
            self.tracker.toYaml(outDir=self.tracker.runDir)

        else:
            print "Skipping purified tracklet analysis..."
            print ""

        if finalTracklets and self.tracker.ranRemoveSubsetTracklets:
            resultFiles = []

            for night, trackletFile, detFile in zip(self.nights, self.tracker.finalTrackletsById, self.tracker.diasources):
                [resultsFile, true_tracklets_num, false_tracklets_num, total_tracklets_num, det_file_size, 
                    tracklet_file_size] = analyzeTracklets(trackletFile, detFile)

                resultFiles.append(resultsFile)

                self._totalFinalTracklets[night] = total_tracklets_num
                self._trueFinalTracklets[night] = true_tracklets_num
                self._falseFinalTracklets[night] = false_tracklets_num
                self._finalTrackletFileSizes[night] = tracklet_file_size
                self._finalTrackletDetFileSizes[night] = det_file_size

                print ""

            self.tracker.ranFinalTrackletAnalysis = True
            self.tracker.finalTrackletResults = sorted(resultFiles)
            self.tracker.toYaml(outDir=self.tracker.runDir)

        else:
            print "Skipping final tracklet analysis..."   
            print ""

        if tracks and self.tracker.ranLinkTracklets:
            resultFiles = []

            for window, trackFile, detFile, idsFile in zip(self.windows, self.tracker.tracks, self.tracker.dets, self.tracker.ids):
                if checkWindow(window, minWindowSize):
                    [resultsFile, performance_ratio, true_tracks_num, false_tracks_num, total_tracks_num, 
                        subset_tracks_num, longest_tracks_num, objects_num, findable_objs_num, found_objs_num, 
                        missed_objs_num, det_file_size, 
                        ids_file_size, track_file_size] = analyzeTracks(trackFile, detFile, idsFile, analyzeSubsets=analyzeSubsets)

                    resultFiles.append(resultsFile)

                    self._uniqueObjects[window] = objects_num
                    self._findableObjects[window] = findable_objs_num
                    self._foundObjects[window] = found_objs_num
                    self._missedObjects[window] = missed_objs_num
                    self._performanceRatio[window] = performance_ratio

                    self._totalTracks[window] = total_tracks_num
                    self._trueTracks[window] = true_tracks_num
                    self._falseTracks[window] = false_tracks_num
                    self._subsetTracks[window] = subset_tracks_num
                    self._longestTracks[window] = longest_tracks_num

                    self._trackFileSizes[window] = track_file_size
                    self._trackDetFileSizes[window] = det_file_size
                    self._trackIdFileSizes[window] = ids_file_size

                    print ""

            self.tracker.ranTrackAnalysis = True
            self.tracker.trackResults = sorted(resultFiles)
            self.tracker.toYaml(outDir=self.tracker.runDir)

        else:
            print "Skipping track analysis..."
            print ""

        if finalTracks and self.tracker.ranRemoveSubsetTracks:
            resultFiles = []

            for window, trackFile, detFile, idsFile in zip(self.windows, self.tracker.finalTracks, self.tracker.dets, self.tracker.ids):
                if checkWindow(window, minWindowSize):
                    [resultsFile, performance_ratio, true_tracks_num, false_tracks_num, total_tracks_num, 
                        subset_tracks_num, longest_tracks_num, objects_num, findable_objs_num, found_objs_num, missed_objs_num, det_file_size, 
                        ids_file_size, track_file_size] = analyzeTracks(trackFile, detFile, idsFile)

                    resultFiles.append(resultsFile)

                    self._totalFinalTracks[window] = total_tracks_num
                    self._trueFinalTracks[window] = true_tracks_num
                    self._falseFinalTracks[window] = false_tracks_num
                    self._subsetFinalTracks[window] = subset_tracks_num
                    self._longestFinalTracks[window] = longest_tracks_num

                    self._finalTrackFileSizes[window] = track_file_size
                    self._finalTrackDetFileSizes[window] = det_file_size
                    self._finalTrackIdFileSizes[window] = ids_file_size

                    print ""

            self.tracker.ranFinalTrackAnalysis = True
            self.tracker.finalTrackResults = sorted(resultFiles)
            self.tracker.toYaml(outDir=self.tracker.runDir)

        else:
            print "Skipping final track analysis..."
            print ""

        self._endTime = time.ctime()

        return

def calcNight(mjd, midnight=LSST_MIDNIGHT):
    """Determine night number for any MJD."""
    night = mjd + 0.5 - midnight
    return night.astype(int)

def findSSMIDs(dataframe, diaids):
    ssmids = []
    for i in diaids:
        ssmid = int(dataframe[dataframe["diaId"] == i]["ssmId"])
        ssmids.append(ssmid)

    return np.array(ssmids)

def checkSubsets(tracks):
    # for each track in tracks, check subsets, if subset remove from array and add to subset array
    # remainings tracks are the longest tracks
    longest_tracks_num = 0
    subset_tracks_num = 0

    for test_track in tracks:
        if test_track.isSubset:
            break
        else: 
            for comparison_track in tracks:
                t =  set(test_track.diasources["diaId"])
                c =  set(comparison_track.diasources["diaId"])

                if t != c:
                    if t.issubset(c):
                        test_track.isSubset = True
                        test_track.subsetTracks.append(comparison_track)
                        subset_tracks_num += 1
                        break

    for test_track in tracks:
        if test_track.isSubset == None:
            test_track.isSubset = False
            longest_tracks_num += 1

    return longest_tracks_num, subset_tracks_num

def checkWindow(window, minWindowSize):
    if int(window.split("-")[1]) - int(window.split("-")[0]) >= minWindowSize:
        return True
    else:
        return False
 
def countUniqueSSMIDs(dataframe):
    return dataframe["ssmId"].nunique()

def countMissedSSMIDs(foundSSMIDs, findableSSMIDs):
    missedSSMIDs = set(findableSSMIDs) - set(foundSSMIDs)
    return list(missedSSMIDs)

def countFindableObjects(dataframe, minDetectionsPerNight=2, minNights=3, windowSize=15, snrLimit=-1):
    unique_ssmids = dataframe["ssmId"].unique()
    findable_ssmids = []
    
    discoverMet = moMetrics.DiscoveryChancesMetric(nObsPerNight=minDetectionsPerNight, tNight=90./60./24., nNightsPerWindow=minNights, tWindow=windowSize, snrLimit=snrLimit)
    
    for unique_ssmid in unique_ssmids:
        detections = dataframe[dataframe["ssmId"] == unique_ssmid]
        
        new_ssobject = np.zeros(len(detections), 
            dtype={"names":["night", "expMJD", "SNR"], 
                   "formats":["int4","int4","float64"]})
        
        new_ssobject["night"] = calcNight(detections["mjd"].values)
        new_ssobject["expMJD"] = detections["mjd"].values
        new_ssobject["SNR"] = detections["snr"].values
        
        discoveryChances = discoverMet.run(new_ssobject, 0, 0)
        if discoveryChances >= 1:
            findable_ssmids.append(unique_ssmid)
       
    return findable_ssmids

def _buildTracklet(dataframe, trackletId, diaids, night, ssmidDict, calcRMS=True):
    new_tracklet = tracklet(trackletId, len(diaids), night)

    for i, diaid in enumerate(diaids):
        diasource = dataframe.loc[diaid]
        new_tracklet.addDiasource(i, diaid, diasource)
        
        if diasource['ssmId'] in ssmidDict:
            ssmidDict[diasource['ssmId']] += 1
        else:
            ssmidDict[diasource['ssmId']] = 1
    
    if calcRMS:
        new_tracklet.updateRMS()
        
    new_tracklet.updateVelocity()
    new_tracklet.updateQuality()
    new_tracklet.updateMembers()
    new_tracklet.updateInfo()
    
    return new_tracklet


def _buildTrack(dataframe, diaids, ssmidDict, calcRMS=False):
    new_track = track(len(diaids))

    for i, diaid in enumerate(diaids):
        diasource = dataframe.loc[diaid]
        new_track.diasources[i]["diaId"] = int(diaid)
        new_track.diasources[i]["visitId"] = diasource["visitId"]
        new_track.diasources[i]["ssmId"] = diasource["ssmId"]
        new_track.diasources[i]["ra"] = diasource["ra"]
        new_track.diasources[i]["dec"] = diasource["dec"]
        new_track.diasources[i]["mjd"] = diasource["mjd"]
        new_track.diasources[i]["mag"] = diasource["mag"]
        new_track.diasources[i]["snr"] = diasource["snr"]
        
        if diasource["ssmId"] in ssmidDict:
            ssmidDict[diasource["ssmId"]] += 1
        else:
            ssmidDict[diasource["ssmId"]] = 1

    new_track.isTrue = checkSSMIDs(new_track.diasources["ssmId"])

    if calcRMS:
        new_track.rms, new_track.raRes, new_track.decRes, new_track.distances = calcRMS(new_track.diasources)

    return new_track

def analyzeTracklets(trackletFile, detFile, vmax=0.5):
    startTime = time.ctime()
    print "Starting analysis for %s at %s" % (os.path.basename(trackletFile), startTime)
    
    # Create outfile to store results
    outFile = trackletFile + ".results"
    outFileOut = open(outFile, "w", 0)
    outFileOut.write("Start time: %s\n\n" % (startTime))
    print "Writing results to %s" % (outFile)

    # Get file sizes
    print "Checking file sizes..."
    detFileSize = os.path.getsize(detFile)
    trackletFileSize = os.path.getsize(trackletFile)

    # Read detections into a dataframe
    print "Reading input detections..."
    dets_df = MopsReader.readDetectionsIntoDataframe(detFile)
    outFileOut.write("Input Detection File Summary:\n")
    outFileOut.write("File size (bytes): %s\n" % (detFileSize))
    outFileOut.write("Detections: %s\n" % (len(dets_df.index)))
    outFileOut.write("Unique objects: %s\n" % (dets_df["ssmId"].nunique()))

    # Count number of true tracklets and findable SSMIDs in dataframe
    print "Counting findable true tracklets..."
    # findable_true_tracklets_num, findable_ssmids = countFindableTrueTrackletsAndSSMIDs(dets_df, 2.0, vmax)
    findable_true_tracklets_num = 0
    findable_ssmids = [0]
    outFileOut.write("Findable objects: %s\n" % (len(findable_ssmids)))
    outFileOut.write("Findable true tracklets: %s\n\n" % (findable_true_tracklets_num))
    
    trackletFileIn = open(trackletFile, "r")
    tracklets = []
    ssmid_dict = {}
    
    # Initalize success (or failure) counters
    total_tracklets_num = 0
    true_tracklets_num = 0
    false_tracklets_num = 0
    

    # Examine each line in trackletFile and read in every line
    #  as a track object. If track contains new detections (diasource)
    #  then add new source to diasource_dict. 
    print "Building tracklets from tracklet file..."
    for line in trackletFileIn:
        # Found a track!
        total_tracklets_num += 1
        new_tracklet_diaids = MopsReader.readTracklet(line)
        new_tracklet = _buildTracklet(dets_df, new_tracklet_diaids, ssmid_dict)

        if new_tracklet.isTrue:
            true_tracklets_num += 1
        else: 
            false_tracklets_num += 1

        tracklets.append(new_tracklet)
        
    endTime = time.ctime()

    outFileOut.write("Output Tracklet File Summary:\n")
    outFileOut.write("File size (bytes): %s\n" % (trackletFileSize))
    outFileOut.write("Unique objects found: %s\n" % (len(ssmid_dict)))
    outFileOut.write("True tracklets found: %s\n" % (true_tracklets_num))
    outFileOut.write("False tracklets found: %s\n" % (false_tracklets_num))
    outFileOut.write("Total tracklets found: %s\n\n" % (total_tracklets_num))
    outFileOut.write("End time: %s\n" % (endTime))

    print "Finished analysis for %s at %s" % (os.path.basename(trackletFile), endTime)

    return outFile, true_tracklets_num, false_tracklets_num, total_tracklets_num, detFileSize, trackletFileSize

def analyzeTracks(trackFile, detFile, idsFile, minDetectionsPerNight=2, minNights=3, windowSize=15, snrLimit=-1, analyzeSubsets=True, verbose=True):
    startTime = time.ctime()
    print "Starting analysis for %s at %s" % (os.path.basename(trackFile), startTime)
    
    # Create outfile to store results
    outFile = trackFile + ".results"
    outFileOut = open(outFile, "w", 0)
    outFileOut.write("Start time: %s\n\n" % (startTime))
    print "Writing results to %s" % (outFile)

    print "Checking file sizes..."
    idsFileSize = os.path.getsize(idsFile)
    detFileSize = os.path.getsize(detFile)
    trackFileSize = os.path.getsize(trackFile)

    # Read ids file 
    print "Counting number of input tracklets..."
    tracklet_num = 0
    for tracklet in open(idsFile, "r"):
        tracklet_num += 1

    outFileOut.write("Input Tracklet (Ids) File Summary:\n")
    outFileOut.write("File size (bytes): %s\n" % (idsFileSize))
    outFileOut.write("Tracklets: %s\n\n" % (tracklet_num))
    
    # Read detections into a dataframe
    print "Reading input detections..."
    dets_df = MopsReader.readDetectionsIntoDataframe(detFile)
    outFileOut.write("Input Detection File Summary:\n")
    outFileOut.write("File size (bytes): %s\n" % (detFileSize))
    outFileOut.write("Detections: %s\n" % (len(dets_df.index)))
    outFileOut.write("Unique objects: %s\n" % (dets_df["ssmId"].nunique()))

    # Count number of true tracks and findable SSMIDs in dataframe
    print "Counting findable objects..."
    findable_ssmids = countFindableObjects(dets_df, minDetectionsPerNight=minDetectionsPerNight, minNights=minNights, windowSize=windowSize, snrLimit=snrLimit)
    outFileOut.write("Findable objects: %s\n\n" % (len(findable_ssmids)))
    
    trackFileIn = open(trackFile, "r")
    tracks = []
    ssmid_dict = {}
    found_ssmids = []
    missed_ssmids = []
    
    # Initalize success (or failure) counters and track array
    total_tracks_num = 0
    true_tracks_num = 0
    false_tracks_num = 0

    # Examine each line in trackFile and read in every line
    #  as a track object. If track contains new detections (diasource)
    #  then add new source to diasource_dict. 
    print "Building tracks from track file..."
    for line in trackFileIn:
        # Found a track!
        total_tracks_num += 1
        new_track_diaids = MopsReader.readTrack(line)
        new_track = _buildTrack(dets_df, new_track_diaids, ssmid_dict)
                 
        if new_track.isTrue:
            # Track is true! 
            true_tracks_num += 1
            if new_track.diasources["ssmId"][0] not in found_ssmids:
                found_ssmids.append(new_track.diasources["ssmId"][0])
        else:
            # Track is false. 
            false_tracks_num += 1

        tracks.append(new_track)
    
    longest_tracks_num = 0
    subset_tracks_num = 0
    if analyzeSubsets:
        print "Counting subset tracks..."    
        longest_tracks_num, subset_tracks_num = checkSubsets(tracks)

    print "Counting missed objects..."
    missed_ssmids = countMissedSSMIDs(found_ssmids, findable_ssmids)

    print "Calculating performance..."
    if len(findable_ssmids) != 0:
        performance_ratio = float(len(found_ssmids))/len(findable_ssmids)
    else:
        performance_ratio = 0.0

    endTime = time.ctime()

    outFileOut.write("Output Track File Summary:\n")
    outFileOut.write("File size (bytes): %s\n" % (trackFileSize))
    outFileOut.write("Objects found: %s\n" % (len(found_ssmids)))
    outFileOut.write("Objects missed: %s\n" % (len(missed_ssmids)))
    outFileOut.write("True tracks found: %s\n" % (true_tracks_num))
    outFileOut.write("False tracks found: %s\n" % (false_tracks_num))
    outFileOut.write("Total tracks found: %s\n" % (total_tracks_num))
    outFileOut.write("Subset tracks found: %s\n" % (subset_tracks_num))
    outFileOut.write("Non-subset tracks found: %s\n\n" % (longest_tracks_num))
    outFileOut.write("MOPs Performance Ratio (found/findable): %.5f\n\n" % (performance_ratio))
    outFileOut.write("End time: %s\n" % (endTime))

    print "Finished analysis for %s at %s" % (os.path.basename(trackFile), endTime)
   
    return outFile, performance_ratio, true_tracks_num, false_tracks_num, total_tracks_num, subset_tracks_num, longest_tracks_num, dets_df["ssmId"].nunique(), len(findable_ssmids), len(found_ssmids), len(missed_ssmids), detFileSize, idsFileSize, trackFileSize
