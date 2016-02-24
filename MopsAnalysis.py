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
from MopsObjects import sso
from MopsParameters import MopsParameters
from MopsTracker import MopsTracker

SAMPLE_SIZE = 50
LSST_MIDNIGHT = 0.166

class runAnalysis(object):

    def __init__(self, parameters, tracker, ssmidsOfInterest=None, sampleSize=10):

        self._parameters = parameters
        self._tracker = tracker
        self._ssmidsOfInterest = ssmidsOfInterest
        self._ssmidsOfInterestObjects = {}
        self._sampleSize = sampleSize

        # General run overview
        self._nights = []
        self._windows = []
        self._uniqueObjects = {}
        self._findableObjects = {}
        self._foundObjects = {}
        self._missedObjects = {}

        # Tracks
        self._totalTracks = {}
        self._trueTracks = {}
        self._falseTracks = {}
        self._subsetTracks = {}
        self._longestTracks = {}
        self._trueTracksSample = {}
        self._falseTracksSample = {}
        self._trackDetFileSizes = {}
        self._trackIdFileSizes = {}
        self._trackFileSizes = {}

        # Final tracks
        self._totalFinalTracks = {}
        self._trueFinalTracks = {}
        self._falseFinalTracks = {}
        self._subsetFinalTracks = {}
        self._longestFinalTracks = {}
        self._trueFinalTracksSample = {}
        self._falseFinalTracksSample = {}
        self._finalTrackDetFileSizes = {}
        self._finalTrackIdFileSizes = {}
        self._finalTrackFileSizes = {}

        # Tracklets (post findTracklets)
        self._totalTracklets = {}
        self._trueTracklets = {}
        self._falseTracklets = {}
        self._trueTrackletsSample = {}
        self._falseTrackletsSample = {}
        self._trackletDetFileSizes = {}
        self._trackletFileSizes = {}

        # Collapsed tracklets
        self._totalCollapsedTracklets = {}
        self._trueCollapsedTracklets = {}
        self._falseCollapsedTracklets = {}
        self._trueCollapsedTrackletsSample = {}
        self._falseCollapsedTrackletsSample = {}
        self._collapsedTrackletDetFileSizes = {}
        self._collapsedTrackletFileSizes = {}

        # Purified tracklets
        self._totalPurifiedTracklets = {}
        self._truePurifiedTracklets = {}
        self._falsePurifiedTracklets = {}
        self._truePurifiedTrackletsSample = {}
        self._falsePurifiedTrackletsSample = {}
        self._purifiedTrackletDetFileSizes = {}
        self._purifiedTrackletFileSizes = {}

        # Final tracklets (post removeSubsets)
        self._totalFinalTracklets = {}
        self._trueFinalTracklets = {}
        self._falseFinalTracklets = {}
        self._trueFinalTrackletsSample = {}
        self._falseFinalTrackletsSample = {}
        self._finalTrackletDetFileSizes = {}
        self._finalTrackletFileSizes = {}
        
        # General analysis information
        self._startTime = 0
        self._endTime = 0

        if self._ssmidsOfInterest == None:
            self._ssmidsOfInterest = selectSampleSSMIDs(tracker.dets, self._sampleSize)

        self.initializeSSOs()
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
        
    @property
    def ssmidsOfInterest(self):
        return self._ssmidsOfInterest

    @ssmidsOfInterest.setter
    def ssmidsOfInterest(self, value):
        self._ssmidsOfInterest = value
    
    @property
    def ssmidsOfInterestObjects(self):
        return self._ssmidsOfInterestObjects

    @ssmidsOfInterestObjects.setter
    def ssmidsOfInterestObjects(self, value):
        self._ssmidsOfInterestObjects = value

    @property
    def sampleSize(self):
        return self._sampleSize

    @sampleSize.setter
    def sampleSize(self, value):
        self._sampleSize = value

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
    def trueTracksSample(self):
        return self._trueTracksSample

    @trueTracksSample.setter
    def trueTracksSample(self, value):
        self._trueTracksSample = value

    @property
    def falseTracksSample(self):
        return self._falseTracksSample

    @falseTracksSample.setter
    def falseTracksSample(self, value):
        self._falseTracksSample = value

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
    def trueFinalTracksSample(self):
        return self._trueFinalTracksSample

    @trueFinalTracksSample.setter
    def trueFinalTracksSample(self, value):
        self._trueFinalTracksSample = value

    @property
    def falseFinalTracksSample(self):
        return self._falseFinalTracksSample

    @falseFinalTracksSample.setter
    def falseFinalTracksSample(self, value):
        self._falseFinalTracksSample = value

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
    def trueTrackletsSample(self):
        return self._trueTrackletsSample

    @trueTrackletsSample.setter
    def trueTrackletsSample(self, value):
        self._trueTrackletsSample = value

    @property
    def falseTrackletsSample(self):
        return self._falseTrackletsSample

    @falseTrackletsSample.setter
    def falseTrackletsSample(self, value):
        self._falseTrackletsSample = value

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
    def trueCollapsedTrackletsSample(self):
        return self._trueCollapsedTrackletsSample

    @trueCollapsedTrackletsSample.setter
    def trueCollapsedTrackletsSample(self, value):
        self._trueCollapsedTrackletsSample = value

    @property
    def falseCollapsedTrackletsSample(self):
        return self._falseCollapsedTrackletsSample

    @falseCollapsedTrackletsSample.setter
    def falseCollapsedTrackletsSample(self, value):
        self._falseCollapsedTrackletsSample = value

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
    def truePurifiedTrackletsSample(self):
        return self._truePurifiedTrackletsSample

    @truePurifiedTrackletsSample.setter
    def truePurifiedTrackletsSample(self, value):
        self._truePurifiedTrackletsSample = value

    @property
    def falsePurifiedTrackletsSample(self):
        return self._falsePurifiedTrackletsSample

    @falsePurifiedTrackletsSample.setter
    def falsePurifiedTrackletsSample(self, value):
        self._falsePurifiedTrackletsSample = value

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
    def trueFinalTrackletsSample(self):
        return self._trueFinalTrackletsSample

    @trueFinalTrackletsSample.setter
    def trueFinalTrackletsSample(self, value):
        self._trueFinalTrackletsSample = value

    @property
    def falseFinalTrackletsSample(self):
        return self._falseFinalTrackletsSample

    @falseFinalTrackletsSample.setter
    def falseFinalTrackletsSample(self, value):
        self._falsePurifiedTrackletsSample = value

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

    def initializeSSOs(self):
        for ssmid in self._ssmidsOfInterest:
            self._ssmidsOfInterestObjects[ssmid] = sso(ssmid)

    def analyze(self, tracklets=True, collapsedTracklets=True, purifiedTracklets=True, finalTracklets=True, tracks=True, finalTracks=True, analyzeSubsets=False, minWindowSize=0):

        self._startTime = time.ctime()

        if tracklets and self.tracker.ranFindTracklets:
                for night, trackletFile, detFile in zip(self.nights, self.tracker.tracklets, self.tracker.diasources):
                    [true_tracklets, false_tracklets, true_tracklets_num, false_tracklets_num, total_tracklets_num, tracklets_of_interest, det_file_size, 
                        tracklet_file_size] = analyzeTracklets(trackletFile, detFile, ssmidsOfInterest=self.ssmidsOfInterest)

                    self._totalTracklets[night] = total_tracklets_num
                    self._trueTracklets[night] = true_tracklets_num
                    self._falseTracklets[night] = false_tracklets_num
                    self._trueTrackletsSample[night] = selectSample(true_tracklets)
                    self._falseTrackletsSample[night] = selectSample(false_tracklets)

                    self._trackletFileSizes[night] = tracklet_file_size
                    self._trackletDetFileSizes[night] = det_file_size

                    for ssmid in tracklets_of_interest:
                        self._ssmidsOfInterestObjects[ssmid].tracklets[night] = tracklets_of_interest[ssmid]

                    print ""
                   
        else:
            print "Skipping tracklet analysis..."
            print ""
        

        if collapsedTracklets and self.tracker.ranCollapseTracklets:
            for night, trackletFile, detFile in zip(self.nights, self.tracker.collapsedTrackletsById, self.tracker.diasources):
                [true_tracklets, false_tracklets, true_tracklets_num, false_tracklets_num, total_tracklets_num, tracklets_of_interest, det_file_size, 
                    tracklet_file_size] = analyzeTracklets(trackletFile, detFile, ssmidsOfInterest=self.ssmidsOfInterest)

                self._totalCollapsedTracklets[night] = total_tracklets_num
                self._trueCollapsedTracklets[night] = true_tracklets_num
                self._falseCollapsedTracklets[night] = false_tracklets_num
                self._trueCollapsedTrackletsSample[night] = selectSample(true_tracklets)
                self._falseCollapsedTrackletsSample[night] = selectSample(false_tracklets)

                self._collapsedTrackletFileSizes[night] = tracklet_file_size
                self._collapsedTrackletDetFileSizes[night] = det_file_size

                for ssmid in tracklets_of_interest:
                    self._ssmidsOfInterestObjects[ssmid].collapsedTracklets[night] = tracklets_of_interest[ssmid]

                print ""
                
        else:
            print "Skipping collapsed tracklet analysis..."
            print ""


        if purifiedTracklets and self.tracker.ranPurifyTracklets:
            for night, trackletFile, detFile in zip(self.nights, self.tracker.purifiedTrackletsById, self.tracker.diasources):
                [true_tracklets, false_tracklets, true_tracklets_num, false_tracklets_num, total_tracklets_num, tracklets_of_interest, det_file_size, 
                    tracklet_file_size] = analyzeTracklets(trackletFile, detFile, ssmidsOfInterest=self.ssmidsOfInterest)

                self._totalPurifiedTracklets[night] = total_tracklets_num
                self._truePurifiedTracklets[night] = true_tracklets_num
                self._falsePurifiedTracklets[night] = false_tracklets_num
                self._truePurifiedTrackletsSample[night] = selectSample(true_tracklets)
                self._falsePurifiedTrackletsSample[night] = selectSample(false_tracklets)

                self._purifiedTrackletFileSizes[night] = tracklet_file_size
                self._purifiedTrackletDetFileSizes[night] = det_file_size

                for ssmid in tracklets_of_interest:
                    self._ssmidsOfInterestObjects[ssmid].purifiedTracklets[night] = tracklets_of_interest[ssmid]

                print ""

        else:
            print "Skipping purified tracklet analysis..."
            print ""

        if finalTracklets and self.tracker.ranRemoveSubsetTracklets:
            for night, trackletFile, detFile in zip(self.nights, self.tracker.finalTrackletsById, self.tracker.diasources):
                [true_tracklets, false_tracklets, true_tracklets_num, false_tracklets_num, total_tracklets_num, tracklets_of_interest, det_file_size, 
                    tracklet_file_size] = analyzeTracklets(trackletFile, detFile, ssmidsOfInterest=self.ssmidsOfInterest)

                self._totalFinalTracklets[night] = total_tracklets_num
                self._trueFinalTracklets[night] = true_tracklets_num
                self._falseFinalTracklets[night] = false_tracklets_num
                self._trueFinalTrackletsSample[night] = selectSample(true_tracklets)
                self._falseFinalTrackletsSample[night] = selectSample(false_tracklets)

                self._finalTrackletFileSizes[night] = tracklet_file_size
                self._finalTrackletDetFileSizes[night] = det_file_size

                for ssmid in tracklets_of_interest:
                    self._ssmidsOfInterestObjects[ssmid].finalTracklets[night] = tracklets_of_interest[ssmid]

                print ""

        else:
            print "Skipping final tracklet analysis..."   
            print ""

        if tracks and self.tracker.ranLinkTracklets:
            for window, trackFile, detFile, idsFile in zip(self.windows, self.tracker.tracks, self.tracker.dets, self.tracker.ids):
                if checkWindow(window, minWindowSize):
                    [true_tracks, false_tracks, true_tracks_num, false_tracks_num, total_tracks_num, 
                        subset_tracks_num, longest_tracks_num, tracks_of_interest, objects_num, findable_objs_num, found_objs_num, det_file_size, 
                        ids_file_size, track_file_size] = analyzeTracks(trackFile, detFile, idsFile, ssmidsOfInterest=self.ssmidsOfInterest, analyzeSubsets=analyzeSubsets)

                    self._uniqueObjects[window] = objects_num
                    self._findableObjects[window] = findable_objs_num
                    self._foundObjects[window] = found_objs_num

                    self._totalTracks[window] = total_tracks_num
                    self._trueTracks[window] = true_tracks_num
                    self._falseTracks[window] = false_tracks_num
                    self._subsetTracks[window] = subset_tracks_num
                    self._longestTracks[window] = longest_tracks_num
                    self._trueTracksSample[window] = selectSample(true_tracks)
                    self._falseTracksSample[window] = selectSample(false_tracks)

                    self._trackFileSizes[window] = track_file_size
                    self._trackDetFileSizes[window] = det_file_size
                    self._trackIdFileSizes[window] = ids_file_size

                    for ssmid in tracks_of_interest:
                        self._ssmidsOfInterestObjects[ssmid].tracks[window] = tracks_of_interest[ssmid]

                    print ""

        else:
            print "Skipping track analysis..."
            print ""

        if finalTracks and self.tracker.ranRemoveSubsetTracks:
            for window, trackFile, detFile, idsFile in zip(self.windows, self.tracker.finalTracks, self.tracker.dets, self.tracker.ids):
                if checkWindow(window, minWindowSize):
                    [true_tracks, false_tracks, true_tracks_num, false_tracks_num, total_tracks_num, 
                        subset_tracks_num, longest_tracks_num, tracks_of_interest, objects_num, findable_objs_num, found_objs_num, det_file_size, 
                        ids_file_size, track_file_size] = analyzeTracks(trackFile, detFile, idsFile, ssmidsOfInterest=self.ssmidsOfInterest)

                    self._totalFinalTracks[window] = total_tracks_num
                    self._trueFinalTracks[window] = true_tracks_num
                    self._falseFinalTracks[window] = false_tracks_num
                    self._subsetFinalTracks[window] = subset_tracks_num
                    self._longestFinalTracks[window] = longest_tracks_num
                    self._trueFinalTracksSample[window] = selectSample(true_tracks)
                    self._falseFinalTracksSample[window] = selectSample(false_tracks)

                    self._finalTrackFileSizes[window] = track_file_size
                    self._finalTrackDetFileSizes[window] = det_file_size
                    self._finalTrackIdFileSizes[window] = ids_file_size

                    for ssmid in tracks_of_interest:
                        self._ssmidsOfInterestObjects[ssmid].finalTracks[window] = tracks_of_interest[ssmid]
                
                    print ""
        else:
            print "Skipping final track analysis..."
            print ""

        self._endTime = time.ctime()

        return

