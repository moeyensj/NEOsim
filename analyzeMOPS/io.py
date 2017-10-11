import os
import numpy as np
import pandas as pd
import sqlite3 as sql
import difflib

from .config import Config 

__all__ = ["readDetectionsIntoDatabase", "readTrackletsIntoDatabase", "readTracksIntoDatabase",
           "buildTrackletDatabase", "buildTrackDatabase", "attachDatabases",
           "_findNewLinesAndDeletedIndices", "_makeNewLinkageDataFrames"]

def readDetectionsIntoDatabase(detsFile, con,
                               detectionsTable=Config.detection_table,
                               diaSourcesTable=Config.diasources_table,
                               mappingTable=Config.mapping_table,
                               detsFileColumns=Config.detection_file_columns,
                               specialIds=Config.detection_file_special_ids,
                               readParams=Config.detection_file_read_params,
                               chunksize=10000, 
                               mapObjectIds=True,
                               verbose=Config.verbose):
    """
    Reads a full detection file into a database and creates a database view representative 
    of the input detections needed for MOPS to run. 

    The input detection file columns should contain the columns needed for MOPS to run. The
    column mapping can be defined using the detsFileColumns keyword argument. The keys to this
    dictionary are the required MOPS columns, the values to those keys should be headers in the 
    input detections file. See `Config.detection_file_columns`. 

    If the input detection file objectIds are not integer values MOPS will not be able to run. To
    map these to MOPS-friendly integer values use the mapObjectIds keyword argument. This will create
    a mapping table in the database. Additionally, if the input dataset has noise detections use the 
    specialIds dictionary (keys are the objectId in the detection file, values should be the desired 
    negative integers to map those objectIds to). 

    Parameters
    ----------
    detsFile : str
        Path to file containing detections. File should have header with column names.

    con : `sqlite3.Connection`
        Connection to sqlite3 database or equivalent.

    detectionsTable : str, optional
        Detection table name. [Default = `Config.detection_table`]

    diaSourcesTable : str, optional
        DiaSources table name. [Default = `Config.diasources_table`]

    mappingTable : str, optional
        Mapping table name. If mapObjectIds is True, mapping table with objectId mapping will
        be created. [Default = `Config.mapping_table`]

    detsFileColumns : dict, optional
        Dictionary containing the column mappings of the input detection file to those needed 
        for MOPS to run. [Default = `Config.detection_file_columns`] 

    specialIds : dict, optional
        Dictionary containing special objectIds, such as those that designate noise. The keys of the
        dictionary should be the objectId in the input detection file, the values should be desired negative
        integer values. [Default = `Config.detection_file_special_ids`]

    readParams : dict, optional
        Dictionary of `Pandas.read_csv` keyword arguments to use when reading in the detections file.
        [Default = `Config.detection_file_read_params`]

    chunksize : int, optional
        Read input detection file into database in sets of rows of chunksize. Useful for 
        big data sets. [Default = 10000]

    mapObjectIds : bool, optional
        If input detection file objectIds are not integer values, set this to True to create 
        an objectId mapping. [Default = True]

    verbose : bool, optional
        Print progress statements? [Default = `Config.verbose`]

    Returns
    -------
    None

    """
    if verbose is True:
        print("Reading {} into {} table".format(detsFile, detectionsTable))
    for chunk in pd.read_csv(detsFile, chunksize=chunksize, **readParams):
        chunk.to_sql(detectionsTable, con, if_exists="append", index=False)
    
    if mapObjectIds is True:
        if verbose is True:
            print("Creating {} table".format(mappingTable))
        con.execute("""CREATE TABLE Mapping (objectId INTEGER PRIMARY KEY, {} VARCHAR)""".format(detsFileColumns["objectId"]))
        
        if verbose is True:
            print("Mapping {} to MOPS-friendly integer objectIds".format(detsFileColumns["objectId"]))
        if specialIds is not None:
            objects = pd.read_sql("""SELECT DISTINCT {} FROM {}
                                     WHERE {} NOT IN ('{}')""".format(detsFileColumns["objectId"],
                                                                      detectionsTable,
                                                                      detsFileColumns["objectId"],
                                                                      "', '".join(specialIds.keys())), con)
            if verbose is True:
                print("Found {} unique objectIds".format(len(objects)))
                print("Mapping the following specialIds to:")
            for key in specialIds:
                if verbose is True:
                    print("\t{} : {}".format(key, specialIds[key]))
            objects["objectId"] = objects.index + 1
            objects = objects.append(pd.DataFrame(zip(specialIds.keys(), specialIds.values()),
                                                  columns=[objects.columns[0], objects.columns[1]]))
        else:
            objects = pd.read_sql("""SELECT DISTINCT {} FROM {}""".format(detsFileColumns["objectId"],
                                                                          detectionsTable), con) 
            if verbose is True:
                print("Found {} unique objectIds".format(len(objects)))                                                       
            objects["objectId"] = objects.index + 1

        if verbose is True:
            print("Building {} table".format(mappingTable))
        objects.sort_values("objectId", inplace=True)
        objects.to_sql(mappingTable, con, index=False, if_exists="append")

        if verbose is True:
            print("Creating {} view using the following columns:".format(diaSourcesTable))
            print("\tdiaId : {}".format(detsFileColumns["diaId"]))
            print("\tvisitId : {}".format(detsFileColumns["visitId"]))
            print("\tobjectId : {}".format(detsFileColumns["objectId"]))
            print("\tra : {}".format(detsFileColumns["ra"]))
            print("\tdec : {}".format(detsFileColumns["dec"]))
            print("\tmjd : {}".format(detsFileColumns["mjd"]))
            print("\tmag : {}".format(detsFileColumns["mag"]))
            print("\tsnr : {}".format(detsFileColumns["snr"]))

        con.execute("""CREATE VIEW {} AS
                            SELECT d.{} AS diaId,
                                   d.{} AS visitId,
                                   m.objectId AS objectId,
                                   d.{} AS ra,
                                   d.{} AS dec,
                                   d.{} AS mjd,
                                   d.{} AS mag,
                                   d.{} AS snr
                            FROM {} AS d
                            JOIN {} AS m ON 
                                d.{} = m.{}
                            ;""".format(diaSourcesTable,
                                        detsFileColumns["diaId"],
                                        detsFileColumns["visitId"],
                                        detsFileColumns["ra"],
                                        detsFileColumns["dec"],
                                        detsFileColumns["mjd"],
                                        detsFileColumns["mag"],
                                        detsFileColumns["snr"],
                                        detectionsTable,
                                        mappingTable,
                                        detsFileColumns["objectId"],
                                        detsFileColumns["objectId"]))
    else:
        if verbose is True:
            print("Creating {} view using the following columns:".format(diaSourcesTable))
            print("\tdiaId : {}".format(detsFileColumns["diaId"]))
            print("\tvisitId : {}".format(detsFileColumns["visitId"]))
            print("\tobjectId : {}".format(detsFileColumns["objectId"]))
            print("\tra : {}".format(detsFileColumns["ra"]))
            print("\tdec : {}".format(detsFileColumns["dec"]))
            print("\tmjd : {}".format(detsFileColumns["mjd"]))
            print("\tmag : {}".format(detsFileColumns["mag"]))
            print("\tsnr : {}".format(detsFileColumns["snr"]))

        con.execute("""CREATE VIEW {} AS
                            SELECT d.{} AS diaId,
                                   d.{} AS visitId,
                                   d.{} AS objectId,
                                   d.{} AS ra,
                                   d.{} AS dec,
                                   d.{} AS mjd,
                                   d.{} AS mag,
                                   d.{} AS snr
                            FROM {} AS d
                            ;""".format(diaSourcesTable,
                                        detsFileColumns["diaId"],
                                        detsFileColumns["visitId"],
                                        detsFileColumns["objectId"],
                                        detsFileColumns["ra"],
                                        detsFileColumns["dec"],
                                        detsFileColumns["mjd"],
                                        detsFileColumns["mag"],
                                        detsFileColumns["snr"],
                                        detectionsTable))
    if verbose is True:
        print("Done.")
    return 

