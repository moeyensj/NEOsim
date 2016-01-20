import os
import time
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import MopsPlotter
import MopsReader
from MopsObjects import diasource
from MopsObjects import tracklet
from MopsObjects import track
from MopsParameters import MopsParameters
from MopsTracker import MopsTracker

class runAnalysis(object):

    def __init__(self, parameters, tracker):

        self._parameters = parameters
        self._tracker = tracker
        self._uniqueObjects = 0
        self._findableObjects = 0
        self._foundObjects = {}
        self._missedObjects = 0
        self._totalTracks = 0
        self._trueTracks = 0
        self._falseTracks = 0
        self._totalTracklets = 0
        self._trueTracklets = 0
        self._falseTracklets = 0
        self._totalCollapsedTracklets = 0
        self._trueCollapsedTracklets = 0
        self._falseCollapsedTracklets = 0
        self._totalPurifiedTracklets = 0
        self._truePurifiedTracklets = 0
        self._falsePurifiedTracklets = 0
        self._totalFinalTracklets = 0
        self._trueFinalTracklets = 0
        self._falseFinalTracklets = 0
        self._startTime = 0
        self._endTime = 0

        self.analyze()

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

    def analyze(self):

        self._startTime = time.ctime()

        for trackFile, detFile, idsFile in zip(self.tracker.tracks, self.tracker.dets, self.tracker.ids):
            true_tracks, false_tracks, total_tracks, unique_ssmids, found_ssmids, findable_ssmids = analyzeTracks(trackFile, detFile, idsFile, found_ssmids=self._foundObjects)

            self._totalTracks += total_tracks
            self._trueTracks += true_tracks
            self._falseTracks += false_tracks
            
            print ""

        self._endTime = time.ctime()

        return

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

def countUniqueSSMIDs(dataframe):
    return dataframe['ssmid'].nunique()

def countFindableSSMIDs(dataframe, min_detections):
    return np.sum(dataframe['ssmid'].value_counts() >= min_detections)

def makeContiguous(angles):
    """ given a set of angles (say, RAs or Decs of observation) which
    span a fairly short arc but may actually cross the 0/360 line,
    make these contiguous by using negative angles or whatever is
    necessary.  if this set of angles does NOT span a short arc (>180
    deg) expect all hell to break loose."""
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

def calcDegToRad(angle):
    return angle*(np.pi/180.0)

def calcRadToDeg(angle):
    return angle*(180.0/np.pi)

def calcAngularDistance(a, b):
    """ return distance between a and b, where a and b are angles in degrees. """
    while abs(a - b) > 180:
        if a > b:
            b += 360.
        else:
            a += 360.
    return a - b

def calcGreatCircleDistance(ra0, dec0, ra1, dec1):
    """
    return the great-circle distance between two points on the sky,
    uses haversine formula
    """
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

def analyzeTracklets(trackletFile, detFile, trackletType):
    startTime = time.ctime()
    print "Starting analysis for %s at %s" % (os.path.basename(trackletFile), startTime)
    
    # Create outfile to store results
    outFile = trackletFile + ".results"
    outFileOut = open(outFile, "w")
    outFileOut.write("Start time: %s\n" % (startTime))
    print "Writing results to %s" % (outFile)
    
    # Read detections into a dataframe
    dets_df = MopsReader.readDetectionsIntoDataframe(detFile)
    
    trackletFileIn = open(trackletFile, "r")
    tracklets = []
    diasource_dict = {}
    
    # Initalize success (or failure) counters
    total_tracklets = 0
    true_tracklets = 0
    false_tracklets = 0

    # Examine each line in trackletFile and read in every line
    #  as a track object. If track contains new detections (diasource)
    #  then add new source to diasource_dict. 
    for line in trackletFileIn:
        # Found a track!
        total_tracklets += 1
        new_tracklet_diaids = MopsReader.readTracklet(line)
        new_tracklet = []
        
        # Look up each diaid in the track, check if diasource object exists.
        #  If it does exist then add it to the new track object, if not then create the object
        #  and update the diasource object dictionary.
        ssmids = []
        for diaid in new_tracklet_diaids:
            if diaid in diasource_dict:
                ssmids.append(diasource_dict[diaid].ssmid)
                new_tracklet.append(diasource_dict[diaid])
            
            else:
                new_diasource = dets_df.loc[diaid]
                new_diasource_obj = diasource(int(diaid), new_diasource['ssmid'],
                             new_diasource['obshistid'], new_diasource['ra'],
                             new_diasource['dec'], new_diasource['mjd'],
                             new_diasource['mag'], new_diasource['snr'])
                diasource_dict[diaid] = new_diasource_obj
                
                ssmids.append(diasource_dict[diaid].ssmid)
                new_tracklet.append(new_diasource_obj)
                
        isTrue = checkSSMIDs(ssmids)  
        if isTrue:
            # Track is true! 
            true_tracklets += 1
        else:
            # Track is false. 
            false_tracklets += 1
            
        final_tracklet = tracklet(new_tracklet) 
        tracklets.append(final_tracklet)
        
    endTime = time.ctime()

    outFileOut.write("True tracklets: %s\n" % (true_tracklets))
    outFileOut.write("False tracklets: %s\n" % (false_tracklets))
    outFileOut.write("Total tracklets: %s\n" % (total_tracklets))
    outFileOut.write("End time: %s\n" % (endTime))

    print "Finished analysis for %s at %s" % (os.path.basename(trackletFile), endTime)

    return true_tracklets, false_tracklets, total_tracklets