def selectSample(objects, number=SAMPLE_SIZE):
    if len(objects) < number:
        return objects
    else:
        return random.sample(objects, number)

def selectSampleSSMIDs(detFiles, number):
    ssmids = []
    sizes = []
    for detFile in detFiles:
        sizes.append(os.path.getsize(detFile))
        
    detFile = detFiles[np.where(sizes == np.max(sizes))[0][0]]
    
    dets_df = MopsReader.readDetectionsIntoDataframe(detFile)
    sample = selectSample(dets_df['ssmid'].unique(), number=number)
    
    return sample

def findSSMIDs(dataframe, diaids):
    ssmids = []
    for i in diaids:
        ssmid = int(dataframe[dataframe['diaid'] == i]['ssmid'])
        ssmids.append(ssmid)

    return np.array(ssmids)

def checkSSMIDs(ssmids):
    uniqueIds = np.unique(ssmids)
    if len(uniqueIds) == 1:
        return True
    else:
        return False

def checkIfInterested(ssmidsToCheck, ssmids):
    if ssmids == None:
        return False, 0
    else: 
        for ssmidToCheck in ssmidsToCheck:
            if ssmidToCheck in ssmids:
                return True, ssmidToCheck
        
        return False, 0

def checkSubsets(tracks):
    # for each track in tracks, check subsets, if subset remove from array and add to subset array
    # remainings tracks are the longest tracks
    longest_tracks = []
    subset_tracks = []

    for test_track in tracks:
        if test_track.isSubset:
            break
        else: 
            for comparison_track in tracks:
                t =  set(test_track.diasources['diaid'])
                c =  set(comparison_track.diasources['diaid'])

                if t != c:
                    if t.issubset(c):
                        test_track.isSubset = True
                        test_track.subsetTracks.append(comparison_track)
                        subset_tracks.append(test_track)
                        break

    for test_track in tracks:
        if test_track.isSubset == None:
            test_track.isSubset = False
            longest_tracks.append(test_track)

    return longest_tracks, subset_tracks

