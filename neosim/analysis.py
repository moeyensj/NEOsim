import os
import time
import shutil
import difflib
import numpy as np
import pandas as pd

import lsst.sims.maf.metrics as metrics

import neosim.reader as reader
import neosim.database as database
from neosim.linkages import Tracklet
from neosim.linkages import Track
from neosim.parameters import Parameters
from neosim.tracker import Tracker
from neosim.results import Results

LSST_MIDNIGHT = 0.166

def calcNight(mjd, midnight=LSST_MIDNIGHT):
    """
    Calculate the integer night for any MJD.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    mjd: (float), MJD to convert
    midNight: (float) [LSST_MIDNIGHT], midnight at LSST site
    ----------------------
    """
    night = mjd + 0.5 - midnight
    return night.astype(int)

def findNewLinesAndDeletedIndices(file1, file2):
    """
    Find new lines and the indices of deleted lines between two files. Compares file one and 
    two, and return the new lines in file two and the indices of lines deleted in file one. 

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    file1: (str), path to file one
    file2: (str), path to file two
    ----------------------
    """
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
    """
    Count the number of tracks that are subsets of others and number of tracks that are not subsets.
    Will uupdate their isSubset attributes.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    tracks: (list of objects), list of MopsObjects tracks
    ----------------------
    """
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
    """
    Count number of unique objects in a Pandas dataframe.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    dataframe: (DataFrame), Pandas dataframe with objectId column
    ----------------------
    """
    # for each track in tracks, check subsets, if subset remove from array and add to subset array
    # remaining tracks are the longest tracks
    return dataframe["objectId"].nunique()

def countMissedObjects(foundObjects, findableObjects):
    """
    Return a list of missed objects

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    foundObjects: (list of ints), list of found objectIds
    findableObjects: (list of ints), list of findable objectIds
    ----------------------
    """
    missedObjects = set(findableObjects) - set(foundObjects)
    return list(missedObjects)

def countFindableObjects(dataframe, minDetectionsPerNight=2, minNights=3, windowSize=15, snrLimit=-1):
    """
    Count the number of findable objects. Uses sims_maf metric.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    dataframe: (DataFrame), dataframe containing detections 
    minDetectionsPerNight: (int) [2], minimum number of detections required for a tracklet
    minNights: (int) [3], minimum number of tracklets per window
    windowSize: (int) [15], number of nights per window
    snrLimit: (int) [-1], SNR limit for detections
    ----------------------
    """
    unique_objects = dataframe["objectId"].unique()
    findable_objects = []
    
    discoverMet = metrics.DiscoveryChancesMetric(nObsPerNight=minDetectionsPerNight, tNight=90./60./24., nNightsPerWindow=minNights, tWindow=windowSize, snrLimit=snrLimit)
    
    for unique_object in unique_objects:
        detections = dataframe[dataframe["objectId"] == unique_object]
        
        new_ssobject = np.zeros(len(detections), 
            dtype={"names":["night", "expMJD", "SNR"], 
                   "formats":["int64", "float64", "float64"]})
        
        new_ssobject["night"] = calcNight(detections["mjd"].values)
        new_ssobject["expMJD"] = detections["mjd"].values
        new_ssobject["SNR"] = detections["snr"].values
        
        discoveryChances = discoverMet.run(new_ssobject, 0, 0)
        if discoveryChances >= 1:
            findable_objects.append(unique_object)
       
    return findable_objects

def _buildTracklet(dataframe, trackletId, diaids, night, createdBy=1, calcRMS=True):
    new_tracklet = tracklet(trackletId, len(diaids), night)

    for i, diaid in enumerate(diaids):
        diasource = dataframe.loc[diaid]
        new_tracklet.addDiasource(i, diaid, diasource)
        new_tracklet.createdBy = createdBy
    
    if calcRMS:
        new_tracklet.updateRMS()
        
    new_tracklet.updateVelocity()
    new_tracklet.updateQuality()
    new_tracklet.updateMembers()
    new_tracklet.updateInfo()
    
    return new_tracklet

def _buildTrack(dataframe, trackId, diaids, window, createdBy=5, calcRMS=True):
    new_track = track(trackId, len(diaids), window)

    for i, diaid in enumerate(diaids):
        diasource = dataframe.loc[diaid]
        new_track.addDiasource(i, diaid, diasource)
        new_track.createdBy = createdBy
    
    if calcRMS:
        new_track.updateRMS()
    
    new_track.updateTime()
    new_track.updateQuality()
    new_track.updateMembers()
    new_track.updateInfo()
    
    return new_track

