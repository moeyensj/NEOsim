import numpy as np
import pandas as pd

__all__ = ["tracklet", "track"]

class tracklet(object):
    def __init__(self, trackletId, diasources_num, night):
        self._trackletId = trackletId
        self._diasources = np.zeros(diasources_num, 
            dtype={"names":["diaId", "visitId", "ssmId", "ra", "dec", "mjd", "mag", "snr"], 
                    "formats":["int64","int64","int64","float64","float64","float64","float64","float64"]})
        self._info = np.zeros(1, 
            dtype={"names":["trackletId", "linkedObjectId", "numLinkedObjects", "numMembers", "velocity", "rms", "night", "createdBy", "deletedBy"],
                    "formats":["int64","int64","int64","int64","float64","float64","float64","float64","int64","int64"]})
        self._members = np.ones(diasources_num,
            dtype={"names":["trackletId", "diaId"],
                    "formats":["int64","int64"]})
        self._numMembers = diasources_num
        self._night = night
        self._isTrue = None
        self._linkedObjectId = -1
        self._numLinkedObjects = 0
        self._velocity = 0 
        self._rms = 0
        self._createdBy = 1
        self._deletedBy = 0

    @property
    def trackletId(self):
        return self._trackletId

    @trackletId.setter
    def trackletId(self, value):
        print "Cannot set trackletId!"
        
    @property
    def diasources(self):
        return self._diasources

    @diasources.setter
    def diasources(self, value):
        print "Cannot set diasources!"

    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, value):
        print "Cannot set info!"
        
    @property
    def members(self):
        return self._members

    @members.setter
    def members(self, value):
        print "Cannot set members!"

    @property
    def numMembers(self):
        return self._numMembers

    @numMembers.setter
    def numMembers(self, value):
        print "Cannot set numberMembers!"

    @property
    def night(self):
        return self._night

    @night.setter
    def night(self, value):
        print "Cannot set night!"

    @property
    def isTrue(self):
        return self._isTrue

    @isTrue.setter
    def isTrue(self, value):
        self._isTrue = value
        
    @property
    def linkedObjectId(self):
        return self._linkedObjectId

    @linkedObjectId.setter
    def linkedObjectId(self, value):
        self._linkedObjectId = value

    @property
    def numLinkedObjects(self):
        return self._numLinkedObjects

    @numLinkedObjects.setter
    def numLinkedObjects(self, value):
        self._numLinkedObjects = value

    @property
    def rms(self):
        return self._rms

    @rms.setter
    def rms(self, value):
        self._rms = value

    @property
    def createdBy(self):
        return self._createdBy

    @createdBy.setter
    def createdBy(self, value):
        self._createdBy = value

    @property
    def deletedBy(self):
        return self._deletedBy

    @deletedBy.setter
    def deletedBy(self, value):
        self._deletedBy = value

    def addDiasource(self, diasource_num, diaid, diasource):
        self._diasources[diasource_num]["diaId"] = int(diaid)
        self._diasources[diasource_num]["visitId"] = diasource["visitId"]
        self._diasources[diasource_num]["ssmId"] = diasource["ssmId"]
        self._diasources[diasource_num]["ra"] = diasource["ra"]
        self._diasources[diasource_num]["dec"] = diasource["dec"]
        self._diasources[diasource_num]["mjd"] = diasource["mjd"]
        self._diasources[diasource_num]["mag"] = diasource["mag"]
        self._diasources[diasource_num]["snr"] = diasource["snr"]

    def updateRMS(self):
        self._rms = calcRMS(self._diasources)

    def updateVelocity(self):
        self._velocity = calcVelocity(self._diasources)

    def updateQuality(self):
        self._isTrue, num_unique_ids = checkSSMIDs(self._diasources["ssmId"])
        if self._isTrue:
            self._linkedObjectId = self._diasources["ssmId"][0]
            self._numLinkedObjects = num_unique_ids
        else:
            self._linkedObjectId = -1
            self._numLinkedObjects = num_unique_ids

    def updateMembers(self):
        self._members["trackletId"] = self._members["trackletId"] * self._trackletId
        self._members["diaId"] = self._diasources["diaId"]

    def updateInfo(self):
        self._info["trackletId"] = self._trackletId 
        self._info["linkedObjectId"] = self._linkedObjectId 
        self._info["numLinkedObjects"] = self._numLinkedObjects 
        self._info["numMembers"] = self._numMembers
        self._info["velocity"] = self._velocity 
        self._info["rms"] = self._rms 
        self._info["night"] = self._night 
        self._info["createdBy"] = self._createdBy 
        self._info["deletedBy"] = self._deletedBy

    def update(self):
        self.updateVelocity()
        self.updateRMS()
        self.updateQuality()
        self.updateMembers()
        self.updateInfo()

    def toAllTrackletsDataframe(self):
        return pd.DataFrame(self._info)

    def toTrackletMembersDataframe(self):
        return pd.DataFrame(self._members)

