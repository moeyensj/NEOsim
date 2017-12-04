import os
import sqlite3 as sql
import numpy as np
import pandas as pd

from .config import Config
from .io import buildSummaryDatabase
from .io import readManyTrackletsIntoDatabase
from .io import readManyTracksIntoDatabases

__all__ = ["calcNight", "calcFindableObjects", 
           "analyzeTracklets", "analyzeTracks",
           "createTrackletSummary", "createTrackSummary",
           "finalizeSummary", "runAnalysis", "findObjectLinkages"]


def calcNight(mjd, midnight=Config.site_midnight):
    """
    Calculate the integer night for any MJD.

    Parameters
    ----------
    mjd : float or `~numpy.ndarray`
        MJD to convert.
    midNight : float, optional
        Midnight in MJD at telescope site.
        [Default = `~analyzemops.config.site_midnight`]
    verbose : bool, optional
        Print progress statements? [Default = `~analyzemops.Config.verbose`]
        
    Returns
    -------
    int or `~numpy.ndarray`
        Night of observation
    """
    night = mjd + 0.5 - midnight
    return night.astype(int)

def calcFindableObjects(diasourcesDb, summaryDb,
                        minDetectionsPerNight=2,
                        minNightsPerWindow=3, 
                        nightsPerWindow=15,
                        ignoreSpecialIds=False,
                        specialIds=Config.detection_file_special_ids,
                        verbose=Config.verbose):
    """
    Calculates the number of objects that should be findable as a 
    tracklet and track by MOPS.

    Parameters
    ----------
    diasourcesDb : str
        Path to DIASources database. If using a tracker object, use: `~analyzemops.Tracker.diasourcesDatabase`
    summaryDb : str
        Path to summary database. If using a tracker object, use: `~analyzemops.Tracker.summaryDatabase`
    minDetectionsPerNight : int, optional
        Minimum number of detections per night. [Default = 2]
    minNightsPerWindow : int, optional
        Minimum number of night per window. [Default = 3]
    nightPerWindow : int, optional
        Window size in number of nights. [Default = 15]
    ignoreSpecialIds : bool, optional
        Ignore noise or special detections. For datasets with many
        fake detections this may be useful. [Default = False]
    specialIds : bool, optional
        If ignoreSpecialIds is True, then use these specialIds.
        [Default = `~analyzemops.Config.detection_file_special_ids`]
    verbose : bool, optional
        Print progress statements? [Default = `~analyzemops.Config.verbose`]

    Returns
    -------
    None
    
    """
    con = sql.connect(summaryDb)
    con.execute("""ATTACH DATABASE '{}' AS diasources;""".format(diasourcesDb))
    

    exp_mjds = pd.read_sql("""SELECT mjd FROM diasources.DiaSources""", con)
    exp_mjds["night"] = calcNight(exp_mjds["mjd"])
    nights = exp_mjds["night"].unique()
    
    # Define windowIds and exp date ranges
    windows = {}
    window_num = 1
    for night in nights:
        in_window = np.where((nights <= night + nightsPerWindow) & (nights >= night))[0]
        if len(in_window) >= minNightsPerWindow:
            windows[window_num] = [nights[in_window][0], nights[in_window][-1]]
            window_num += 1
    
    # Read AllWindows table (which should be empty at this stage) and 
    allWindows = pd.read_sql("""SELECT * FROM AllWindows""", con)
    allWindows = pd.DataFrame(0, index=np.arange(len(windows.keys())), columns=allWindows.columns)
    allWindows["windowId"] = windows.keys()
    
    for window in windows.keys():
        mjd_start = exp_mjds[exp_mjds["night"] == windows[window][0]]["mjd"].min()
        mjd_end = exp_mjds[exp_mjds["night"] == windows[window][1]]["mjd"].max()
        detections = pd.read_sql("""SELECT * FROM diasources.DiaSources
                                    WHERE mjd >= {} AND mjd <= {}""".format(mjd_start, mjd_end), con)
        detections["night"] = calcNight(detections["mjd"])
        
        if ignoreSpecialIds is True:
            # Lets remove specialIds
            not_special_ids = np.in1d(detections["objectId"].unique(), specialIds.values(), invert=True)
            objects_to_investigate = detections["objectId"].unique()[not_special_ids]
        else:
            objects_to_investigate = detections["objectId"].unique()

        # Count number of detections for each object
        num_detections = detections[detections["objectId"].isin(objects_to_investigate)]
        detections_per_night = pd.DataFrame({"detections": num_detections.groupby(["objectId", "night"]).size()}).reset_index()
        windowMembers = pd.DataFrame({"numDiaSources": num_detections.groupby(["objectId"]).size()}).reset_index()
        
        # Objects with equal to or more than the minimum number of detections required for a 
        # tracklet are detectable as a tracklet
        tracklet_condition = detections_per_night["detections"] >= minDetectionsPerNight
        detectable_tracklets = detections_per_night[tracklet_condition]["objectId"].unique()

        # Objects that have at least the minimum number of nights with a valid tracklet should be 
        # detectable as track
        track_condition = detections_per_night[tracklet_condition]["objectId"].value_counts() >= minNightsPerWindow
        detectable_tracks = detections_per_night[tracklet_condition]["objectId"].value_counts()[track_condition].index.values
        
        # Populate windowMembers DataFrame and save to summary database
        windowMembers["windowId"] = np.ones(len(windowMembers), dtype=int) * window
        windowMembers["findableAsTracklet"] = np.zeros(len(windowMembers), dtype=int)
        windowMembers["findableAsTrack"] = np.zeros(len(windowMembers), dtype=int)
        windowMembers["foundAsTracklet"] = np.zeros(len(windowMembers), dtype=int)
        windowMembers["foundAsTrack"] = np.zeros(len(windowMembers), dtype=int)
        windowMembers.loc[windowMembers["objectId"].isin(detectable_tracklets), "findableAsTracklet"] = 1    
        windowMembers.loc[windowMembers["objectId"].isin(detectable_tracks), "findableAsTrack"] = 1 
        windowMembers.to_sql("WindowMembers", con, index=False, if_exists="append")
        
        # Populate allWindows columns that can be populated at this stage
        columns = ["nightStart", "nightEnd", "numObjects", "numDiaSources",
                   "numObjectsFindableAsTracklet", "numObjectsFindableAsTrack"]
        allWindows.loc[allWindows["windowId"] == window, columns] = [calcNight(mjd_start),
                                                                     calcNight(mjd_end),
                                                                     detections["objectId"].nunique(),
                                                                     windowMembers["numDiaSources"].sum(),
                                                                     windowMembers["findableAsTracklet"].sum(),
                                                                     windowMembers["findableAsTrack"].sum()]
        allWindows.to_sql("AllWindows", con, index=False, if_exists="replace")
    return 