def analyzeTracklets(trackletFile, detFile, outDir="results/", cursor=None, collapsedTrackletFile=None, purifiedTrackletFile=None, 
    removeSubsetTrackletFile=None, trackletIdCountStart=1, objectsDataframe=None, resultsObject=None):
    startTime = time.ctime()
    night = reader.readNight(detFile)
    print("Starting tracklet analysis for night {} at {}").format(night, startTime)
    print()
    
    # Create outfile to store results
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    outFile = os.path.join(os.path.abspath(outDir), "", str(night) + ".results")
    outFileOut = open(outFile, "w", 0)
    outFileOut.write("Start time: {}\n\n").format(startTime)
    print("- Writing results to {}").format(outFile)

    # Get file sizes
    print("- Checking file sizes...")
    det_file_size = os.path.getsize(detFile)
    tracklet_file_size = os.path.getsize(trackletFile)
    if collapsedTrackletFile is not None:
        collapsed_tracklet_file_size = os.path.getsize(collapsedTrackletFile)
    if purifiedTrackletFile is not None:
        purified_tracklet_file_size = os.path.getsize(purifiedTrackletFile)
    if removeSubsetTrackletFile is not None:
        remove_subset_tracklet_file_size = os.path.getsize(removeSubsetTrackletFile)

    # Read detections into a dataframe
    print("- Reading input detections...")
    dets_df = reader.readDetectionsIntoDataframe(detFile)
    detections_num = len(dets_df.index)
    unique_objects = dets_df["objectId"].nunique()
    
    # Count number of true tracklets and findable objects in dataframe
    print("- Counting findable objects...")
    findable_objects = countFindableObjects(dets_df, minDetectionsPerNight=2, minNights=1, windowSize=1, snrLimit=-1)
    
    if resultsObject is not None:
        print("- Updating results object...")
        resultsObject.nights.append(night)
        resultsObject.nightlyDetections[night] = detections_num
        resultsObject.nightlyDetectionFileSizes[night] = det_file_size
        resultsObject.toYaml(outDir=outDir)
    
    # Write detection file properties to outfile
    print("- Writing detection file summary to outfile...")
    print()
    outFileOut.write("Input Detection File Summary:\n")
    outFileOut.write("File name: {}\n").format(detFile)
    outFileOut.write("File size (bytes): {}\n").format(det_file_size)
    outFileOut.write("Detections: {}\n").format(detections_num)
    outFileOut.write("Unique objects: {}\n").format(unique_objects)
    outFileOut.write("Findable objects: {}\n\n").format(len(findable_objects))
    
    trackletFileIn = open(trackletFile, "r")
    true_object_dict = {}
    false_object_dict = {}
    
    # Initalize success (or failure) counters
    total_tracklets_num = 0
    true_tracklets_num = 0
    false_tracklets_num = 0
    tracklet_ids = []
    
    # Initialize tracklet dataframes
    print("Analyzing tracklet file...")
    print("- Building dataframes...")
    allTrackletsDataframe = pd.DataFrame(columns=["trackletId", "linkedObjectId", "numLinkedObjects", "numMembers", "velocity", "rms", "night", "createdBy", "deletedBy"])
    trackletMembersDataframe = pd.DataFrame(columns=["trackletId", "diaId"])
    
    # Examine each line in trackletFile and read in every line
    #  as a track object. If track contains new detections (diasource)
    #  then add new source to diasource_dict.
    print("- Building tracklets...")
    for i, line in enumerate(trackletFileIn):
        tracklet_id = trackletIdCountStart + i
        tracklet_ids.append(tracklet_id)
        
        new_tracklet_diaids = reader.readTracklet(line)
        new_tracklet = _buildTracklet(dets_df, tracklet_id, new_tracklet_diaids, night, createdBy=1)

        total_tracklets_num += 1
        if new_tracklet.isTrue:
            true_tracklets_num += 1
            if new_tracklet.diasources["objectId"][0] in true_object_dict:
                true_object_dict[new_tracklet.diasources["objectId"][0]] += 1
            else:
                true_object_dict[new_tracklet.diasources["objectId"][0]] = 1

        else: 
            false_tracklets_num += 1
            for unique_object in new_tracklet.diasources["objectId"]:
                if unique_object in false_object_dict:
                    false_object_dict[unique_object] += 1
                else:
                    false_object_dict[unique_object] = 1
            
        trackletMembersDataframe = pd.concat([trackletMembersDataframe, new_tracklet.toTrackletMembersDataframe()], ignore_index=True)
        allTrackletsDataframe = pd.concat([allTrackletsDataframe, new_tracklet.toAllTrackletsDataframe()], ignore_index=True)
        
    print("- Appended new tracklets to dataframes...")
        
    prev_start_tracklet_id = trackletIdCountStart
    if len(tracklet_ids) >= 1:
        start_tracklet_id = max(tracklet_ids) + 1
    else:
        start_tracklet_id = 1
    
    if resultsObject is not None:
        print("- Updating results object...")
        resultsObject.totalTracklets[night] = total_tracklets_num
        resultsObject.trueTracklets[night] = true_tracklets_num
        resultsObject.falseTracklets[night] = false_tracklets_num
        resultsObject.trackletFileSizes[night] = tracklet_file_size
        resultsObject.toYaml(outDir=outDir)

    if objectsDataframe is not None:
        print("- Updating objects dataframe...")
        for unique_object in true_object_dict:
            objectsDataframe.loc[objectsDataframe["objectId"] == unique_object, "numTrueTracklets"] += true_object_dict[unique_object]

        for unique_object in false_object_dict:
            objectsDataframe.loc[objectsDataframe["objectId"] == unique_object, "numFalseTracklets"] += false_object_dict[unique_object]


    print("- Writing results to outfile...")
    outFileOut.write("Output Tracklet File Summary:\n")
    outFileOut.write("File name: {}\n").format(trackletFile)
    outFileOut.write("File size (bytes): {}\n").format(tracklet_file_size)
    outFileOut.write("Unique objects in true tracklets: {}\n").format(len(true_object_dict))
    outFileOut.write("Unique objects in false tracklets: {}\n").format(len(false_object_dict))
    outFileOut.write("Total unique objects: {}\n").format(len(true_object_dict) + len(false_object_dict))
    outFileOut.write("True tracklets: {}\n").format(true_tracklets_num)
    outFileOut.write("False tracklets: {}\n").format(false_tracklets_num)
    outFileOut.write("Total tracklets: {}\n\n").format(total_tracklets_num)
        
    print()
    
    if collapsedTrackletFile is not None:
        print("Analyzing collapsed tracklets...")
        created_by_collapse, deleted_by_collapse_ind = findNewLinesAndDeletedIndices(trackletFile, collapsedTrackletFile)
        print("collapseTracklets merged {} tracklets into {} collinear tracklets...").format(len(deleted_by_collapse_ind), len(created_by_collapse))
        
        true_collapsed_object_dict = {}
        false_collapsed_object_dict = {}
        
        total_collapsed_tracklets_num = 0
        true_collapsed_tracklets_num = 0
        false_collapsed_tracklets_num = 0
        
        print("- Updating dataframe properties...")
        for ind in deleted_by_collapse_ind:
            allTrackletsDataframe.loc[allTrackletsDataframe["trackletId"] == (ind + prev_start_tracklet_id), "deletedBy"] = 2
            
        print("- Building collapsed tracklets...")
        for i, line in enumerate(created_by_collapse):
            tracklet_id = start_tracklet_id + i
            tracklet_ids.append(tracklet_id) 
            
            new_tracklet_diaids = reader.readTracklet(line)
            new_tracklet = _buildTracklet(dets_df, tracklet_id, new_tracklet_diaids, night, createdBy=2)
            
            total_collapsed_tracklets_num += 1
            if new_tracklet.isTrue:
                true_collapsed_tracklets_num += 1
                if new_tracklet.diasources["objectId"][0] in true_collapsed_object_dict:
                    true_collapsed_object_dict[new_tracklet.diasources["objectId"][0]] += 1
                else:
                    true_collapsed_object_dict[new_tracklet.diasources["objectId"][0]] = 1
            else: 
                false_collapsed_tracklets_num += 1
                for unique_object in new_tracklet.diasources["objectId"]:
                    if unique_object in false_collapsed_object_dict:
                        false_collapsed_object_dict[unique_object] += 1
                    else:
                        false_collapsed_object_dict[unique_object] = 1
               
            trackletMembersDataframe = pd.concat([trackletMembersDataframe, new_tracklet.toTrackletMembersDataframe()], ignore_index=True)
            allTrackletsDataframe = pd.concat([allTrackletsDataframe, new_tracklet.toAllTrackletsDataframe()], ignore_index=True)
            
        print("- Appended new tracklets to dataframes...")
        
        prev_start_tracklet_id = start_tracklet_id
        if len(tracklet_ids) >= 1:
            start_tracklet_id = max(tracklet_ids) + 1
        else:
            start_tracklet_id = 1
        
        if resultsObject is not None:
            print("- Updating results object...")
            resultsObject.totalCollapsedTracklets[night] = total_collapsed_tracklets_num
            resultsObject.trueCollapsedTracklets[night] = true_collapsed_tracklets_num
            resultsObject.falseCollapsedTracklets[night] = false_collapsed_tracklets_num
            resultsObject.collapsedTrackletFileSizes[night] = collapsed_tracklet_file_size
            resultsObject.toYaml(outDir=outDir)

        if objectsDataframe is not None:
            print("- Updating objects dataframe...")
            for unique_object in true_collapsed_object_dict:
                objectsDataframe.loc[objectsDataframe["objectId"] == unique_object, "numTrueCollapsedTracklets"] += true_collapsed_object_dict[unique_object]

            for unique_object in false_collapsed_object_dict:
                objectsDataframe.loc[objectsDataframe["objectId"] == unique_object, "numFalseCollapsedTracklets"] += false_collapsed_object_dict[unique_object]
            
        print("- Writing results to outfile...")
        outFileOut.write("Output Collapsed Tracklet File Summary:\n")
        outFileOut.write("File name: {}\n").format(collapsedTrackletFile)
        outFileOut.write("File size (bytes): {}\n").format(collapsed_tracklet_file_size)
        outFileOut.write("Unique objects in true collapsed tracklets: {}\n").format(len(true_collapsed_object_dict))
        outFileOut.write("Unique objects in false collapsed tracklets: {}\n").format(len(false_collapsed_object_dict))
        outFileOut.write("Total unique objects: {}\n").format(len(true_collapsed_object_dict) + len(false_collapsed_object_dict))
        outFileOut.write("Tracklets collapsed: {}\n").formatlen(deleted_by_collapse_ind)
        outFileOut.write("Tracklets created: {}\n").formatlen(created_by_collapse)
        outFileOut.write("True collapsed tracklets: {}\n").format(true_collapsed_tracklets_num)
        outFileOut.write("False collapsed tracklets: {}\n").format(false_collapsed_tracklets_num)
        outFileOut.write("Total collapsed tracklets: {}\n\n").format(total_collapsed_tracklets_num)
        outFileOut.write("collapseTracklets merged {} tracklets into {} collinear tracklets...\n\n").format(len(deleted_by_collapse_ind), len(created_by_collapse))
        outFileOut.write("*** Note: These numbers only reflect tracklets affected by collapseTracklets. ***\n")
        outFileOut.write("***            File may contain other unaffected tracklets.                   ***\n\n")
        print()
        
    if purifiedTrackletFile is not None:
        print("Analyzing purified tracklets...")
        created_by_purified, deleted_by_purified_ind = findNewLinesAndDeletedIndices(collapsedTrackletFile, purifiedTrackletFile)
        print("purifiedTracklets removed detections from {} tracklets and created {} tracklets...").format(len(deleted_by_purified_ind), len(created_by_purified))
        
        true_purified_object_dict = {}
        false_purified_object_dict = {}
        
        total_purified_tracklets_num = 0
        true_purified_tracklets_num = 0
        false_purified_tracklets_num = 0
        
        print("- Updating dataframe properties...")
        for ind in deleted_by_purified_ind:
            allTrackletsDataframe.loc[allTrackletsDataframe["trackletId"] == (ind + prev_start_tracklet_id), "deletedBy"] = 3
            
        print("- Building purified tracklets...")
        for i, line in enumerate(created_by_purified):
            tracklet_id = start_tracklet_id + i 
            tracklet_ids.append(tracklet_id) 
            
            new_tracklet_diaids = reader.readTracklet(line)
            new_tracklet = _buildTracklet(dets_df, tracklet_id, new_tracklet_diaids, night, createdBy=3)
            
            total_purified_tracklets_num += 1
            if new_tracklet.isTrue:
                true_purified_tracklets_num += 1
                if new_tracklet.diasources["objectId"][0] in true_purified_object_dict:
                    true_purified_object_dict[new_tracklet.diasources["objectId"][0]] += 1
                else:
                    true_purified_object_dict[new_tracklet.diasources["objectId"][0]] = 1
            else: 
                false_purified_tracklets_num += 1
                for unique_object in new_tracklet.diasources["objectId"]:
                    if unique_object in false_purified_object_dict:
                        false_purified_object_dict[unique_object] += 1
                    else:
                        false_purified_object_dict[unique_object] = 1
                
            trackletMembersDataframe = pd.concat([trackletMembersDataframe, new_tracklet.toTrackletMembersDataframe()], ignore_index=True)
            allTrackletsDataframe = pd.concat([allTrackletsDataframe, new_tracklet.toAllTrackletsDataframe()], ignore_index=True)
            
        print("- Appended new tracklets to dataframes...")
           
        prev_start_tracklet_id = start_tracklet_id
        if len(tracklet_ids) >= 1:
            start_tracklet_id = max(tracklet_ids) + 1
        else:
            start_tracklet_id = 1
        
        if resultsObject is not None:
            print("- Updating results object...")
            resultsObject.totalPurifiedTracklets[night] = total_purified_tracklets_num
            resultsObject.truePurifiedTracklets[night] = true_purified_tracklets_num
            resultsObject.falsePurifiedTracklets[night] = false_purified_tracklets_num
            resultsObject.purifiedTrackletFileSizes[night] = purified_tracklet_file_size
            resultsObject.toYaml(outDir=outDir)

        if objectsDataframe is not None:
            print("- Updating objects dataframe...")
            for unique_object in true_purified_object_dict:
                objectsDataframe.loc[objectsDataframe["objectId"] == unique_object, "numTruePurifiedTracklets"] += true_purified_object_dict[unique_object]

            for unique_object in false_purified_object_dict:
                objectsDataframe.loc[objectsDataframe["objectId"] == unique_object, "numFalsePurifiedTracklets"]+= false_purified_object_dict[unique_object]

        print("- Writing results to outfile...")
        outFileOut.write("Output Purified Tracklet File Summary:\n")
        outFileOut.write("File name: {}\n").format(purifiedTrackletFile)
        outFileOut.write("File size (bytes): {}\n").format(purified_tracklet_file_size)
        outFileOut.write("Unique objects in true purified tracklets: {}\n").format(len(true_purified_object_dict))
        outFileOut.write("Unique objects in false purified tracklets: {}\n").format(len(false_purified_object_dict))
        outFileOut.write("Total unique objects: {}\n").format(len(true_purified_object_dict) + len(false_purified_object_dict))
        outFileOut.write("Tracklets purified: {}\n").formatlen(deleted_by_purified_ind)
        outFileOut.write("Tracklets created: {}\n").formatlen(created_by_purified)
        outFileOut.write("True purified tracklets: {}\n").format(true_purified_tracklets_num)
        outFileOut.write("False purified tracklets: {}\n").format(false_purified_tracklets_num)
        outFileOut.write("Total purified tracklets: {}\n\n").format(total_purified_tracklets_num)
        outFileOut.write("purifiedTracklets removed detections from {} tracklets and created {} tracklets...\n\n").format(len(deleted_by_purified_ind), len(created_by_purified))
        outFileOut.write("*** Note: These numbers only reflect tracklets affected by purifyTracklets. ***\n")
        outFileOut.write("***          File may contain other unaffected tracklets.                   ***\n\n")
        
        print()

    if removeSubsetTrackletFile is not None:
        print("Analyzing final tracklets...")
        created_by_removeSubsets, deleted_by_removeSubsets_ind = findNewLinesAndDeletedIndices(purifiedTrackletFile, removeSubsetTrackletFile)
        print("removeSubsets removed {} tracklets...").format(len(deleted_by_removeSubsets_ind))
        
        true_final_object_dict = {}
        false_final_object_dict = {}
        
        total_final_tracklets_num = 0
        true_final_tracklets_num = 0
        false_final_tracklets_num = 0
        
        print("- Updating dataframe properties...")
        for ind in deleted_by_purified_ind:
            allTrackletsDataframe.loc[allTrackletsDataframe["trackletId"] == (ind + prev_start_tracklet_id), "deletedBy"] = 4
            
        print("- Building final tracklets...")
        for i, line in enumerate(created_by_removeSubsets):
            tracklet_id = start_tracklet_id + i 
            tracklet_ids.append(tracklet_id)
            
            new_tracklet_diaids = reader.readTracklet(line)
            new_tracklet = _buildTracklet(dets_df, tracklet_id, new_tracklet_diaids, night, createdBy=4)
            
            total_final_tracklets_num += 1
            if new_tracklet.isTrue:
                true_final_tracklets_num += 1
                if new_tracklet.diasources["objectId"][0] in true_final_object_dict:
                    true_final_object_dict[new_tracklet.diasources["objectId"][0]] += 1
                else:
                    true_final_object_dict[new_tracklet.diasources["objectId"][0]] = 1
            else: 
                false_final_tracklets_num += 1
                for unique_object in new_tracklet.diasources["objectId"]:
                    if unique_object in false_final_object_dict:
                        false_final_object_dict[unique_object] += 1
                    else:
                        false_final_object_dict[unique_object] = 1
                
            trackletMembersDataframe = pd.concat([trackletMembersDataframe, new_tracklet.toTrackletMembersDataframe()], ignore_index=True)
            allTrackletsDataframe = pd.concat([allTrackletsDataframe, new_tracklet.toAllTrackletsDataframe()], ignore_index=True)
            
        print("- Appended new tracklets to dataframes...")
        
        prev_start_tracklet_id = start_tracklet_id
        if len(tracklet_ids) >= 1:
            start_tracklet_id = max(tracklet_ids) + 1
        else:
            start_tracklet_id = 1
        
        if resultsObject is not None:
            print("- Updating results object...")
            resultsObject.totalFinalTracklets[night] = total_final_tracklets_num
            resultsObject.trueFinalTracklets[night] = true_final_tracklets_num
            resultsObject.falseFinalTracklets[night] = false_final_tracklets_num
            resultsObject.finalTrackletFileSizes[night] = remove_subset_tracklet_file_size
            resultsObject.toYaml(outDir=outDir)

        if objectsDataframe is not None:
            print("- Updating objects dataframe...")
            for unique_object in true_final_object_dict:
                objectsDataframe.loc[objectsDataframe["objectId"] == unique_object, "numTrueFinalTracklets"] += true_final_object_dict[unique_object]

            for unique_object in false_final_object_dict:
                objectsDataframe.loc[objectsDataframe["objectId"] == unique_object, "numFalseFinalTracklets"] += false_final_object_dict[unique_object]

        print("- Writing results to outfile...")
        outFileOut.write("Output Final Tracklet File Summary:\n")
        outFileOut.write("File name: {}\n").format(removeSubsetTrackletFile)
        outFileOut.write("File size (bytes): {}\n").format(remove_subset_tracklet_file_size)
        outFileOut.write("Unique objects in true final tracklets: {}\n").format(len(true_final_object_dict))
        outFileOut.write("Unique objects in false final tracklets: {}\n").format(len(false_final_object_dict))
        outFileOut.write("Total unique objects: {}\n").format(len(true_final_object_dict) + len(false_final_object_dict))
        outFileOut.write("Tracklets removed: {}\n").formatlen(deleted_by_removeSubsets_ind)
        outFileOut.write("True final tracklets: {}\n").format(true_final_tracklets_num)
        outFileOut.write("False final tracklets: {}\n").format(false_final_tracklets_num)
        outFileOut.write("Total final tracklets: {}\n\n").format(total_final_tracklets_num)
        outFileOut.write("removeSubsets removed {} tracklets...\n\n").format(len(deleted_by_removeSubsets_ind))
        outFileOut.write("*** Note: These numbers only reflect tracklets affected by removeSubsets. ***\n")
        outFileOut.write("***          File may contain other unaffected tracklets.                 ***\n\n")
       
        print()
        
    if cursor is not None:
        print("Converting dataframes to sqlite tables...")
        print("Updating TrackletMembers tables...")
        trackletMembersDataframe.to_sql("TrackletMembers", cursor, if_exists="append", index=False)
        print("Updating AllTracklets tables...")
        allTrackletsDataframe.to_sql("AllTracklets", cursor, if_exists="append", index=False)
        
        print()
        
    endTime = time.ctime()
    outFileOut.write("End time: {}\n").format(endTime)
        
    print("Finished tracklet analysis for night {} at {}").format(night, endTime)
    print()
    
    return outFile, allTrackletsDataframe, trackletMembersDataframe, tracklet_ids

