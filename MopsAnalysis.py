import os
import time
import yaml
import random
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

SAMPLE_SIZE_PER_NIGHT = 50

class runAnalysis(object):

    def __init__(self, parameters, tracker):

        self._parameters = parameters
        self._tracker = tracker
        self._nights = []
        self._windows = []
        self._uniqueObjects = {}
        self._findableObjects = {}
        self._foundObjects = {}
        self._missedObjects = {}
        self._totalTracks = {}
        self._trueTracks = {}
        self._falseTracks = {}
        self._trueTracksSample = {}
        self._falseTracksSample = {}
        self._totalTracklets = {}
        self._trueTracklets = {}
        self._falseTracklets = {}
        self._trueTrackletsSample = {}
        self._falseTrackletsSample = {}
        self._totalCollapsedTracklets = {}
        self._trueCollapsedTracklets = {}
        self._falseCollapsedTracklets = {}
        self._trueCollapsedTrackletsSample = {}
        self._falseCollapsedTrackletsSample = {}
        self._totalPurifiedTracklets = {}
        self._truePurifiedTracklets = {}
        self._falsePurifiedTracklets = {}
        self._truePurifiedTrackletsSample = {}
        self._falsePurifiedTrackletsSample = {}
        self._totalFinalTracklets = {}
        self._trueFinalTracklets = {}
        self._falseFinalTracklets = {}
        self._trueFinalTrackletsSample = {}
        self._falseFinalTrackletsSample = {}
        self._startTime = 0
        self._endTime = 0

        self.findNights()
        self.findWindows()
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

    def findNights(self):
        for detFile in self.tracker.diaSources:
            self._nights.append(MopsReader.readNight(detFile))

    def findWindows(self):
        for trackFile in self.tracker.tracks:
            self._windows.append(MopsReader.readWindow(trackFile))

    def analyze(self, tracklets=True, collapsedTracklets=True, purifiedTracklets=True, finalTracklets=True, tracks=True):

        self._startTime = time.ctime()

        if tracklets:
            for night, trackletFile, detFile in zip(self.nights, self.tracker.tracklets, self.tracker.diaSources):
                true_tracklets, false_tracklets, true_tracklets_num, false_tracklets_num, total_tracklets_num = analyzeTracklets(trackletFile, detFile)

                self._totalTracklets[night] = total_tracklets_num
                self._trueTracklets[night] = true_tracklets_num
                self._falseTracklets[night] = false_tracklets_num
                self._trueTrackletsSample[night] = selectSample(true_tracklets)
                self._falseTrackletsSample[night] = selectSample(false_tracklets)
                
                print ""

        if collapsedTracklets:
            for night, trackletFile, detFile in zip(self.nights, self.tracker.collapsedTrackletsById, self.tracker.diaSources):
                true_tracklets, false_tracklets, true_tracklets_num, false_tracklets_num, total_tracklets_num = analyzeTracklets(trackletFile, detFile)

                self._totalCollapsedTracklets[night] = total_tracklets_num
                self._trueCollapsedTracklets[night] = true_tracklets_num
                self._falseCollapsedTracklets[night] = false_tracklets_num
                self._trueCollapsedTrackletsSample[night] = selectSample(true_tracklets)
                self._falseCollapsedTrackletsSample[night] = selectSample(false_tracklets)
                
                print ""

        if purifiedTracklets:
            for night, trackletFile, detFile in zip(self.nights, self.tracker.purifiedTrackletsById, self.tracker.diaSources):
                true_tracklets, false_tracklets, true_tracklets_num, false_tracklets_num, total_tracklets_num = analyzeTracklets(trackletFile, detFile)

                self._totalPurifiedTracklets[night] = total_tracklets_num
                self._truePurifiedTracklets[night] = true_tracklets_num
                self._falsePurifiedTracklets[night] = false_tracklets_num
                self._truePurifiedTrackletsSample[night] = selectSample(true_tracklets)
                self._falsePurifiedTrackletsSample[night] = selectSample(false_tracklets)
                
                print ""

        if finalTracklets:
            for night, trackletFile, detFile in zip(self.nights, self.tracker.finalTrackletsById, self.tracker.diaSources):
                true_tracklets, false_tracklets, true_tracklets_num, false_tracklets_num, total_tracklets_num = analyzeTracklets(trackletFile, detFile)

                self._totalFinalTracklets[night] = total_tracklets_num
                self._trueFinalTracklets[night] = true_tracklets_num
                self._falseFinalTracklets[night] = false_tracklets_num
                self._trueFinalTrackletsSample[night] = selectSample(true_tracklets)
                self._falseFinalTrackletsSample[night] = selectSample(false_tracklets)
                
                print ""

        if tracks:
            for window, trackFile, detFile, idsFile in zip(self.windows, self.tracker.tracks, self.tracker.dets, self.tracker.ids):
                true_tracks, false_tracks, true_tracks_num, false_tracks_num, total_tracks_num, unique_ssmids, found_ssmids, findable_ssmids = analyzeTracks(trackFile, detFile, idsFile, found_ssmids=self._foundObjects)

                self._totalTracks[window] = total_tracks_num
                self._trueTracks[window] = true_tracks_num
                self._falseTracks[window] = false_tracks_num
                self._trueTracksSample[window] = selectSample(true_tracks)
                self._falseTracksSample[window] = selectSample(false_tracks)
                
                print ""

        self._endTime = time.ctime()

        return