def checkWindow(window, minWindowSize):
    if int(window.split('-')[1]) - int(window.split('-')[0]) >= minWindowSize:
        return True
    else:
        return False
 
def countUniqueSSMIDs(dataframe):
    return dataframe['ssmid'].nunique()

def countFindableTrueTrackletsAndSSMIDs(dataframe, minDetections, vmax):
    findableTrueTracklets = 0
    
    possible_ssmids = dataframe.groupby("ssmid").filter(lambda x: len(x) >= minDetections)
    unique_ssmids = possible_ssmids['ssmid'].unique()
    findable_ssmids = []
    
    for unique_ssmid in unique_ssmids:
        detections = possible_ssmids[possible_ssmids["ssmid"] == unique_ssmid]
        detections.sort(columns="mjd")

        start_mjd = min(detections['mjd'])
        end_mjd = max(detections['mjd'])

        dt = end_mjd - start_mjd
        max_distance = dt*vmax

        total_distance = 0.0
        total_time = 0.0

        for det0, det1 in zip(detections.iloc[:-1].itertuples(), detections.iloc[1:].itertuples()):
            total_distance += calcGreatCircleDistance(det0[3], det0[4], det1[3], det1[4])

        if max_distance > total_distance:
             findableTrueTracklets += 1
             findable_ssmids.append(unique_ssmid)
                
    return findableTrueTracklets, findable_ssmids

