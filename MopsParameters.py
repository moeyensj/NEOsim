__all__ = ["MopsParameters"]

class DefaultMopsParameters:

    velocity_max = 2.0
    velocity_min = 0.0
    ra_tolerance = 0.002
    dec_tolerance = 0.002
    angular_tolerance = 5
    velocity_tolerance = 0.05
    rms_max = 0.001
    window_size = 15

class MopsParameters(object):
    def __init__(self, velocity_max=None, 
                velocity_min=None, 
                ra_tolerance=None,
                dec_tolerance=None,
                angular_tolerance=None,
                velocity_tolerance=None,
                rms_max=None,
                window_size=None):

        self._vMax = velocity_max
        self._vMin = velocity_min
        self._raTol = ra_tolerance
        self._decTol = dec_tolerance
        self._angTol = angular_tolerance
        self._vTol = velocity_tolerance
        self._rmsMax = rms_max
        self._windowSize = window_size

        defaults = DefaultMopsParameters()

        if velocity_max == None:
            self._vMax = defaults.velocity_max

        if velocity_min == None:
            self._vMin = defaults.velocity_min

        if ra_tolerance == None:
            self._raTol = defaults.ra_tolerance

        if dec_tolerance == None:
            self._decTol = defaults.dec_tolerance

        if angular_tolerance == None: 
            self._angTol = defaults.angular_tolerance

        if velocity_tolerance == None:
            self._vTol = defaults.velocity_tolerance

        if rms_max == None:
            self._rmsMax = defaults.rms_max

        if window_size == None:
            self._windowSize = defaults.window_size

        print '------- MOPS Parameters --------'
        self.info()
        print ''

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

    @property
    def rmsMax(self):
        return self._rmsMax
    
    @rmsMax.setter
    def rmsMax(self, value):
        self._rmsMax = value

    @property
    def windowSize(self):
        return self._windowSize
    
    @windowSize.setter
    def windowSize(self, value):
        self._windowSize = value

    def info(self):
        
        print 'Current Parameter Values:'
        print ''
        print '---- findTracklets ----'
        print '\tMaximum velocity:          %s' % (self._vMax)
        print '\tMinimum velocity:          %s' % (self._vMin)
        print '---- collapseTracklets ----'
        print '\tRight Ascension tolerance: %s' % (self._raTol)
        print '\tDeclination tolerance:     %s' % (self._decTol)
        print '\tAngular tolerance:         %s' % (self._angTol)
        print '\tVelocity tolerance:        %s' % (self._vTol)
        print '---- purifyTracklets ----'
        print '\tMaximum RMS:               %s' % (self._rmsMax)
        print '---- makeLinkTrackletsInput_byNight.py ----'
        print '\tWindow size:               %s' % (self._windowSize)

        return

    def save(self, outDir=None):

        import yaml

        if outDir == None:
            outname = 'parameters.yaml'
        else:
            outname = outDir + '/parameters.yaml'

        print 'Saving MopsParameters to %s' % (outname)

        stream = file(outname, 'w')
        yaml.dump(self, stream)   
        stream.close()

        return