def readTrackletsIntoDatabase(trackletFile, con,
                              collapsedTrackletFile=None,
                              purifiedTrackletFile=None,
                              finalTrackletFile=None,
                              trackletIdStart=1,
                              verbose=Config.verbose):
    """
    Read a nightly set of tracklet files into a tracklets database. 
    
    Parameters
    ----------
    trackletFile : str
        Path to tracklet files made by findTracklets.

    con : `sqlite3.Connection` or similar
        Database connection, database needs to have an allTracklets and trackletMembers table.
    
    collapsedTrackletFile : str, optional
        Path to collapseTracklets file for the same night as trackletFile. [Default = None]

    purifiedTrackletFile : str, optional
        Path to purifyTracklets file for the same night as trackletFile. [Default = None]
    
    finalTrackletFile : str, optional
        Path to final tracklet file (removeSubsets) for the same night as trackletFile.
        [Default = None]
    
    trackletIdStart : int, optional
        TrackletId from which to start numbering new tracklets. [Default = 1]

    verbose : bool, optional
        Print progress statements? [Default = `Config.verbose`]

    Returns
    -------
    None

    """
    if verbose is True:
        print("Reading {} into database...".format(trackletFile))
    # Read in a tracklets file. With the current version of MOPS 10 million tracklets in a night is roughly
    # a file of order a GB. This can be read in memory, if, in the unfortunate event that more tracklets are generated
    # a night. We might need to swap to reading in chunks.
    trackletMembers = pd.read_csv(trackletFile, header=None, names=["diaId"])
    if len(trackletMembers) == 0:
        if verbose is True:
            print("{} has no tracklets. Skipping.".format(trackFile))
        return        
    # Create an array of integer trackletIds
    trackletIds = np.arange(trackletIdStart, trackletIdStart + len(trackletMembers), dtype=int)
    trackletId_max = trackletIds[-1]
    # Read in the trackletFile where every row is a string of diaIds delimited by whitespace
    # Split the string of diaIds into separate columns and then stack the columns so that every tracklet has 
    # a row for every diaId
    trackletMembers = pd.DataFrame(pd.DataFrame(trackletMembers["diaId"].str.split(" ").tolist(), index=trackletIds).stack(), columns=["diaId"])
    trackletMembers.reset_index(1, drop=True, inplace=True)
    trackletMembers["trackletId"] = trackletMembers.index
    trackletMembers = trackletMembers[["trackletId", "diaId"]]
    # Not all tracklets have the same number of detections, empty detections needs to be dropped
    trackletMembers["diaId"].replace("", np.nan, inplace=True)
    trackletMembers.dropna(inplace=True)
    
    allTracklets = pd.DataFrame(trackletMembers["trackletId"].unique(), columns=["trackletId"])
    allTracklets["numMembers"] = trackletMembers["trackletId"].value_counts().sort_index().values
    allTracklets["createdBy"] = np.ones(len(allTracklets), dtype=int) * 1
    allTracklets["deletedBy"] = np.zeros(len(allTracklets), dtype=int)
    allTracklets["_lineNum_1"] = np.arange(1, len(allTracklets) + 1, dtype=int)
    allTracklets["_lineNum_2"] = np.nan
    allTracklets["_lineNum_3"] = np.nan
    allTracklets["_lineNum_4"] = np.nan
    
    allTracklets_temp = allTracklets
    trackletMembers_temp = trackletMembers
    prev_line_col = "_lineNum_1"
    
    if collapsedTrackletFile is not None:
        if verbose is True:
            print("Reading {} into database...".format(collapsedTrackletFile))
        # collapseTracklets can both create and destroy tracklets by merging
        created_by_collapse, created_by_collapse_inds, deleted_by_collapse_ind = _findNewLinesAndDeletedIndices(trackletFile, collapsedTrackletFile)
        trackletFile = collapsedTrackletFile

        # If collapseTracklets deleted any tracklets, set deletedBy to 2
        if len(deleted_by_collapse_ind) > 0:
            allTracklets.loc[allTracklets[prev_line_col].isin(deleted_by_collapse_ind), "deletedBy"] = 2
        
        # If collapseTracklets created any tracklets, create temporary allTracklets and trackletMember
        # DataFrames for the new tracklets
        if len(created_by_collapse) > 0:
            trackletMembers_temp, allTracklets_temp = _makeNewLinkageDataFrames(created_by_collapse, linkageType="trackletId", createdBy=2, idStart=allTracklets["trackletId"].max() + 1)         
            allTracklets_temp["_lineNum_2"] = created_by_collapse_inds
        
            # Combine the temporary DataFrames with the main ones
            trackletMembers = pd.concat([trackletMembers, trackletMembers_temp], ignore_index=True)
            allTracklets = pd.concat([allTracklets, allTracklets_temp], ignore_index=True)
            trackletMembers.reset_index(inplace=True, drop=True)
            allTracklets.reset_index(inplace=True, drop=True)
        
        # Fill in the line numbers for tracklets that weren't deleted or created by collapseTracklets
        total_lines_collapsed = len(allTracklets[allTracklets["createdBy"] == 2]) + len(allTracklets[(allTracklets["createdBy"] == 1) & (allTracklets["deletedBy"] == 0)])
        line_nums_collapsed = np.arange(1, total_lines_collapsed + 1)
        line_nums_not_assigned = np.in1d(line_nums_collapsed, allTracklets[allTracklets["createdBy"] == 2]["_lineNum_2"].values, invert=True)
        allTracklets.sort_values(prev_line_col, inplace=True)
        allTracklets.loc[allTracklets[(allTracklets["createdBy"] == 1) & (allTracklets["deletedBy"] == 0)].index.values, "_lineNum_2"] = line_nums_collapsed[line_nums_not_assigned]          
        
        prev_line_col = "_lineNum_2"
            
    if purifiedTrackletFile is not None:
        if verbose is True:
            print("Reading {} into database...".format(purifiedTrackletFile))
        # purifyTracklets can only delete tracklets by removing individual detections (this may change)
        created_by_purify, created_by_purify_inds, deleted_by_purify_ind = _findNewLinesAndDeletedIndices(trackletFile, purifiedTrackletFile)
        trackletFile = purifiedTrackletFile
   
        # If purifyTracklets deleted any tracklets, set deletedBy to 3
        if len(deleted_by_purify_ind) > 0:
            allTracklets.loc[allTracklets[prev_line_col].isin(deleted_by_purify_ind), "deletedBy"] = 3
           
        # If purifyTracklets created any new tracklets, create temporary allTracklets and trackletMember 
        # DataFrames for the new tracklets
        if len(created_by_purify) > 0:
            trackletMembers_temp, allTracklets_temp = _makeNewLinkageDataFrames(created_by_purify, linkageType="trackletId", createdBy=3, idStart=allTracklets["trackletId"].max() + 1)
            allTracklets_temp["_lineNum_3"] = created_by_purify_inds
            
            # Combine the temporary DataFrames with the main ones
            trackletMembers = pd.concat([trackletMembers, trackletMembers_temp], ignore_index=True)
            allTracklets = pd.concat([allTracklets, allTracklets_temp], ignore_index=True)
            trackletMembers.reset_index(inplace=True, drop=True)
            allTracklets.reset_index(inplace=True, drop=True)
        
        # Fill in the line numbers for tracklets that weren't deleted or created by purifyTracklets
        total_lines_purified = (len(allTracklets[allTracklets["createdBy"] == 3])
                                + len(allTracklets[((allTracklets["createdBy"] == 1) | (allTracklets["createdBy"] == 2))
                                                   & (allTracklets["deletedBy"] == 0)]))
        line_nums_purified = np.arange(1, total_lines_purified + 1)
        line_nums_not_assigned = np.in1d(line_nums_purified, allTracklets[allTracklets["createdBy"] == 3]["_lineNum_3"].values, invert=True)
        allTracklets.sort_values(prev_line_col, inplace=True)
        allTracklets.loc[allTracklets[((allTracklets["createdBy"] == 2) | (allTracklets["createdBy"] == 1)) & (allTracklets["deletedBy"] == 0)].index.values, "_lineNum_3"] = line_nums_purified[line_nums_not_assigned]          
        
        prev_line_col = "_lineNum_3"
        
    if finalTrackletFile is not None:
        if verbose is True:
            print("Reading {} into database...".format(finalTrackletFile))
        # removeSubsets can only delete tracklets (this may change)
        created_by_remove_subsets, created_by_remove_subsets_inds, deleted_by_remove_subsets_ind = _findNewLinesAndDeletedIndices(trackletFile, finalTrackletFile)
        
        # If removeSubsets deleted any tracklets, set deletedBy to 4
        if len(deleted_by_remove_subsets_ind) > 0:
            allTracklets.loc[allTracklets[prev_line_col].isin(deleted_by_remove_subsets_ind), "deletedBy"] = 4
            
        # If removeSubsets created any new tracklets, create temporary allTracklets and trackletMember 
        # DataFrames for the new tracklets
        if len(created_by_remove_subsets) > 0:    
            trackletMembers_temp, allTracklets_temp = _makeNewLinkageDataFrames(created_by_remove_subsets, linkageType="trackletId", createdBy=4, idStart=allTracklets["trackletId"].max() + 1)
            allTracklets_temp["_lineNum_4"] = created_by_remove_subsets_inds
            
            # Combine the temporary DataFrames with the main ones
            trackletMembers = pd.concat([trackletMembers, trackletMembers_temp], ignore_index=True)
            allTracklets = pd.concat([allTracklets, allTracklets_temp], ignore_index=True)
            trackletMembers.reset_index(inplace=True, drop=True)
            allTracklets.reset_index(inplace=True, drop=True)
        
        # Fill in the line numbers for tracklets that weren't deleted or created by removeSubsets
        total_lines_remove_subsets = (len(allTracklets[allTracklets["createdBy"] == 4])
                                + len(allTracklets[((allTracklets["createdBy"] == 1) | (allTracklets["createdBy"] == 2) | (allTracklets["createdBy"] == 3))
                                                   & (allTracklets["deletedBy"] == 0)]))
        line_nums_remove_subsets = np.arange(1, total_lines_remove_subsets + 1)
        line_nums_not_assigned = np.in1d(line_nums_remove_subsets, allTracklets[allTracklets["createdBy"] == 4]["_lineNum_4"].values, invert=True)
        allTracklets.sort_values(prev_line_col, inplace=True)
        allTracklets.loc[allTracklets[((allTracklets["createdBy"] == 3) | (allTracklets["createdBy"] == 2) | (allTracklets["createdBy"] == 1)) & (allTracklets["deletedBy"] == 0)].index.values, "_lineNum_4"] = line_nums_remove_subsets[line_nums_not_assigned]
        
    # Arrange allTracklet columns
    allTracklets = allTracklets[["trackletId", "numMembers", "createdBy", "deletedBy", "_lineNum_1", "_lineNum_2", "_lineNum_3", "_lineNum_4"]]
    
    # Store DataFrames in database
    trackletMembers.to_sql("TrackletMembers", con, if_exists="append", index=False)
    allTracklets.to_sql("AllTracklets", con, if_exists="append", index=False)
    if verbose is True:
        print("Done.")
        print("")
    return allTracklets, trackletMembers

