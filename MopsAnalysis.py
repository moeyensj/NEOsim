import os
import time
import yaml
import random
import difflib
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

    # Instance Methods

    def findNights(self):
        for detFile in self.tracker.diasources:
            self._nights.append(MopsReader.readNight(detFile))

    def findWindows(self):
        for trackFile in self.tracker.tracks:
            self._windows.append(MopsReader.readWindow(trackFile))

    def analyze(self, tracklets=True, collapsedTracklets=True, purifiedTracklets=True, finalTracklets=True, tracks=True, finalTracks=True, analyzeSubsets=True):

        self._startTime = time.ctime()
        # to be upgraded
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

def findNewLinesAndDeletedIndices(file1, file2):
    file1In = open(file1, "r")
    file2In = open(file2, "r")
    
    # Here we use unified_diff. Unfortunately, at this stage ndiff would be more informative with
    #  regards to index tracking however it is dreadfully slow with big files due to a series 
    #  of internal nested for loops. We set context lines = 1 so as to use them to rematch
    #  the file one index relative to the delta created by unified_diff.
    udiff = list(difflib.unified_diff(file1In.readlines(), file2In.readlines(), n=1))
    
    new_lines = []
    deleted_linenums = []
    
    file1_index = -1
    for i, line in enumerate(udiff[3:]):
        if line[0] == " ":
            # This is a context line. Scan file one for this
            #  line and then re-establish file one index. 
            #  This is necessary since we are not using ndiff.
            for j, l1 in enumerate(open(file1, "r")):
                if l1[:-2] == line[1:-2]:
                    file1_index = j
        else:
            if line[0] == "+":
                # This line only exists in file two. 
                # Lets add this line to a list of newly 
                #  created lines. We will build linkages later.
                new_lines.append(line[1:-2])
            elif line[0] == "-":
                # This line only exists in file one.
                # Lets append the index to our list of deleted
                #  line numbers.
                file1_index += 1
                deleted_linenums.append(file1_index)
            
    return new_lines, deleted_linenums

def checkSubsets(tracks):
    # for each track in tracks, check subsets, if subset remove from array and add to subset array
    # remaining tracks are the longest tracks
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
                        test_track.subsetOf = comparison_track.trackId
                        test_track.updateInfo()
                        subset_tracks_num += 1
                        break

    for test_track in tracks:
        if test_track.isSubset == None:
            test_track.isSubset = False
            longest_tracks_num += 1

    return longest_tracks_num, subset_tracks_num, tracks
 
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
                   "formats":["int64","int64","float64"]})
        
        new_ssobject["night"] = calcNight(detections["mjd"].values)
        new_ssobject["expMJD"] = detections["mjd"].values
        new_ssobject["SNR"] = detections["snr"].values
        
        discoveryChances = discoverMet.run(new_ssobject, 0, 0)
        if discoveryChances >= 1:
            findable_ssmids.append(unique_ssmid)
       
    return findable_ssmids

def _buildTracklet(dataframe, trackletId, diaids, night, ssmidDict, createdBy=1, calcRMS=True):
    new_tracklet = tracklet(trackletId, len(diaids), night)

    for i, diaid in enumerate(diaids):
        diasource = dataframe.loc[diaid]
        new_tracklet.addDiasource(i, diaid, diasource)
        new_tracklet.createdBy = createdBy
        
        if diasource["ssmId"] in ssmidDict:
            ssmidDict[diasource["ssmId"]] += 1
        else:
            ssmidDict[diasource["ssmId"]] = 1
    
    if calcRMS:
        new_tracklet.updateRMS()
        
    new_tracklet.updateVelocity()
    new_tracklet.updateQuality()
    new_tracklet.updateMembers()
    new_tracklet.updateInfo()
    
    return new_tracklet

def _buildTrack(dataframe, trackId, diaids, window, ssmidDict, createdBy=5, calcRMS=True):
    new_track = track(trackId, len(diaids), window)

    for i, diaid in enumerate(diaids):
        diasource = dataframe.loc[diaid]
        new_track.addDiasource(i, diaid, diasource)
        new_track.createdBy = createdBy
        
        if diasource["ssmId"] in ssmidDict:
            ssmidDict[diasource["ssmId"]] += 1
        else:
            ssmidDict[diasource["ssmId"]] = 1
    
    if calcRMS:
        new_track.updateRMS()
    
    new_track.updateTime()
    new_track.updateQuality()
    new_track.updateMembers()
    new_track.updateInfo()
    
    return new_track

