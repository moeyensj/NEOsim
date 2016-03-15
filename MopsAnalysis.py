import os
import time
import yaml
import shutil
import difflib
import numpy as np
import pandas as pd

import moMetrics
import MopsPlotter
import MopsReader
import MopsDatabase
from MopsObjects import tracklet
from MopsObjects import track
from MopsParameters import MopsParameters
from MopsTracker import MopsTracker
from MopsResults import MopsResults

LSST_MIDNIGHT = 0.166

def calcNight(mjd, midnight=LSST_MIDNIGHT):
    """Determine night number for any MJD."""
    night = mjd + 0.5 - midnight
    return night.astype(int)

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
 
def countUniqueObjects(dataframe):
    return dataframe["ssmId"].nunique()

def countMissedObjects(foundSSMIDs, findableSSMIDs):
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

def analyzeTracklets(trackletFile, detFile, outDir="results/", cursor=None, collapsedTrackletFile=None, purifiedTrackletFile=None, removeSubsetTrackletFile=None, trackletIdCountStart=1,  resultsObject=None):
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
    detections_num = len(dets_df.index)
    unique_ssmids = dets_df["ssmId"].nunique()
    
    # Count number of true tracklets and findable SSMIDs in dataframe
    print "- Counting findable objects..."
    findable_ssmids = countFindableObjects(dets_df, minDetectionsPerNight=2, minNights=1, windowSize=1, snrLimit=-1)
    
    if resultsObject is not None:
        print "- Updating results object..."
        resultsObject.nights.append(night)
        resultsObject.nightlyDetections[night] = detections_num
        resultsObject.nightlyDetectionFileSizes[night] = det_file_size
        resultsObject.toYaml(outDir=outDir)
    
    # Write detection file properties to outfile
    print "- Writing detection file summary to outfile..."
    print ""
    outFileOut.write("Input Detection File Summary:\n")
    outFileOut.write("File name: %s\n" % (detFile))
    outFileOut.write("File size (bytes): %s\n" % (det_file_size))
    outFileOut.write("Detections: %s\n" % (detections_num))
    outFileOut.write("Unique objects: %s\n" % (unique_ssmids))
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
    if len(tracklet_ids) >= 1:
        start_tracklet_id = max(tracklet_ids) + 1
    else:
        start_tracklet_id = 1
    
    if resultsObject is not None:
        print "- Updating results object..."
        resultsObject.totalTracklets[night] = total_tracklets_num
        resultsObject.trueTracklets[night] = true_tracklets_num
        resultsObject.falseTracklets[night] = false_tracklets_num
        resultsObject.trackletFileSizes[night] = tracklet_file_size
        resultsObject.toYaml(outDir=outDir)

    print "- Writing results to outfile..."
    outFileOut.write("Output Tracklet File Summary:\n")
    outFileOut.write("File name: %s\n" % (trackletFile))
    outFileOut.write("File size (bytes): %s\n" % (tracklet_file_size))
    outFileOut.write("Unique objects: %s\n" % (len(ssmid_dict)))
    outFileOut.write("True tracklets: %s\n" % (true_tracklets_num))
    outFileOut.write("False tracklets: %s\n" % (false_tracklets_num))
    outFileOut.write("Total tracklets: %s\n\n" % (total_tracklets_num))
        
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
        if len(tracklet_ids) >= 1:
            start_tracklet_id = max(tracklet_ids) + 1
        else:
            start_tracklet_id = 1
        
        if resultsObject is not None:
            print "- Updating results object..."
            resultsObject.totalCollapsedTracklets[night] = total_collapsed_tracklets_num
            resultsObject.trueCollapsedTracklets[night] = true_collapsed_tracklets_num
            resultsObject.falseCollapsedTracklets[night] = false_collapsed_tracklets_num
            resultsObject.collapsedTrackletFileSizes[night] = collapsed_tracklet_file_size
            resultsObject.toYaml(outDir=outDir)
            
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
        if len(tracklet_ids) >= 1:
            start_tracklet_id = max(tracklet_ids) + 1
        else:
            start_tracklet_id = 1
        
        if resultsObject is not None:
            print "- Updating results object..."
            resultsObject.totalPurifiedTracklets[night] = total_purified_tracklets_num
            resultsObject.truePurifiedTracklets[night] = true_purified_tracklets_num
            resultsObject.falsePurifiedTracklets[night] = false_purified_tracklets_num
            resultsObject.purifiedTrackletFileSizes[night] = purified_tracklet_file_size
            resultsObject.toYaml(outDir=outDir)

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
        if len(tracklet_ids) >= 1:
            start_tracklet_id = max(tracklet_ids) + 1
        else:
            start_tracklet_id = 1
        
        if resultsObject is not None:
            print "- Updating results object..."
            resultsObject.totalFinalTracklets[night] = total_final_tracklets_num
            resultsObject.trueFinalTracklets[night] = true_final_tracklets_num
            resultsObject.falseFinalTracklets[night] = false_final_tracklets_num
            resultsObject.finalTrackletFileSizes[night] = remove_subset_tracklet_file_size
            resultsObject.toYaml(outDir=outDir)

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