def readTracksIntoDatabase(trackFile, trackOutFile, con,
                           finalTrackFile=None,
                           trackIdStart=1,
                           verbose=Config.verbose):
    """
    Read a nightly set of track files into a tracks database. 
    
    Parameters
    ----------
    trackFile : str
        Path to track file from linkTracklets.

    con : `sqlite3.Connection` or similar
        Database connection, database needs to have an allTracks and trackMembers table.
    
    finalTrackFile : str, optional
        Path to final track file (removeSubsets) for the same window as trackFile.
        [Default = None]
    
    trackIdStart : int, optional
        TrackId from which to start numbering new tracks. [Default = 1]

    verbose : bool, optional
        Print progress statements? [Default = `Config.verbose`]

    Returns
    -------
    None
    """
    if verbose is True:
        print("Reading {} into database...".format(trackFile))
    trackMembers = pd.read_csv(trackFile, header=None, names=["diaId"])
    if len(trackMembers) == 0:
        if verbose is True:
            print("{} has no tracks. Skipping.".format(trackFile))
        return
    # Create an array of integer trackIds
    trackIds = np.arange(trackIdStart, trackIdStart + len(trackMembers), dtype=int)
    trackId_max = trackIds[-1]
    # Read in the trackFile where every row is a string of diaIds delimited by whitespace
    # Split the string of diaIds into separate columns and then stack the columns so that every track has 
    # a row for every diaId
    trackMembers = pd.DataFrame(pd.DataFrame(trackMembers["diaId"].str.split(" ").tolist(), index=trackIds).stack(), columns=["diaId"])
    trackMembers.reset_index(1, drop=True, inplace=True)
    trackMembers["trackId"] = trackMembers.index
    trackMembers = trackMembers[["trackId", "diaId"]]
    # Not all tracks have the same number of detections, empty detections needs to be dropped
    trackMembers["diaId"].replace("", np.nan, inplace=True)
    trackMembers.dropna(inplace=True)
    
    allTracks = pd.DataFrame(trackMembers["trackId"].unique(), columns=["trackId"])
    allTracks["numMembers"] = trackMembers["trackId"].value_counts().sort_index().values
    allTracks["createdBy"] = np.ones(len(allTracks), dtype=int) * 5
    allTracks["deletedBy"] = np.zeros(len(allTracks), dtype=int)
    allTracks["_lineNum_5"] = np.arange(1, len(allTracks) + 1, dtype=int)
    allTracks["_lineNum_6"] = np.nan
    
    # Read in chi-squared values from trackOutFile
    chiSq = pd.read_csv(trackOutFile, sep=" ", skiprows=7, skipfooter=9, error_bad_lines=False, warn_bad_lines=False,  engine='python',
                        names=["_temp", "chiSqDec", "chiSqRa", "fitRange"])
    chiSq.drop(chiSq[chiSq["_temp"] != "chi_sq:"].index, inplace=True)
    chiSq.reset_index(drop=True, inplace=True)
    chiSq["trackId"] = allTracks["trackId"]
    chiSq.drop(['_temp'], axis = 1, inplace = True)
    allTracks = allTracks.merge(chiSq, on="trackId")
      
    if finalTrackFile is not None:
        if verbose is True:
            print("Reading {} into database...".format(finalTrackFile))
        # removeSubsets can only delete tracks (this may change)
        created_by_remove_subsets, created_by_remove_subsets_inds, deleted_by_remove_subsets_ind = _findNewLinesAndDeletedIndices(trackFile, finalTrackFile)
        
        # If removeSubsets deleted any tracks, set deletedBy to 4
        if len(deleted_by_remove_subsets_ind) > 0:
            allTracks.loc[allTracks["_lineNum_5"].isin(deleted_by_remove_subsets_ind), "deletedBy"] = 6
            
        # If removeSubsets created any new tracks, create temporary allTracks and trackMember 
        # DataFrames for the new tracks
        if len(created_by_remove_subsets) > 0:    
            trackMembers_temp, allTracks_temp = _makeNewLinkageDataFrames(created_by_remove_subsets, linkageType="trackId", createdBy=5, idStart=allTracks["trackId"].max() + 1)
            allTracks_temp["_lineNum_6"] = created_by_remove_subsets_inds
            
            # Combine the temporary DataFrames with the main ones
            trackMembers = pd.concat([trackMembers, trackMembers_temp], ignore_index=True)
            allTracks = pd.concat([allTracks, allTracks_temp], ignore_index=True)
            trackMembers.reset_index(inplace=True, drop=True)
            allTracks.reset_index(inplace=True, drop=True)
        
        # Fill in the line numbers for tracks that weren't deleted or created by removeSubsets
        total_lines_remove_subsets = (len(allTracks[allTracks["createdBy"] == 6])
                                + len(allTracks[((allTracks["createdBy"] == 5) & (allTracks["deletedBy"] == 0))]))
        line_nums_remove_subsets = np.arange(1, total_lines_remove_subsets + 1)
        line_nums_not_assigned = np.in1d(line_nums_remove_subsets, allTracks[allTracks["createdBy"] == 6]["_lineNum_6"].values, invert=True)
        allTracks.sort_values("_lineNum_5", inplace=True)
        allTracks.loc[allTracks[(allTracks["createdBy"] == 5) & (allTracks["deletedBy"] == 0)].index.values, "_lineNum_6"] = line_nums_remove_subsets[line_nums_not_assigned]

    # Arrange allTrack columns
    allTracks = allTracks[["trackId", "numMembers", "createdBy", "deletedBy", "chiSqDec", "chiSqRa", "fitRange", "_lineNum_5", "_lineNum_6"]]
    
    # Store DataFrames in database
    trackMembers.to_sql("TrackMembers", con, if_exists="append", index=False)
    allTracks.to_sql("AllTracks", con, if_exists="append", index=False)
    if verbose is True:
        print("Done.")
        print("")
    return 

