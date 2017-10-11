import os
import sqlite3
import pandas as pd

def findMissedObjects(con):
    missed_objects = pd.read_sql("""SELECT * FROM AllObjects
                                    WHERE numTrueTracks = 0
                                    AND findableAsTrack = 1;""", con)
    return missed_objects


def findFoundObjects(con):
    found_objects = pd.read_sql("""SELECT * FROM AllObjects
                                    WHERE numTrueTracks > 0;""", con)
    return found_objects


def findFindableObjects(con):
    findable_objects = pd.read_sql("""SELECT * FROM AllObjects
                                    WHERE findableAsTrack = 1;""", con)
    return findable_objects


def findMissedObjectsDetections(con):
    missed_objects_detections = pd.read_sql("""SELECT * FROM DiaSources
                                               WHERE objectId IN
                                                   (SELECT objectId FROM AllObjects
                                                    WHERE numTrueTracks = 0
                                                    AND findableAsTrack = 1)
                                               ORDER BY diaId;""", con)
    return missed_objects_detections


def findFoundObjectsDetections(con):
    found_objects_detections = pd.read_sql("""SELECT * FROM DiaSources
                                               WHERE objectId IN
                                                   (SELECT objectId FROM AllObjects
                                                    WHERE numTrueTracks > 0)
                                               ORDER BY diaId;""", con)
    return found_objects_detections


def findMissedObjectsTracklets(con):
    missed_objects_tracklets = pd.read_sql("""SELECT AllTracklets.trackletId,
                                                     DiaSources.objectId,
                                                     DiaSources.diaId,
                                                     DiaSources.ra,
                                                     DiaSources.dec,
                                                     AllTracklets.velocity,
                                                     AllTracklets.rms,
                                                     AllObjects.findableAsTrack,
                                                     AllObjects.numTrueTracks
                                               FROM AllTracklets
                                               JOIN TrackletMembers ON
                                                   AllTracklets.trackletId = TrackletMembers.trackletId
                                               JOIN DiaSources ON
                                                   TrackletMembers.diaId = DiaSources.diaId
                                               JOIN AllObjects ON
                                                   DiaSources.objectId = AllObjects.objectId
                                               WHERE AllObjects.findableAsTrack = 1
                                               AND AllObjects.numTrueTracks = 0;
                                            """, con)
    return missed_objects_tracklets


def findFoundObjectsTracklets(con):
    found_objects_tracklets = pd.read_sql("""SELECT AllTracklets.trackletId,
                                                     DiaSources.objectId,
                                                     DiaSources.diaId,
                                                     DiaSources.ra,
                                                     DiaSources.dec,
                                                     AllTracklets.velocity,
                                                     AllTracklets.rms,
                                                     AllObjects.findableAsTrack,
                                                     AllObjects.numTrueTracks
                                               FROM AllTracklets
                                               JOIN TrackletMembers ON
                                                   AllTracklets.trackletId = TrackletMembers.trackletId
                                               JOIN DiaSources ON
                                                   TrackletMembers.diaId = DiaSources.diaId
                                               JOIN AllObjects ON
                                                   DiaSources.objectId = AllObjects.objectId
                                               WHERE AllObjects.numTrueTracks > 0;
                                            """, con)
    return found_objects_tracklets


def findObjectsTracklets(con):
    tracklets = pd.read_sql("""SELECT AllTracklets.trackletId,
                                      DiaSources.objectId,
                                      DiaSources.diaId,
                                      DiaSources.ra,
                                      DiaSources.dec,
                                      AllTracklets.velocity,
                                      AllTracklets.rms,
                                      AllObjects.findableAsTrack,
                                      AllObjects.numTrueTracks
                               FROM AllTracklets
                               JOIN TrackletMembers ON
                                   AllTracklets.trackletId = TrackletMembers.trackletId
                               JOIN DiaSources ON
                                   TrackletMembers.diaId = DiaSources.diaId
                               JOIN AllObjects ON
                                    DiaSources.objectId = AllObjects.objectId;
                            """, con)
    return tracklets


