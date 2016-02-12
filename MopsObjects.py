import numpy as np

__all__ = ["track", "sso"]

class track(object):
    def __init__(self, diasources, isTrue=None):

        self._diasources = diasources
        self._isTrue = isTrue
        self._tracklets = None
        self._rms = None
        self._raRes = None
        self._decRes = None
        self._distances = None
        self._isSubset = None
        self._subsetTracks = []

    @property
    def diasources(self):
        return self._diasources

    @diasources.setter
    def diasources(self, value):
        self._diasources = value

    @property
    def isTrue(self):
        return self._isTrue

    @isTrue.setter
    def isTrue(self, value):
        self._isTrue = value

    @property
    def tracklets(self):
        return self._tracklets

    @tracklets.setter
    def tracklets(self, value):
        self._tracklets = value

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

class sso(object):
    def __init__(self, ssmid):

        self._ssmid = ssmid
        self._diasources = {}
        self._tracklets = {}
        self._collapsedTracklets = {}
        self._purifiedTracklets = {}
        self._finalTracklets = {}
        self._tracks = {}

    @property
    def ssmid(self):
        return self._ssmid

    @ssmid.setter
    def ssmid(self, value):
        self._ssmid = value

    @property
    def diasources(self):
        return self._diasources

    @diasources.setter
    def diasources(self, value):
        self._diasources = value

    @property
    def tracklets(self):
        return self._tracklets

    @tracklets.setter
    def tracklets(self, value):
        self._tracklets = value  

    @property
    def collapsedTracklets(self):
        return self._collapsedTracklets

    @collapsedTracklets.setter
    def collapsedTracklets(self, value):
        self._collapsedTracklets = value

    @property
    def purifiedTracklets(self):
        return self._purifiedTracklets

    @purifiedTracklets.setter
    def purifiedTracklets(self, value):
        self._purifiedTracklets = value

    @property
    def finalTracklets(self):
        return self._finalTracklets

    @finalTracklets.setter
    def finalTracklets(self, value):
        self._finalTracklets = value  

    @property
    def tracks(self):
        return self._tracks

    @tracks.setter
    def tracks(self, value):
        self._tracks = value  