def analyzeTracks(trackFile, detFile, idsFile, outDir="results/", cursor=None, removeSubsetTrackFile=None, minDetectionsPerNight=2, minNights=3, windowSize=15, 
    snrLimit=-1, analyzeSubsets=True, trackIdCountStart=1, resultsObject=None):
    startTime = time.ctime()
    startNight, endNight = MopsReader.readWindow(detFile)
    window = str(startNight) + "-" + str(endNight)
    print "Starting track analysis for window (nights: %s - %s) at %s" % (str(startNight), str(endNight), startTime)
    
    # Create outfile to store results
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    outFile = os.path.join(os.path.abspath(outDir), "", window + ".results")
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
    detections_num = len(dets_df.index)
    unique_ssmids = dets_df["ssmId"].nunique()

    # Count number of true tracks and findable SSMIDs in dataframe
    print "- Counting findable objects..."
    findable_ssmids = countFindableObjects(dets_df, minDetectionsPerNight=minDetectionsPerNight, minNights=minNights, windowSize=windowSize, snrLimit=snrLimit)

    if resultsObject is not None:
        print "- Updating results object..."
        resultsObject.windows.append(window)
        resultsObject.windowDetections[window] = detections_num
        resultsObject.windowDetectionFileSizes[window] = det_file_size
        resultsObject.trackIdFileSizes[window] = ids_file_size
        resultsObject.trackFileSizes[window] = track_file_size
        resultsObject.toYaml(outDir=outDir)

    # Write detection file properties to outfile
    print "- Writing detection file summary to outfile..."
    print ""
    outFileOut.write("Input Detection File Summary:\n")
    outFileOut.write("File name: %s\n" % (detFile))
    outFileOut.write("File size (bytes): %s\n" % (det_file_size))
    outFileOut.write("Detections: %s\n" % (detections_num))
    outFileOut.write("Unique objects: %s\n" % (unique_ssmids))
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
        track_id = trackIdCountStart + i 
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

    if len(track_ids) >= 1:
        start_track_id = max(track_ids) + 1
    else:
        start_track_id = 1

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
    missed_ssmids = countMissedObjects(found_ssmids, findable_ssmids)

    print "- Calculating performance..."
    if len(findable_ssmids) != 0:
        performance_ratio = float(len(found_ssmids))/len(findable_ssmids)
    else:
        performance_ratio = 0.0

    if resultsObject is not None:
        print "- Updating results object..."
        resultsObject.uniqueObjects[window] = unique_ssmids
        resultsObject.findableObjects[window] = len(findable_ssmids)
        resultsObject.foundObjects[window] = len(found_ssmids)
        resultsObject.missedObjects[window] = len(missed_ssmids)
        resultsObject.performanceRatio[window] = performance_ratio

        resultsObject.totalTracks[window] = total_tracks_num
        resultsObject.trueTracks[window] = true_tracks_num
        resultsObject.falseTracks[window] = false_tracks_num
        resultsObject.subsetTracks[window] = subset_tracks_num
        resultsObject.longestTracks[window] = longest_tracks_num
        resultsObject.toYaml(outDir=outDir)


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

        if resultsObject is not None:
            print "- Updating results object..."
            resultsObject.totalFinalTracks[window] = total_final_tracks_num
            resultsObject.trueFinalTracks[window] = true_final_tracks_num
            resultsObject.falseFinalTracks[window] = false_final_tracks_num
            resultsObject.finalTrackFileSizes[window] = final_track_file_size
            resultsObject.toYaml(outDir=outDir)

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

def analyzeMultipleTracklets(trackletFiles, detFiles, outDir="results/", collapsedTrackletFiles=None, purifiedTrackletFiles=None, removeSubsetTrackletFiles=None,
                            toDatabase=True, fullDetFile=None, resultsObject=None):
    
    if toDatabase:
        cursor, database = MopsDatabase.buildTrackletDatabase("nightly.db", outDir)

        if fullDetFile is not None:
            print "Reading detections into database..."
            MopsReader.readDetectionsIntoDatabase(fullDetFile, cursor)
    else:
        database = None
        cursor = None

    resultFiles = []
    tracklet_id_start_count = 1
    all_tracklet_ids = []
    for i, (trackletFile, detFile) in enumerate(zip(trackletFiles, detFiles)):
        kwargs = {"collapsedTrackletFile": None, "purifiedTrackletFile": None, "removeSubsetTrackletFile": None}

        if collapsedTrackletFiles is not None:
            kwargs["collapsedTrackletFile"] = collapsedTrackletFiles[i]

        if purifiedTrackletFiles is not None:
            kwargs["purifiedTrackletFile"] = purifiedTrackletFiles[i]

        if removeSubsetTrackletFiles is not None:
            kwargs["removeSubsetTrackletFile"] = removeSubsetTrackletFiles[i]

        resultFile, allTrackletsDataframe, trackletMembersDataframe, tracklet_ids = analyzeTracklets(trackletFile, detFile, 
            outDir=outDir, trackletIdCountStart=tracklet_id_start_count, cursor=cursor, resultsObject=resultsObject, **kwargs)

        resultFiles.append(resultFile)
        all_tracklet_ids.extend(tracklet_ids)

        if len(all_tracklet_ids) >= 1:
            tracklet_id_start_count = max(all_tracklet_ids) + 1
        else: 
            tracklet_id_start_count = 1

    return sorted(resultFiles), database

