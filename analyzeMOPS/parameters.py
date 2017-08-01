import os
import yaml

__all__ = ["Parameters"]


class DefaultParameters:

    # findTracklets
    velocity_max = 0.5
    velocity_min = 0.0

    # collapseTracklets, purifyTracklets
    ra_tolerance = 0.002
    dec_tolerance = 0.002
    angular_tolerance = 5
    velocity_tolerance = 0.05
    method = "greedy"
    use_rms_filter = True
    tracklet_rms_max = 0.001

    # removeSubsets (tracklets)
    remove_subset_tracklets = False
    keep_only_longest_tracklets = False

    # makeLinkTrackletsInput_byNight
    window_size = 15

    # linkTracklets
    detection_error_threshold = 0.0004
    dec_acceleration_max = 0.02
    ra_acceleration_max = 0.02
    latest_first_endpoint = None
    earliest_last_endpoint = None
    nights_min = 3
    detections_min = 6
    output_buffer_size = 1000
    leaf_node_size_max = None
    track_rms_max = 0.05
    track_addition_threshold = 0.5
    default_astrometric_error = 0.2 / 3600
    track_chi_square_minimum = 0.0
    sky_center_ra = 340.0
    sky_center_dec = -15.0
    observatory_lat = -30.169
    observatory_lon = -70.804

    # removeSubsets (tracks)
    remove_subset_tracks = True
    keep_only_longest_tracks = False