def findObjectDetections(con, objectId):
    detections = pd.read_sql("""SELECT * FROM DiaSources
                                WHERE objectId = %s;""" % objectId, con)
    return detections


def findObjectTracklets(con, objectId):
    tracklets = pd.read_sql("""SELECT AllTracklets.trackletId,
                                      AllTracklets.linkedObjectId,
                                      AllTracklets.numLinkedObjects,
                                      AllTracklets.numMembers,
                                      AllTracklets.velocity,
                                      AllTracklets.rms,
                                      AllTracklets.night,
                                      AllTracklets.createdBy,
                                      AllTracklets.deletedBy,
                                      DiaSources.diaId,
                                      DiaSources.visitId,
                                      DiaSources.objectId,
                                      DiaSources.ra,
                                      DiaSources.dec,
                                      DiaSources.mjd,
                                      DiaSources.mag,
                                      DiaSources.snr
                               FROM AllTracklets
                               JOIN TrackletMembers ON
                                    AllTracklets.trackletId = TrackletMembers.trackletId
                               JOIN DiaSources ON
                                        TrackletMembers.diaId = DiaSources.diaId
                               WHERE AllTracklets.trackletId IN
                                    (SELECT TrackletMembers.trackletId
                                     FROM TrackletMembers
                                     JOIN DiaSources ON
                                         TrackletMembers.diaId = DiaSources.diaId
                                     WHERE DiaSources.objectId = %s);
                                    """ % objectId, con)
    return tracklets


def countMissedObjects(con):
    missed_objects = findMissedObjects(con)["objectId"].nunique()
    return missed_objects


def countFoundObjects(con):
    found_objects = findFoundObjects(con)["objectId"].nunique()
    return found_objects


def countFindableObjects(con):
    findable_objects = findFindableObjects(con)["objectId"].nunique()
    return findable_objects


def countTrueTracklets(con):
    true_tracklets = pd.read_sql("""SELECT AllObjects.numTrueTracklets
                                    FROM AllObjects""", con)
    return true_tracklets["numTrueTracklets"].sum()


def countFalseTracklets(con):
    false_tracklets = pd.read_sql("""SELECT AllObjects.numFalseTracklets
                                    FROM AllObjects""", con)
    return false_tracklets["numFalseTracklets"].sum()


def countTracklets(con):
    tracklets = pd.read_sql("""SELECT AllObjects.numTrueTracklets,
                                   AllObjects.numFalseTracklets
                            FROM AllObjects""", con)
    return (tracklets["numTrueTracklets"].sum() +
            tracklets["numFalseTracklets"].sum())


def countTrueCollapsedTracklets(con):
    true_collapsed_tracklets = pd.read_sql("""SELECT AllObjects.numTrueCollapsedTracklets
                                              FROM AllObjects""", con)
    return true_collapsed_tracklets["numTrueCollapsedTracklets"].sum()


def countFalseCollapsedTracklets(con):
    false_collapsed_tracklets = pd.read_sql("""SELECT AllObjects.numFalseCollapsedTracklets
                                              FROM AllObjects""", con)
    return false_collapsed_tracklets["numFalseCollapsedTracklets"].sum()


def countCollapsedTracklets(con):
    collapsed_tracklets = pd.read_sql("""SELECT AllObjects.numTrueCollapsedTracklets,
                                   AllObjects.numFalseCollapsedTracklets
                            FROM AllObjects""", con)
    return (collapsed_tracklets["numTrueCollapsedTracklets"].sum() +
            collapsed_tracklets["numFalseCollapsedTracklets"].sum())


def countTruePurifiedTracklets(con):
    true_purified_tracklets = pd.read_sql("""SELECT AllObjects.numTruePurifiedTracklets
                                              FROM AllObjects""", con)
    return true_purified_tracklets["numTruePurifiedTracklets"].sum()