def buildTrackletDatabase(database, outDir,
                          verbose=Config.verbose):
    """
    Build tracklet database with AllTracklets and TrackletMembers table,
    and the Tracklets, CollapsedTracklets, PurifiedTracklets and 
    FinalTracklets views. 
    
    Parameters
    ----------
    database : str
        Database name.

    outDir : str
        Path to desired out directory for the database.

    verbose : bool, optional
        Print progress statements? [Default = `Config.verbose`]
    
    Returns
    -------
    con : `sqlite3.Connection`
        Connection to the database.

    databasePath : str
        Full path to database.
    """
    database = os.path.join(os.path.abspath(outDir), "", database)
    con = sql.connect(database)
    
    if verbose is True:
        print("Creating DiaSources table...")
    con.execute("""
        CREATE TABLE DiaSources (
            diaId INTEGER PRIMARY KEY,
            visitId INTEGER,
            objectId INTEGER,
            ra REAL,
            dec REAL,
            mjd REAL,
            mag REAL,
            snr REAL
        );
        """)

    if verbose is True:
        print("Creating AllTracklets table...")
    con.execute("""
        CREATE TABLE AllTracklets (
            trackletId INTEGER PRIMARY KEY,
            linkedObjectId INTEGER,
            numLinkedObjects INTEGER,
            numMembers INTEGER,
            velocity REAL,
            rms REAL,
            night REAL,
            createdBy INTEGER,
            deletedBy INTEGER,
            _lineNum_1 INTEGER,
            _lineNum_2 INTEGER,
            _lineNum_3 INTEGER,
            _lineNum_4 INTEGER
        );
        """)

    if verbose is True:
        print("Creating TrackletMembers table...")
    con.execute("""
        CREATE TABLE TrackletMembers (
            trackletId INTEGER,
            diaId INTEGER
        );
        """)
    
    if verbose is True:           
        print("Creating Tracklets view...")
    con.execute("""
        CREATE VIEW Tracklets AS
        SELECT * FROM AllTracklets
        WHERE createdBy = 1
        """)

    if verbose is True:
        print("Creating CollapsedTracklets view...")
    con.execute("""
        CREATE VIEW CollapsedTracklets AS
        SELECT * FROM AllTracklets
        WHERE deletedBy = 2
        OR createdBy = 2
        """)

    if verbose is True:
        print("Creating PurifiedTracklets view...")
    con.execute("""
        CREATE VIEW PurifiedTracklets AS
        SELECT * FROM AllTracklets
        WHERE deletedBy = 3
        OR createdBy = 3
        """)

    if verbose is True:
        print("Creating FinalTracklets view...")
        print("")
    con.execute("""
        CREATE VIEW FinalTracklets AS
        SELECT * FROM AllTracklets
        WHERE deletedBy = 4
        OR createdBy = 4
        """)

    return con, database

