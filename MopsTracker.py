import numpy as np

__all__ = ["MopsTracker"]

class MopsTracker(object):

    def __init__(self, name, parameters):

        self._diaSources = None
        self._tracklets = None
        self._trackletsByIndex = None
        self._collapsedTracklets = None
        self._purifiedTracklets = None
        self._trackletsById = None
        self._trackletsByNightDets = None
        self._trackletsByNightIds = None
        self._tracks = None
        self._name = name

        self._diaSourcesDir = None 
        self._trackletsDir = None 
        self._collapsedTrackletsDir = None
        self._purifiedTrackletsDir = None
        self._trackletsByNightDir = None
        self._tracksDir = None

        self._ranFindTracklets = False
        self._ranIdsToIndices = False
        self._ranCollapseTracklets = False
        self._ranPurifyTracklets = False
        self._ranIndiciesToIds = False
        self._ranMakeLinkTrackletsInputByNight = False
        self._ranLinkTracklets = False

        self._vMax = None
        self._vMin = None
        self._raTol = None
        self._decTol = None
        self._angTol = None
        self._vTol = None

        print '------- MOPS Tracker --------'
        print 'Tracker initialized...'

        self.readParameters(parameters)

        print ''

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
    def purifiedTracklets(self):
        return self._purifiedTracklets

    @purifiedTracklets.setter
    def purifiedTracklets(self, value):
        self._purifiedTracklets = value

    @property
    def trackletsById(self):
        return self._trackletsById

    @trackletsById.setter
    def trackletsById(self, value):
        self._trackletsById = value

    @property
    def trackletsByNightDets(self):
        return self._trackletsByNightDets
    
    @trackletsByNightDets.setter
    def trackletsByNightDets(self, value):
        self._trackletsByNightDets = value

    @property
    def trackletsByNightIds(self):
        return self._trackletsByNightIds
    
    @trackletsByNightIds.setter
    def trackletsByNightIds(self, value):
        self._trackletsByNightIds = value

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
    def purifiedTrackletsDir(self, value):
        self._purifiedTrackletsDir = value

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
    
    def readParameters(self, parameters):
        print 'Reading parameter values...'

        self.vMax = parameters.vMax
        print '\tMaximum velocity:          %s' % (parameters._vMax)
        self.vMin = parameters.vMin
        print '\tMinimum velocity:          %s' % (parameters._vMin)
        self.raTol = parameters.raTol
        print '\tRight Ascension tolerance: %s' % (parameters._raTol)
        self.decTol = parameters.decTol
        print '\tDeclination tolerance:     %s' % (parameters._decTol)
        self.angTol = parameters.angTol
        print '\tAngular tolerance:         %s' % (parameters._angTol)
        self.vTol = parameters.vTol
        print '\tVelocity tolerance:        %s' % (parameters._vTol)
        self.rmsMax = parameters.rmsMax
        print '\tMaximum RMS:               %s' % (parameters._rmsMax)

        return

    def status(self):

        print "Current run status:"
        print "\tfindTracklets:                     %s" % (self._ranFindTracklets)
        print "\tidsToIndices.py:                   %s" % (self._ranIdsToIndices)
        print "\tcollapseTracklets:                 %s" % (self._ranCollapseTracklets)
        print "\tpurifyTracklets:                   %s" % (self._ranPurifyTracklets)
        print "\tindicesToIds.py:                   %s" % (self._ranIndicesToIds)        
        print "\tmakeLinkTrackletsInputByNight.py:  %s" % (self._ranMakeLinkTrackletsInputByNight)
        print "\tlinkTracklets:                     %s" % (self._ranLinkTracklets)

        return