def analyzeMultipleTracks(trackFiles, detFiles, idsFiles, outDir="results/", removeSubsetTrackFiles=None,
                            toDatabase=True, resultsObject=None, minDetectionsPerNight=2, minNights=3, windowSize=15):

    databases = []
    resultFiles = []
    track_id_start_count = 1
    all_track_ids = []

    for i, (trackFile, detFile, idsFile) in enumerate(zip(trackFiles, detFiles, idsFiles)):
        if toDatabase:
            startNight, endNight = MopsReader.readWindow(detFile)
            windowDatabase = str(startNight) + "-" + str(endNight) + ".db"
            cursor, database = MopsDatabase.buildTrackDatabase(windowDatabase, outDir)
        else:
            cursor = None

        kwargs = {"removeSubsetTrackFile": None}

        if removeSubsetTrackFiles is not None:
            kwargs["removeSubsetTrackFile"] = removeSubsetTrackFiles[i]

        resultFile, allTracksDataframe, trackMembersDataframe, track_ids = analyzeTracks(trackFile, detFile, idsFile,
            outDir=outDir, trackIdCountStart=track_id_start_count, cursor=cursor, resultsObject=resultsObject, 
            minDetectionsPerNight=minDetectionsPerNight, minNights=minNights, windowSize=windowSize, snrLimit=-1, analyzeSubsets=True, **kwargs)
       
        if toDatabase:
            databases.append(database)

        resultFiles.append(resultFile)
        all_track_ids.extend(track_ids)

        if len(all_track_ids) >= 1:
            track_id_start_count = max(all_track_ids) + 1
        else:
            track_id_start_count = 1

    return sorted(resultFiles), sorted(databases)

def analyze(parameters, tracker, outDir="", tracklets=True, tracks=True, toDatabase=True, resultsObject=None,
            minDetectionsPerNight=2, minNights=3, windowSize=15, fullDetFile=None, overwrite=False):

    outDir = os.path.join(tracker.runDir, "results")
    tracker.resultsDir = outDir
    if os.path.exists(outDir):
        if overwrite:
            shutil.rmtree(outDir)
            os.mkdir(outDir)
            print "Overwrite triggered: deleting existing results directory..."
            print ""
        else:
            raise NameError("Results directory exists! Cannot continue!")
    else:
        os.mkdir(outDir)

    if resultsObject is None:
        print "Initializing new results object..."
        resultsObject = MopsResults(parameters, tracker)

    if tracklets:

        resultFiles, database = analyzeMultipleTracklets(tracker.tracklets, tracker.diasources, outDir=outDir, 
            collapsedTrackletFiles=tracker.collapsedTrackletsById, purifiedTrackletFiles=tracker.purifiedTrackletsById,
            removeSubsetTrackletFiles=tracker.finalTrackletsById, toDatabase=toDatabase, fullDetFile=fullDetFile, 
            resultsObject=resultsObject)

        tracker.trackletResults = resultFiles
        tracker.trackletDatabase = database
        tracker.toYaml(outDir=tracker.runDir)
        tracker.toYaml(outDir=tracker.resultsDir)

    resultsObject.toYaml(outDir=tracker.runDir)
    resultsObject.toYaml(outDir=tracker.resultsDir)

    if tracks:

        resultFiles, databases = analyzeMultipleTracks(tracker.tracks, tracker.dets, tracker.ids, outDir=outDir, 
          removeSubsetTrackFiles=tracker.finalTracks, toDatabase=toDatabase, resultsObject=resultsObject, 
          minDetectionsPerNight=minDetectionsPerNight, minNights=minNights, windowSize=windowSize)

        tracker.trackResults = resultFiles
        tracker.trackDatabases = databases
        tracker.toYaml(outDir=tracker.runDir)
        tracker.toYaml(outDir=tracker.resultsDir)

    resultsObject.toYaml(outDir=tracker.runDir)
    resultsObject.toYaml(outDir=tracker.resultsDir)

    return resultsObject

