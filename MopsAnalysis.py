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

def countSSMIDs(dataframe):
    return dataframe['ssmid'].nunique()

def calcAngularDistance(a, b):
    """ return distance between a and b, where a and b are angles in degrees. """
    while abs(a - b) > 180:
        if a > b:
            b += 360.
        else:
            a += 360.
    return a - b

def convertToStandardDegrees(angle):
    while angle > 360.:
        angle -= 360.
    while angle < 0.:
        angle += 360.
    return angle

def calcGreatCircleDistance(RA0, Dec0, RA1, Dec1):
    """
    return the great-circle distance between two points on the sky,
    uses haversine formula
    """
    deg_to_rad = numpy.pi / 180.
    rad_to_deg = 180. / numpy.pi

    RADist = angularDistance(RA0, RA1);
    DecDist = angularDistance(Dec0, Dec1);    
    #convert all factors to radians
    RADist = deg_to_rad*convertToStandardDegrees(RADist);
    DecDist = deg_to_rad*convertToStandardDegrees(DecDist);
    Dec0 = deg_to_rad*convertToStandardDegrees(Dec0);
    Dec1 = deg_to_rad*convertToStandardDegrees(Dec1);
    r = 2*numpy.arcsin(numpy.sqrt( (numpy.sin(DecDist/2.))**2 + 
                                 numpy.cos(Dec0)*numpy.cos(Dec1)*(numpy.sin(RADist/2))**2) );
    #back to degrees
    return rad_to_deg*r;

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
    
def getRmsForTrack(dets, lineNum):
    t0 = min(map(lambda x: x.mjd, dets))
    ras = []
    decls = []
    mjds = []
    for det in dets:
        ras.append(det.ra)
        decls.append(det.dec)
        mjds.append(det.mjd - t0)
    ras = makeContiguous(ras)
    decls = makeContiguous(decls)
    ras = numpy.array(ras)
    decls = numpy.array(decls)
    mjds = numpy.array(mjds)

    raFunc, raRes, rank, svd, rcond = numpy.polyfit(mjds, ras, 2, full=True)
    decFunc, decRes, rank, svd, rcond = numpy.polyfit(mjds, decls, 2, full=True)
    raFunc = numpy.poly1d(raFunc)
    decFunc = numpy.poly1d(decFunc)

    #now get the euclidean distance between predicted and observed for each point
    netSqDist = 0.0
    dists = []
    for i in range(len(mjds)):
        predRa = raFunc(mjds[i])
        predDec = decFunc(mjds[i])
        dist = greatCircleDistance(predRa, predDec, ras[i], decls[i])
        dists.append(dist)
        if (dist > .1):
            print "Unexpected weirdness at line number %i, diasource had angular distance of %f from best-fit curve prediction" % (lineNum, dist)
            print "Predicted RA, Dec were ", predRa, predDec
            print "observed RA, Dec were ", ras[i], decls[i]
            print "all RAs were ", ras
            print "all decs were ", decls
        sqDist = dist**2
        #print "got euclidean distance was ", sqDist
        netSqDist += sqDist

    rms = numpy.sqrt(netSqDist / len(dets))
    if (rms > .1):
        print "Unexpected weirdness at line number %i, RMS error was %f " % (lineNum, rms)
    return rms, raRes, decRes, dists

def analyzeTrackFile(trackFile):
    trackFileIn = open(trackFile, "r")
    for line in TrackFileIn:
        track(*MopsReader.readTrack(line))

class runAnalysis(object):

    def __init__(self, parameters, tracker):

        self._parameters = parameters
        self._tracker = tracker
              
        self._foundObjects = None
        self._missedObjects = None
        self._totalTracklets = None
        self._trueTracklets = None
        self._falseTracklets = None
        self._totalTracks = None
        self._trueTracks = None
        self._falseTracks = None