def analyzeTracklets(trackletDb, diasourcesDb, 
                     detectionsTable=Config.detection_table,
                     detsFileColumns=Config.detection_file_columns,
                     chunksize=100000,
                     verbose=Config.verbose):
    """
    Populate the AllTracklets table in trackletDb with information on the 
    truth or falseness of tracklets, the number of linked objects in each tracklet,
    the number of detections.

    TODO: Add in rms, velocity. 

    Parameters
    ----------
    trackletDb : str
        Path to tracklet database. If using a tracker object, use: `~analyzemops.Tracker.trackletDatabase`
    diasourcesDb : str
        Path to DIASources database. If using a tracker object, use: `~analyzemops.Tracker.diasourcesDatabase`
    detectionsTable : str, optional
        Name of the detections table. [Default = `~analyzemops.Config.detection_table`]
    detsFileColumns : dict, optional
        Dictionary of column mapping in detections table. 
        [Default = `~analyzemops.Config.detection_file_columns`]
    chunksize : int, optional
        Analyze tracklets in batches of this number.
        [Default = 100000]
    verbose : bool, optional
        Print progress statements? [Default = `~analyzemops.Config.verbose`]

    Returns
    -------
    None
    """
    # Connect to tracklets database and attach the detections database
    con = sql.connect(trackletDb)
    con.execute("""ATTACH DATABASE '{}' AS diasources;""".format(diasourcesDb))

    # Tracklets we are going to analyze: minimum ID <= tracketIds < maximum ID + 1
    trackletId_range = pd.read_sql("""SELECT MIN(trackletId) AS min, MAX(trackletId) AS max FROM AllTracklets""", con).values[0]
    # If there are no tracklets in this database then return
    if trackletId_range[0] is None:
        if verbose is True:
            print("There are no tracklets in this database.")
            print("")
            return
    # Add one to maximum tracklet ID to adjust boundary 
    trackletId_range[1] += 1

    trackletId_chunks = np.append(np.arange(trackletId_range[0], trackletId_range[1], chunksize), trackletId_range[1])
    if verbose:
        print("Starting analysis for {} tracklets in {} batches of {}.".format(trackletId_range[1] - trackletId_range[0],
                                                                               len(trackletId_chunks) - 1,
                                                                               chunksize))
        print("")


    for trackletId_start, trackletId_end in zip(trackletId_chunks[:-1], trackletId_chunks[1:]):
        if verbose is True:
            print("Analyzing tracklets {} through {}...".format(trackletId_start, trackletId_end - 1))
        detections = pd.read_sql("""SELECT TrackletMembers.trackletId, Mapping.objectId, AllTracklets.numMembers FROM diasources.{0}
                                    JOIN TrackletMembers ON
                                        TrackletMembers.diaId = {0}.{1}
                                    JOIN AllTracklets ON
                                        AllTracklets.trackletId = TrackletMembers.trackletId
                                    JOIN mapping ON
                                        diasources.mapping.{2} = diasources.{0}.{2}
                                    WHERE (TrackletMembers.trackletId >= {3}
                                           AND TrackletMembers.trackletId < {4})""".format(detectionsTable,
                                                                                           detsFileColumns["diaId"],
                                                                                           detsFileColumns["objectId"],
                                                                                           trackletId_start,
                                                                                           trackletId_end), con) 
        # Drop duplicate rows, true tracklets will now only be present once with false tracklets 
        # occurent multiple times
        if verbose is True:
            print("Counting numbers of linked objects in each tracklet...")
            print("Checking if tracklets are true or false...")
        detections.drop_duplicates(inplace=True)
        unique_ids_per_tracklet = detections["trackletId"].value_counts()       
        num_linked_objects = unique_ids_per_tracklet.sort_index().values
        true_tracklets = unique_ids_per_tracklet[unique_ids_per_tracklet == 1].index.values
        true_tracklets.sort()
        linked_objects = detections[detections["trackletId"].isin(true_tracklets)]["objectId"].values
        false_tracklets =  unique_ids_per_tracklet[unique_ids_per_tracklet > 1].index.values
        false_tracklets.sort()
        if verbose is True:
            print("Found {} true tracklets...".format(len(true_tracklets)))
            print("Found {} false tracklets...".format(len(false_tracklets)))

        # Read the night of observation
        nights = pd.read_sql("""SELECT TrackletMembers.trackletId, diasources.{0}.{2} FROM TrackletMembers
                                JOIN diasources.{0} ON
                                    diasources.{0}.{1} = TrackletMembers.diaId
                                WHERE (TrackletMembers.trackletId >= {3} 
                                       AND TrackletMembers.trackletId < {4})""".format(detectionsTable,
                                                                                       detsFileColumns["diaId"],
                                                                                       detsFileColumns["mjd"],
                                                                                       trackletId_start,
                                                                                       trackletId_end), con)
        nights["night"] = calcNight(nights[detsFileColumns["mjd"]])
        nights.drop(detsFileColumns["mjd"], axis=1, inplace=True)
        nights.drop_duplicates(inplace=True)

        # Read and update the AllTracklets table
        if verbose is True:
            print("Updating AllTracklets table...")
        allTracklets = pd.read_sql("""SELECT * FROM AllTracklets
                                      WHERE trackletId >= {} AND trackletId < {}""".format(trackletId_start,
                                                                                           trackletId_end), con)
        
        allTracklets.loc[allTracklets["trackletId"].isin(true_tracklets),"linkedObjectId"] = linked_objects
        allTracklets["numLinkedObjects"] = num_linked_objects
        allTracklets["night"] = nights["night"].values
        
        # Save analyzed tracklets to a temporary table
        allTracklets.to_sql("AllTracklets_temp", con, index=False, if_exists="append")
        
        # Delete rows for analyzed tracklets from existing table
        con.execute("""DELETE FROM AllTracklets
                       WHERE trackletId >= {} AND trackletId < {}""".format(trackletId_start,
                                                                            trackletId_end))
        con.commit()
        
        # Save analyzed tracklets to existing table
        allTracklets.to_sql("AllTracklets", con, index=False, if_exists="append")
        
        # Delete redundant table 
        con.execute("""DROP TABLE AllTracklets_temp""")
        con.commit()
        if verbose is True:
            print("Done with tracklets {} through {}.".format(trackletId_start, trackletId_end - 1))
            print("")

    return 