def analyzeTracklets(trackletFile, detFile, outDir, cursor=None, collapsedTrackletFile=None, purifiedTrackletFile=None, removeSubsetTrackletFile=None, analysisObject=None, trackletIdCountStart=1):
    startTime = time.ctime()
    night = MopsReader.readNight(detFile)
    print "Starting tracklet analysis for night %s at %s" % (night, startTime)
    
    # Create outfile to store results
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    outFile = os.path.join(os.path.abspath(outDir), "", str(night) + ".results")
    outFileOut = open(outFile, "w", 0)
    outFileOut.write("Start time: %s\n\n" % (startTime))
    print "- Writing results to %s" % (outFile)

    # Get file sizes
    print "- Checking file sizes..."
    det_file_size = os.path.getsize(detFile)
    tracklet_file_size = os.path.getsize(trackletFile)
    if collapsedTrackletFile is not None:
        collapsed_tracklet_file_size = os.path.getsize(collapsedTrackletFile)
    if purifiedTrackletFile is not None:
        purified_tracklet_file_size = os.path.getsize(purifiedTrackletFile)
    if removeSubsetTrackletFile is not None:
        remove_subset_tracklet_file_size = os.path.getsize(removeSubsetTrackletFile)

    # Read detections into a dataframe
    print "- Reading input detections..."
    dets_df = MopsReader.readDetectionsIntoDataframe(detFile)
    
    # Count number of true tracklets and findable SSMIDs in dataframe
    print "- Counting findable objects..."
    findable_ssmids = countFindableObjects(dets_df, minDetectionsPerNight=2, minNights=1, windowSize=1, snrLimit=-1)
    
    if analysisObject is not None:
        print "- Updating analysis object..."
        analysisObject.nightlyDetectionFileSizes[night] = det_file_size
    
    # Write detection file properties to outfile
    print "- Writing detection file summary to outfile..."
    print ""
    outFileOut.write("Input Detection File Summary:\n")
    outFileOut.write("File name: %s\n" % (detFile))
    outFileOut.write("File size (bytes): %s\n" % (det_file_size))
    outFileOut.write("Detections: %s\n" % (len(dets_df.index)))
    outFileOut.write("Unique objects: %s\n" % (dets_df["ssmId"].nunique()))
    outFileOut.write("Findable objects: %s\n\n" % (len(findable_ssmids)))
    
    trackletFileIn = open(trackletFile, "r")
    ssmid_dict = {}
    
    # Initalize success (or failure) counters
    total_tracklets_num = 0
    true_tracklets_num = 0
    false_tracklets_num = 0
    tracklet_ids = []
    
    # Initialize tracklet dataframes
    print "Analyzing tracklet file..."
    print "- Building dataframes..."
    allTrackletsDataframe = pd.DataFrame(columns=["trackletId", "linkedObjectId", "numLinkedObjects", "numMembers", "velocity", "rms", "night", "createdBy", "deletedBy"])
    trackletMembersDataframe = pd.DataFrame(columns=["trackletId", "diaId"])
    
    # Examine each line in trackletFile and read in every line
    #  as a track object. If track contains new detections (diasource)
    #  then add new source to diasource_dict.
    print "- Building tracklets..."
    for i, line in enumerate(trackletFileIn):
        tracklet_id = trackletIdCountStart + i
        tracklet_ids.append(tracklet_id)
        
        new_tracklet_diaids = MopsReader.readTracklet(line)
        new_tracklet = _buildTracklet(dets_df, tracklet_id, new_tracklet_diaids, night, ssmid_dict, createdBy=1)

        total_tracklets_num += 1
        if new_tracklet.isTrue:
            true_tracklets_num += 1
        else: 
            false_tracklets_num += 1
            
        trackletMembersDataframe = trackletMembersDataframe.append(new_tracklet.toTrackletMembersDataframe())
        allTrackletsDataframe = allTrackletsDataframe.append(new_tracklet.toAllTrackletsDataframe())
        
    print "- Appended new tracklets to dataframes..."
        
    prev_start_tracklet_id = trackletIdCountStart
    start_tracklet_id = max(tracklet_ids) + 1

    print "- Writing results to outfile..."
    outFileOut.write("Output Tracklet File Summary:\n")
    outFileOut.write("File name: %s\n" % (trackletFile))
    outFileOut.write("File size (bytes): %s\n" % (tracklet_file_size))
    outFileOut.write("Unique objects: %s\n" % (len(ssmid_dict)))
    outFileOut.write("True tracklets: %s\n" % (true_tracklets_num))
    outFileOut.write("False tracklets: %s\n" % (false_tracklets_num))
    outFileOut.write("Total tracklets: %s\n\n" % (total_tracklets_num))
    
    if analysisObject is not None:
        print "- Updating analysis object..."
        
        analysisObject.totalTracklets[night] = total_tracklets_num
        analysisObject.trueTracklets[night] = true_tracklets_num
        analysisObject.falseTracklets[night] = false_tracklets_num
        analysisObject.trackletFileSizes[night] = tracklet_file_size
        
    print ""
    
    if collapsedTrackletFile is not None:
        print "Analyzing collapsed tracklets..."
        created_by_collapse, deleted_by_collapse_ind = findNewLinesAndDeletedIndices(trackletFile, collapsedTrackletFile)
        print "collapseTracklets merged %s tracklets into %s collinear tracklets..." % (len(deleted_by_collapse_ind), len(created_by_collapse))
        
        collapsed_ssmid_dict = {}
        
        total_collapsed_tracklets_num = 0
        true_collapsed_tracklets_num = 0
        false_collapsed_tracklets_num = 0
        
        print "- Updating dataframe properties..."
        for ind in deleted_by_collapse_ind:
            allTrackletsDataframe.loc[allTrackletsDataframe["trackletId"] == (ind + prev_start_tracklet_id), "deletedBy"] = 2
            
        print "- Building collapsed tracklets..."
        for i, line in enumerate(created_by_collapse):
            tracklet_id = start_tracklet_id + i
            tracklet_ids.append(tracklet_id) 
            
            new_tracklet_diaids = MopsReader.readTracklet(line)
            new_tracklet = _buildTracklet(dets_df, tracklet_id, new_tracklet_diaids, night, collapsed_ssmid_dict, createdBy=2)
            
            total_collapsed_tracklets_num += 1
            if new_tracklet.isTrue:
                true_collapsed_tracklets_num += 1
            else: 
                false_collapsed_tracklets_num += 1
                
            trackletMembersDataframe = trackletMembersDataframe.append(new_tracklet.toTrackletMembersDataframe())
            allTrackletsDataframe = allTrackletsDataframe.append(new_tracklet.toAllTrackletsDataframe())
            
        print "- Appended new tracklets to dataframes..."
        
        prev_start_tracklet_id = start_tracklet_id
        start_tracklet_id = max(tracklet_ids) + 1
        
        if analysisObject is not None:
            print "- Updating analysis object..."

            analysisObject.totalCollapsedTracklets[night] = total_collapsed_tracklets_num
            analysisObject.trueCollapsedTracklets[night] = true_collapsed_tracklets_num
            analysisObject.falseCollapsedTracklets[night] = false_collapsed_tracklets_num
            analysisObject.collapsedTrackletFileSizes[night] = collapsed_tracklet_file_size
            
        print "- Writing results to outfile..."
        outFileOut.write("Output Collapsed Tracklet File Summary:\n")
        outFileOut.write("File name: %s\n" % (collapsedTrackletFile))
        outFileOut.write("File size (bytes): %s\n" % (collapsed_tracklet_file_size))
        outFileOut.write("Unique objects: %s\n" % (len(collapsed_ssmid_dict)))
        outFileOut.write("Tracklets collapsed: %s\n" % len(deleted_by_collapse_ind))
        outFileOut.write("Tracklets created: %s\n" % len(created_by_collapse))
        outFileOut.write("True collapsed tracklets: %s\n" % (true_collapsed_tracklets_num))
        outFileOut.write("False collapsed tracklets: %s\n" % (false_collapsed_tracklets_num))
        outFileOut.write("Total collapsed tracklets: %s\n" % (total_collapsed_tracklets_num))
        outFileOut.write("*** Note: These numbers only reflect tracklets affected by collapseTracklets. ***\n")
        outFileOut.write("***            File may contain other unaffected tracklets.                   ***\n\n")
        print ""
        
    if purifiedTrackletFile is not None:
        print "Analyzing purified tracklets..."
        created_by_purified, deleted_by_purified_ind = findNewLinesAndDeletedIndices(collapsedTrackletFile, purifiedTrackletFile)
        print "purifiedTracklets removed detections from %s tracklets and created %s tracklets..." % (len(deleted_by_purified_ind), len(created_by_purified))
        
        purified_ssmid_dict = {}
        
        total_purified_tracklets_num = 0
        true_purified_tracklets_num = 0
        false_purified_tracklets_num = 0
        
        print "- Updating dataframe properties..."
        for ind in deleted_by_purified_ind:
            allTrackletsDataframe.loc[allTrackletsDataframe["trackletId"] == (ind + prev_start_tracklet_id), "deletedBy"] = 3
            
        print "- Building purified tracklets..."
        for i, line in enumerate(created_by_purified):
            tracklet_id = start_tracklet_id + i 
            tracklet_ids.append(tracklet_id) 
            
            new_tracklet_diaids = MopsReader.readTracklet(line)
            new_tracklet = _buildTracklet(dets_df, tracklet_id, new_tracklet_diaids, night, purified_ssmid_dict, createdBy=3)
            
            total_purified_tracklets_num += 1
            if new_tracklet.isTrue:
                true_purified_tracklets_num += 1
            else: 
                false_purified_tracklets_num += 1
                
            trackletMembersDataframe = trackletMembersDataframe.append(new_tracklet.toTrackletMembersDataframe())
            allTrackletsDataframe = allTrackletsDataframe.append(new_tracklet.toAllTrackletsDataframe())
            
        print "- Appended new tracklets to dataframes..."
           
        prev_start_tracklet_id = start_tracklet_id
        start_tracklet_id = max(tracklet_ids) + 1
        
        if analysisObject is not None:
            print "- Updating analysis object..."

            analysisObject.totalPurifiedTracklets[night] = total_purified_tracklets_num
            analysisObject.truePurifiedTracklets[night] = true_purified_tracklets_num
            analysisObject.falsePurifiedTracklets[night] = false_purified_tracklets_num
            analysisObject.purifiedTrackletFileSizes[night] = purified_tracklet_file_size

        print "- Writing results to outfile..."
        outFileOut.write("Output Purified Tracklet File Summary:\n")
        outFileOut.write("File name: %s\n" % (purifiedTrackletFile))
        outFileOut.write("File size (bytes): %s\n" % (purified_tracklet_file_size))
        outFileOut.write("Unique objects: %s\n" % (len(purified_ssmid_dict)))
        outFileOut.write("Tracklets purified: %s\n" % len(deleted_by_purified_ind))
        outFileOut.write("Tracklets created: %s\n" % len(created_by_purified))
        outFileOut.write("True purified tracklets: %s\n" % (true_purified_tracklets_num))
        outFileOut.write("False purified tracklets: %s\n" % (false_purified_tracklets_num))
        outFileOut.write("Total purified tracklets: %s\n" % (total_purified_tracklets_num))
        outFileOut.write("*** Note: These numbers only reflect tracklets affected by purifyTracklets. ***\n")
        outFileOut.write("***          File may contain other unaffected tracklets.                   ***\n\n")
        
        print ""

    if removeSubsetTrackletFile is not None:
        print "Analyzing final tracklets..."
        created_by_removeSubsets, deleted_by_removeSubsets_ind = findNewLinesAndDeletedIndices(purifiedTrackletFile, removeSubsetTrackletFile)
        print "removeSubsets removed %s tracklets..." % (len(deleted_by_removeSubsets_ind))
        
        final_ssmid_dict = {}
        
        total_final_tracklets_num = 0
        true_final_tracklets_num = 0
        false_final_tracklets_num = 0
        
        print "- Updating dataframe properties..."
        for ind in deleted_by_purified_ind:
            allTrackletsDataframe.loc[allTrackletsDataframe["trackletId"] == (ind + prev_start_tracklet_id), "deletedBy"] = 4
            
        print "- Building final tracklets..."
        for i, line in enumerate(created_by_removeSubsets):
            tracklet_id = start_tracklet_id + i 
            tracklet_ids.append(tracklet_id)
            
            new_tracklet_diaids = MopsReader.readTracklet(line)
            new_tracklet = _buildTracklet(dets_df, tracklet_id, new_tracklet_diaids, night, final_ssmid_dict, createdBy=4)
            
            total_final_tracklets_num += 1
            if new_tracklet.isTrue:
                true_final_tracklets_num += 1
            else: 
                false_final_tracklets_num += 1
                
            trackletMembersDataframe = trackletMembersDataframe.append(new_tracklet.toTrackletMembersDataframe())
            allTrackletsDataframe = allTrackletsDataframe.append(new_tracklet.toAllTrackletsDataframe())
            
        print "- Appended new tracklets to dataframes..."
        
        prev_start_tracklet_id = start_tracklet_id
        start_tracklet_id = max(tracklet_ids) + 1
        
        if analysisObject is not None:
            print "- Updating analysis object..."

            analysisObject.totalFinalTracklets[night] = total_final_tracklets_num
            analysisObject.trueFinalTracklets[night] = true_final_tracklets_num
            analysisObject.falseFinalTracklets[night] = false_final_tracklets_num
            analysisObject.finalTrackletFileSizes[night] = remove_subset_tracklet_file_size

        print "- Writing results to outfile..."
        outFileOut.write("Output Final Tracklet File Summary:\n")
        outFileOut.write("File name: %s\n" % (removeSubsetTrackletFile))
        outFileOut.write("File size (bytes): %s\n" % (remove_subset_tracklet_file_size))
        outFileOut.write("Unique objects: %s\n" % (len(final_ssmid_dict)))
        outFileOut.write("Tracklets removed: %s\n" % len(deleted_by_removeSubsets_ind))
        outFileOut.write("True final tracklets: %s\n" % (true_final_tracklets_num))
        outFileOut.write("False final tracklets: %s\n" % (false_final_tracklets_num))
        outFileOut.write("Total final tracklets: %s\n" % (total_final_tracklets_num))
        outFileOut.write("*** Note: These numbers only reflect tracklets affected by removeSubsets. ***\n")
        outFileOut.write("***          File may contain other unaffected tracklets.                 ***\n\n")
       
        print ""
        
    if cursor is not None:
        print "Converting dataframes to sqlite tables..."
        print "Updating TrackletMembers tables..."
        trackletMembersDataframe.to_sql("TrackletMembers", cursor, if_exists="append", index=False)
        print "Updating AllTracklets tables..."
        allTrackletsDataframe.to_sql("AllTracklets", cursor, if_exists="append", index=False)
        
        print ""
        
    endTime = time.ctime()
    outFileOut.write("End time: %s\n" % (endTime))
        
    print "Finished tracklet analysis for night %s at %s" % (night, endTime)
    print ""
    
    return outFile, allTrackletsDataframe, trackletMembersDataframe, tracklet_ids

