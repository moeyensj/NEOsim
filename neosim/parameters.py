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
    rms_max = 0.001

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
                 rms_max=None,
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
                 remove_subset_tracks=None,
                 keep_only_longest_tracks=None,
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

        if rms_max is None:
            self._rmsMax = defaults.rms_max

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

        if remove_subset_tracks is None:
            self._rmSubsetTracks = defaults.remove_subset_tracks

        if keep_only_longest_tracks is None:
            self._keepOnlyLongestTracks = defaults.remove_subset_tracks

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

    def info(self):
        print("------- MOPS Parameters --------")
        print("Current Parameter Values:")
        print()
        print("---- findTracklets ----")
        print("\tMaximum velocity:                         {}").format(self._vMax)
        print("\tMinimum velocity:                         {}").format(self._vMin)
        print("---- collapseTracklets ----")
        print("\tRight Ascension tolerance:                {}").format(self._raTol)
        print("\tDeclination tolerance:                    {}").format(self._decTol)
        print("\tAngular tolerance:                        {}").format(self._angTol)
        print("\tVelocity tolerance:                       {}").format(self._vTol)
        print("\tMethod:                                   {}").format(self._method)
        print("\tUse RMS filter:                           {}").format(self._useRMSfilt)
        print("\tMaximum RMS:                              {}").format(self._rmsMax)
        print("---- purifyTracklets ----")
        print("\tMaximum RMS:                              {}").format(self._rmsMax)
        print("---- removeSubsets (tracklets) ----")
        print("\tRemove subsets:                           {}").format(self._rmSubsetTracklets)
        print("\tKeep only longest:                        {}").format(self._keepOnlyLongestTracklets)
        print("---- makeLinkTrackletsInput_byNight.py ----")
        print("\tWindow size:                              {}").format(self._windowSize)
        print("---- linkTracklets ----")
        print("\tDetection error threshold:                {}").format(self._detErrThresh)
        print("\tMaximum right ascension acceleration:     {}").format(self._raAccelMax)
        print("\tMaximum declination acceleration:         {}").format(self._decAccelMax)
        print("\tLatest first endpoint:                    {}").format(self._latestFirstEnd)
        print("\tEarliest last endpoint:                   {}").format(self._earliestLastEnd)
        print("\tMinimum nights:                           {}").format(self._nightMin)
        print("\tMinimum detections:                       {}").format(self._detectMin)
        print("\tOutput buffer size:                       {}").format(self._bufferSize)
        print("\tMaximum leaf node size:                   {}").format(self._leafNodeSizeMax)
        print("---- removeSubsets (tracks) ----")
        print("\tRemove subsets:                           {}").format(self._rmSubsetTracks)
        print("\tKeep only longest:                        {}").format(self._keepOnlyLongestTracks)
        print()

        return

    def toYaml(self, outDir=None):
        if outDir is None:
            outname = "parameters.yaml"
        else:
            outname = os.path.join(outDir, "parameters.yaml")

        print("Saving parameters to {}").format(outname)

        stream = file(outname, "w")
        yaml.dump(self, stream)
        stream.close()

        return

    @classmethod
    def fromYaml(cls, yamlFile):
        print("Loading parameters from {}").format(yamlFile)

        cls = yaml.load(file(yamlFile, "r"))

        return cls