def analyzeTracks(trackDb, diasourcesDb, 
                  detectionsTable=Config.detection_table,
                  detsFileColumns=Config.detection_file_columns,
                  chunksize=100000,
                  verbose=Config.verbose):
    """
    Populate the AllTracks table in trackDb with information on the 
    truth or falseness of tracks, the number of linked objects in each track,
    the number of detections, the arc of observation.

    TODO: Add in rms. 

    Parameters
    ----------
    trackDb : str 
        Path to track database. If using a tracker object, use: `~analyzemops.Tracker.trackDatabases`
    diasourcesDb : str
        Path to DIASources database. If using a tracker object, use: `~analyzemops.Tracker.diasourcesDatabase`
    detectionsTable : str, optional
        Name of the detections table. [Default = `~analyzemops.Config.detection_table`]
    detsFileColumns : dict, optional
        Dictionary of column mapping in detections table.
        [Default = `~analyzemops.Config.detection_file_columns`]
    chunksize : int, optional
        Analyze tracks in batches of this number.
        [Default = 100000]
    verbose : bool, optional
        Print progress statements? [Default = `~analyzemops.Config.verbose`]

    Returns
    -------
    None
    """
    con = sql.connect(trackDb)
    con.execute("""ATTACH DATABASE '{}' AS diasources;""".format(diasourcesDb))

    # Tracks we are going to analyze: minimum ID <= trackIds < maximum ID + 1
    trackId_range = pd.read_sql("""SELECT MIN(trackId) AS min, MAX(trackId) AS max FROM AllTracks""", con).values[0]
    # If there are no tracks in this database then return
    if trackId_range[0] is None:
        if verbose is True:
            print("There are no tracks in this window.")
            print("")
            return
    trackId_range[1] += 1

    trackId_chunks = np.append(np.arange(trackId_range[0], trackId_range[1], chunksize), trackId_range[1])
    if verbose:
        print("Starting analysis for {} tracks in {} batches of {}.".format(trackId_range[1] - trackId_range[0],
                                                                            len(trackId_chunks) - 1,
                                                                            chunksize))
        print("")

    for trackId_start, trackId_end in zip(trackId_chunks[:-1], trackId_chunks[1:]):
        if verbose is True:
            print("Analyzing tracks {} through {}...".format(trackId_start, trackId_end - 1))
        detections = pd.read_sql("""SELECT TrackMembers.trackId, Mapping.objectId, AllTracks.numMembers FROM diasources.{0}
                                    JOIN TrackMembers ON
                                        TrackMembers.diaId = {0}.{1}
                                    JOIN AllTracks ON
                                        AllTracks.trackId = TrackMembers.trackId
                                    JOIN mapping ON
                                        diasources.mapping.{2} = diasources.{0}.{2}
                                    WHERE (TrackMembers.trackId >= {3} 
                                           AND TrackMembers.trackId < {4})""".format(detectionsTable,
                                                                               detsFileColumns["diaId"],
                                                                               detsFileColumns["objectId"],
                                                                               trackId_start,
                                                                               trackId_end), con)
        
        # Drop duplicate rows, true tracks will now only be present once with false tracks 
        # occurent multiple times
        if verbose is True:
            print("Counting numbers of linked objects in each track...")
            print("Checking if tracks are true or false...")
        detections.drop_duplicates(inplace=True)
        unique_ids_per_track = detections["trackId"].value_counts()
        num_linked_objects = unique_ids_per_track.sort_index().values
        true_tracks = unique_ids_per_track[unique_ids_per_track == 1].index.values
        true_tracks.sort()
        linked_objects = detections[detections["trackId"].isin(true_tracks)]["objectId"].values
        false_tracks = unique_ids_per_track[unique_ids_per_track > 1].index.values
        false_tracks.sort()
        if verbose is True:
            print("Found {} true tracks...".format(len(true_tracks)))
            print("Found {} false tracks...".format(len(false_tracks)))
        
        # Read the night of observation
        nights = pd.read_sql("""SELECT TrackMembers.trackId, diasources.{0}.{2} FROM TrackMembers
                                JOIN diasources.{0} ON
                                    diasources.{0}.{1} = TrackMembers.diaId
                                WHERE (TrackMembers.trackId >= {3} 
                                       AND TrackMembers.trackId < {4})""".format(detectionsTable,
                                                                                 detsFileColumns["diaId"],
                                                                                 detsFileColumns["mjd"],
                                                                                 trackId_start,
                                                                                 trackId_end), con)
        nights["night"] = calcNight(nights[detsFileColumns["mjd"]])
        windowStartAndNight = nights.drop_duplicates(keep="first", subset=["trackId"])
        windowStartTime = windowStartAndNight[detsFileColumns["mjd"]].values
        windowNight = windowStartAndNight["night"].values
        windowEndTime = nights.drop_duplicates(keep="last", subset=["trackId"])[detsFileColumns["mjd"]].values

        if verbose is True:
            print("Updating AllTracks table...")
        allTracks = pd.read_sql("""SELECT * FROM AllTracks
                                   WHERE (trackId >= {} AND trackId < {})""".format(trackId_start,
                                                                                    trackId_end), con)
        allTracks.loc[allTracks["trackId"].isin(true_tracks), "linkedObjectId"] = linked_objects
        allTracks["numLinkedObjects"] = num_linked_objects
        allTracks["windowStart"] = windowNight
        allTracks["startTime"] = windowStartTime
        allTracks["endTime"] = windowEndTime

        # Save analyzed tracks to a temporary table
        allTracks.to_sql("AllTracks_temp", con, index=False, if_exists="replace")
        
        # Delete rows for analyzed tracks from existing table
        con.execute("""DELETE FROM AllTracks
                        WHERE trackId >= {} AND trackId < {}""".format(trackId_start,
                                                                       trackId_end))
        con.commit()
        
        # Save analyzed tracklets to existing table
        allTracks.to_sql("AllTracks", con, index=False, if_exists="append")
        
        # Delete redundant table 
        con.execute("""DROP TABLE AllTracks_temp""")
        con.commit()
        if verbose is True:
            print("Done with tracks {} through {}.".format(trackId_start, trackId_end - 1))
            print("")

    return 