def analyzeTracks(trackFile, detFile, idsFile, outDir="results/", cursor=None, removeSubsetTrackFile=None, minDetectionsPerNight=2, minNights=3, windowSize=15, 
    snrLimit=-1, analyzeSubsets=True, trackIdCountStart=1, objectsDataframe=None, resultsObject=None):
    startTime = time.ctime()
    startNight, endNight = reader.readWindow(detFile)
    window = str(startNight) + "-" + str(endNight)
    print("Starting track analysis for window (nights: {} - {}) at {}").format(str(startNight), str(endNight), startTime)
    print()
    
    # Create outfile to store results
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    outFile = os.path.join(os.path.abspath(outDir), "", window + ".results")
    outFileOut = open(outFile, "w", 0)
    outFileOut.write("Start time: {}\n\n").format(startTime)
    print("- Writing results to {}").format(outFile)

    print("- Checking file sizes...")
    ids_file_size = os.path.getsize(idsFile)
    det_file_size = os.path.getsize(detFile)
    track_file_size = os.path.getsize(trackFile)
    if removeSubsetTrackFile is not None:
        final_track_file_size = os.path.getsize(removeSubsetTrackFile)

    # Read ids file 
    print("- Counting number of input tracks...")
    track_num = 0
    for trackLine in open(idsFile, "r"):
        track_num += 1

    outFileOut.write("Input Track (Ids) File Summary:\n")
    outFileOut.write("File name: {}\n").format(idsFile)
    outFileOut.write("File size (bytes): {}\n").format(ids_file_size)
    outFileOut.write("Tracks: {}\n\n").format(track_num)
    
    # Read detections into a dataframe
    print("- Reading input detections...")
    dets_df = reader.readDetectionsIntoDataframe(detFile)
    detections_num = len(dets_df.index)
    unique_objects = dets_df["objectId"].nunique()

    # Count number of true tracks and findable objects in dataframe
    print("- Counting findable objects...")
    findable_objects = countFindableObjects(dets_df, minDetectionsPerNight=minDetectionsPerNight, minNights=minNights, windowSize=windowSize, snrLimit=snrLimit)

    if resultsObject is not None:
        print("- Updating results object...")
        resultsObject.windows.append(window)
        resultsObject.windowDetections[window] = detections_num
        resultsObject.windowDetectionFileSizes[window] = det_file_size
        resultsObject.trackIdFileSizes[window] = ids_file_size
        resultsObject.trackFileSizes[window] = track_file_size
        resultsObject.toYaml(outDir=outDir)

    # Write detection file properties to outfile
    print("- Writing detection file summary to outfile...")
    print()
    outFileOut.write("Input Detection File Summary:\n")
    outFileOut.write("File name: {}\n").format(detFile)
    outFileOut.write("File size (bytes): {}\n").format(det_file_size)
    outFileOut.write("Detections: {}\n").format(detections_num)
    outFileOut.write("Unique objects: {}\n").format(unique_objects)
    outFileOut.write("Findable objects: {}\n\n").format(len(findable_objects))

    trackFileIn = open(trackFile, "r")
    tracks = []
    true_object_dict = {}
    false_object_dict = {}
    found_objects = []
    missed_objects = []
    
    # Initalize success (or failure) counters
    total_tracks_num = 0
    true_tracks_num = 0
    false_tracks_num = 0
    track_ids = []

    print("Analyzing track file...")
    print("- Building dataframes...")
    allTracksDataframe = pd.DataFrame(columns=["trackId", "linkedObjectId", "numLinkedObjects", "numMembers", "rms", "windowStart", "startTime", "endTime", "subsetOf", "createdBy", "deletedBy"])
    trackMembersDataframe = pd.DataFrame(columns=["trackId", "diaId"])

    # Examine each line in trackFile and read in every line
    #  as a track object. If track contains new detections (diasource)
    #  then add new source to diasource_dict. 
    print("- Building tracks...")
    for i, line in enumerate(trackFileIn):
        track_id = trackIdCountStart + i 
        track_ids.append(track_id)
        
        new_track_diaids = reader.readTrack(line)
        new_track = _buildTrack(dets_df, track_id, new_track_diaids, startNight, createdBy=5)

        total_tracks_num += 1     
        if new_track.isTrue:
            true_tracks_num += 1
            if new_track.diasources["objectId"][0] not in found_objects:
                found_objects.append(new_track.diasources["objectId"][0])

            if new_track.diasources["objectId"][0] in true_object_dict:
                true_object_dict[new_track.diasources["objectId"][0]] += 1
            else:
                true_object_dict[new_track.diasources["objectId"][0]] = 1
        else: 
            false_tracks_num += 1
            for unique_object in new_track.diasources["objectId"]:
                if unique_object in false_object_dict:
                    false_object_dict[unique_object] += 1
                else:
                    false_object_dict[unique_object] = 1

        tracks.append(new_track)

        trackMembersDataframe = pd.concat([trackMembersDataframe, new_track.toTrackMembersDataframe()], ignore_index=True)
        allTracksDataframe = pd.concat([allTracksDataframe, new_track.toAllTracksDataframe()], ignore_index=True)

    print("- Appended new tracks to dataframes...")

    if len(track_ids) >= 1:
        start_track_id = max(track_ids) + 1
    else:
        start_track_id = 1

    longest_tracks_num = 0
    subset_tracks_num = 0
    if analyzeSubsets:
        print("- Counting subset tracks...")
        longest_tracks_num, subset_tracks_num, tracks = checkSubsets(tracks)

        print("- Updating AllTracks dataframe...")
        for trackLine in tracks:
            if track.isSubset:
                allTracksDataframe.loc[allTracksDataframe["trackId"] == track.trackId, "subsetOf"] = track.subsetOf
            else:
                continue

    print("- Counting missed objects...")
    missed_objects = countMissedObjects(found_objects, findable_objects)

    print("- Calculating performance...")
    if len(findable_objects) != 0:
        performance_ratio = float(len(found_objects))/len(findable_objects)
    else:
        performance_ratio = 0.0

    if resultsObject is not None:
        print("- Updating results object...")
        resultsObject.uniqueObjects[window] = unique_objects
        resultsObject.findableObjects[window] = len(findable_objects)
        resultsObject.foundObjects[window] = len(found_objects)
        resultsObject.missedObjects[window] = len(missed_objects)
        resultsObject.performanceRatio[window] = performance_ratio

        resultsObject.totalTracks[window] = total_tracks_num
        resultsObject.trueTracks[window] = true_tracks_num
        resultsObject.falseTracks[window] = false_tracks_num
        resultsObject.subsetTracks[window] = subset_tracks_num
        resultsObject.longestTracks[window] = longest_tracks_num
        resultsObject.toYaml(outDir=outDir)

    if objectsDataframe is not None:
        print("- Updating objects dataframe...")
        for unique_object in true_object_dict:
            objectsDataframe.loc[objectsDataframe["objectId"] == unique_object, "numTrueTracks"] += true_object_dict[unique_object]

        for unique_object in false_object_dict:
            objectsDataframe.loc[objectsDataframe["objectId"] == unique_object, "numFalseTracks"] += false_object_dict[unique_object]

    print("- Writing results to outfile...")
    outFileOut.write("Output Track File Summary:\n")
    outFileOut.write("File name: {}\n").format(trackFile)
    outFileOut.write("File size (bytes): {}\n").format(track_file_size)
    outFileOut.write("Objects found: {}\n").format(len(found_objects))
    outFileOut.write("Objects missed: {}\n").format(len(missed_objects))
    outFileOut.write("Unique objects in true tracks: {}\n").format(len(true_object_dict))
    outFileOut.write("Unique objects in false tracks: {}\n").format(len(false_object_dict))
    outFileOut.write("Total unique objects: {}\n").format(len(true_object_dict) + len(false_object_dict))
    outFileOut.write("True tracks: {}\n").format(true_tracks_num)
    outFileOut.write("False tracks {}\n").format(false_tracks_num)
    outFileOut.write("Total tracks: {}\n").format(total_tracks_num)
    outFileOut.write("Subset tracks: {}\n").format(subset_tracks_num)
    outFileOut.write("Longest tracks: {}\n\n").format(longest_tracks_num)
    outFileOut.write("MOPs Performance Ratio (found/findable): %.5f\n\n").format(performance_ratio)

    print()

    if removeSubsetTrackFile is not None:
        print("Analyzing final tracks...")
        created_by_removeSubsets, deleted_by_removeSubsets_ind = findNewLinesAndDeletedIndices(trackFile, removeSubsetTrackFile)
        print("removeSubsets removed {} tracks...").format(len(deleted_by_removeSubsets_ind))

        true_final_object_dict = {}
        false_final_object_dict = {}

        total_final_tracks_num = 0
        true_final_tracks_num = 0
        false_final_tracks_num = 0

        print("- Updating dataframe properties...")
        for ind in deleted_by_removeSubsets_ind:
            allTracksDataframe.loc[allTracksDataframe["trackId"] == ind + trackIdCountStart, "deletedBy"] = 6

        print("- Building final tracks...")
        for i, line in enumerate(created_by_removeSubsets):
            track_id = start_track_id + i
            track_ids.append(track_id)
            
            new_track_diaids = reader.readTrack(line)
            new_track = _buildTrack(dets_df, track_id, new_track_diaids, startNight, createdBy=5)

            total_final_tracks_num += 1     
            if new_track.isTrue:
                true_final_tracks_num += 1
                if new_track.diasources["objectId"][0] in true_final_object_dict:
                    true_final_object_dict[new_track.diasources["objectId"][0]] += 1
                else:
                    true_final_object_dict[new_track.diasources["objectId"][0]] = 1
            else: 
                false_tracks_num += 1
                for unique_object in new_track.diasources["objectId"]:
                    if unique_object in false_object_dict:
                        false_final_object_dict[unique_object] += 1
                    else:
                        false_final_object_dict[unique_object] = 1

            trackMembersDataframe = pd.concat([trackMembersDataframe, new_track.toTrackMembersDataframe()], ignore_index=True)
            allTracksDataframe = pd.concat([allTracksDataframe, new_track.toAllTracksDataframe()], ignore_index=True)

        print("- Appended new tracks to dataframes...")

        if resultsObject is not None:
            print("- Updating results object...")
            resultsObject.totalFinalTracks[window] = total_final_tracks_num
            resultsObject.trueFinalTracks[window] = true_final_tracks_num
            resultsObject.falseFinalTracks[window] = false_final_tracks_num
            resultsObject.finalTrackFileSizes[window] = final_track_file_size
            resultsObject.toYaml(outDir=outDir)

        if objectsDataframe is not None:
            print("- Updating objects dataframe...")
            for unique_object in true_final_object_dict:
                objectsDataframe.loc[objectsDataframe["objectId"] == unique_object, "numTrueFinalTracks"] += true_final_object_dict[unique_object]

            for unique_object in false_final_object_dict:
                objectsDataframe.loc[objectsDataframe["objectId"] == unique_object, "numFalseFinalTracks"] += false_final_object_dict[unique_object]

        print("- Writing results to outfile...")
        outFileOut.write("Output Final Track File Summary:\n")
        outFileOut.write("File name: {}\n").format(removeSubsetTrackFile)
        outFileOut.write("File size (bytes): {}\n").format(final_track_file_size)
        outFileOut.write("Unique objects in true tracks: {}\n").format(len(true_final_object_dict))
        outFileOut.write("Unique objects in false tracks: {}\n").format(len(false_final_object_dict))
        outFileOut.write("Total unique objects: {}\n").format(len(true_final_object_dict) + len(false_final_object_dict))
        outFileOut.write("True final tracks: {}\n").format(true_final_tracks_num)
        outFileOut.write("False final tracks {}\n").format(false_final_tracks_num)
        outFileOut.write("Total final tracks: {}\n\n").format(total_final_tracks_num)
        outFileOut.write("removeSubsets removed {} tracks...\n\n").format(len(deleted_by_removeSubsets_ind))
        outFileOut.write("*** Note: These numbers only reflect tracks affected by removeSubsets. ***\n")
        outFileOut.write("***          File may contain other unaffected tracks.                 ***\n\n")
        print()

    if cursor is not None:
        print("Converting dataframes to sqlite tables...")
        print("Updating TrackMembers table...")
        trackMembersDataframe.to_sql("TrackMembers", cursor, if_exists="append", index=False)
        print("Updating AllTracks table...")
        allTracksDataframe.to_sql("AllTracks", cursor, if_exists="append", index=False)
        
        print()

    endTime = time.ctime()
    outFileOut.write("End time: {}\n").format(endTime)

    print("Finished track analysis for window (nights: {} - {}) at {}").format(str(startNight), str(endNight), endTime)
    print()
    
    return outFile, allTracksDataframe, trackMembersDataframe, track_ids

