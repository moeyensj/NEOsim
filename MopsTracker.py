__all__ = ["MopsTracker"]

class MopsTracker(object):

    def __init__(self, runDir, verbose=True):

        self._diaSources = None
        self._tracklets = None
        self._trackletsByIndex = None
        self._collapsedTracklets = None
        self._collapsedTrackletsById = None
        self._purifiedTracklets = None
        self._purifiedTrackletsById = None
        self._finalTracklets = None
        self._finalTrackletsById = None
        self._dets = None
        self._ids = None
        self._tracks = None
        self._runDir = runDir

        self._diaSourcesDir = None 
        self._trackletsDir = None 
        self._trackletsByIndexDir = None
        self._collapsedTrackletsDir = None
        self._collapsedTrackletsByIdDir = None
        self._purifiedTrackletsDir = None
        self._purifiedTrackletsByIdDir = None
        self._finalTrackletsDir = None
        self._finalTrackletsByIdDir = None
        self._trackletsByNightDir = None
        self._tracksDir = None

        self._ranFindTracklets = False
        self._ranIdsToIndices = False
        self._ranCollapseTracklets = False
        self._ranPurifyTracklets = False
        self._ranRemoveSubsets = False
        self._ranIndicesToIds = False
        self._ranMakeLinkTrackletsInputByNight = False
        self._ranLinkTracklets = False

        if verbose:
            self.info()

    @property
    def diaSources(self):
        return self._diaSources

    @diaSources.setter
    def diaSources(self, value):
        self._diaSources = value

    @property
    def tracklets(self):
        return self._tracklets

    @tracklets.setter
    def tracklets(self, value):
        self._tracklets = value

    @property
    def trackletsByIndex(self):
        return self._trackletsByIndex
    
    @trackletsByIndex.setter
    def trackletsByIndex(self, value):
        self._trackletsByIndex = value

    @property
    def collapsedTracklets(self):
        return self._collapsedTracklets

    @collapsedTracklets.setter
    def collapsedTracklets(self, value):
        self._collapsedTracklets = value

    @property
    def collapsedTrackletsById(self):
        return self._collapsedTrackletsById

    @collapsedTrackletsById.setter
    def collapsedTrackletsById(self, value):
        self._collapsedTrackletsById = value

    @property
    def purifiedTracklets(self):
        return self._purifiedTracklets

    @purifiedTracklets.setter
    def purifiedTracklets(self, value):
        self._purifiedTracklets = value

    @property
    def purifiedTrackletsById(self):
        return self._purifiedTrackletsById

    @purifiedTrackletsById.setter
    def purifiedTrackletsById(self, value):
        self._purifiedTrackletsById = value

    @property
    def finalTracklets(self):
        return self._finalTracklets
    
    @finalTracklets.setter
    def finalTracklets(self, value):
        self._finalTracklets = value

    @property
    def finalTrackletsById(self):
        return self._finalTrackletsById

    @finalTrackletsById.setter
    def finalTrackletsById(self, value):
        self._finalTrackletsById = value

    @property
    def dets(self):
        return self._dets
    
    @dets.setter
    def dets(self, value):
        self._dets = value

    @property
    def ids(self):
        return self._ids
    
    @ids.setter
    def ids(self, value):
        self._ids = value

    @property
    def tracks(self):
        return self._tracks

    @tracks.setter
    def tracks(self, value):
        self._tracks = value

    @property
    def runDir(self):
        return self._runDir

    @runDir.setter
    def runDir(self, value):
        self._runDir = value

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
    def trackletsByIndexDir(self):
        return self._trackletsByIndexDir

    @trackletsByIndexDir.setter
    def trackletsByIndexDir(self, value):
        self._trackletsByIndexDir = value

    @property
    def collapsedTrackletsDir(self):
        return self._collapsedTrackletsDir
    
    @collapsedTrackletsDir.setter
    def collapsedTrackletsDir(self, value):
        self._collapsedTrackletsDir = value

    @property
    def collapsedTrackletsByIdDir(self):
        return self._collapsedTrackletsByIdDir
    
    @collapsedTrackletsByIdDir.setter
    def collapsedTrackletsByIdDir(self, value):
        self._collapsedTrackletsByIdDir = value

    @property
    def purifiedTrackletsDir(self):
        return self._purifiedTrackletsDir
    
    @purifiedTrackletsDir.setter
    def purifiedTrackletsDir(self, value):
        self._purifiedTrackletsDir = value

    @property
    def purifiedTrackletsByIdDir(self):
        return self._purifiedTrackletsByIdDir
    
    @purifiedTrackletsByIdDir.setter
    def purifiedTrackletsByIdDir(self, value):
        self._purifiedTrackletsByIdDir = value

    @property
    def finalTrackletsDir(self):
        return self._finalTrackletsDir
    
    @finalTrackletsDir.setter
    def finalTrackletsDir(self, value):
        self._finalTrackletsDir = value

    @property
    def finalTrackletsByIdDir(self):
        return self._finalTrackletsByIdDir

    @finalTrackletsByIdDir.setter
    def finalTrackletsByIdDir(self, value):
        self._finalTrackletsByIdDir = value

    @property
    def trackletsByNightDir(self):
        return self._trackletsByNightDir

    @trackletsByNightDir.setter
    def trackletsByNightDir(self, value):
        self._trackletsByNightDir = value

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
    def ranIdsToIndices(self):
        return self._ranIdsToIndices

    @ranIdsToIndices.setter
    def ranIdsToIndices(self, value):
        self._ranIdsToIndices = value
    
    @property
    def ranCollapseTracklets(self):
        return self._ranCollapseTracklets

    @ranCollapseTracklets.setter
    def ranCollapseTracklets(self, value):
        self._ranCollapseTracklets = value

    @property
    def ranPurifyTracklets(self):
        return self._ranPurifyTracklets

    @ranPurifyTracklets.setter
    def ranPurifyTracklets(self, value):
        self._ranPurifyTracklets = value

    @property
    def ranRemoveSubsets(self):
        return self._ranRemoveSubsets

    @ranRemoveSubsets.setter
    def ranRemoveSubsets(self, value):
        self._ranRemoveSubsets = value

    @property
    def ranIdsToIndices(self):
        return self._ranIdsToIndices

    @ranIdsToIndices.setter
    def ranIdsToIndices(self, value):
        self._ranIdsToIndices = value    

    @property
    def ranIndicesToIds(self):
        return self._ranIndicesToIds
    
    @ranIndicesToIds.setter
    def ranIndicesToIds(self, value):
        self._ranIndicesToIds = value

    @property
    def ranMakeLinkTrackletsInputByNight(self):
        return self._ranMakeLinkTrackletsInputByNight

    @ranMakeLinkTrackletsInputByNight.setter
    def ranMakeLinkTrackletsInputByNight(self, value):
        self._ranMakeLinkTrackletsInputByNight = value
    
    @property
    def ranLinkTracklets(self):
        return self._ranLinkTracklets

    @ranLinkTracklets.setter
    def ranLinkTracklets(self, value):
        self._ranLinkTracklets = value

    @property
    def vMax(self):
        return self._vMax
    
    @vMax.setter
    def vMax(self, value):
        self._vMax = value

    @property
    def vMin(self):
        return self._vMin

    @vMin.setter
    def vMin(self, value):
        self._vMin = value 

    @property
    def raTol(self):
        return self._raTol

    @raTol.setter
    def raTol(self, value):
        self._raTol = value

    @property
    def decTol(self):
        return self._decTol

    @decTol.setter
    def decTol(self, value):
        self._decTol = value

    @property
    def angTol(self):
        return self._angTol

    @angTol.setter
    def angTol(self, value):
        self._angTol = value

    @property
    def vTol(self):
        return self._vTol

    @vTol.setter
    def vTol(self, value):
        self._vTol = value

    def info(self):
        print "------- MOPS Tracker --------"
        print "Current run status:"
        print ""
        print "\tfindTracklets:                     %s" % (self._ranFindTracklets)
        print "\tidsToIndices.py:                   %s" % (self._ranIdsToIndices)
        print "\tcollapseTracklets:                 %s" % (self._ranCollapseTracklets)
        print "\tpurifyTracklets:                   %s" % (self._ranPurifyTracklets)
        print "\tremoveSubsets                      %s" % (self._ranRemoveSubsets)
        print "\tindicesToIds.py:                   %s" % (self._ranIndicesToIds)        
        print "\tmakeLinkTrackletsInputByNight.py:  %s" % (self._ranMakeLinkTrackletsInputByNight)
        print "\tlinkTracklets:                     %s" % (self._ranLinkTracklets)
        print ""
        
        return