def createTrackletSummary(trackletDb, diasourcesDb, summaryDb,
                          tracklets=True,
                          collapsedTracklets=True,
                          purifiedTracklets=True,
                          finalTracklets=True,
                          verbose=Config.verbose):
    """
    Populates the summary database with information on the tracklets created by 
    MOPS for each unique object.

    Parameters
    ----------
    trackletDb : str
        Path to tracklet database. If using a tracker object, use: `~analyzemops.Tracker.trackletDatabase`
    diasourcesDb : str
        Path to DIASources database. If using a tracker object, use: `~analyzemops.Tracker.diasourcesDatabase`
    summaryDb : str
        Path to summary database. If using a tracker object, use: `~analyzemops.Tracker.summaryDatabase`
    collapsedTracklets : bool, optional
        Summarize collapsed tracklets? [Default = True]
    purifiedTracklets : bool, optional
        Summarize purified trackklets? [Default = True]
    finalTracklets : bool, optional
        Summarize final tracklets? [Default = True]
    verbose : bool, optional
        Print progress statements? [Default = `~analyzemops.Config.verbose`]
    
    Returns
    -------
    None
    """
    con = sql.connect(summaryDb)
    con.execute("""ATTACH DATABASE '{}' AS diasources;""".format(diasourcesDb))
    con.execute("""ATTACH DATABASE '{}' AS tracklets;""".format(trackletDb))

    allObjects = pd.read_sql("""SELECT * FROM AllObjects""", con)
    if len(allObjects) is 0:
        # Initialize allObjects table with unique objects
        unique_objects = pd.read_sql("""SELECT DISTINCT objectId FROM diasources.DiaSources""", con)["objectId"].values
        allObjects = pd.read_sql("""SELECT * FROM AllObjects""", con)
        allObjects = pd.DataFrame(0, index=np.arange(len(unique_objects)), columns=allObjects.columns)
        allObjects["objectId"] = unique_objects
        allObjects.to_sql("AllObjects", con, index=False, if_exists="append")
    
    if tracklets is True:

        if verbose:
            print("Counting number of true tracklets per unique object...")

        numTrueTracklets = pd.read_sql("""SELECT linkedObjectId, COUNT(*) AS numTrueTracklets FROM tracklets.AllTracklets
                                          WHERE (numLinkedObjects = 1 AND createdBy = 1 AND deletedBy = 0)
                                          GROUP BY linkedObjectId, numLinkedObjects""", con)

        if verbose:
            print("Counting number of false tracklets per unique object...")

        numFalseTracklets = pd.read_sql("""SELECT diasources.DiaSources.objectId, COUNT(tracklets.AllTracklets.trackletId) AS numFalseTracklets FROM tracklets.AllTracklets
                                           JOIN tracklets.TrackletMembers ON
                                               tracklets.TrackletMembers.trackletId = tracklets.AllTracklets.trackletId
                                           JOIN diasources.DiaSources ON 
                                               diasources.DiaSources.diaId = tracklets.TrackletMembers.diaId
                                           WHERE (numLinkedObjects > 1 AND createdBy = 1 AND deletedBy = 0)
                                           GROUP BY diasources.DiaSources.objectId""", con)

        allObjects.loc[allObjects["objectId"].isin(numTrueTracklets["linkedObjectId"]), "numTrueTracklets"] = numTrueTracklets["numTrueTracklets"]
        allObjects.loc[allObjects["objectId"].isin(numFalseTracklets["objectId"]), "numFalseTracklets"] = numFalseTracklets["numFalseTracklets"]

    if collapsedTracklets is True:

        if verbose:
            print("Counting number of true collapsed tracklets per unique object...")

        numTrueCollapsedTracklets = pd.read_sql("""SELECT linkedObjectId, COUNT(*) AS numTrueCollapsedTracklets FROM tracklets.AllTracklets
                                                   WHERE (numLinkedObjects = 1 AND createdBy = 2 AND deletedBy = 0)
                                                   GROUP BY linkedObjectId, numLinkedObjects""", con)

        if verbose:
            print("Counting number of true collapsed tracklets per unique object...")

        numFalseCollapsedTracklets = pd.read_sql("""SELECT diasources.DiaSources.objectId, COUNT(tracklets.AllTracklets.trackletId) AS numFalseCollapsedTracklets FROM tracklets.AllTracklets
                                                    JOIN tracklets.TrackletMembers ON
                                                        tracklets.TrackletMembers.trackletId = tracklets.AllTracklets.trackletId
                                                    JOIN diasources.DiaSources ON 
                                                        diasources.DiaSources.diaId = tracklets.TrackletMembers.diaId
                                                    WHERE (numLinkedObjects > 1 AND createdBy = 2 AND deletedBy = 0)
                                                    GROUP BY diasources.DiaSources.objectId""", con)

        allObjects.loc[allObjects["objectId"].isin(numTrueCollapsedTracklets["linkedObjectId"]), "numTrueCollapsedTracklets"] = numTrueCollapsedTracklets["numTrueCollapsedTracklets"]
        allObjects.loc[allObjects["objectId"].isin(numFalseCollapsedTracklets["objectId"]), "numFalseCollapsedTracklets"] = numFalseCollapsedTracklets["numFalseCollapsedTracklets"]

    if purifiedTracklets is True:

        if verbose is True:
            print("Counting number of true purified tracklets per unique object...")

        numTruePurifiedTracklets = pd.read_sql("""SELECT linkedObjectId, COUNT(*) AS numTruePurifiedTracklets FROM tracklets.AllTracklets
                                                  WHERE (numLinkedObjects = 1 AND createdBy = 3 AND deletedBy = 0)
                                                  GROUP BY linkedObjectId, numLinkedObjects""", con)

        if verbose is True:
            print("Counting number of false purified tracklets per unique object...")

        numFalsePurifiedTracklets = pd.read_sql("""SELECT diasources.DiaSources.objectId, COUNT(tracklets.AllTracklets.trackletId) AS numFalsePurifiedTracklets FROM tracklets.AllTracklets
                                                   JOIN tracklets.TrackletMembers ON
                                                       tracklets.TrackletMembers.trackletId = tracklets.AllTracklets.trackletId
                                                   JOIN diasources.DiaSources ON 
                                                       diasources.DiaSources.diaId = tracklets.TrackletMembers.diaId
                                                   WHERE (numLinkedObjects > 1 AND createdBy = 3 AND deletedBy = 0)
                                                   GROUP BY diasources.DiaSources.objectId""", con)

        allObjects.loc[allObjects["objectId"].isin(numTruePurifiedTracklets["linkedObjectId"]), "numTruePurifiedTracklets"] = numTruePurifiedTracklets["numTruePurifiedTracklets"]
        allObjects.loc[allObjects["objectId"].isin(numFalsePurifiedTracklets["objectId"]), "numFalsePurifiedTracklets"] = numFalsePurifiedTracklets["numFalsePurifiedTracklets"]

    if finalTracklets is True:

        if verbose is True:
            print("Counting number of true final tracklets per unique object...")

        numTrueFinalTracklets = pd.read_sql("""SELECT linkedObjectId, COUNT(*) AS numTrueFinalTracklets FROM tracklets.AllTracklets
                                               WHERE (numLinkedObjects = 1 AND createdBy = 4 AND deletedBy = 0)
                                               GROUP BY linkedObjectId, numLinkedObjects""", con)

        if verbose is True:
            print("Counting number of false final tracklets per unique object...")

        numFalseFinalTracklets = pd.read_sql("""SELECT diasources.DiaSources.objectId, COUNT(tracklets.AllTracklets.trackletId) AS numFalseFinalTracklets FROM tracklets.AllTracklets
                                                JOIN tracklets.TrackletMembers ON
                                                    tracklets.TrackletMembers.trackletId = tracklets.AllTracklets.trackletId
                                                JOIN diasources.DiaSources ON 
                                                    diasources.DiaSources.diaId = tracklets.TrackletMembers.diaId
                                                WHERE (numLinkedObjects > 1 AND createdBy = 4 AND deletedBy = 0)
                                                GROUP BY diasources.DiaSources.objectId""", con)

        allObjects.loc[allObjects["objectId"].isin(numTrueFinalTracklets["linkedObjectId"]), "numTrueFinalTracklets"] = numTrueFinalTracklets["numTrueFinalTracklets"]
        allObjects.loc[allObjects["objectId"].isin(numFalseFinalTracklets["objectId"]), "numFalseFinalTracklets"] = numFalseFinalTracklets["numFalseFinalTracklets"]


    if verbose is True:
        print("Saving AllObjects table to summary database...")
        print("")
    allObjects.to_sql("AllObjects", con, index=False, if_exists="replace")

    return