def analyzeMultipleTracklets(trackletFiles, detFiles, outDir="results/", collapsedTrackletFiles=None, purifiedTrackletFiles=None, removeSubsetTrackletFiles=None,
                            cursor=None, objectsDataframe=None, resultsObject=None):
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
            outDir=outDir, trackletIdCountStart=tracklet_id_start_count, cursor=cursor, objectsDataframe=objectsDataframe, resultsObject=resultsObject, **kwargs)

        resultFiles.append(resultFile)
        all_tracklet_ids.extend(tracklet_ids)

        if len(all_tracklet_ids) >= 1:
            tracklet_id_start_count = max(all_tracklet_ids) + 1
        else: 
            tracklet_id_start_count = 1

    return sorted(resultFiles)

def analyzeMultipleTracks(trackFiles, detFiles, idsFiles, outDir="results/", removeSubsetTrackFiles=None,
                            toDatabase=True, objectsDataframe=None, resultsObject=None, minDetectionsPerNight=2, minNights=3, windowSize=15):

    databases = []
    resultFiles = []
    track_id_start_count = 1
    all_track_ids = []

    for i, (trackFile, detFile, idsFile) in enumerate(zip(trackFiles, detFiles, idsFiles)):
        if toDatabase:
            startNight, endNight = reader.readWindow(detFile)
            windowDatabase = str(startNight) + "-" + str(endNight) + ".db"
            cursor, database = database.buildTrackDatabase(windowDatabase, outDir)
        else:
            cursor = None

        kwargs = {"removeSubsetTrackFile": None}

        if removeSubsetTrackFiles is not None:
            kwargs["removeSubsetTrackFile"] = removeSubsetTrackFiles[i]

        resultFile, allTracksDataframe, trackMembersDataframe, track_ids = analyzeTracks(trackFile, detFile, idsFile,
            outDir=outDir, trackIdCountStart=track_id_start_count, cursor=cursor, objectsDataframe=objectsDataframe, resultsObject=resultsObject, 
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
            print("Overwrite triggered: deleting existing results directory...")
            print()
        else:
            raise NameError("Results directory exists! Cannot continue!")
    else:
        os.mkdir(outDir)

    if resultsObject is None:
        print("Initializing new results object...")
        resultsObject = Results(parameters, tracker)

    cursor = None
    database = None
    if toDatabase:
        cursor, database = database.buildTrackletDatabase("main.db", outDir)

    objects_df = None
    if fullDetFile:
        print("Reading full detections file into dataframe...")
        full_dets_df = reader.readDetectionsIntoDataframe(fullDetFile)
        unique_objects, numDetections = np.unique(full_dets_df["objectId"], return_counts=True)

        print("Counting findable objects as tracklets...")
        findable_objects_as_tracklets = countFindableObjects(full_dets_df, minDetectionsPerNight=2, minNights=1, windowSize=1, snrLimit=-1)

        print("Counting findable objects as tracks...")
        findable_objects_as_tracks = countFindableObjects(full_dets_df, minDetectionsPerNight=2, minNights=3, windowSize=15, snrLimit=-1)

        print("Building objects dataframe...")
        table = np.zeros(len(unique_objects), 
            dtype={"names":["objectId", "numDetections", "findableAsTracklet", "findableAsTrack", 
                        "numFalseTracklets", "numTrueTracklets", "numFalseCollapsedTracklets", "numTrueCollapsedTracklets",
                        "numFalsePurifiedTracklets", "numTruePurifiedTracklets", "numFalseFinalTracklets", "numTrueFinalTracklets",
                        "numFalseTracks", "numTrueTracks", "numFalseFinalTracks", "numTrueFinalTracks"], 
                    "formats":["int64","int64","bool","bool",
                        "int64","int64","int64","int64",
                        "int64","int64","int64","int64",
                        "int64","int64","int64","int64"]})

        table["objectId"] = unique_objects
        table["numDetections"] = numDetections
        objects_df = pd.DataFrame(table)

        print("Updating objects dataframe...")
        for unique_object in findable_objects_as_tracklets:
            objects_df.loc[objects_df["objectId"] == unique_object, "findableAsTracklet"] = True

        for unique_object in findable_objects_as_tracks:
            objects_df.loc[objects_df["objectId"] == unique_object, "findableAsTrack"] = True

        if toDatabase:
            print("Reading full detections file into database...")
            reader.readDetectionsIntoDatabase(fullDetFile, cursor, table="DiaSources", header=None)

        print()

    if tracklets:

        print("Starting tracklet analysis for {} nights...").format(len(tracker.tracklets))
        print()

        resultFiles = analyzeMultipleTracklets(tracker.tracklets, tracker.diasources, outDir=outDir, 
            collapsedTrackletFiles=tracker.collapsedTrackletsById, purifiedTrackletFiles=tracker.purifiedTrackletsById,
            removeSubsetTrackletFiles=tracker.finalTrackletsById, cursor=cursor, objectsDataframe=objects_df, resultsObject=resultsObject)

        tracker.trackletResults = resultFiles
        tracker.mainDatabase = database
        tracker.toYaml(outDir=tracker.runDir)
        tracker.toYaml(outDir=tracker.resultsDir)

        print()

    resultsObject.toYaml(outDir=tracker.runDir)
    resultsObject.toYaml(outDir=tracker.resultsDir)

    print()

    if tracks:

        print("Starting track analysis for {} windows...").format(len(tracker.tracks))
        print()

        resultFiles, databases = analyzeMultipleTracks(tracker.tracks, tracker.dets, tracker.ids, outDir=outDir, 
          removeSubsetTrackFiles=tracker.finalTracks, toDatabase=toDatabase, objectsDataframe=objects_df, resultsObject=resultsObject, 
          minDetectionsPerNight=minDetectionsPerNight, minNights=minNights, windowSize=windowSize)

        tracker.trackResults = resultFiles
        tracker.windowDatabases = databases
        tracker.toYaml(outDir=tracker.runDir)
        tracker.toYaml(outDir=tracker.resultsDir)

        print()

    resultsObject.toYaml(outDir=tracker.runDir)
    resultsObject.toYaml(outDir=tracker.resultsDir)

    print()

    if fullDetFile:
        print("Converting object dataframe to sqlite table...")
        print("Updating AllObjects table...")
        objects_df.to_sql("AllObjects", cursor, if_exists="append", index=False)
        print()

    print("Analysis finished.")

    return resultsObject, objects_df