def selectSample(objects):
    if len(objects) < SAMPLE_SIZE_PER_NIGHT:
        return objects
    else:
        return random.sample(objects, SAMPLE_SIZE_PER_NIGHT)

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

def analyzeTracklets(trackletFile, detFile):
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
    total_tracklets_num = 0
    true_tracklets_num = 0
    false_tracklets_num = 0

    # Initialize tracklet arrays
    true_tracklets = []
    false_tracklets = []

    # Examine each line in trackletFile and read in every line
    #  as a track object. If track contains new detections (diasource)
    #  then add new source to diasource_dict. 
    for line in trackletFileIn:
        # Found a track!
        total_tracklets_num += 1
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
            true_tracklets_num += 1
            final_tracklet = tracklet(new_tracklet)
            true_tracklets.append(final_tracklet)
        else:
            # Track is false. 
            false_tracklets_num += 1
            final_tracklet = tracklet(new_tracklet)
            false_tracklets.append(final_tracklet)
        
    endTime = time.ctime()

    outFileOut.write("True tracklets: %s\n" % (true_tracklets_num))
    outFileOut.write("False tracklets: %s\n" % (false_tracklets_num))
    outFileOut.write("Total tracklets: %s\n" % (total_tracklets_num))
    outFileOut.write("End time: %s\n" % (endTime))

    print "Finished analysis for %s at %s" % (os.path.basename(trackletFile), endTime)

    return true_tracklets, false_tracklets, true_tracklets_num, false_tracklets_num, total_tracklets_num

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
    total_tracks_num = 0
    true_tracks_num = 0
    false_tracks_num = 0
    unique_ssmids = countUniqueSSMIDs(dets_df)
    findable_ssmids = countFindableSSMIDs(dets_df, min_detections)

    # Initialize track arrays
    false_tracks = []
    true_tracks = []

    if found_ssmids == None:
        found_ssmids = {}

    # Examine each line in trackFile and read in every line
    #  as a track object. If track contains new detections (diasource)
    #  then add new source to diasource_dict. 
    for line in trackFileIn:
        # Found a track!
        total_tracks_num += 1
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
            true_tracks_num += 1
            final_track = track(new_track) 
            final_track.isTrue = isTrue
            final_track.rms, final_track.raRes, final_track.decRes, final_track.distances = calcRMS(final_track.diasources)
            true_tracks.append(final_track)
        else:
            # Track is false. 
            false_tracks_num += 1
            final_track = track(new_track) 
            final_track.isTrue = isTrue
            final_track.rms, final_track.raRes, final_track.decRes, final_track.distances = calcRMS(final_track.diasources)
            false_tracks.append(final_track)
        
    endTime = time.ctime()

    outFileOut.write("True tracks: %s\n" % (true_tracks_num))
    outFileOut.write("False tracks: %s\n" % (false_tracks_num))
    outFileOut.write("Total tracks: %s\n" % (total_tracks_num))
    outFileOut.write("Findable objects: %s\n" % (unique_ssmids))
    outFileOut.write("Found objects: %s\n" % (len(found_ssmids)))
    outFileOut.write("End time: %s\n" % (endTime))

    print "Finished analysis for %s at %s" % (os.path.basename(trackFile), endTime)

    return true_tracks, false_tracks, true_tracks_num, false_tracks_num, total_tracks_num, unique_ssmids, found_ssmids, findable_ssmids