def countFindableTrueTracks(dataframe, minDetectionsPerNight, minNights):
    findableTracks = 0
    
    possible_ssmids = dataframe.groupby("ssmid").filter(lambda x: len(x) >= minDetectionsPerNight*minNights)
    unique_ssmids = possible_ssmids['ssmid'].unique()
    findable_ssmids = []
    
    for unique_ssmid in unique_ssmids:
        detections = possible_ssmids[possible_ssmids["ssmid"] == unique_ssmid]
        unique, counts = np.unique(detections.sort(columns="mjd")['mjd'].unique().astype(int), return_counts=True)
        if len(counts[counts >= minDetectionsPerNight]) >= minNights:
            findableTracks += 1
            findable_ssmids.append(unique_ssmid)

    return findableTracks, findable_ssmids

def countFindableObjects(dataframe, minDetectionsPerNight=2, minNights=3, windowSize=15, snrLimit=-1):
    unique_ssmids = dataframe['ssmid'].unique()
    findable_ssmids = []
    
    discoverMet = moMetrics.DiscoveryChancesMetric(nObsPerNight=minDetectionsPerNight, tNight=90./60./24., nNightsPerWindow=minNights, tWindow=windowSize, snrLimit=snrLimit)
    
    for unique_ssmid in unique_ssmids:
        detections = dataframe[dataframe["ssmid"] == unique_ssmid]
        
        new_ssobject = np.zeros(len(detections), 
            dtype={'names':['night', 'expMJD','SNR'], 
                   'formats':['>i4','>i4','float64']})
        
        new_ssobject['night'] = calcNight(detections['mjd'].values)
        new_ssobject['expMJD'] = detections['mjd'].values
        new_ssobject['SNR'] = detections['snr'].values
        
        discoveryChances = discoverMet.run(new_ssobject, 0, 0)
        if discoveryChances >= 1:
            findable_ssmids.append(unique_ssmid)
       
    return findable_ssmids