def buildTrackDatabase(database, outDir,
                       verbose=Config.verbose):
    """
    Build track database with AllTracks and TrackMembers table,
    and the Tracks and FinalTracks views.  
    
    Parameters
    ----------
    database : str
        Database name.

    outDir : str
        Path to desired out directory for the database.

    verbose : bool, optional
        Print progress statements? [Default = `Config.verbose`]
        
    Returns
    -------
    con : `sqlite3.Connection`
        Connection to the database

    databasePath : str
        Full path to database
    """
    database = os.path.join(os.path.abspath(outDir), "", database)
    con = sql.connect(database)

    if verbose is True:
        print("Creating AllTracks table...")
    con.execute("""
        CREATE TABLE AllTracks (
            trackId INTEGER PRIMARY KEY,
            linkedObjectId INTEGER,
            numLinkedObjects INTEGER,
            numMembers INTEGER,
            rms REAL,
            windowStart REAL,
            startTime REAL,
            endTime REAL,
            subsetOf INTEGER,
            createdBy INTEGER,
            deletedBy INTEGER,
            chiSqDec FLOAT,
            chiSqRa FLOAT,
            fitRange FLOAT,
            _lineNum_5 INTEGER,
            _lineNum_6 INTEGER
        );
        """)
    if verbose is True:
        print("Creating TrackMembers table...")
    con.execute("""
        CREATE TABLE TrackMembers (
            trackId INTEGER,
            diaId INTEGER
        );
        """)

    if verbose is True:
        print("Creating Tracks view...")
    con.execute("""
        CREATE VIEW Tracks AS
        SELECT * FROM AllTracks
        WHERE createdBy = 5
        """)

    if verbose is True:
        print("Creating FinalTracks view...")
        print("")
    con.execute("""
        CREATE VIEW FinalTracks AS
        SELECT * FROM AllTracks
        WHERE deletedBy = 6
        OR createdBy = 6
        """)

    return con, database

