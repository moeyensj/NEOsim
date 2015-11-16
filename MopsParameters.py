__all__ = ["MopsParameters"]

class DefaultMopsParameters:

    velocity_max = 2.0
    velocity_min = 0.0
    ra_tolerance = 0.002
    dec_tolerance = 0.002
    angular_tolerance = 5
    velocity_tolerance = 0.05

class MopsParameters(object):
    def __init__(self, velocity_max=None, 
                velocity_min=None, 
                ra_tolerance=None,
                dec_tolerance=None,
                angular_tolerance=None,
                velocity_tolerance=None):

        self._vmax = velocity_max
        self._vmin = velocity_min
        self._raTol = ra_tolerance
        self._decTol = dec_tolerance
        self._angTol = angular_tolerance
        self._vTol = velocity_tolerance

        defaults = DefaultMopsParameters()

        if velocity_max == None:
            self._vmax = defaults.velocity_max

        if velocity_min == None:
            self._vmin = defaults.velocity_min

        if ra_tolerance == None:
            self._raTol = defaults.ra_tolerance

        if dec_tolerance == None:
            self._decTol = defaults.dec_tolerance

        if angular_tolerance == None: 
            self._angTol = defaults.angular_tolerance

        if velocity_tolerance == None:
            self._vTol = defaults.velocity_tolerance

    @property
    def vmax(self):
        return self._vmax

    @vmax.setter
    def vmax(self, value):
        self._vmax = value

    @property
    def vmin(self):
        return self._vmin
    
    @vmin.setter
    def vmin(self, value):
        self._vmin = value

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

    def summary(self):
        print 'Current Parameter Values:'

        print '\tMaximum velocity:          %s' % (self._vmax)
        print '\tMinimum velocity:          %s' % (self._vmin)
        print '\tRight Ascension tolerance: %s' % (self._raTol)
        print '\tDeclination tolerance:     %s' % (self._decTol)
        print '\tAngular tolerance:         %s' % (self._angTol)
        print '\tVelocity tolerance:        %s' % (self._vTol)
    