def analyzeTracks(trackFile, detFile, idsFile, outDir, cursor=None, removeSubsetTrackFile=None, minDetectionsPerNight=2, minNights=3, windowSize=15, 
    snrLimit=-1, analyzeSubsets=True, analysisObject=None, verbose=True):
    startTime = time.ctime()
    startNight, endNight = MopsReader.readWindow(detFile)
    print "Starting track analysis for window (nights: %s - %s) at %s" % (str(startNight), str(endNight), startTime)
    
    # Create outfile to store results
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    window = str(startNight) + "-" + str(endNight)
    outFile = os.path.join(os.path.abspath(outDir), "", str(window) + ".results")
    outFileOut = open(outFile, "w", 0)
    outFileOut.write("Start time: %s\n\n" % (startTime))
    print "- Writing results to %s" % (outFile)

    print "- Checking file sizes..."
    ids_file_size = os.path.getsize(idsFile)
    det_file_size = os.path.getsize(detFile)
    track_file_size = os.path.getsize(trackFile)
    if removeSubsetTrackFile is not None:
        final_track_file_size = os.path.getsize(removeSubsetTrackFile)

    # Read ids file 
    print "- Counting number of input tracks..."
    track_num = 0
    for track in open(idsFile, "r"):
        track_num += 1

    outFileOut.write("Input Track (Ids) File Summary:\n")
    outFileOut.write("File name: %s\n" % (idsFile))
    outFileOut.write("File size (bytes): %s\n" % (ids_file_size))
    outFileOut.write("Tracks: %s\n\n" % (track_num))
    
    # Read detections into a dataframe
    print "- Reading input detections..."
    dets_df = MopsReader.readDetectionsIntoDataframe(detFile)

    # Count number of true tracks and findable SSMIDs in dataframe
    print "- Counting findable objects..."
    findable_ssmids = countFindableObjects(dets_df, minDetectionsPerNight=minDetectionsPerNight, minNights=minNights, windowSize=windowSize, snrLimit=snrLimit)

    if analysisObject is not None:
        print "- Updating analysis object..."
        analysisObject.windowDetectionFileSizes[night] = det_file_size

    # Write detection file properties to outfile
    print "- Writing detection file summary to outfile..."
    print ""
    outFileOut.write("Input Detection File Summary:\n")
    outFileOut.write("File name: %s\n" % (detFile))
    outFileOut.write("File size (bytes): %s\n" % (det_file_size))
    outFileOut.write("Detections: %s\n" % (len(dets_df.index)))
    outFileOut.write("Unique objects: %s\n" % (dets_df["ssmId"].nunique()))
    outFileOut.write("Findable objects: %s\n\n" % (len(findable_ssmids)))

    trackFileIn = open(trackFile, "r")
    tracks = []
    ssmid_dict = {}
    found_ssmids = []
    missed_ssmids = []
    
    # Initalize success (or failure) counters
    total_tracks_num = 0
    true_tracks_num = 0
    false_tracks_num = 0
    track_ids = []

    print "Analyzing track file..."
    print "- Building dataframes..."
    allTracksDataframe = pd.DataFrame(columns=["trackId", "linkedObjectId", "numLinkedObjects", "numMembers", "rms", "windowStart", "startTime", "endTime", "subsetOf", "createdBy", "deletedBy"])
    trackMembersDataframe = pd.DataFrame(columns=["trackId", "diaId"])

    # Examine each line in trackFile and read in every line
    #  as a track object. If track contains new detections (diasource)
    #  then add new source to diasource_dict. 
    print "- Building tracks..."
    for i, line in enumerate(trackFileIn):
        track_id = i + 1
        track_ids.append(track_id)
        
        new_track_diaids = MopsReader.readTrack(line)
        new_track = _buildTrack(dets_df, track_id, new_track_diaids, startNight, ssmid_dict, createdBy=5)

        total_tracks_num += 1     
        if new_track.isTrue:
            true_tracks_num += 1
            if new_track.diasources["ssmId"][0] not in found_ssmids:
                found_ssmids.append(new_track.diasources["ssmId"][0])
        else:
            false_tracks_num += 1

        tracks.append(new_track)

        trackMembersDataframe = trackMembersDataframe.append(new_track.toTrackMembersDataframe())
        allTracksDataframe = allTracksDataframe.append(new_track.toAllTracksDataframe())

    print "- Appended new tracks to dataframes..."

    start_track_id = max(track_ids) + 1
    
    longest_tracks_num = 0
    subset_tracks_num = 0
    if analyzeSubsets:
        print "- Counting subset tracks..."   
        longest_tracks_num, subset_tracks_num, tracks = checkSubsets(tracks)

        print "- Updating AllTracks dataframe..."   
        for track in tracks:
            if track.isSubset:
                allTracksDataframe.loc[allTracksDataframe["trackId"] == track.trackId, "subsetOf"] = track.subsetOf
            else:
                continue

    print "- Counting missed objects..."
    missed_ssmids = countMissedSSMIDs(found_ssmids, findable_ssmids)

    print "- Calculating performance..."
    if len(findable_ssmids) != 0:
        performance_ratio = float(len(found_ssmids))/len(findable_ssmids)
    else:
        performance_ratio = 0.0

    print "- Writing results to outfile..."
    outFileOut.write("Output Track File Summary:\n")
    outFileOut.write("File name: %s\n" % (trackFile))
    outFileOut.write("File size (bytes): %s\n" % (track_file_size))
    outFileOut.write("Objects found: %s\n" % (len(found_ssmids)))
    outFileOut.write("Objects missed: %s\n" % (len(missed_ssmids)))
    outFileOut.write("True tracks: %s\n" % (true_tracks_num))
    outFileOut.write("False tracks %s\n" % (false_tracks_num))
    outFileOut.write("Total tracks: %s\n" % (total_tracks_num))
    outFileOut.write("Subset tracks: %s\n" % (subset_tracks_num))
    outFileOut.write("Longest tracks: %s\n\n" % (longest_tracks_num))
    outFileOut.write("MOPs Performance Ratio (found/findable): %.5f\n\n" % (performance_ratio))

    print ""

    if removeSubsetTrackFile is not None:
        print "Analyzing final tracks..."
        created_by_removeSubsets, deleted_by_removeSubsets_ind = findNewLinesAndDeletedIndices(trackFile, removeSubsetTrackFile)
        print "removeSubsets removed %s tracks..." % (len(deleted_by_removeSubsets_ind))

        total_final_tracks_num = 0
        true_final_tracks_num = 0
        false_final_tracks_num = 0

        print "- Updating dataframe properties..."
        for ind in deleted_by_removeSubsets_ind:
            allTracksDataframe.loc[allTracksDataframe["trackId"] == ind + 1, "deletedBy"] = 6

        print "- Building final tracks..."
        for i, line in enumerate(created_by_removeSubsets):
            track_id = start_track_id + i
            track_ids.append(track_id)
            
            new_track_diaids = MopsReader.readTrack(line)
            new_track = _buildTrack(dets_df, track_id, new_track_diaids, windowStart, ssmid_dict, createdBy=5)

            total_final_tracks_num += 1     
            if new_track.isTrue:
                true_final_tracks_num += 1
            else:
                false_final_tracks_num += 1

            trackMembersDataframe = trackMembersDataframe.append(new_track.toTrackMembersDataframe())
            allTracksDataframe = allTracksDataframe.append(new_track.toAllTracksDataframe())

        print "- Appended new tracks to dataframes..."

        if analysisObject is not None:
            print "- Updating analysis object..."

            analysisObject.totalFinalTracks[night] = total_final_tracks_num
            analysisObject.trueFinalTracks[night] = true_final_tracks_num
            analysisObject.falseFinalTracks[night] = false_final_tracks_num
            analysisObject.finalTrackFileSizes[night] = final_track_file_size

        print "- Writing results to outfile..."
        outFileOut.write("Output Final Track File Summary:\n")
        outFileOut.write("File name: %s\n" % (removeSubsetTrackFile))
        outFileOut.write("File size (bytes): %s\n" % (final_track_file_size))
        outFileOut.write("True final tracks: %s\n" % (true_final_tracks_num))
        outFileOut.write("False final tracks %s\n" % (false_final_tracks_num))
        outFileOut.write("Total final tracks: %s\n" % (total_final_tracks_num))
        outFileOut.write("*** Note: These numbers only reflect tracks affected by removeSubsets. ***\n")
        outFileOut.write("***          File may contain other unaffected tracks.                 ***\n\n")
        print ""

    if cursor is not None:
        print "Converting dataframes to sqlite tables..."
        print "Updating TrackMembers tables..."
        trackMembersDataframe.to_sql("TrackMembers", cursor, if_exists="append", index=False)
        print "Updating AllTracks tables..."
        allTracksDataframe.to_sql("AllTracks", cursor, if_exists="append", index=False)
        
        print ""

    endTime = time.ctime()
    outFileOut.write("End time: %s\n" % (endTime))

    print "Finished track analysis for window (nights: %s - %s) at %s" % (str(startNight), str(endNight), endTime)
    print ""
    
    return outFile, allTracksDataframe, trackMembersDataframe, track_ids