def createTrackSummary(trackDb, diasourcesDb, summaryDb,
                       tracks=True,
                       finalTracks=True,
                       verbose=Config.verbose):
    """
    Populates the summary database with information on the tracks created by 
    MOPS for each unique object.

    Parameters
    ----------
    trackDb : str
        Path to the tracks database.
    diasourcesDb : str
        Path to DIASources database. If using a tracker object, use: `~analyzemops.Tracker.diasourcesDatabase`
    summaryDb : str
        Path to summary database. If using a tracker object, use: `~analyzemops.Tracker.summaryDatabase`
    tracks : bool, optional
        Summarize tracks? [Default = True]
    finalTracks : bool, optional
        Summarize final tracks? [Default = True]
    verbose : bool, optional
        Print progress statements? [Default = `~analyzemops.Config.verbose`]

    Returns
    -------
    None
    """

    con = sql.connect(summaryDb)
    con.execute("""ATTACH DATABASE '{}' AS diasources;""".format(diasourcesDb))
    con.execute("""ATTACH DATABASE '{}' AS tracks;""".format(trackDb))

    allObjects = pd.read_sql("""SELECT * FROM AllObjects""", con)
    if len(allObjects) is 0:
        # Initialize allObjects table with unique objects
        unique_objects = pd.read_sql("""SELECT DISTINCT objectId FROM diasources.DiaSources""", con)["objectId"].values
        allObjects = pd.read_sql("""SELECT * FROM AllObjects""", con)
        allObjects = pd.DataFrame(0, index=np.arange(len(unique_objects)), columns=allObjects.columns)
        allObjects["objectId"] = unique_objects
        allObjects.to_sql("AllObjects", con, index=False, if_exists="append")

    if tracks is True:

        if verbose:
            print("Counting number of true tracks per unique object...")

        numTrueTracks = pd.read_sql("""SELECT linkedObjectId, COUNT(*) AS numTrueTracks FROM tracks.AllTracks
                                          WHERE (numLinkedObjects = 1 AND createdBy = 5 AND deletedBy = 0)
                                          GROUP BY linkedObjectId, numLinkedObjects""", con)

        if verbose:
            print("Counting number of false tracks per unique object...")

        numFalseTracks = pd.read_sql("""SELECT diasources.DiaSources.objectId, COUNT(tracks.AllTracks.trackId) AS numFalseTracks FROM tracks.AllTracks
                                        JOIN tracks.TrackMembers ON
                                            tracks.TrackMembers.trackId = tracks.AllTracks.trackId
                                        JOIN diasources.DiaSources ON 
                                            diasources.DiaSources.diaId = tracks.TrackMembers.diaId
                                        WHERE (numLinkedObjects > 1 AND createdBy = 5 AND deletedBy = 0)
                                        GROUP BY diasources.DiaSources.objectId""", con)

        allObjects.loc[allObjects["objectId"].isin(numTrueTracks["linkedObjectId"]), "numTrueTracks"] += numTrueTracks["numTrueTracks"]
        allObjects.loc[allObjects["objectId"].isin(numTrueTracks["linkedObjectId"]) == False, "numTrueTracks"] += 0

        allObjects.loc[allObjects["objectId"].isin(numFalseTracks["objectId"]), "numFalseTracks"] += numFalseTracks["numFalseTracks"]
        allObjects.loc[allObjects["objectId"].isin(numFalseTracks["objectId"]) == False, "numFalseTracks"] += 0

    if finalTracks is True:

        if verbose is True:
            print("Counting number of true final tracks per unique object...")

        numTrueFinalTracks = pd.read_sql("""SELECT linkedObjectId, COUNT(*) AS numTrueFinalTracks FROM tracks.AllTracks
                                            WHERE (numLinkedObjects = 1 AND createdBy = 6 AND deletedBy = 0)
                                            GROUP BY linkedObjectId, numLinkedObjects""", con)

        if verbose is True:
            print("Counting number of false final tracks per unique object...")

        numFalseFinalTracks = pd.read_sql("""SELECT diasources.DiaSources.objectId, COUNT(tracks.AllTracks.trackId) AS numFalseFinalTracks FROM tracks.AllTracks
                                             JOIN tracks.TrackMembers ON
                                                 tracks.TrackMembers.trackId = tracks.AllTracks.trackId
                                             JOIN diasources.DiaSources ON 
                                                 diasources.DiaSources.diaId = tracks.TrackMembers.diaId
                                             WHERE (numLinkedObjects > 1 AND createdBy = 6 AND deletedBy = 0)
                                             GROUP BY diasources.DiaSources.objectId""", con)

        allObjects.loc[allObjects["objectId"].isin(numTrueFinalTracks["linkedObjectId"]), "numTrueFinalTracks"] += numTrueFinalTracks["numTrueFinalTracks"]
        allObjects.loc[allObjects["objectId"].isin(numTrueFinalTracks["linkedObjectId"]) == False, "numTrueFinalTracks"] += 0

        allObjects.loc[allObjects["objectId"].isin(numFalseFinalTracks["objectId"]), "numFalseFinalTracks"] += numFalseFinalTracks["numFalseFinalTracks"]
        allObjects.loc[allObjects["objectId"].isin(numFalseFinalTracks["objectId"]) == False, "numFalseFinalTracks"] += 0


    if verbose is True:
        print("Saving AllObjects table to summary database...")
        print("")
    allObjects.to_sql("AllObjects", con, index=False, if_exists="replace")

    return 

