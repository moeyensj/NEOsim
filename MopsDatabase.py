import os
import sqlite3
import pandas as pd

def buildTrackletDatabase(database, outDir):

    database = os.path.join(os.path.abspath(outDir), "", database)
    con = sqlite3.connect(database)

    print "Creating DiaSources table..."
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

    print "Creating AllObjects table..."
    con.execute("""
        CREATE TABLE AllObjects (
            objectId INTEGER PRIMARY KEY,
            numDetections INTEGER,
            findableAsTracklet BOOL,
            findableAsTrack BOOL,
            numFalseTracklets INTEGER,
            numTrueTracklets INTEGER,
            numFalseCollapsedTracklets INTEGER,
            numTrueCollapsedTracklets INTEGER,
            numFalsePurifiedTracklets INTEGER,
            numTruePurifiedTracklets INTEGER,
            numFalseFinalTracklets INTEGER,
            numTrueFinalTracklets INTEGER,
            numFalseTracks INTEGER,
            numTrueTracks INTEGER,
            numFalseFinalTracks INTEGER,
            numTrueFinalTracks INTEGER
        );
        """)

    print "Creating FoundObjects view..."
    con.execute("""
        CREATE VIEW FoundObjects AS
        SELECT * FROM AllObjects
        WHERE numTrueTracks > 0
        """)

    print "Creating MissedObjects view..."
    con.execute("""
        CREATE VIEW MissedObjects AS
        SELECT * FROM AllObjects
        WHERE numTrueTracks = 0
        """)

    print "Creating AllTracklets table..."
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
            deletedBy INTEGER
        );
        """)

    print "Creating TrackletMembers table..."
    con.execute("""
        CREATE TABLE TrackletMembers (
            trackletId INTEGER,
            diaId INTEGER
        );
        """)

    print "Creating Tracklets view..."
    con.execute("""
        CREATE VIEW Tracklets AS
        SELECT * FROM AllTracklets
        WHERE createdBy = 1
        """)

    print "Creating CollapsedTracklets view..."
    con.execute("""
        CREATE VIEW CollapsedTracklets AS
        SELECT * FROM AllTracklets
        WHERE deletedBy = 2
        OR createdBy = 2
        """)

    print "Creating PurifiedTracklets view..."
    con.execute("""
        CREATE VIEW PurifiedTracklets AS
        SELECT * FROM AllTracklets
        WHERE deletedBy = 3
        OR createdBy = 3
        """)

    print "Creating FinalTracklets view..."
    con.execute("""
        CREATE VIEW FinalTracklets AS
        SELECT * FROM AllTracklets
        WHERE deletedBy = 4
        OR createdBy = 4
        """)

    print ""

    return con, database

def buildTrackDatabase(database, outDir):

    database = os.path.join(os.path.abspath(outDir), "", database)
    con = sqlite3.connect(database)

    print "Creating AllTracks table..."
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
            deletedBy INTEGER
        );
        """)

    print "Creating TrackMembers table..."
    con.execute("""
        CREATE TABLE TrackMembers (
            trackId INTEGER,
            diaId INTEGER
        );
        """)

    print "Creating Tracks view..."
    con.execute("""
        CREATE VIEW Tracks AS
        SELECT * FROM AllTracks
        WHERE createdBy = 5
        """)

    print "Creating FinalTracks view..."
    con.execute("""
        CREATE VIEW FinalTracks AS
        SELECT * FROM AllTracks
        WHERE deletedBy = 6
        OR createdBy = 6
        """)

    print ""

    return con, database

def attachDatabases(con, databases):
    attached_names = []

    if len(databases) > 10:
        print "Warning: Cannot attach more than 10 databases..."
        print "Proceeding with the first 10 databases..."
        databases = databases[0:10]
        
    for i, window in enumerate(databases):
        attached_names.append("db%s" % i)
        print "Attaching %s to con as db%s..." % (window, i)
        con.execute("""ATTACH DATABASE '%s' AS db%s;""" % (window, i))
    return attached_names

def arrayToSqlQuery(array):
    sample = ""
    for i in array:
        sample += str(i) + ', '

    sample = '(' + sample[0:-2] + ')'
    return sample

def findTrackletMembers(con, trackletId):
    diaids = pd.read_sql("""SELECT diaId FROM TrackletMembers
                            WHERE trackletId == %s""" % (trackletId), con)["diaId"].values
    return diaids

def findTrackMembers(con, trackId, window):
    diaids = pd.read_sql("""SELECT diaId FROM %s.TrackMembers
                            WHERE trackId == %s""" % (window, trackId), con)["diaId"].values
    return diaids

def findDetections(con, diaids):
    diaids_query = arrayToSqlQuery(diaids)
    detections = pd.read_sql("""SELECT * FROM DiaSources
                                WHERE diaId IN %s""" % diaids_query, con)
    return detections