def readManyTrackletsIntoDatabase(tracker, verbose=Config.verbose):
    """
    Read many tracklet files into a single database. Adds the path to the newly created database
    to the trackletDatabase attribute of the given tracker. Saves the updated 
    tracker to the run directory. 

    Parameters
    ----------
    tracker : `analyzemops.tracker`
        A tracker populated with MOPS output files.

    verbose : bool, optional
        Print progress statements? [Default = `Config.verbose`]

    Returns
    -------
    'analyzemops.tracker'
        The updated tracker with the trackletDatabase attribute populated.
    """
    tracklet_con, tracklet_db = buildTrackletDatabase("tracklets.db", tracker.runDir)
    tracker.trackletDatabase = tracklet_db
    
    for i, trackletFile in enumerate(tracker.tracklets):
        max_tracklet_id = pd.read_sql("""SELECT MAX(trackletId) AS trackletId FROM AllTracklets""", tracklet_con)["trackletId"].values[0]
        if max_tracklet_id is not None:
            trackletIdStart = max_tracklet_id + 1
        else:
            trackletIdStart = 1
        
        kwargs = {"collapsedTrackletFile": None, 
                  "purifiedTrackletFile": None, 
                  "finalTrackletFile": None, 
                  "trackletIdStart": trackletIdStart}

        if tracker.collapsedTrackletsById is not None:
            kwargs["collapsedTrackletFile"] = tracker.collapsedTrackletsById[i]

        if tracker.purifiedTrackletsById is not None:
            kwargs["purifiedTrackletFile"] = tracker.purifiedTrackletsById[i]

        if tracker.finalTrackletsById is not None:
            kwargs["finalTrackletFile"] = tracker.finalTrackletsById[i]
            
        readTrackletsIntoDatabase(trackletFile, tracklet_con, verbose=verbose, **kwargs)
        tracker.toYaml(outDir=tracker.runDir)
        
    return tracker