class track(object):
    def __init__(self, trackId, diasources_num, windowStart):
        self._trackId = trackId
        self._diasources = np.zeros(diasources_num, 
            dtype={"names":["diaId", "visitId", "ssmId", "ra", "dec", "mjd", "mag", "snr"], 
                   "formats":["int64","int64","int64","float64","float64","float64","float64","float64"]})
        self._info = np.zeros(1, 
            dtype={"names":["trackId", "linkedObjectId", "numLinkedObjects", "numMembers", "rms", "windowStart", "startTime", "endTime", "subsetOf", "createdBy", "deletedBy"],
                    "formats":["int64","int64","int64","int64","float64","float64","float64","float64","int64","int64","int64"]})
        self._members = np.ones(diasources_num,
            dtype={"names":["trackId", "diaId"],
                  "formats":["int64","int64"]})
        self._numMembers = diasources_num
        self._windowStart = windowStart
        self._isTrue = None
        self._linkedObjectId = -1
        self._numLinkedObjects = 0
        self._rms = 0
        self._isSubset = None
        self._subsetOf = 0
        self._startTime = 0
        self._endTime = 0
        self._createdBy = 5
        self._deletedBy = 0

    @property
    def trackId(self):
        return self._trackId

    @trackId.setter
    def trackId(self, value):
        print "Cannot set trackId!"
    
    @property
    def diasources(self):
        return self._diasources

    @diasources.setter
    def diasources(self, value):
        print "Cannot set diasources!" 

    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, value):
        print "Cannot set info!"

    @property
    def members(self):
        return self._members

    @members.setter
    def members(self, value):
        print "Cannot set members!"

    @property
    def numMembers(self):
        return self._numMembers

    @numMembers.setter
    def numMembers(self, value):
        print "Cannot set numberMembers!"

    @property
    def windowStart(self):
        return self._windowStart

    @windowStart.setter
    def windowStart(self, value):
        print "Cannot set windowStart!"
        
    @property
    def isTrue(self):
        return self._isTrue

    @isTrue.setter
    def isTrue(self, value):
        self._isTrue = value
        
    @property
    def linkedObjectId(self):
        return self._linkedObjectId

    @linkedObjectId.setter
    def linkedObjectId(self, value):
        self._linkedObjectId = value

    @property
    def numLinkedObjects(self):
        return self._numLinkedObjects

    @numLinkedObjects.setter
    def numLinkedObjects(self, value):
        self._numLinkedObjects = value

    @property
    def rms(self):
        return self._rms

    @rms.setter
    def rms(self, value):
        self._rms = value

    @property
    def isSubset(self):
        return self._isSubset

    @isSubset.setter
    def isSubset(self, value):
        self._isSubset = value

    @property
    def subsetOf(self):
        return self._subsetOf

    @subsetOf.setter
    def subsetOf(self, value):
        self._subsetOf = value

    @property
    def startTime(self):
        return self._startTime

    @startTime.setter
    def startTime(self, value):
        self._startTime = value

    @property
    def endTime(self):
        return self._endTime

    @endTime.setter
    def endTime(self, value):
        self._endTime = value

    @property
    def createdBy(self):
        return self._createdBy

    @createdBy.setter
    def createdBy(self, value):
        self._createdBy = value

    @property
    def deletedBy(self):
        return self._deletedBy

    @deletedBy.setter
    def deletedBy(self, value):
        self._deletedBy = value

    def addDiasource(self, diasource_num, diaid, diasource):
        self._diasources[diasource_num]["diaId"] = int(diaid)
        self._diasources[diasource_num]["visitId"] = diasource["visitId"]
        self._diasources[diasource_num]["ssmId"] = diasource["ssmId"]
        self._diasources[diasource_num]["ra"] = diasource["ra"]
        self._diasources[diasource_num]["dec"] = diasource["dec"]
        self._diasources[diasource_num]["mjd"] = diasource["mjd"]
        self._diasources[diasource_num]["mag"] = diasource["mag"]
        self._diasources[diasource_num]["snr"] = diasource["snr"]

    def updateRMS(self):
        self._rms = calcRMS(self._diasources)

    def updateQuality(self):
        self._isTrue, num_unique_ids = checkSSMIDs(self._diasources["ssmId"])
        if self._isTrue:
            self._linkedObjectId = self._diasources["ssmId"][0]
            self._numLinkedObjects = num_unique_ids
        else:
            self._linkedObjectId = -1
            self._numLinkedObjects = num_unique_ids

    def updateTime(self):
        self._startTime = min(self.diasources["mjd"])
        self._endTime = max(self.diasources["mjd"])

    def updateMembers(self):
        self._members["trackId"] = self._members["trackId"] * self._trackId
        self._members["diaId"] = self._diasources["diaId"]

    def updateInfo(self):
        self._info["trackId"] = self._trackId 
        self._info["linkedObjectId"] = self._linkedObjectId 
        self._info["numLinkedObjects"] = self._numLinkedObjects 
        self._info["numMembers"] = self._numMembers
        self._info["rms"] = self._rms 
        self._info["windowStart"] = self._windowStart
        self._info["startTime"] = self._startTime 
        self._info["endTime"] = self._endTime 
        self._info["subsetOf"] = self._subsetOf
        self._info["createdBy"] = self._createdBy 
        self._info["deletedBy"] = self._deletedBy

    def update(self):
        self.updateRMS()
        self.updateQuality()
        self.updateTime()
        self.updateMembers()
        self.updateInfo()

    def toAllTracksDataframe(self):
        return pd.DataFrame(self._info)

    def toTrackMembersDataframe(self):
        return pd.DataFrame(self._members)