class Parameters(object):
    def __init__(self, velocity_max=None,
                 velocity_min=None,
                 ra_tolerance=None,
                 dec_tolerance=None,
                 angular_tolerance=None,
                 velocity_tolerance=None,
                 method=None,
                 use_rms_filter=None,
                 tracklet_rms_max=None,
                 remove_subset_tracklets=None,
                 keep_only_longest_tracklets=None,
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
                 track_rms_max=None,
                 track_addition_threshold=None,
                 default_astrometric_error=None,
                 track_chi_square_minimum=None,
                 sky_center_ra=None,
                 sky_center_dec=None,
                 observatory_lat=None,
                 observatory_lon=None,
                 remove_subset_tracks=None,
                 keep_only_longest_tracks=None):

        self._vMax = velocity_max
        self._vMin = velocity_min
        self._raTol = ra_tolerance
        self._decTol = dec_tolerance
        self._angTol = angular_tolerance
        self._vTol = velocity_tolerance
        self._method = method
        self._useRMSfilt = use_rms_filter
        self._trackletRMSmax = tracklet_rms_max
        self._rmSubsetTracklets = remove_subset_tracklets
        self._keepOnlyLongestTracklets = keep_only_longest_tracklets
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
        self._trackRMSmax = track_rms_max
        self._trackAdditionThresh = track_addition_threshold
        self._defaultAstromErr = default_astrometric_error
        self._trackChiSqMin = track_chi_square_minimum
        self._skyCenterRA = sky_center_ra
        self._skyCenterDec = sky_center_dec
        self._obsLat = observatory_lat
        self._obsLon = observatory_lon
        self._rmSubsetTracks = remove_subset_tracks
        self._keepOnlyLongestTracks = keep_only_longest_tracks

        defaults = DefaultParameters()

        if velocity_max is None:
            self._vMax = defaults.velocity_max

        if velocity_min is None:
            self._vMin = defaults.velocity_min

        if ra_tolerance is None:
            self._raTol = defaults.ra_tolerance

        if dec_tolerance is None:
            self._decTol = defaults.dec_tolerance

        if angular_tolerance is None:
            self._angTol = defaults.angular_tolerance

        if velocity_tolerance is None:
            self._vTol = defaults.velocity_tolerance

        if method is None:
            self._method = defaults.method

        if use_rms_filter is None:
            self._useRMSfilt = defaults.use_rms_filter

        if tracklet_rms_max is None:
            self._trackletRMSmax = defaults.tracklet_rms_max

        if remove_subset_tracklets is None:
            self._rmSubsetTracklets = defaults.remove_subset_tracklets

        if keep_only_longest_tracklets is None:
            self._keepOnlyLongestTracklets = defaults.keep_only_longest_tracklets

        if window_size is None:
            self._windowSize = defaults.window_size

        if detection_error_threshold is None:
            self._detErrThresh = defaults.detection_error_threshold

        if dec_acceleration_max is None:
            self._decAccelMax = defaults.dec_acceleration_max

        if ra_acceleration_max is None:
            self._raAccelMax = defaults.ra_acceleration_max

        if latest_first_endpoint is None:
            self._latestFirstEnd = defaults.latest_first_endpoint

        if earliest_last_endpoint is None:
            self._earliestLastEnd = defaults.earliest_last_endpoint

        if nights_min is None:
            self._nightMin = defaults.nights_min

        if detections_min is None:
            self._detectMin = defaults.detections_min

        if output_buffer_size is None:
            self._bufferSize = defaults.output_buffer_size

        if leaf_node_size_max is None:
            self._leafNodeSizeMax = defaults.leaf_node_size_max

        if track_rms_max is None:
            self._trackRMSmax = defaults.track_rms_max

        if track_addition_threshold is None:
            self._trackAdditionThresh = defaults.track_addition_threshold
 
        if default_astrometric_error is None:
            self._defaultAstromErr = defaults.default_astrometric_error

        if track_chi_square_minimum is None:
            self._trackChiSqMin = defaults.track_chi_square_minimum

        if sky_center_ra is None:
            self._skyCenterRA = defaults.sky_center_ra

        if sky_center_dec is None: 
            self._skyCenterDec = defaults.sky_center_dec

        if observatory_lat is None:
            self._obsLat = defaults.observatory_lat

        if observatory_lon is None:
            self._obsLon = defaults.observatory_lon

        if remove_subset_tracks is None:
            self._rmSubsetTracks = defaults.remove_subset_tracks

        if keep_only_longest_tracks is None:
            self._keepOnlyLongestTracks = defaults.remove_subset_tracks

    def __repr__(self):
        representation = ("------- MOPS Parameters --------\n" + 
                          "Current Parameter Values:\n\n" + 
                          "---- findTracklets ----\n" + 
                          "\tMaximum velocity:                         {}\n" + 
                          "\tMinimum velocity:                         {}\n" + 
                          "---- collapseTracklets ----\n" + 
                          "\tRight Ascension tolerance:                {}\n" + 
                          "\tDeclination tolerance:                    {}\n" + 
                          "\tAngular tolerance:                        {}\n" + 
                          "\tVelocity tolerance:                       {}\n" + 
                          "\tMethod:                                   {}\n" + 
                          "\tUse RMS filter:                           {}\n" + 
                          "\tTracklet RMS maximum:                     {}\n" + 
                          "---- purifyTracklets ----\n" + 
                          "\tTracklet RMS maximum:                     {}\n" + 
                          "---- removeSubsets (tracklets) ----\n" + 
                          "\tRemove subsets:                           {}\n" + 
                          "\tKeep only longest:                        {}\n" + 
                          "---- makeLinkTrackletsInput_byNight.py ----\n" + 
                          "\tWindow size:                              {}\n" + 
                          "---- linkTracklets ----\n" + 
                          "\tDetection error threshold:                {}\n" + 
                          "\tMaximum right ascension acceleration:     {}\n" + 
                          "\tMaximum declination acceleration:         {}\n" + 
                          "\tLatest first endpoint:                    {}\n" + 
                          "\tEarliest last endpoint:                   {}\n" + 
                          "\tMinimum nights:                           {}\n" + 
                          "\tMinimum detections:                       {}\n" + 
                          "\tOutput buffer size:                       {}\n" + 
                          "\tMaximum leaf node size:                   {}\n" + 
                          "\tTrack RMS maximum:                        {}\n" + 
                          "\tTrack addition threshold:                 {}\n" + 
                          "\tDefault astrometric error:                {}\n" + 
                          "\tTrack chi-squared minimum:                {}\n" + 
                          "\tSky center RA                             {}\n" + 
                          "\tSky center Dec                            {}\n" + 
                          "\tObservatory latitude                      {}\n" + 
                          "\tObservatory longitude                     {}\n" + 
                          "---- removeSubsets (tracks) ----\n" + 
                          "\tRemove subsets:                           {}\n" + 
                          "\tKeep only longest:                        {}\n\n")
        return representation.format(self._vMax,
                                     self._vMin,
                                     self._raTol,
                                     self._decTol,
                                     self._angTol,
                                     self._vTol,
                                     self._method,
                                     self._useRMSfilt,
                                     self._trackletRMSmax,
                                     self._trackletRMSmax,
                                     self._rmSubsetTracklets,
                                     self._keepOnlyLongestTracklets,
                                     self._windowSize,
                                     self._detErrThresh,
                                     self._raAccelMax,
                                     self._decAccelMax,
                                     self._latestFirstEnd,
                                     self._earliestLastEnd,
                                     self._nightMin,
                                     self._detectMin,
                                     self._bufferSize,
                                     self._leafNodeSizeMax,
                                     self._trackRMSmax,
                                     self._trackAdditionThresh,
                                     self._defaultAstromErr,
                                     self._trackChiSqMin,
                                     self._skyCenterRA,
                                     self._skyCenterDec,
                                     self._obsLat,
                                     self._obsLon,
                                     self._rmSubsetTracks,
                                     self._keepOnlyLongestTracks)

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
    def trackletRMSmax(self):
        return self._trackletRMSmax

    @trackletRMSmax.setter
    def trackletRMSmax(self, value):
        self._trackletRMSmax = value

    @property
    def rmSubsetTracklets(self):
        return self._rmSubsetTracklets

    @rmSubsetTracklets.setter
    def rmSubsetTracklets(self, value):
        self._rmSubsetTracklets = value

    @property
    def keepOnlyLongestTracklets(self):
        return self._keepOnlyLongestTracklets

    @keepOnlyLongestTracklets.setter
    def keepOnlyLongestTracklets(self, value):
        self._keepOnlyLongestTracklets = value

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

    @property
    def trackRMSmax(self):
        return self._trackRMSmax

    @trackRMSmax.setter
    def trackRMSmax(self, value):
        self._trackRMSmax = value

    @property
    def trackAdditionThresh(self):
        return self._trackAdditionThresh

    @trackAdditionThresh.setter
    def trackAdditionThresh(self, value):
        self._trackAdditionThresh = value

    @property
    def defaultAstromErr(self):
        return self._defaultAstromErr

    @defaultAstromErr.setter
    def defaultAstromErr(self, value):
        self._defaultAstromErr = value

    @property
    def trackChiSqMin(self):
        return self._trackChiSqMin

    @trackChiSqMin.setter
    def trackChiSqMin(self, value):
        self._trackChiSqMin = value

    @property
    def skyCenterRA(self):
        return self._skyCenterRA

    @skyCenterRA.setter
    def skyCenterRA(self, value):
        self._skyCenterRA = value

    @property
    def skyCenterDec(self):
        return self._skyCenterDec

    @skyCenterDec.setter
    def skyCenterDec(self, value):
        self._skyCenterDec = value

    @property
    def obsLat(self):
        return self._obsLat

    @obsLat.setter
    def obsLat(self, value):
        self._obsLat = value

    @property
    def obsLon(self):
        return self._obsLon

    @obsLon.setter
    def obsLon(self, value):
        self._obsLon = value

    @property
    def rmSubsetTracks(self):
        return self._rmSubsetTracks

    @rmSubsetTracks.setter
    def rmSubsetTracks(self, value):
        self._rmSubsetTracks = value

    @property
    def keepOnlyLongestTracks(self):
        return self._keepOnlyLongestTracks

    @keepOnlyLongestTracks.setter
    def keepOnlyLongestTracks(self, value):
        self._keepOnlyLongestTracks = value

    def toYaml(self, outDir=None):
        if outDir is None:
            outname = "parameters.yaml"
        else:
            outname = os.path.join(outDir, "parameters.yaml")

        print "Saving parameters to %s" % (outname)

        stream = file(outname, "w")
        yaml.dump(self, stream)
        stream.close()

        return

    @classmethod
    def fromYaml(cls, yamlFile):
        print "Loading parameters from %s" % (yamlFile)

        cls = yaml.load(file(yamlFile, "r"))

        return cls