def findDetectionsWithObjectId(con, objectId):
    detections = pd.read_sql("""SELECT * FROM DiaSources
                                WHERE objectId = %s""" % objectId, con)
    return detections

def findNearbyDetections(con, ra0, dec0, ra1, dec1, night, windowSize=1):
    night_min = night
    night_max = night_min + windowSize
    
    nearby_detections = pd.read_sql_query("""SELECT * FROM DiaSources
                                            WHERE (mjd BETWEEN %f AND %f) AND (dec BETWEEN %f and %f) AND (ra BETWEEN %f AND %f)
                                            """ % (night_min, night_max, dec0, dec1, ra0, ra1), con)
    return nearby_detections

def findTrackletDetections(con, trackletId):
    diaids = findTrackletMembers(con, trackletId)
    detections = findDetections(con, diaids)
    return detections

def findTrackDetections(con, trackId, window):
    diaids = findTrackMembers(con, trackId, window)
    detections = findDetections(con, diaids)
    return detections

def findTrackletInfo(con, trackletId):
    info = pd.read_sql("""SELECT * FROM AllTracklets
                        WHERE trackletId = %s""" % trackletId, con)
    return info

def findTrackInfo(con, trackId, window):
    info = pd.read_sql("""SELECT * FROM %s.AllTracks
                        WHERE trackId = %s""" % (window, trackId), con)
    return info

def selectFalseTracklets(con):
    falseTracklets = pd.read_sql("""SELECT trackletId FROM AllTracklets
                                    WHERE linkedObjectId = -1""", con)
    return falseTracklets

def selectTrueTracklets(con):
    trueTracklets = pd.read_sql("""SELECT trackletId FROM AllTracklets
                                    WHERE linkedObjectId != -1""", con)
    return trueTracklets

def selectFalseTracks(con, window):
    falseTracks = pd.read_sql("""SELECT trackId FROM %s.AllTracks
                                    WHERE linkedObjectId = -1""" % (window), con)
    return falseTracks

def selectTrueTracks(con, window):
    trueTracks = pd.read_sql("""SELECT trackId FROM %s.AllTracks
                                    WHERE linkedObjectId != -1""" % (window), con)
    return trueTracks

def selectFindableObjectsAsTracklets(con):
    objects = pd.read_sql("""SELECT * FROM AllObjects
                                WHERE findableAsTracklet = 1""", con)
    return objects

def selectFindableObjectsAsTracks(con):
    objects = pd.read_sql("""SELECT * FROM AllObjects
                                WHERE findableAsTrack = 1""", con)
    return objects

def selectFoundObjects(con):
    objects = pd.read_sql("""SELECT * FROM AllObjects
                                WHERE numTrueTracks > 0""", con)
    return objects

def selectMissedObjects(con):
    objects = pd.read_sql("""SELECT * FROM AllObjects
                                WHERE findableAsTrack = 1
                                AND numTrueTracks = 0""", con)
    return objects

def findObjectLinkages(con, objectId, attachedWindows, onlyFalseLinkages=False):
    detections = findDetectionsWithObjectId(con, objectId)
    diaids = detections["diaId"].values

    if onlyFalseLinkages:
        tracklet_ids_all = pd.read_sql("""SELECT DISTINCT trackletId FROM TrackletMembers
                                        WHERE diaId IN %s""" % (arrayToSqlQuery(diaids)), con)["trackletId"].values
        tracklet_ids  = pd.read_sql("""SELECT DISTINCT trackletId FROM AllTracklets
                                    WHERE trackletId IN %s
                                    AND linkedObjectId = -1""" % (arrayToSqlQuery(tracklet_ids_all)), con)["trackletId"].values
        track_ids = {}
        for window in attachedWindows:
            track_ids_window = pd.read_sql("""SELECT DISTINCT trackId FROM %s.TrackMembers
                                                WHERE diaId IN %s""" % (window, arrayToSqlQuery(diaids)), con)["trackId"].values
            false_track_ids_window = pd.read_sql("""SELECT DISTINCT trackId FROM %s.AllTracks
                                                        WHERE trackId IN %s
                                                        AND linkedObjectId = -1""" % (window, arrayToSqlQuery(track_ids_window)), con)["trackId"].values
            track_ids[window] = false_track_ids_window
    else:
        tracklet_ids = pd.read_sql("""SELECT DISTINCT trackletId FROM TrackletMembers
                                        WHERE diaId IN %s""" % (arrayToSqlQuery(diaids)), con)["trackletId"].values
        track_ids = {}
        for window in attachedWindows:
            track_ids_window = pd.read_sql("""SELECT DISTINCT trackId FROM %s.TrackMembers
                                        WHERE diaId IN %s""" % (window, arrayToSqlQuery(diaids)), con)["trackId"].values
            track_ids[window] = track_ids_window 
        
    return tracklet_ids, track_ids