def analyzeTracks(trackFile, detFile, idsFile, found_ssmids=None, min_detections=6, verbose=True):
    startTime = time.ctime()
    print "Starting analysis for %s at %s" % (os.path.basename(trackFile), startTime)
    
    # Create outfile to store results
    outFile = trackFile + ".results"
    outFileOut = open(outFile, "w")
    outFileOut.write("Start time: %s\n" % (startTime))
    print "Writing results to %s" % (outFile)
    
    # Read detections into a dataframe
    dets_df = MopsReader.readDetectionsIntoDataframe(detFile)
    
    trackFileIn = open(trackFile, "r")
    tracks = []
    diasource_dict = {}
    
    # Initalize success (or failure) counters
    total_tracks = 0
    true_tracks = 0
    false_tracks = 0
    unique_ssmids = countUniqueSSMIDs(dets_df)
    findable_ssmids = countFindableSSMIDs(dets_df, min_detections)
    if found_ssmids == None:
        found_ssmids = {}

    # Examine each line in trackFile and read in every line
    #  as a track object. If track contains new detections (diasource)
    #  then add new source to diasource_dict. 
    for line in trackFileIn:
        # Found a track!
        total_tracks += 1
        new_track_diaids = MopsReader.readTrack(line)
        new_track = []
        
        # Look up each diaid in the track, check if diasource object exists.
        #  If it does exist then add it to the new track object, if not then create the object
        #  and update the diasource object dictionary.
        ssmids = []
        for diaid in new_track_diaids:
            if diaid in diasource_dict:
                ssmids.append(diasource_dict[diaid].ssmid)
                new_track.append(diasource_dict[diaid])
                
                if diasource_dict[diaid].ssmid in found_ssmids:
                    found_ssmids[diasource_dict[diaid].ssmid] += 1
                else:
                    found_ssmids[diasource_dict[diaid].ssmid] = 1
            
            else:
                new_diasource = dets_df.loc[diaid]
                new_diasource_obj = diasource(int(diaid), new_diasource['ssmid'],
                             new_diasource['obshistid'], new_diasource['ra'],
                             new_diasource['dec'], new_diasource['mjd'],
                             new_diasource['mag'], new_diasource['snr'])
                diasource_dict[diaid] = new_diasource_obj
                
                ssmids.append(diasource_dict[diaid].ssmid)
                new_track.append(new_diasource_obj)
                
        isTrue = checkSSMIDs(ssmids)  
        if isTrue:
            # Track is true! 
            true_tracks += 1
        else:
            # Track is false. 
            false_tracks += 1
            
        final_track = track(new_track) 
        final_track.isTrue = isTrue
        final_track.rms, final_track.raRes, final_track.decRes, final_track.distances = calcRMS(final_track.diasources)
        tracks.append(final_track)
        
    endTime = time.ctime()

    outFileOut.write("True tracks: %s\n" % (true_tracks))
    outFileOut.write("False tracks: %s\n" % (false_tracks))
    outFileOut.write("Total tracks: %s\n" % (total_tracks))
    outFileOut.write("Findable objects: %s\n" % (unique_ssmids))
    outFileOut.write("Found objects: %s\n" % (len(found_ssmids)))
    outFileOut.write("End time: %s\n" % (endTime))

    print "Finished analysis for %s at %s" % (os.path.basename(trackFile), endTime)

    return true_tracks, false_tracks, total_tracks, unique_ssmids, found_ssmids, findable_ssmids