def makeContiguous(angles):
    a0 = angles[0]
    output = [a0]
    for angle in angles[1:]:
        while abs(angle - a0) > 180:
            if angle > a0:
                angle -= 360.
            else:
                angle += 360.
        output.append(angle)
    return output

def convertToStandardDegrees(angle):
    while angle > 360.:
        angle -= 360.
    while angle < 0.:
        angle += 360.
    return angle

def calcNight(mjd, midnight=LSST_MIDNIGHT):
    """Determine night number for any MJD."""
    night = mjd + 0.5 - midnight
    return night.astype(int)

def calcDegToRad(angle):
    return angle*(np.pi/180.0)

def calcRadToDeg(angle):
    return angle*(180.0/np.pi)

def calcAngularDistance(a, b):
    while abs(a - b) > 180:
        if a > b:
            b += 360.
        else:
            a += 360.
    return a - b

def calcGreatCircleDistance(ra0, dec0, ra1, dec1):
    ra_dist = calcAngularDistance(ra0, ra1);
    dec_dist = calcAngularDistance(dec0, dec1);    
    # Convert all factors to radians
    ra_dist = calcDegToRad(convertToStandardDegrees(ra_dist));
    dec_dist = calcDegToRad(convertToStandardDegrees(dec_dist));
    dec0 = calcDegToRad(convertToStandardDegrees(dec0));
    dec1 = calcDegToRad(convertToStandardDegrees(dec1));
    r = 2*np.arcsin(np.sqrt((np.sin(dec_dist/2.))**2 + np.cos(dec0)*np.cos(dec1)*(np.sin(ra_dist/2))**2));
    # Back to degrees
    return calcRadToDeg(r);
    