def readManyTracksIntoDatabases(tracker, verbose=Config.verbose):
    """
    Read many track files into databases. Adds the paths to the newly created databases
    to the windowDatabases attribute of the given tracker. Saves the updated 
    tracker to the run directory. 

    Parameters
    ----------
    tracker : `analyzemops.tracker`
        A tracker populated with MOPS output files.

    verbose : bool, optional
        Print progress statements? [Default = `Config.verbose`]

    Returns
    -------
    'analyzemops.tracker'
        The updated tracker with the windowDatabases attribute populated.
    """
    tracker.windowDatabases = []
    trackIdStart = 1
    
    for i, (trackFile, trackOutFile) in enumerate(zip(tracker.tracks, tracker.trackOuts)):
        track_con, track_db = buildTrackDatabase(trackFile.split("/")[-1].split(".")[0] + ".db", tracker.runDir)
        tracker.windowDatabases.append(track_db)
        
        kwargs = {"finalTrackFile": None, 
                  "trackIdStart": trackIdStart}

        if tracker.finalTracks is not None:
            kwargs["finalTrackFile"] = tracker.finalTracks[i]
            
        readTracksIntoDatabase(trackFile, trackOutFile, track_con, verbose=verbose, **kwargs)
        
        max_track_id = pd.read_sql("""SELECT MAX(trackId) AS trackId FROM AllTracks""", track_con)["trackId"].values[0]
        if max_track_id is None:
            max_track_id = max_track_id_old
        max_track_id_old = max_track_id
        trackIdStart = max_track_id + 1
        
        tracker.toYaml(outDir=tracker.runDir) 
    return tracker

