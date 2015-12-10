__all__ = ["MopsParameters"]

class DefaultMopsParameters:

    # findTracklets
    velocity_max = "0.5"
    velocity_min = "0.0"

    # collapseTracklets, purifyTracklets
    ra_tolerance = "0.002"
    dec_tolerance = "0.002"
    angular_tolerance = "5"
    velocity_tolerance = "0.05"
    method = "greedy"
    use_rms_filter = "False"
    rms_max = "0.001"

    # removeSubsets
    remove_subsets = "True"
    keep_only_longest = "False"
    
    # makeLinkTrackletsInput_byNight
    window_size = "15"

    # linkTracklets
    detection_error_threshold = "0.0002"
    dec_acceleration_max = "0.02"
    ra_acceleration_max = "0.02"
    latest_first_endpoint = None
    earliest_last_endpoint = None
    nights_min = "3"
    detections_min = "6"
    output_buffer_size = "1000"
    leaf_node_size_max = None

class MopsParameters(object):
    def __init__(self, velocity_max=None, 
                velocity_min=None, 
                ra_tolerance=None,
                dec_tolerance=None,
                angular_tolerance=None,
                velocity_tolerance=None,
                method=None,
                use_rms_filter=None,
                rms_max=None,
                remove_subsets=None,
                keep_only_longest=None,
                window_size=None,
                detection_error_threshold=None,
                dec_acceleration_max=None,
                ra_acceleration_max=None,
                latest_first_endpoint=None,
                earliest_last_endpoint=None,
                nights_min=None,
                detections_min=None,
                output_buffer_size=None,
                leaf_node_size_max=None,
                verbose=True):

        self._vMax = velocity_max
        self._vMin = velocity_min
        self._raTol = ra_tolerance
        self._decTol = dec_tolerance
        self._angTol = angular_tolerance
        self._vTol = velocity_tolerance
        self._method = method
        self._useRMSfilt = use_rms_filter
        self._rmsMax = rms_max
        self._rmSubsets = remove_subsets
        self._keepOnlyLongest = keep_only_longest
        self._windowSize = window_size
        self._detErrThresh = detection_error_threshold
        self._decAccelMax = dec_acceleration_max
        self._raAccelMax = ra_acceleration_max
        self._latestFirstEnd = latest_first_endpoint
        self._earliestLastEnd = earliest_last_endpoint
        self._nightMin = nights_min
        self._detectMin = detections_min
        self._bufferSize = output_buffer_size
        self._leafNodeSizeMax = leaf_node_size_max
       
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

        if method == None:
            self._method = defaults.method

        if use_rms_filter == None:
            self._useRMSfilt = defaults.use_rms_filter

        if rms_max == None:
            self._rmsMax = defaults.rms_max

        if remove_subsets == None:
            self._rmSubsets = defaults.remove_subsets

        if keep_only_longest == None:
            self._keepOnlyLongest = defaults.keep_only_longest

        if window_size == None:
            self._windowSize = defaults.window_size

        if detection_error_threshold == None:
            self._detErrThresh = defaults.detection_error_threshold

        if dec_acceleration_max == None:
            self._decAccelMax = defaults.dec_acceleration_max

        if ra_acceleration_max == None:
            self._raAccelMax = defaults.ra_acceleration_max

        if latest_first_endpoint == None:
            self._latestFirstEnd = defaults.latest_first_endpoint

        if earliest_last_endpoint == None:
            self._earliestLastEnd = defaults.earliest_last_endpoint

        if nights_min == None:
            self._nightMin = defaults.nights_min

        if detections_min == None:
            self._detectMin = defaults.detections_min

        if output_buffer_size == None:
            self._bufferSize = defaults.output_buffer_size

        if leaf_node_size_max == None:
            self._leafNodeSizeMax = defaults.leaf_node_size_max

        if verbose:
            self.info()

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
    def method(self):
        return self._method
    
    @method.setter
    def method(self, value):
        self._method = value

    @property
    def useRMSfilt(self):
        return self._useRMSfilt
    
    @useRMSfilt.setter
    def useRMSfilt(self, value):
        self._useRMSfilt = value

    @property
    def rmsMax(self):
        return self._rmsMax
    
    @rmsMax.setter
    def rmsMax(self, value):
        self._rmsMax = value

    @property
    def rmSubsets(self):
        return self._rmSubsets
    
    @rmSubsets.setter
    def rmSubsets(self, value):
        self._rmSubsets = value

    @property
    def keepOnlyLongest(self):
        return self._keepOnlyLongest
    
    @keepOnlyLongest.setter
    def keepOnlyLongest(self, value):
        self._keepOnlyLongest = value 

    @property
    def windowSize(self):
        return self._windowSize
    
    @windowSize.setter
    def windowSize(self, value):
        self._windowSize = value

    @property
    def detErrThresh(self):
        return self._detErrThresh
    
    @detErrThresh.setter
    def detErrThresh(self, value):
        self._detErrThresh = value
        
    @property
    def decAccelMax(self):
        return self._decAccelMax
    
    @decAccelMax.setter
    def decAccelMax(self, value):
        self._decAccelMax = value

    @property
    def raAccelMax(self):
        return self._raAccelMax
    
    @raAccelMax.setter
    def raAccelMax(self, value):
        self._raAccelMax = value

    @property
    def latestFirstEnd(self):
        return self._latestFirstEnd
    
    @latestFirstEnd.setter
    def latestFirstEnd(self, value):
        self._latestFirstEnd = value

    @property
    def earliestLastEnd(self):
        return self._earliestLastEnd
    
    @earliestLastEnd.setter
    def earliestLastEnd(self, value):
        self._earliestLastEnd = value

    @property
    def nightMin(self):
        return self._nightMin
    
    @nightMin.setter
    def nightMin(self, value):
        self._nightMin = value

    @property
    def detectMin(self):
        return self._detectMin
    
    @detectMin.setter
    def detectMin(self, value):
        self._detectMin = value

    @property
    def bufferSize(self):
        return self._bufferSize
    
    @bufferSize.setter
    def bufferSize(self, value):
        self._bufferSize = value

    @property
    def leafNodeSizeMax(self):
        return self._leafNodeSizeMax
    
    @leafNodeSizeMax.setter
    def leafNodeSizeMax(self, value):
        self._leafNodeSizeMax = value

    def info(self):
        print "------- MOPS Parameters --------"
        print "Current Parameter Values:"
        print ""
        print "---- findTracklets ----"
        print "\tMaximum velocity:                         %s" % (self._vMax)
        print "\tMinimum velocity:                         %s" % (self._vMin)
        print "---- collapseTracklets ----"
        print "\tRight Ascension tolerance:                %s" % (self._raTol)
        print "\tDeclination tolerance:                    %s" % (self._decTol)
        print "\tAngular tolerance:                        %s" % (self._angTol)
        print "\tVelocity tolerance:                       %s" % (self._vTol)
        print "\tMethod:                                   %s" % (self._method)
        print "\tUse RMS filter:                           %s" % (self._useRMSfilt)
        print "\tMaximum RMS:                              %s" % (self._rmsMax)
        print "---- purifyTracklets ----"
        print "\tMaximum RMS:                              %s" % (self._rmsMax)
        print "---- removeSubsets ----"
        print "\tRemove subsets:                           %s" % (self._rmSubsets)
        print "\tKeep only longest:                        %s" % (self._keepOnlyLongest)
        print "---- makeLinkTrackletsInput_byNight.py ----"
        print "\tWindow size:                              %s" % (self._windowSize)
        print "---- linkTracklets ----"
        print "\t Detection error threshold:               %s" % (self._detErrThresh)
        print "\t Maximum right ascension acceleration:    %s" % (self._raAccelMax)
        print "\t Maximum declination acceleration:        %s" % (self._decAccelMax)
        print "\t Latest first endpoint:                   %s" % (self._latestFirstEnd)
        print "\t Earliest last endpoint:                  %s" % (self._earliestLastEnd)
        print "\t Minimum nights:                          %s" % (self._nightMin)
        print "\t Minimum detections:                      %s" % (self._detectMin)
        print "\t Output buffer size:                      %s" % (self._bufferSize)
        print "\t Maximum leaf node size:                  %s" % (self._leafNodeSizeMax)
        print ""
        
        return

    def save(self, outDir=None):

        import yaml

        if outDir == None:
            outname = "parameters.yaml"
        else:
            outname = outDir + "parameters.yaml"

        print "Saving MopsParameters to %s" % (outname)

        stream = file(outname, "w")
        yaml.dump(self, stream)   
        stream.close()

        print ""

        return