def calcRMS(diasources):
    t0 = min(map(lambda x: x.mjd, diasources))
    ras = []
    decs = []
    mjds = []
    for diasource in diasources:
        ras.append(diasource.ra)
        decs.append(diasource.dec)
        mjds.append(diasource.mjd - t0)
    ras = makeContiguous(ras)
    decs = makeContiguous(decs)
    ras = np.array(ras)
    decs = np.array(decs)
    mjds = np.array(mjds)

    raFunc, raRes, rank, svd, rcond = np.polyfit(mjds, ras, 2, full=True)
    decFunc, decRes, rank, svd, rcond = np.polyfit(mjds, decs, 2, full=True)
    raFunc = np.poly1d(raFunc)
    decFunc = np.poly1d(decFunc)

    #now get the euclidean distance between predicted and observed for each point
    netSqDist = 0.0
    dists = []
    for i in range(len(mjds)):
        predRa = raFunc(mjds[i])
        predDec = decFunc(mjds[i])
        dist = calcGreatCircleDistance(predRa, predDec, ras[i], decs[i])
        dists.append(dist)
        if (dist > .1):
            print "Unexpected wierdness, diasource had angular distance of %f from best-fit curve prediction" % (dist)
            print "Predicted RA, Dec were ", predRa, predDec
            print "observed RA, Dec were ", ras[i], decs[i]
            print "all RAs were ", ras
            print "all decs were ", decs
        sqDist = dist**2
        #print "got euclidean distance was ", sqDist
        netSqDist += sqDist

    rms = np.sqrt(netSqDist / len(diasources))
    if (rms > .1):
        print "RMS error was %f " % (rms)
    return rms, raRes[0], decRes[0], dists

