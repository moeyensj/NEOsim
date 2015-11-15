import numpy as np

__all__ = ["MopsTracker"]

class MopsTracker(object):

    def __init__(self, name):

        self._diaSources = None
        self._tracklets = None
        self._collapsedTracklets = None
        self._purifiedTracklets = None
        self._tracks = None
        self._name = name

        self._diaSourcesDir = None 
        self._trackletsDir = None 
        self._collapsedTrackletsDir = None
        self._purifiedTrackletsDir = None
        self._tracksDir = None

        self._ranFindTracklets = False
        self._ranCollapseTracklets = False
        self._ranPurifyTracklets = False
        self._ranLinkTracks = False

    @property
    def diaSources(self):
        return self._diaSources

    @diaSources.setter
    def diaSources(self, value):
        self._diaSources = np.array(value)

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
    def tracks(self):
        return self._tracks

    @tracks.setter
    def tracks(self, value):
        self._tracks = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def diaSourcesDir(self):
        return self._diaSourcesDir

    @diaSourcesDir.setter
    def diaSourcesDir(self, value):
        self._diaSourcesDir = value

    @property
    def trackletsDir(self):
        return self._trackletsDir
    
    @trackletsDir.setter
    def trackletsDir(self, value):
        self._trackletsDir = value

    @property
    def collapsedTrackletsDir(self):
        return self._collapsedTrackletsDir
    
    @collapsedTrackletsDir.setter
    def collapsedTrackletsDir(self, value):
        self._collapsedTrackletsDir = value

    @property
    def purifiedTrackletsDir(self):
        return self._purifiedTrackletsDir
    
    @purifiedTrackletsDir.setter
    def purifedTrackletsDir(self, value):
        self._purifiedTrackletsDir = value

    @property
    def tracksDir(self):
        return self._tracksDir
    
    @tracksDir.setter
    def tracksDir(self, value):
        self._tracksDir = value

    @property
    def ranFindTracklets(self):
        return self._ranFindTracklets

    @ranFindTracklets.setter
    def ranFindTracklets(self, value):
        self._ranFindTracklets = value

    @property
    def ranCollapseTracklets(self):
        return self._ranCollapseTracklets

    @ranCollapseTracklets.setter
    def ranCollapseTracklets(self, value):
        self._ranCollapseTracklets = value

    @property
    def ranPurifiedTracklets(self):
        return self._ranPurifyTracklets

    @ranPurifiedTracklets.setter
    def ranPurifiedTracklets(self, value):
        self._ranPurifiedTracklets = value

    @property
    def ranLinkTracks(self):
        return self._ranLinkTracks

    @ranLinkTracks.setter
    def ranLinkTracks(self, value):
        self._ranLinkTracks = value