def _findNewLinesAndDeletedIndices(file1, file2):
    """
    Find new lines and the indices of deleted lines between two files. Compares file one and 
    two, and return the new lines and their indices in file two and the indices of lines deleted in file one. 

    Parameters
    ----------
    file1 : str
        Path to file one.

    file2 : str
        Path to file two.
    
    Returns
    -------
    list
        A list of the new lines in file 2.

    `numpy.ndarray`
        Indices (line numbers) of new lines in file 2.

    `numpy.ndarray`
        Indices (line numbers) of lines deleted in file 1.
    """
    file1In = open(file1, "r")
    file2In = open(file2, "r")
    
    # Here we use unified_diff. Unfortunately, at this stage ndiff would be more informative with
    #  regards to index tracking however it is dreadfully slow with big files due to a series 
    #  of internal nested for loops. 
    udiff = list(difflib.unified_diff(file1In.readlines(), file2In.readlines(), n=0))
    
    new_lines = []
    new_line_nums = []
    deleted_lines = []
    deleted_line_nums = []

    
    for line in udiff[2:]:
        line_elements = line.split()
        if line_elements[0] == '@@':
            file1_index = int(line_elements[1].split(",")[0][1:])
            file2_index = int(line_elements[2].split(",")[0][1:])
        else:
            if line_elements[0][0] == "+":
                # This line only exists in file two. 
                # Lets add this line to a list of newly 
                #  created lines. 
                new_lines.append(line[1:-2])
                new_line_nums.append(file2_index)
                file2_index += 1
            elif line_elements[0][0] == "-":
                # This line only exists in file one.
                # Lets append the index to our list of deleted
                #  line numbers.
                deleted_lines.append(line)
                deleted_line_nums.append(file1_index)
                file1_index += 1
            
    return new_lines, np.array(new_line_nums), np.array(deleted_line_nums)

def _makeNewLinkageDataFrames(newLines, linkageType="trackletId", createdBy=1, idStart=1):
    """
    Create a linkage members dataframe from a new set of lines.
    
    Parameters
    ----------
    newLines : list 
        List of strings with new linkages.

    linkageType : str, optional
        One of trackletId or trackId. [Default = 'trackletId']

    createdBy : int, optional
        If linkage was created by findTracklets: 1, collapseTracklets: 2, purifyTracklets: 3,
        removeSubsets (on Tracklets): 4, linkTracklets: 5, removeSubsets (on Tracks): 6
        [Default = 1]

    idStart : int, optional
        Linkage ID number from which to start assigning new linkage IDs.
        [Default = 1]
        
    Returns
    -------
    `pandas.DataFrame`
        LinkageMembers DataFrame: Column of linkage IDs with one row per member detection ID.
    
    `pandas.DataFrame`
        AllLinkages DataFrame: Column of linkage IDs with one row per linkage, with columns of createdBy and 
        numMembers.
    """
    # Assign linkage ids 
    ids = np.arange(idStart, idStart + len(newLines), dtype=int)
    # Create a dataframe with new linkages
    # Read in the trackletFile where every row is a string of diaIds delimited by whitespace
    # Split the string of diaIds into separate columns and then stack the columns so that every tracklet has 
    # a row for every diaId
    linkageMembers = pd.DataFrame(newLines, columns=["diaId"])
    # Split string of diaIds and stack them 
    linkageMembers = pd.DataFrame(pd.DataFrame(linkageMembers["diaId"].str.split(" ").tolist(), index=ids).stack(), columns=["diaId"])
    # Reset the index to account for stacking
    linkageMembers.reset_index(1, drop=True, inplace=True)
    linkageMembers[linkageType] = linkageMembers.index
    linkageMembers = linkageMembers[[linkageType, "diaId"]]
    linkageMembers["diaId"].replace("", np.nan, inplace=True)
    linkageMembers.dropna(inplace=True)
    
    allLinkages = pd.DataFrame(linkageMembers[linkageType].unique(), columns=[linkageType])
    allLinkages["numMembers"] = linkageMembers[linkageType].value_counts().sort_index().values
    allLinkages["createdBy"] = np.ones(len(allLinkages), dtype=int)*createdBy
    allLinkages["deletedBy"] = np.zeros(len(allLinkages), dtype=int)
    
    return linkageMembers, allLinkages

