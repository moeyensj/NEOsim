import numpy as np

__all__ = ["MopsObjects"]

class diasource(object):
    def __init__(self, diaid, ssmid, obshistid, ra, dec, mjd, mag, snr):

        self._diaid = diaid
        self._ssmid = ssmid
        self._obshistid = obshistid
        self._ra = ra
        self._dec = dec
        self._mjd = mjd
        self._mag = mag
        self._snr = snr
        
    @property
    def diaid(self):
        return self._diaid

    @diaid.setter
    def diaid(self, value):
        self._diaid = value

    @property
    def ssmid(self):
        return self._ssmid

    @ssmid.setter
    def ssmid(self, value):
        self._ssmid = value

    @property
    def obshistid(self):
        return self._obshistid

    @obshistid.setter
    def obshistid(self, value):
        self._obshistid = value

    @property
    def ra(self):
        return self._ra

    @ra.setter
    def ra(self, value):
        self._ra = value

    @property
    def dec(self):
        return self._dec

    @dec.setter
    def dec(self, value):
        self._dec = value

    @property
    def mjd(self):
        return self._mjd

    @mjd.setter
    def mjd(self, value):
        self._mjd = value

    @property
    def mag(self):
        return self._mag

    @mag.setter
    def mag(self, value):
        self._mag = value

    @property
    def snr(self):
        return self._snr

    @snr.setter
    def snr(self, value):
        self._snr = value

class tracklet(object):
    def __init__(self, diasources):

        self._diasources = diasources
        
    @property
    def diasources(self):
        return self._diasources

    @diasources.setter
    def diasources(self, value):
        self._diasources = value

class track(object):
    def __init__(self, diasources):

        self._diasources = diasources
        self._rms = None
        self._raRes = None
        self._decRes = None
        self._distances = None
        self._isTrue = None
        self._isSubset = None
        self._subsetTracks = []

    @property
    def diasources(self):
        return self._diasources

    @diasources.setter
    def diasources(self, value):
        self._diasources = value

    @property
    def rms(self):
        return self._rms

    @rms.setter
    def rms(self, value):
        self._rms = value

    @property
    def raRes(self):
        return self._raRes

    @raRes.setter
    def raRes(self, value):
        self._raRes = value

    @property
    def decRes(self):
        return self._decRes

    @decRes.setter
    def decRes(self, value):
        self._decRes = value

    @property
    def distances(self):
        return self._distances

    @distances.setter
    def distances(self, value):
        self._distances = value

    @property
    def isTrue(self):
        return self._isTrue

    @isTrue.setter
    def isTrue(self, value):
        self._isTrue = value

    @property
    def isSubset(self):
        return self._isSubset

    @isSubset.setter
    def isSubset(self, value):
        self._isSubset = value

    @property
    def subsetTracks(self):
        return self._subsetTracks

    @subsetTracks.setter
    def subsetTracks(self, value):
        self._subsetTracks = value