def _buildTracklet(dataframe, diaids, ssmidDict):
    new_tracklet = tracklet(len(diaids))

    for i, diaid in enumerate(diaids):
        diasource = dataframe.loc[diaid]
        new_tracklet.diasources[i]['diaid'] = int(diaid)
        new_tracklet.diasources[i]['obshistid'] = diasource['obshistid']
        new_tracklet.diasources[i]['ssmid'] = diasource['ssmid']
        new_tracklet.diasources[i]['ra'] = diasource['ra']
        new_tracklet.diasources[i]['dec'] = diasource['dec']
        new_tracklet.diasources[i]['mjd'] = diasource['mjd']
        new_tracklet.diasources[i]['mag'] = diasource['mag']
        new_tracklet.diasources[i]['snr'] = diasource['snr']
        
        if diasource['ssmid'] in ssmidDict:
            ssmidDict[diasource['ssmid']] += 1
        else:
            ssmidDict[diasource['ssmid']] = 1

    new_tracklet.isTrue = checkSSMIDs(new_tracklet.diasources['ssmid'])

    return new_tracklet


def _buildTrack(dataframe, diaids, ssmidDict, calcRMS=False):
    new_track = track(len(diaids))

    for i, diaid in enumerate(diaids):
        diasource = dataframe.loc[diaid]
        new_track.diasources[i]['diaid'] = int(diaid)
        new_track.diasources[i]['obshistid'] = diasource['obshistid']
        new_track.diasources[i]['ssmid'] = diasource['ssmid']
        new_track.diasources[i]['ra'] = diasource['ra']
        new_track.diasources[i]['dec'] = diasource['dec']
        new_track.diasources[i]['mjd'] = diasource['mjd']
        new_track.diasources[i]['mag'] = diasource['mag']
        new_track.diasources[i]['snr'] = diasource['snr']
        
        if diasource['ssmid'] in ssmidDict:
            ssmidDict[diasource['ssmid']] += 1
        else:
            ssmidDict[diasource['ssmid']] = 1

    new_track.isTrue = checkSSMIDs(new_track.diasources['ssmid'])

    if calcRMS:
        new_track.rms, new_track.raRes, new_track.decRes, new_track.distances = calcRMS(new_track.diasources)

    return new_track

def analyzeTracklets(trackletFile, detFile, vmax=0.5, ssmidsOfInterest=None):
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
    outFileOut.write("Unique objects: %s\n" % (dets_df['ssmid'].nunique()))

    # Count number of true tracklets and findable SSMIDs in dataframe
    print "Counting findable true tracklets..."
    findable_true_tracklets_num, findable_ssmids = countFindableTrueTrackletsAndSSMIDs(dets_df, 2.0, vmax)
    outFileOut.write("Findable objects: %s\n" % (len(findable_ssmids)))
    outFileOut.write("Findable true tracklets: %s\n\n" % (findable_true_tracklets_num))
    
    trackletFileIn = open(trackletFile, "r")
    tracklets = []
    interested_tracklets = {}
    ssmid_dict = {}
    
    # Initalize success (or failure) counters
    total_tracklets_num = 0
    true_tracklets_num = 0
    false_tracklets_num = 0

    # Initialize tracklet arrays
    true_tracklets = []
    false_tracklets = []

    # Examine each line in trackletFile and read in every line
    #  as a track object. If track contains new detections (diasource)
    #  then add new source to diasource_dict. 
    print "Building tracklets from tracklet file..."
    for line in trackletFileIn:
        # Found a track!
        total_tracklets_num += 1
        new_tracklet_diaids = MopsReader.readTracklet(line)
        new_tracklet = _buildTracklet(dets_df, new_tracklet_diaids, ssmid_dict)

        interested, ssmid = checkIfInterested(new_tracklet.diasources['ssmid'], ssmidsOfInterest)
        if interested:
            if ssmid in interested_tracklets:
                interested_tracklets[ssmid].append(new_tracklet)
            else:
                interested_tracklets[ssmid] = []
                interested_tracklets[ssmid].append(new_tracklet)

        if new_tracklet.isTrue:
            true_tracklets_num += 1
            true_tracklets.append(new_tracklet)
        else: 
            false_tracklets_num += 1
            false_tracklets.append(new_tracklet)
        
    endTime = time.ctime()

    outFileOut.write("Output Tracklet File Summary:\n")
    outFileOut.write("File size (bytes): %s\n" % (trackletFileSize))
    outFileOut.write("Unique objects found: %s\n" % (len(ssmid_dict)))
    outFileOut.write("True tracklets found: %s\n" % (true_tracklets_num))
    outFileOut.write("False tracklets found: %s\n" % (false_tracklets_num))
    outFileOut.write("Total tracklets found: %s\n\n" % (total_tracklets_num))
    outFileOut.write("End time: %s\n" % (endTime))

    print "Finished analysis for %s at %s" % (os.path.basename(trackletFile), endTime)

    return true_tracklets, false_tracklets, true_tracklets_num, false_tracklets_num, total_tracklets_num, interested_tracklets, detFileSize, trackletFileSize