def finalizeSummary(summaryDb, diasourcesDb, trackletDb, trackDbs,
                    tracklets=True,
                    collapsedTracklets=True,
                    purifiedTracklets=True,
                    finalTracklets=True,
                    tracks=True,
                    finalTracks=True,
                    verbose=Config.verbose):
    """
    Finalize run summary by populating the remaining columns AllWindows, WindowMembers and AllObjects tables
    using the results of tracklet and track summaries. 

    Must have run both `~analyzemops.analysis.createTrackletSummary` and `~analyzemops.analysis.createTrackSummary`

    TODO: Raise error on tracklet and track summary if not previously run.

    Parameters
    ----------
    summaryDb : str
        Path to summary database. If using a tracker object, use: `~analyzemops.Tracker.summaryDatabase`
    diasourcesDb : str
        Path to DIASources database. If using a tracker object, use: `~analyzemops.Tracker.diasourcesDatabase`
    trackletDb : str
        Path to tracklet database. If using a tracker object, use: `~analyzemops.Tracker.trackletDatabase`
    trackDbs : str 
        Path to track databases. If using a tracker object, use: `~analyzemops.Tracker.trackDatabases`
    collapsedTracklets : bool, optional
        Finalize summary for collapsed tracklets? [Default = True]
    purifiedTracklets : bool, optional
        Finalize summary for purified trackklets? [Default = True]
    finalTracklets : bool, optional
        Finalize summary for final tracklets? [Default = True]
    tracks : bool, optional
        Finalize summary for tracks? [Default = True]
    finalTracks : bool, optional
        Finalize summary for final tracks? [Default = True]
    verbose : bool, optional
        Print progress statements? [Default = `~analyzemops.Config.verbose`]

    Returns
    -------
    None
    """
    con = sql.connect(summaryDb)
    con.execute("""ATTACH DATABASE '{}' AS tracklets;""".format(trackletDb))
    con.execute("""ATTACH DATABASE '{}' as diasources;""".format(diasourcesDb))
    allWindows = pd.read_sql("""SELECT * FROM AllWindows""", con)
    windowIds = allWindows["windowId"].values
    
    for window in windowIds:

        if verbose is True:
            print("Finalizing summary for window ID: {}".format(window))

        try:
            trackDb = trackDbs[window-1]
        except:
            tracks = False
            finalTracks = False
        
        con.execute("""ATTACH DATABASE '{}' AS tracks;""".format(trackDb))
        windowMembers = pd.read_sql("""SELECT * FROM WindowMembers
                                       WHERE windowId = {}""".format(window), con)

        night_start = allWindows[allWindows["windowId"] == window]["nightStart"].values[0]
        night_end = allWindows[allWindows["windowId"] == window]["nightEnd"].values[0]
        true_tracklets = 0
        false_tracklets = 0
        true_tracks = 0
        false_tracks = 0
        
        if tracklets is True:

            if verbose:
                print("Counting total number of true tracklets...")

            numTrueTracklets = pd.read_sql("""SELECT linkedObjectId, COUNT(*) AS numTrueTracklets FROM tracklets.AllTracklets
                                              WHERE (numLinkedObjects = 1 AND createdBy = 1 AND deletedBy = 0 
                                                     AND night >= {} AND night <= {})
                                              GROUP BY linkedObjectId, numLinkedObjects""".format(night_start, night_end), con)
            total_numTrueTracklets = numTrueTracklets["numTrueTracklets"].sum()
            allWindows.loc[allWindows["windowId"] == window, "numTrueTracklets"] = total_numTrueTracklets
            true_tracklets += total_numTrueTracklets

            windowMembers.loc[windowMembers["objectId"].isin(numTrueTracklets["linkedObjectId"]), "foundAsTracklet"] = 1

            if verbose:
                print("Counting total number of false tracklets...")

            numFalseTracklets = pd.read_sql("""SELECT diasources.DiaSources.objectId, COUNT(tracklets.AllTracklets.trackletId) AS numFalseTracklets FROM tracklets.AllTracklets
                                               JOIN tracklets.TrackletMembers ON
                                                   tracklets.TrackletMembers.trackletId = tracklets.AllTracklets.trackletId
                                               JOIN diasources.DiaSources ON 
                                                   diasources.DiaSources.diaId = tracklets.TrackletMembers.diaId
                                               WHERE (numLinkedObjects > 1 AND createdBy = 1 AND deletedBy = 0
                                                      AND night >= {} AND night <= {})
                                               GROUP BY diasources.DiaSources.objectId""".format(night_start, night_end), con)
            total_numFalseTracklets = numFalseTracklets["numFalseTracklets"].sum()
            allWindows.loc[allWindows["windowId"] == window, "numFalseTracklets"] = total_numFalseTracklets 
            false_tracklets += total_numFalseTracklets

        if collapsedTracklets is True:

            if verbose:
                print("Counting total number of true collapsed tracklets...")

            numTrueCollapsedTracklets = pd.read_sql("""SELECT linkedObjectId, COUNT(*) AS numTrueCollapsedTracklets FROM tracklets.AllTracklets
                                                       WHERE (numLinkedObjects = 1 AND createdBy = 2 AND deletedBy = 0
                                                              AND night >= {} AND night <= {})
                                                       GROUP BY linkedObjectId, numLinkedObjects""".format(night_start, night_end), con)
            total_numTrueCollapsedTracklets = numTrueCollapsedTracklets["numTrueCollapsedTracklets"].sum()
            allWindows.loc[allWindows["windowId"] == window, "numTrueCollapsedTracklets"] = total_numTrueCollapsedTracklets
            true_tracklets += total_numTrueCollapsedTracklets

            windowMembers.loc[windowMembers["objectId"].isin(numTrueCollapsedTracklets["linkedObjectId"]), "foundAsTracklet"] = 1

            if verbose:
                print("Counting total number of true collapsed tracklets...")

            numFalseCollapsedTracklets = pd.read_sql("""SELECT diasources.DiaSources.objectId, COUNT(tracklets.AllTracklets.trackletId) AS numFalseCollapsedTracklets FROM tracklets.AllTracklets
                                                        JOIN tracklets.TrackletMembers ON
                                                            tracklets.TrackletMembers.trackletId = tracklets.AllTracklets.trackletId
                                                        JOIN diasources.DiaSources ON 
                                                            diasources.DiaSources.diaId = tracklets.TrackletMembers.diaId
                                                        WHERE (numLinkedObjects > 1 AND createdBy = 2 AND deletedBy = 0
                                                               AND night >= {} AND night <= {})
                                                        GROUP BY diasources.DiaSources.objectId""".format(night_start, night_end), con)
            total_numFalseCollapsedTracklets = numFalseCollapsedTracklets["numFalseCollapsedTracklets"].sum()
            allWindows.loc[allWindows["windowId"] == window, "numFalseCollapsedTracklets"] = total_numFalseCollapsedTracklets
            false_tracklets += total_numFalseCollapsedTracklets
        

        if purifiedTracklets is True:

            if verbose is True:
                print("Counting total number of true purified tracklets...")

            numTruePurifiedTracklets = pd.read_sql("""SELECT linkedObjectId, COUNT(*) AS numTruePurifiedTracklets FROM tracklets.AllTracklets
                                                      WHERE (numLinkedObjects = 1 AND createdBy = 3 AND deletedBy = 0
                                                             AND night >= {} AND night <= {})
                                                      GROUP BY linkedObjectId, numLinkedObjects""".format(night_start, night_end), con)
            total_numTruePurifiedTracklets = numTruePurifiedTracklets["numTruePurifiedTracklets"].sum()
            allWindows.loc[allWindows["windowId"] == window, "numTruePurifiedTracklets"] = total_numTruePurifiedTracklets
            true_tracklets += total_numTruePurifiedTracklets

            windowMembers.loc[windowMembers["objectId"].isin(numTruePurifiedTracklets["linkedObjectId"]), "foundAsTracklet"] = 1

            if verbose is True:
                print("Counting total number of false purified tracklets...")

            numFalsePurifiedTracklets = pd.read_sql("""SELECT diasources.DiaSources.objectId, COUNT(tracklets.AllTracklets.trackletId) AS numFalsePurifiedTracklets FROM tracklets.AllTracklets
                                                       JOIN tracklets.TrackletMembers ON
                                                           tracklets.TrackletMembers.trackletId = tracklets.AllTracklets.trackletId
                                                       JOIN diasources.DiaSources ON 
                                                           diasources.DiaSources.diaId = tracklets.TrackletMembers.diaId
                                                       WHERE (numLinkedObjects > 1 AND createdBy = 3 AND deletedBy = 0
                                                              AND night >= {} AND night <= {})
                                                       GROUP BY diasources.DiaSources.objectId""".format(night_start, night_end), con)
            total_numFalsePurifiedTracklets = numFalsePurifiedTracklets["numFalsePurifiedTracklets"].sum()
            allWindows.loc[allWindows["windowId"] == window, "numFalsePurifiedTracklets"] = total_numFalsePurifiedTracklets
            false_tracklets += total_numFalsePurifiedTracklets

        if finalTracklets is True:

            if verbose is True:
                print("Counting total number of true final tracklets...")

            numTrueFinalTracklets = pd.read_sql("""SELECT linkedObjectId, COUNT(*) AS numTrueFinalTracklets FROM tracklets.AllTracklets
                                                   WHERE (numLinkedObjects = 1 AND createdBy = 4 AND deletedBy = 0
                                                          AND night >= {} AND night <= {})
                                                   GROUP BY linkedObjectId, numLinkedObjects""".format(night_start, night_end), con)
            total_numTrueFinalTracklets = numTrueFinalTracklets["numTrueFinalTracklets"].sum()
            allWindows.loc[allWindows["windowId"] == window, "numTrueFinalTracklets"] = total_numTrueFinalTracklets
            true_tracklets += total_numTrueFinalTracklets

            windowMembers.loc[windowMembers["objectId"].isin(numTrueFinalTracklets["linkedObjectId"]), "foundAsTracklet"] = 1

            if verbose is True:
                print("Counting total number of false final tracklets...")

            numFalseFinalTracklets = pd.read_sql("""SELECT diasources.DiaSources.objectId, COUNT(tracklets.AllTracklets.trackletId) AS numFalseFinalTracklets FROM tracklets.AllTracklets
                                                    JOIN tracklets.TrackletMembers ON
                                                        tracklets.TrackletMembers.trackletId = tracklets.AllTracklets.trackletId
                                                    JOIN diasources.DiaSources ON 
                                                        diasources.DiaSources.diaId = tracklets.TrackletMembers.diaId
                                                    WHERE (numLinkedObjects > 1 AND createdBy = 4 AND deletedBy = 0
                                                           AND night >= {} AND night <= {})
                                                    GROUP BY diasources.DiaSources.objectId""".format(night_start, night_end), con)
            total_numFalseFinalTracklets = numFalseFinalTracklets["numFalseFinalTracklets"].sum()
            allWindows.loc[allWindows["windowId"] == window, "numFalseFinalTracklets"] = total_numFalseFinalTracklets
            false_tracklets += total_numFalseFinalTracklets

        try: 
            allWindows.loc[allWindows["windowId"] == window, "contaminationTracklets"] = false_tracklets / (true_tracklets + false_tracklets) 
        except:
            allWindows.loc[allWindows["windowId"] == window, "contaminationTracklets"] = 0

        found_as_tracklet = windowMembers["foundAsTracklet"].sum()
        allWindows.loc[allWindows["windowId"] == window, "numObjectsFoundAsTracklet"] = found_as_tracklet  
        
        if tracks: 
            
        
            if verbose:
                print("Counting total number of true tracks...")

            numTrueTracks = pd.read_sql("""SELECT linkedObjectId, COUNT(tracks.AllTracks.trackId) AS numTrueTracks FROM tracks.AllTracks
                                           WHERE (numLinkedObjects = 1 AND createdBy = 5 AND deletedBy = 0)
                                           GROUP BY linkedObjectId, numLinkedObjects""", con)
            total_numTrueTracks = numTrueTracks["numTrueTracks"].sum()
            allWindows.loc[allWindows["windowId"] == window, "numTrueTracks"] = total_numTrueTracks
            true_tracks += total_numTrueTracks

            windowMembers.loc[windowMembers["objectId"].isin(numTrueTracks["linkedObjectId"]), "foundAsTrack"] = 1

            if verbose:
                print("Counting total number of false tracks...")

            numFalseTracks = pd.read_sql("""SELECT diasources.DiaSources.objectId, COUNT(tracks.AllTracks.trackId) AS numFalseTracks FROM tracks.AllTracks
                                            JOIN tracks.TrackMembers ON
                                                tracks.TrackMembers.trackId = tracks.AllTracks.trackId
                                            JOIN diasources.DiaSources ON 
                                                diasources.DiaSources.diaId = tracks.TrackMembers.diaId
                                            WHERE (numLinkedObjects > 1 AND createdBy = 5 AND deletedBy = 0)
                                            GROUP BY diasources.DiaSources.objectId""", con)
            total_numFalseTracks = numFalseTracks["numFalseTracks"].sum()
            allWindows.loc[allWindows["windowId"] == window, "numFalseTracks"] = total_numFalseTracks
            false_tracks += total_numFalseTracks

        if finalTracks is True:

            if verbose is True:
                print("Counting total number of true final tracks...")

            numTrueFinalTracks = pd.read_sql("""SELECT linkedObjectId, COUNT(tracks.AllTracks.trackId) AS numTrueFinalTracks FROM tracks.AllTracks
                                                WHERE (numLinkedObjects = 1 AND createdBy = 6 AND deletedBy = 0)
                                                GROUP BY linkedObjectId, numLinkedObjects""", con)
            total_numTrueFalseTracks = numTrueFinalTracks["numTrueFinalTracks"].sum()
            allWindows.loc[allWindows["windowId"] == window, "numTrueFinalTracks"] = total_numTrueFalseTracks
            true_tracks += total_numTrueFalseTracks

            windowMembers.loc[windowMembers["objectId"].isin(numTrueFinalTracks["linkedObjectId"]), "foundAsTrack"] = 1

            if verbose is True:
                print("Counting total number of false final tracks...")

            numFalseFinalTracks = pd.read_sql("""SELECT diasources.DiaSources.objectId, COUNT(tracks.AllTracks.trackId) AS numFalseFinalTracks FROM tracks.AllTracks
                                                 JOIN tracks.TrackMembers ON
                                                     tracks.TrackMembers.trackId = tracks.AllTracks.trackId
                                                 JOIN diasources.DiaSources ON 
                                                     diasources.DiaSources.diaId = tracks.TrackMembers.diaId
                                                 WHERE (numLinkedObjects > 1 AND createdBy = 6 AND deletedBy = 0)
                                                 GROUP BY diasources.DiaSources.objectId""", con)
            total_numFalseFinalTracks = numFalseFinalTracks["numFalseFinalTracks"].sum()
            allWindows.loc[allWindows["windowId"] == window, "numFalseFinalTracks"] = total_numFalseFinalTracks
            false_tracks += total_numFalseFinalTracks

        windowMembers.to_sql("WindowMembersTemp", con, index=0, if_exists="append")

        try:
            allWindows.loc[allWindows["windowId"] == window, "contaminationTracks"] = false_tracks / (true_tracks + false_tracks)
        except:
            allWindows.loc[allWindows["windowId"] == window, "contaminationTracks"] = 0
        con.execute("""DETACH DATABASE 'tracks'""".format(trackDb))
        
        found_as_track = windowMembers["foundAsTrack"].sum()
        allWindows.loc[allWindows["windowId"] == window, "numObjectsFoundAsTrack"] = found_as_track
        completeness =  found_as_track / windowMembers["findableAsTrack"].sum()
        allWindows.loc[allWindows["windowId"] == window, "completeness"] = completeness
        
        if verbose is True:
            print("")

    allWindows.to_sql("AllWindows", con, index=0, if_exists="replace")
    con.execute("""DROP TABLE WindowMembers;""")
    con.execute("""ALTER TABLE WindowMembersTemp
                   RENAME TO WindowMembers;""")
    
    if verbose is True:
            print("Updating AllObjects Table...")
    allObjects = pd.read_sql("""SELECT * FROM AllObjects""", con)
    findable = pd.read_sql("""SELECT objectId, SUM(findableAsTracklet), SUM(findableAsTrack), SUM(foundAsTracklet), SUM(foundAsTrack) FROM WindowMembers
               GROUP BY objectId""", con)
    allObjects.loc[allObjects["objectId"].isin(findable[findable["SUM(findableAsTracklet)"] >= 1]["objectId"].values), "findableAsTracklet"] = 1
    allObjects.loc[allObjects["objectId"].isin(findable[findable["SUM(findableAsTrack)"] >= 1]["objectId"].values), "findableAsTrack"] = 1
    allObjects.loc[allObjects["objectId"].isin(findable[findable["SUM(foundAsTracklet)"] >= 1]["objectId"].values), "foundAsTracklet"] = 1
    allObjects.loc[allObjects["objectId"].isin(findable[findable["SUM(foundAsTrack)"] >= 1]["objectId"].values), "foundAsTrack"] = 1
    allObjects.to_sql("AllObjects", con, index=False, if_exists="replace") 
    return 