def checkSSMIDs(ssmids):
    uniqueIds = np.unique(ssmids)
    if len(uniqueIds) == 1:
        return True, len(uniqueIds)
    else:
        return False, len(uniqueIds)

def makeContiguous(angles):
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
    while abs(a - b) > 180:
        if a > b:
            b += 360.
        else:
            a += 360.
    return a - b

def calcGreatCircleDistance(ra0, dec0, ra1, dec1):
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

def calcVelocity(diasources):
    dt = max(diasources["mjd"]) - min(diasources["mjd"])
    dist_deg = calcGreatCircleDistance(diasources["ra"][0], diasources["dec"][0],
        diasources["ra"][-1], diasources["dec"][-1])
    velocity_deg_day = dist_deg / dt
    return velocity_deg_day
    
def calcRMS(diasources):
    t0 = min(diasources["mjd"])
    mjds = diasources["mjd"] - t0
    ras = makeContiguous(diasources["ra"])
    decs = makeContiguous(diasources["dec"])

    raFunc, raRes, rank, svd, rcond = np.polyfit(mjds, ras, 2, full=True)
    decFunc, decRes, rank, svd, rcond = np.polyfit(mjds, decs, 2, full=True)
    raFunc = np.poly1d(raFunc)
    decFunc = np.poly1d(decFunc)

    #now get the euclidean distance between predicted and observed for each point
    netSqDist = 0.0
    dists = []
    for i, mjd in enumerate(mjds):
        predRa = raFunc(mjd)
        predDec = decFunc(mjd)
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
    return rms