def analyzeTracks(trackFile, detFile, idsFile, minDetectionsPerNight=2, minNights=3, windowSize=15, snrLimit=-1, ssmidsOfInterest=None, analyzeSubsets=False, verbose=True):
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
    outFileOut.write("Unique objects: %s\n" % (dets_df['ssmid'].nunique()))

    # Count number of true tracks and findable SSMIDs in dataframe
    print "Counting findable objects..."
    findable_ssmids = countFindableObjects(dets_df, minDetectionsPerNight=minDetectionsPerNight, minNights=minNights, windowSize=windowSize, snrLimit=snrLimit)
    outFileOut.write("Findable objects: %s\n\n" % (len(findable_ssmids)))
    
    trackFileIn = open(trackFile, "r")
    tracks = []
    interested_tracks = {}
    ssmid_dict = {}
    found_ssmids = []
    
    # Initalize success (or failure) counters
    total_tracks_num = 0
    true_tracks_num = 0
    false_tracks_num = 0

    # Initialize track arrays
    false_tracks = []
    true_tracks = []
    tracks = []
    subset_tracks = []
    longest_tracks = []

    # Examine each line in trackFile and read in every line
    #  as a track object. If track contains new detections (diasource)
    #  then add new source to diasource_dict. 
    print "Building tracks from track file..."
    for line in trackFileIn:
        # Found a track!
        total_tracks_num += 1
        new_track_diaids = MopsReader.readTrack(line)
        new_track = _buildTrack(dets_df, new_track_diaids, ssmid_dict)

        interested, ssmid = checkIfInterested(new_track.diasources['ssmid'], ssmidsOfInterest)
        if interested:
            if ssmid in interested_tracks:
                interested_tracks[ssmid].append(new_track)
            else:
                interested_tracks[ssmid] = []
                interested_tracks[ssmid].append(new_track)
                 
        if new_track.isTrue:
            # Track is true! 
            true_tracks_num += 1
            true_tracks.append(new_track)
            if new_track.diasources['ssmid'][0] not in found_ssmids:
                found_ssmids.append(new_track.diasources['ssmid'][0])
        else:
            # Track is false. 
            false_tracks_num += 1
            false_tracks.append(new_track)

        tracks.append(new_track)
    
    longest_tracks = []
    subset_tracks = []
    if analyzeSubsets:
        print "Counting subset tracks..."    
        longest_tracks, subset_tracks = checkSubsets(tracks)

    endTime = time.ctime()

    outFileOut.write("Output Track File Summary:\n")
    outFileOut.write("File size (bytes): %s\n" % (trackFileSize))
    outFileOut.write("Objects found: %s\n" % (len(found_ssmids)))
    outFileOut.write("True tracks found: %s\n" % (true_tracks_num))
    outFileOut.write("False tracks found: %s\n" % (false_tracks_num))
    outFileOut.write("Total tracks found: %s\n" % (total_tracks_num))
    outFileOut.write("Subset tracks found: %s\n" % (len(subset_tracks)))
    outFileOut.write("Non-subset tracks found: %s\n\n" % (len(longest_tracks)))
    outFileOut.write("End time: %s\n" % (endTime))

    print "Finished analysis for %s at %s" % (os.path.basename(trackFile), endTime)
   
    return true_tracks, false_tracks, true_tracks_num, false_tracks_num, total_tracks_num, len(subset_tracks), len(longest_tracks), interested_tracks, dets_df['ssmid'].nunique(), len(findable_ssmids), len(found_ssmids), detFileSize, idsFileSize, trackFileSize