def runAnalysis(tracker, parameters,
                verbose=Config.verbose):
    """
    Run the full analysis suite on a MOPS run.

    TODO: Work on verbose outputs for increased clarity.

    Parameters
    ----------
    parameters : `~analyzemops.Parameters`
        User or default defined MOPS parameter object.
    tracker : `~analyzemops.Tracker`
        Tracker object keeps track of output files and directories.
    verbose : bool, optional
        Print progress statements? [Default = `~analyzemops.Config.verbose`]

    Returns
    -------
    None
    """
    if verbose is True:
        print("------- Analyze MOPS -------")

    # Build summary database
    summaryCon, summaryDatabase = buildSummaryDatabase("summary.db", tracker.runDir)
    tracker.summaryDatabase = summaryDatabase
    tracker.toYaml(outDir=tracker.runDir)
    
    # Find the objects that should be findable in each window. 
    calcFindableObjects(tracker.diasourcesDatabase, tracker.summaryDatabase,
                        minDetectionsPerNight=parameters.detectMin/parameters.nightMin,
                        minNightsPerWindow=parameters.nightMin, 
                        nightsPerWindow=parameters.windowSize,
                        ignoreSpecialIds=True,
                        specialIds=Config.detection_file_special_ids,
                        verbose=verbose)
    
    
    # Build tracklet database and read in tracklets
    tracker = readManyTrackletsIntoDatabase(tracker)
    
    # Build track databases and read in tracks
    tracker = readManyTracksIntoDatabases(tracker)
    
    # Analyze tracklets
    analyzeTracklets(tracker.trackletDatabase, tracker.diasourcesDatabase)
    
    # Analyze tracks
    for trackDatabase in tracker.trackDatabases:
        analyzeTracks(trackDatabase, tracker.diasourcesDatabase)
    
    # Summarize tracklet performance across run and objects
    createTrackletSummary(tracker.trackletDatabase, tracker.diasourcesDatabase, tracker.summaryDatabase)
    
    # Summarize track performance across run and objects
    for trackDatabase in tracker.trackDatabases:
        createTrackSummary(trackDatabase, tracker.diasourcesDatabase, tracker.summaryDatabase)

    # Finalize analysis across run
    finalizeSummary(tracker.summaryDatabase, tracker.diasourcesDatabase, tracker.trackletDatabase, tracker.trackDatabases,
                    tracklets=True,
                    collapsedTracklets=True,
                    purifiedTracklets=True,
                    finalTracklets=True,
                    tracks=True,
                    finalTracks=True,
                    verbose=True)
    return