def countFalsePurifiedTracklets(con):
    false_purified_tracklets = pd.read_sql("""SELECT AllObjects.numFalsePurifiedTracklets
                                              FROM AllObjects""", con)
    return false_purified_tracklets["numFalsePurifiedTracklets"].sum()


def countPurifiedTracklets(con):
    purified_tracklets = pd.read_sql("""SELECT AllObjects.numTruePurifiedTracklets,
                                   AllObjects.numFalsePurifiedTracklets
                            FROM AllObjects""", con)
    return (purified_tracklets["numTruePurifiedTracklets"].sum() +
            purified_tracklets["numFalsePurifiedTracklets"].sum())


def countTrueTracks(con):
    true_tracks = pd.read_sql("""SELECT AllObjects.numTrueTracks
                                 FROM AllObjects""", con)
    return true_tracks["numTrueTracks"].sum()


def countFalseTracks(con):
    false_tracks = pd.read_sql("""SELECT AllObjects.numFalseTracks
                                  FROM AllObjects""", con)
    return false_tracks["numFalseTracks"].sum()


def countTracks(con):
    tracks = pd.read_sql("""SELECT AllObjects.numTrueTracks,
                                   AllObjects.numFalseTracks
                            FROM AllObjects""", con)
    return tracks["numTrueTracks"].sum() + tracks["numFalseTracks"].sum()


def calcFindTrackletsEfficiency(con):
    efficiency = (countTrueTracklets(con) /
                  float(_checkZero(countTracklets(con))))
    return efficiency


def calcCollapseTrackletsEfficiency(con):
    efficiency = (countTrueCollapsedTracklets(con) /
                  float(_checkZero(countCollapsedTracklets(con))))
    return efficiency


def calcPurifyTrackletsEfficiency(con):
    efficiency = (countTruePurifiedTracklets(con) /
                  float(_checkZero(countPurifiedTracklets(con))))
    return efficiency


def calcLinkTrackletsEfficiency(con):
    efficiency = (countTrueTracks(con) /
                  float(_checkZero(countTracks(con))))
    return efficiency


def calcCompleteness(con):
    completeness = (countFoundObjects(con) /
                    float(_checkZero(countFindableObjects(con))))
    return completeness


def results(con):
    print "Completeness:                  %s" % calcCompleteness(con)
    print "Findable Objects:              %s" % countFindableObjects(con)
    print "Found Objects:                 %s" % countFoundObjects(con)
    print "Missed Objects:                %s" % countMissedObjects(con)
    print ""
    print "findTracklets Efficiency:      %s" % calcFindTrackletsEfficiency(con)
    print "True Tracklets:                %s" % countTrueTracklets(con)
    print "False Tracklets:               %s" % countFalseTracklets(con)
    print "Total Tracklets:               %s" % countTracklets(con)
    print ""
    print "collapsedTracklets Efficiency: %s" % calcCollapseTrackletsEfficiency(con)
    print "True Collapsed Tracklets:      %s" % countTrueCollapsedTracklets(con)
    print "False Collapsed Tracklets:     %s" % countFalseCollapsedTracklets(con)
    print "Total Collapsed Tracklets:     %s" % countCollapsedTracklets(con)
    print ""
    print "purifyTracklets Efficiency:    %s" % calcPurifyTrackletsEfficiency(con)
    print "True Purified Tracklets:       %s" % countTruePurifiedTracklets(con)
    print "False Purified Tracklets:      %s" % countFalsePurifiedTracklets(con)
    print "Total Purified Tracklets:      %s" % countPurifiedTracklets(con)
    print ""
    print "linkTracklets Efficiency:      %s" % calcLinkTrackletsEfficiency(con)
    print "True Tracks:                   %s" % countTrueTracks(con)
    print "False Tracks:                  %s" % countFalseTracks(con)
    print "Total Tracks:                  %s" % countTracks(con)
    return


def _checkZero(num):
    if num == 0:
        return 1
    else:
        return num