def findObjectLinkages(objectId, diasourcesDb, trackletDb, trackDbs,
                       detectionsTable=Config.detection_table,
                       detsFileColumns=Config.detection_file_columns,
                       mappingTable=Config.mapping_table):
    """
    Finds an object's DIASources and any true or false tracklets and tracks
    that object may be part of. 

    TODO: Add more function comments, add more columns to dataframe outputs.

    Parameters
    ----------
    objectId : int or str
        The objectId of the object as it appears in the original data file before 
        mapping to integer IDs occurs. See `~analzemops.io.readDetectionsIntoDatabase` for more details.
    diasourcesDb : str
        Path to DIASources database. If using a tracker object, use: `~analyzemops.Tracker.diasourcesDatabase`
    trackletDb : str
        Path to tracklet database. If using a tracker object, use: `~analyzemops.Tracker.trackletDatabase`
    trackDbs : str 
        Path to track databases. If using a tracker object, use: `~analyzemops.Tracker.trackDatabases`
    detectionsTable : str, optional
        Name of the detections table. [Default = `~analyzemops.Config.detection_table`]
    detsFileColumns : dict, optional
        Dictionary of column mapping in detections table. 
        [Default = `~analyzemops.Config.detection_file_columns`]

    Returns
    -------
    `~pandas.DataFrame`
        DIASources: diaId, objectId, ra, dec
    `~pandas.DataFrame`
        Tracklets: trackletId, objectId, ra, dec
    `~pandas.DataFrame`
        Tracks: trackId, objectId, ra, dec
    """
    con = sql.connect(diasourcesDb)
    con.execute("""ATTACH DATABASE '{}' AS tracklets;""".format(trackletDb))
    
    # Find 
    diasources = pd.read_sql("""SELECT DISTINCT TrackletMembers.diaId, {0}.{4} AS objectId, {0}.{1} AS ra, {0}.{2} AS dec FROM TrackletMembers
                                   JOIN allTracklets ON
                                       allTracklets.trackletId = TrackletMembers.trackletId
                                   JOIN {0} ON
                                       {0}.{3} = TrackletMembers.diaId
                                   WHERE TrackletMembers.trackletId IN (
                                       SELECT DISTINCT trackletId FROM TrackletMembers
                                           JOIN {0} ON
                                               {0}.{3} = TrackletMembers.diaId
                                           WHERE {0}.{4} = '{5}')""".format(detectionsTable,
                                                                         detsFileColumns["ra"],
                                                                         detsFileColumns["dec"],
                                                                         detsFileColumns["diaId"],
                                                                         detsFileColumns["objectId"],
                                                                         objectId), con)
    
    
    tracklets = pd.read_sql("""SELECT TrackletMembers.trackletId, {0}.{4} AS objectId, {0}.{1} AS ra, {0}.{2} AS dec FROM TrackletMembers
                                   JOIN allTracklets ON
                                       allTracklets.trackletId = TrackletMembers.trackletId
                                   JOIN {0} ON
                                       {0}.{3} = TrackletMembers.diaId
                                   WHERE TrackletMembers.trackletId IN (
                                       SELECT DISTINCT trackletId FROM TrackletMembers
                                           JOIN {0} ON
                                               {0}.{3} = TrackletMembers.diaId
                                           WHERE {0}.{4} = '{5}')""".format(detectionsTable,
                                                                         detsFileColumns["ra"],
                                                                         detsFileColumns["dec"],
                                                                         detsFileColumns["diaId"],
                                                                         detsFileColumns["objectId"],
                                                                         objectId), con)
    tracks = []
    for trackDb in trackDbs:
        con.execute("""ATTACH DATABASE '{}' AS tracks""".format(trackDb))
        tracks.append(pd.read_sql("""SELECT TrackMembers.trackId, {0}.{4} AS objectId, {0}.{1} AS ra, {0}.{2} AS dec FROM TrackMembers
                                    JOIN allTracks ON
                                       allTracks.trackId = TrackMembers.trackId
                                    JOIN {0} ON
                                       {0}.{3} = TrackMembers.diaId
                                    WHERE TrackMembers.trackId IN (
                                       SELECT DISTINCT trackId FROM TrackMembers
                                           JOIN {0} ON
                                               {0}.{3} = TrackMembers.diaId
                                           WHERE {0}.{4} = '{5}')""".format(detectionsTable,
                                                                            detsFileColumns["ra"],
                                                                            detsFileColumns["dec"],
                                                                            detsFileColumns["diaId"],
                                                                            detsFileColumns["objectId"],
                                                                            objectId), con))
        con.execute("""DETACH DATABASE tracks""")
    tracks = pd.concat(tracks)
    tracks.reset_index(inplace=True, drop=True)
        
    return diasources, tracklets, tracks