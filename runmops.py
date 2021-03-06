#!/usr/bin/env python

"""

A simple script to run MOPS. (Work in progress)

Command-line call:
python runMops.py {nightly DIA source directory} {output directory}

Requirements:
MOPS setup (with MOPS_DIR path variable pointing to bin mops_daymops)

Contact moeyensj@uw.edu with questions and / or concerns.

"""

import os
import subprocess
import glob
import argparse
import yaml
import shutil
import multiprocessing

from analyzemops.parameters import Parameters
from analyzemops.tracker import Tracker

# File suffixes
DIASOURCE_SUFFIX = ".dias"
TRACKLET_SUFFIX = ".tracklets"
TRACKLET_BY_INDEX_SUFFIX = TRACKLET_SUFFIX + ".byIndices"
COLLAPSED_TRACKLET_SUFFIX = TRACKLET_SUFFIX + ".collapsed"
PURIFIED_TRACKLET_SUFFIX = TRACKLET_SUFFIX + ".purified"
FINAL_TRACKLET_SUFFIX = TRACKLET_SUFFIX + ".final"
TRACKLET_BY_ID_SUFFIX = ".byDiaIds"
TRACK_SUFFIX = ".track"
FINAL_TRACK_SUFFIX = TRACK_SUFFIX + ".final"

TRACKLETS_DIR = "tracklets/"
COLLAPSED_TRACKLETS_DIR = "trackletsCollapsed/"
PURIFIED_TRACKLETS_DIR = "trackletsPurified/"
FINAL_TRACKLETS_DIR = "trackletsFinal/"
TRACKLETS_BY_NIGHT_DIR = "trackletsByNight/"
TRACKS_DIR = "tracks/"
FINAL_TRACKS_DIR = "tracksFinal/"

VERBOSE = True

__all__ = ["directoryBuilder", "runFindTracklets", "runIdsToIndices",
           "runCollapseTracklets", "runPurifyTracklets", "runRemoveSubsets",
           "runIndicesToIds", "runMakeLinkTrackletsInputByNight", "runLinkTracklets"]

defaults = Parameters()

def directoryBuilder(runDir,
                     findTracklets=True,
                     collapseTracklets=True,
                     purifyTracklets=True,
                     removeSubsetTracklets=True,
                     linkTracklets=True,
                     removeSubsetTracks=True,
                     overwrite=False,
                     verbose=VERBOSE):
    """
    Builds the directory structure for MOPS output files. Returns output
    directory keyed dictionary of file paths.

    Possible keys:
        "trackletsDir",
        "collapsedDir",
        "purifiedDir",
        "finalTrackletsDir",
        "trackletsByNightDir",
        "tracksDir",
        "finalTracksDir"

    Parameters
    ----------
    runDir : str
        Name of the top folder

    findTracklets : bool, optional
        Build findTracklets output directory? [Default = True]

    collapseTracklets : bool, optional
        Build collapseTracklets output directory? [Default = True]

    purifyTracklets : bool, optional
        Build purifyTracklets output directory? [Default = True]

    removeSubsetTracklets : bool, optional
        Build removeSubsets tracklets output directory? [Default = True]

    removeSubsetTracks : bool, optional 
        Build removeSubsets tracks ouput directory? [Default = True]

    overwrite : bool, optional
        Use carefully! If directory structure exists delete it. [Default = False]

    Returns
    -------
    dict
        Dictionary with keys like "trackletsDir", "collapsedDir", etc... with paths to 
        the respective directories as values.

    """
    # Check if path exists, if it does only continue if overwrite is true
    if os.path.exists(runDir):
        if overwrite:
            shutil.rmtree(runDir)
            os.mkdir(runDir)
            print("Overwrite triggered: deleting existing directory...")
            print("")
        else:
            raise NameError("Run directory exists! Cannot continue!")
    else:
        os.mkdir(runDir)

    dirsOut = {}

    if findTracklets:
        dirsOut["trackletsDir"] = TRACKLETS_DIR

    if collapseTracklets:
        dirsOut["collapsedDir"] = COLLAPSED_TRACKLETS_DIR

    if purifyTracklets:
        dirsOut["purifiedDir"] = PURIFIED_TRACKLETS_DIR

    if removeSubsetTracklets:
        dirsOut["finalTrackletsDir"] = FINAL_TRACKLETS_DIR

    if linkTracklets:
        dirsOut["trackletsByNightDir"] = TRACKLETS_BY_NIGHT_DIR
        dirsOut["tracksDir"] = TRACKS_DIR

    if removeSubsetTracks:
        dirsOut["finalTracksDir"] = FINAL_TRACKS_DIR

    for d in dirsOut:
        newDir = os.path.join(runDir, dirsOut[d])

        if os.path.exists(newDir):
            print("%s already exists.")
        else:
            os.mkdir(newDir)

        dirsOut[d] = newDir

    return dirsOut


def runFindTracklets(diasources, outDir,
                     vmax=defaults.vMax,
                     vmin=defaults.vMin,
                     verbose=VERBOSE):
    """
    Runs findTracklets.

    Generates tracklets given a set of DIA sources.

    Parameters
    ----------
    diasources : list
        List of paths to nightly diasource files.

    outDir : str
        Tracklet output directory.

    vmax : float, optional
        Maximum velocity tracklets can have in degrees per day.
        [Default = `analyzemops.parameters.vMax`]

    vmin : float, optional
        Minimum velocity tracklets can have in degrees per day.
        [Default = `analyzemops.parameters.vMin`]

    verbose : bool, optional
        Print progress statements? [Default = True]
    
    Returns
    -------
    list
        List of findTracklets output files.
    """
    function = "findTracklets"
    tracklets = []

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    for diasource in diasources:
        trackletsOut = _out(outDir, diasource, TRACKLET_SUFFIX)

        call = [function, "-i", diasource, "-o",
                trackletsOut, "-v", str(vmax), "-m", str(vmin)]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        tracklets.append(trackletsOut)

    if verbose:
        _status(function, False)

    return sorted(tracklets)


def runIdsToIndices(tracklets, diasources, outDir,
                    verbose=VERBOSE):
    """
    Runs idsToIndices.py.

    Rearranges tracklets by index as opposed to id. This format is required
    by collapseTracklets, purifyTracklets and removeSubsets.

    Parameters
    ----------
    tracklets : list
        List of tracklet files.

    diasources : list
        List of diasources.

    outDir : str
        Tracklet by index output directory.

    verbose : bool, optional
        Print progress statements? [Default = True]
    
    Returns
    -------
    list
        Tracklets printed by index files.
    """
    function = "idsToIndices.py"
    byIndex = []

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    for tracklet, diasource in zip(tracklets, diasources):
        byIndexOut = _out(outDir, diasource, TRACKLET_BY_INDEX_SUFFIX)

        script = str(os.getenv("MOPS_DIR")) + "/bin/idsToIndices.py"
        call = ["python", script, tracklet, diasource, byIndexOut]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        byIndex.append(byIndexOut)

    if verbose:
        _status(function, False)

    return sorted(byIndex)


def runCollapseTracklets(trackletsByIndex, diasources, outDir,
                         raTol=defaults.raTol,
                         decTol=defaults.decTol,
                         angTol=defaults.angTol,
                         vTol=defaults.vTol,
                         method=defaults.method,
                         useRMSfilt=defaults.useRMSfilt,
                         trackletRMSmax=defaults.trackletRMSmax,
                         verbose=VERBOSE):
    """
    Runs collapseTracklets.

    Parameters
    ----------
    trackletsByIndex : list
        List of tracklets printed by index.

    diasources : list
        List of nightly diasource files.
    
    outDir : str
        Collapsed tracklet output directory.

    raTol : float, optional
        RA tolerance in degrees when making tracklets.
        [Default = `analyzemops.parameters.raTol`]

    decTol : float, optional
        Dec tolerance in degrees when making tracklets.
        [Default = `analyzemops.parameters.decTol`]

    angTol : float, optional
        Angular tolerance in degrees when making tracklets.
        [Default = `analyzemops.parameters.angTol`]

    vTol : float, optional
        Tolerance in velocity in degrees per day when making tracklets.
        [Default = `analyzemops.parameters.vTol`]

    method : {"greedy", "minimumRMS", "bestFit"}, optional
        If greedy, then we choose as many compatible tracklets as possible,
        as returned by the tree search.  If minimumRMS, we take the results
        of the tree search and repeatedly find the tracklet which would have
        the lowest resulting RMS value if added, then add it. If bestFit, 
        we repeatedly choose the tracklet which is closest to the current
        approximate line first, rather than re-calculating best-fit line
        for each possible tracklet. 
        [Default = `analyzemops.parameters.method`]

    useRMSfilt : bool, optional
        Enforce a maximum RMS distance for any tracklet which is the
        product of collapsing.
        [Default = `analyzemops.parameters.useRMSfilt`]

    trackletRMSmax : float, optional
        Only used if ``useRMSfilt = True``. Describes the function for RMS filtering.
        Tracklets will not be collapsed unless the resulting tracklet would have 
        RMS <= maxRMSm * average magnitude + maxRMSb. Defaults are 0. and .001.
        [Default = `analyzemops.parameters.trackletRMSmax`]

    verbose : bool, optional
        Print progress statements? [Default = True]
    
    Returns
    -------
    list
        List of collapseTracklets output files.
    """
    function = "collapseTracklets"
    collapsedTracklets = []

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    for tracklet, diasource in zip(trackletsByIndex, diasources):
        collapsedTracklet = _out(outDir, diasource, COLLAPSED_TRACKLET_SUFFIX)

        call = ["collapseTracklets", diasource, tracklet, str(raTol),
                str(decTol), str(angTol), str(vTol), collapsedTracklet,
                "--method", method,
                "--useRMSFilt", str(useRMSfilt),
                "--maxRMS", str(trackletRMSmax)]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        collapsedTracklets.append(collapsedTracklet)

    if verbose:
        _status(function, False)

    return sorted(collapsedTracklets)


def runPurifyTracklets(collapsedTracklets, diasources, outDir,
                       trackletRMSmax=defaults.trackletRMSmax,
                       verbose=VERBOSE):
    """
    Runs purifyTracklets.

    Parameters
    ----------
    collapsedTrackets : list
        List of collapsed tracklet files.

    diasources : list
        List of nightly diasource files.

    outDir: str
        Purified tracklet output directory.

    trackletRMSmax : float, optional
        Maximum tracklet RMS.  
        [Default = `analyzemops.parameters.trackletRMSmax`]

    verbose : bool, optional
        Print progress statements? [Default = True]

    Returns
    -------
    list 
        List of purified tracklet files.
    """
    function = "purifyTracklets"
    purifiedTracklets = []

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    for tracklet, diasource in zip(collapsedTracklets, diasources):
        purifiedTracklet = _out(outDir, diasource, PURIFIED_TRACKLET_SUFFIX)

        call = ["purifyTracklets",
                "--detsFile", diasource,
                "--pairsFile", tracklet,
                "--maxRMS", str(trackletRMSmax),
                "--outFile", purifiedTracklet]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        purifiedTracklets.append(purifiedTracklet)

    if verbose:
        _status(function, False)

    return sorted(purifiedTracklets)


def runRemoveSubsets(purifiedTracklets, diasources, outDir,
                     rmSubsets=defaults.rmSubsetTracklets,
                     keepOnlyLongest=defaults.keepOnlyLongestTracklets,
                     suffix=FINAL_TRACKLET_SUFFIX,
                     verbose=VERBOSE):
    """
    Runs removeSubsets.

    Parameters
    ----------
    purifiedTracklets : list
        List of purified tracklet files.

    diasources : list
        List of nightly diasource files.

    outDir : str
        Final tracklet output directory.

    rmSubsets : bool, optional
        Remove subsets? This flag gives the ability to run removeSubsets as
        where it does nothing on the inputs.
        [Default = `analyzemops.parameters.rmSubsetTracklets]

    keepOnlyLongest : bool, optional
        If ``rmSubsets = True``, keep only the longest tracklets and remove all 
        subsets. 
        [Default = `analyzemops.parameters.keepOnlyLongestTracklets]

    suffix : str, optional
        Suffix to append to input file names when saving output files. 
        [Default = ".final"]

    verbose : bool, optional
        Print progress statements? [Default = True]
    
    Returns
    -------
    list
        Final tracklet files.
    """
    function = "removeSubsets"
    finalTracklets = []

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    for tracklet, diasource in zip(purifiedTracklets, diasources):
        finalTracklet = _out(outDir, tracklet, suffix)

        call = ["removeSubsets",
                "--inFile", tracklet,
                "--outFile", finalTracklet,
                "--removeSubsets", str(rmSubsets),
                "--keepOnlyLongest", str(keepOnlyLongest)]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        finalTracklets.append(finalTracklet)

    if verbose:
        _status(function, False)

    return sorted(finalTracklets)


def runIndicesToIds(finalTracklets, diasources, outDir, suffix,
                    verbose=VERBOSE):
    """
    Runs indicesToIds.py.

    Convert back to original tracklet format.

    Parameters
    ----------
    finalTracklets : list
        List of final (subset removed) tracklets files.

    diasources : list
        List of nightly diasource files.

    outDir : str
        Tracklet by ID output directory.

    suffix : str
        Suffix to append to input files names when saving outputs. 

    verbose : bool, optional
        Print progress statements? [Default = True]
    
    Returns
    -------
    list
        Final tracklet files printed by diasource id.
    """
    function = "indicesToIds.py"
    byId = []

    outfile = open(outDir + "/indicesToIds.out", "w")
    errfile = open(outDir + "/indicesToIds.err", "w")

    if verbose:
        _status(function, True)

    for tracklet, diasource in zip(finalTracklets, diasources):
        byIdOut = _out(outDir, diasource, suffix + TRACKLET_BY_ID_SUFFIX)

        script = str(os.getenv("MOPS_DIR")) + "/bin/indicesToIds.py"
        call = ["python", script, tracklet, diasource, byIdOut]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        byId.append(byIdOut)

    if verbose:
        _status(function, False)

    return sorted(byId)


def runMakeLinkTrackletsInputByNight(diasourcesDir, trackletsDir, outDir,
                                     diasSuffix=DIASOURCE_SUFFIX,
                                     trackletSuffix=(FINAL_TRACKLET_SUFFIX +
                                                     TRACKLET_BY_ID_SUFFIX),
                                     windowSize=defaults.windowSize,
                                     verbose=VERBOSE):
    """
    Runs makeLinkTrackletsInput_byNight.py.

    Reads tracklet files into dets and ids as required by linkTracklets.

    Parameters
    ----------
    diasourcesDir : str
        Directory containing nightly diasource files.
    
    trackletsDir : str
        Directory containing final (subset removed) tracklets.
    
    outDir : str
        Dets and ids file output directory.

    diaSuffix : str, optional
        Suffix to append to window diasource files. [Default = ".dets"]

    trackletSuffix : str, optional
        Suffix to append to window tracklet files. [Default = ".ids"]

    windowSize : int, optional
        Number of nights in a window in which to combine nightly diasources
        and tracklets into. [Default = `analyzemops.parameters.windowSize`]

    verbose : bool, optional
        Print progress statements? [Default = True]
    
    Returns
    -------
    list
        List of per window diasource files.

    list
        List of per window tracklets.
    """
    function = "makeLinkTrackletsInput_byNight.py"

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    script = str(os.getenv("MOPS_DIR")) + "/bin/makeLinkTrackletsInput_byNight.py"
    call = ["python", script,
            "--windowSize", str(windowSize),
            "--diasSuffix", diasSuffix,
            "--trackletSuffix", trackletSuffix,
            diasourcesDir,
            trackletsDir,
            outDir]
    subprocess.call(call, stdout=outfile, stderr=errfile)

    ids = glob.glob(outDir + "*.ids")
    dets = glob.glob(outDir + "*.dets")

    if verbose:
        _status(function, False)

    return sorted(dets), sorted(ids)


def runLinkTracklets(dets, ids, outDir,
                     enableMultiprocessing=True,
                     processes=8,
                     detErrThresh=defaults.detErrThresh,
                     decAccelMax=defaults.decAccelMax,
                     raAccelMax=defaults.raAccelMax,
                     nightMin=defaults.nightMin,
                     detectMin=defaults.detectMin,
                     bufferSize=defaults.bufferSize,
                     latestFirstEnd=defaults.latestFirstEnd,
                     earliestLastEnd=defaults.earliestLastEnd,
                     leafNodeSizeMax=defaults.leafNodeSizeMax,
                     trackRMSmax=defaults.trackRMSmax, 
                     trackAdditionThresh=defaults.trackAdditionThresh,
                     defaultAstromErr=defaults.defaultAstromErr,
                     trackChiSqMin=defaults.trackChiSqMin,
                     skyCenterRA=defaults.skyCenterRA,
                     skyCenterDec=defaults.skyCenterDec,
                     obsLat=defaults.obsLat,
                     obsLon=defaults.obsLon,
                     verbose=VERBOSE):
    """
    Runs linkTracklets.

    Parameters
    ----------
    dets : list,
        List of per window diasource files.
    
    ids : list
        List of per window tracklet files.

    outDir : str
        Tracks output directory.

    enableMultiprocessing : bool, optional
        Use multiple processors? [Default = True]

    processes : int, optional
        If ``enableMultiprocessing = True`` then use this many processors. 
        [Default = 8]
    
    detErrThresh : float, optional
        Maximum allowed observational error.
        [Default = `analyzemops.parameters.detErrThresh`]

    decAccelMax : float, optional
        Maximum sky-plane acceleration of a track (declination).
        [Default = `analyzemops.parameters.decAccelMax`]

    raAccelMax : float, optional
        Maximum sky-plane acceleration of a track (RA).
        [Default = `analyzemops.parameters.raAccelMax`]

    nightMin : int, optional
        Require tracks contain detections from at least this many nights.
        [Default = `analyzemops.parameters.nightMin`]

    detectMin : int, optional
        Require tracks contain at least this many detections.
        [Default = `analyzemops.parameters.detectMin`]

    bufferSize : int, optional
        Number of tracks to buffer in memory before flushing output.
        [Default = `analyzemops.parameters.bufferSize`]

    latestFirstEnd : float, optional
        If specified, only search for tracks with first endpoint before time specified.
        [Default = `analyzemops.parameters.latestFirstEnd`]

    earliestLastEnd : float, optional 
        If specified, only search for tracks with last endpoint after time specified.
        [Default = `analyzemops.parameters.earliestLastEnd`]

    leafNodeSizeMax : float, optional
        Set max leaf node size for nodes in KDTree
        [Default = `analyzemops.parameters.leafNodeSizeMax`]

    trackRMSmax : float, optional
        Maximum RMS for adding individual track detections to a track.
        [Default = `analyzemops.parameters.trackRMSmax`] 

    trackAdditionThresh : float, optional
        [purpose not clear]!!! in radians.
        [Default = `analyzemops.parameters.trackAdditionThresh`]

    defaultAstromErr : float, optional
        [purpose not clear]!!! in degrees.
        [Default = `analyzemops.parameters.defaultAstromErr`]

    trackChiSqMin : float, optional
        Minimum chi-squared fit for track to be accepted.
        [Default = `analyzemops.parameters.trackChiSqMin`]

    skyCenterRA : float, optional 
        Topocentric recentering RA in degrees.
        [Default = `analyzemops.parameters.skyCenterRA`]

    skyCenterDec : float, optional
        Topocentric recentering Dec in degrees.
        [Default = `analyzemops.parameters.skyCenterDec`]

    obsLat : float, optional
        Observatory latitude in degrees.
        [Default = `analyzemops.parameters.obsLat`]

    obsLon : float, optional
        Observatory East longitude in degrees.
        [Default = `analyzemops.parameters.obsLon`]

    verbose : bool, optional
        Print progress statements? [Default = True]
    
    Returns
    -------
    list
        List of track files.
    """
    function = "linkTracklets"
    tracks = []
    outfiles = []
    errfiles = []

    if verbose:
        _status(function, True)

    if enableMultiprocessing:
        print("Multiprocessing Enabled!")
        print("Using %s CPUs in parallel." % (processes))

        calls = []

        for detIn, idIn in zip(dets, ids):
            trackOut = _out(outDir, detIn, TRACK_SUFFIX)
            outfileName = trackOut + ".out"
            errfileName = trackOut + ".err"

            call = ["linkTracklets",
                    "-e", str(detErrThresh),
                    "-D", str(decAccelMax),
                    "-R", str(raAccelMax),
                    "-u", str(nightMin),
                    "-s", str(detectMin),
                    "-b", str(bufferSize),
                    "-r", str(trackRMSmax),
                    "-T", str(trackAdditionThresh),
                    "-a", str(defaultAstromErr),
                    "-q", str(trackChiSqMin),
                    "-x", str(skyCenterRA),
                    "-y", str(skyCenterDec),
                    "-z", str(obsLat),
                    "-w", str(obsLon),
                    "-d", detIn,
                    "-t", idIn,
                    "-o", trackOut]

            if latestFirstEnd is not None:
                call.extend(["-F", str(latestFirstEnd)])
            if earliestLastEnd is not None:
                call.extend(["-L", str(earliestLastEnd)])
            if leafNodeSizeMax is not None:
                call.extend(["-n", str(leafNodeSizeMax)])

            tracks.append(trackOut)
            outfiles.append(outfileName)
            errfiles.append(errfileName)

            calls.append(call)

        p = multiprocessing.Pool(processes=processes)
        p.map(_runWindow, calls)

    else:

        for detIn, idIn in zip(dets, ids):
            trackOut = _out(outDir, detIn, TRACK_SUFFIX)
            outfileName = trackOut + ".out"
            errfileName = trackOut + ".err"
            outfile = open(outfileName, "w")
            errfile = open(errfileName, "w")

            call = ["linkTracklets",
                    "-e", str(detErrThresh),
                    "-D", str(decAccelMax),
                    "-R", str(raAccelMax),
                    "-u", str(nightMin),
                    "-s", str(detectMin),
                    "-b", str(bufferSize),
                    "-r", str(trackRMSmax),
                    "-T", str(trackAdditionThresh),
                    "-a", str(defaultAstromErr),
                    "-q", str(trackChiSqMin),
                    "-x", str(skyCenterRA),
                    "-y", str(skyCenterDec),
                    "-z", str(obsLat),
                    "-w", str(obsLon),
                    "-d", detIn,
                    "-t", idIn,
                    "-o", trackOut]

            if latestFirstEnd is not None:
                call.extend(["-F", str(latestFirstEnd)])
            if earliestLastEnd is not None:
                call.extend(["-L", str(earliestLastEnd)])
            if leafNodeSizeMax is not None:
                call.extend(["-n", str(leafNodeSizeMax)])

            subprocess.call(call, stdout=outfile, stderr=errfile)

            tracks.append(trackOut)
            outfiles.append(outfileName)
            errfiles.append(errfileName)

    if verbose:
        _status(function, False)

    return sorted(tracks), sorted(outfiles), sorted(errfiles)


def runMops(parameters, tracker,
            findTracklets=True,
            collapseTracklets=True,
            purifyTracklets=True,
            removeSubsetTracklets=True,
            linkTracklets=True,
            removeSubsetTracks=True,
            enableMultiprocessing=True,
            processes=8,
            overwrite=False,
            verbose=VERBOSE):
    """
    Runs Moving Object Pipeline.

    Parameters
    ----------
    parameters : `analyzemops.parameters`
        User or default defined MOPS parameter object.

    tracker : `analyzemops.tracker`
        Tracker object keeps track of output files and directories.

    findTracklets : bool, optional
        Run findTracklets? [Default = True]

    collapseTracklets : bool, optional
        Run collapseTracklets? [Default = True]

    purifyTracklets: bool, optional
        Run purifyTracklets? [Default = True]

    removeSubsetTracklets : bool, optional
        Run removeSubsets on tracklets? [Default = True]

    linkTracklets : bool, optional
        Run linkTracklets? [Default = True]

    removeSubsetTracks : bool, optional
        Run removeSubsets on tracks? [Default = True]

    enableMultiprocessing : bool, optional
        Use multiple processors? [Default = True]

    processes : int, optional
        If ``enableMultiprocessing = True`` then use this many processors. 
        [Default = 8]

    overwrite : bool, optional
        If directory structure exists, overwrite the files? [Default = False]

    verbose : bool, optional
        Print progress statements? [Default = True]
    
    Returns
    -------
    `analzemops.parameters`
        The original parameters object.

    `analyzemops.tracker`
        The updated tracker object.
    """
    if verbose:
        print("------- Run MOPS -------")
        print("Running LSST's Moving Object Pipeline")
        print("")

    runDir = tracker.runDir
    diasources = tracker.diasources
    diasourcesDir = tracker.diasourcesDir

    # If overwrite, delete progress stored in tracker.
    if overwrite:
        print("Overwrite triggered: clearing tracker...")
        print("")
        tracker = Tracker(runDir)
        tracker.getDetections(diasourcesDir)
    
    elif tracker.ranDirectoryBuilder is True and overwrite is False:
        dirs = {"trackletsDir": tracker.trackletsDir,
                "collapsedDir": tracker.collapsedTrackletsDir,
                "purifiedDir": tracker.purifiedTrackletsDir,
                "finalTrackletsDir": tracker.finalTrackletsDir,
                "trackletsByNightDir": tracker.trackletsByNightDir,
                "tracksDir": tracker.tracksDir,
                "finalTracksDir": tracker.finalTracksDir}
    else:
        dirs = directoryBuilder(
                runDir,
                findTracklets=findTracklets,
                collapseTracklets=collapseTracklets,
                purifyTracklets=purifyTracklets,
                removeSubsetTracklets=removeSubsetTracklets,
                linkTracklets=linkTracklets,
                removeSubsetTracks=removeSubsetTracks,
                overwrite=overwrite,
                verbose=verbose)
        tracker.ranDirectoryBuilder = True

        # Populate tracker with directory information
        if findTracklets is True:
            tracker.trackletsDir = dirs["trackletsDir"]
            tracker.trackletsByIndexDir = dirs["trackletsDir"]

        if collapseTracklets is True:
            tracker.collapsedTrackletsDir = dirs["collapsedDir"]
            tracker.collapsedTrackletsByIdDir = dirs["collapsedDir"]

        if purifyTracklets is True:
            tracker.purifiedTrackletsDir = dirs["purifiedDir"]
            tracker.purifiedTrackletsByIdDir = dirs["purifiedDir"]

        if removeSubsetTracklets is True:
            tracker.finalTrackletsDir = dirs["finalTrackletsDir"]
            tracker.finalTrackletsByIdDir = dirs["finalTrackletsDir"]

        if linkTracklets is True:
            tracker.trackletsByNightDir = dirs["trackletsByNightDir"]
            tracker.tracksDir = dirs["tracksDir"]

        if removeSubsetTracks is True:
            tracker.finalTracksDir = dirs["finalTracksDir"]
        tracker.toYaml(outDir=runDir)

    # Save parameters
    parameters.toYaml(outDir=runDir)
    print("")

    # Run findTracklets
    if findTracklets:
        if tracker.ranFindTracklets is False:
            tracker.tracklets = runFindTracklets(tracker.diasources,
                                                 tracker.trackletsDir,
                                                 vmax=parameters.vMax,
                                                 vmin=parameters.vMin,
                                                 verbose=verbose)
            tracker.ranFindTracklets = True
            inputTrackletsDir = dirs["trackletsDir"]
            inputTrackletSuffix = TRACKLET_SUFFIX
            tracker.toYaml(outDir=runDir)
        else:
            print("findTracklets has already completed, moving on...")

        print("")

    if collapseTracklets:
        if tracker.ranIdsToIndices is False:
            # Run idsToIndices
            tracker.trackletsByIndex = runIdsToIndices(tracker.tracklets, 
                                                       tracker.diasources,
                                                       tracker.trackletsDir,
                                                       verbose=verbose)
            tracker.ranIdsToIndices = True
            tracker.toYaml(outDir=runDir)
        else:
            print("idsToIndices has already completed, moving on...")

        print("")

        # Run collapseTracklets
        if tracker.ranCollapseTracklets is False:
            tracker.collapsedTracklets = runCollapseTracklets(tracker.trackletsByIndex,
                                                              tracker.diasources,
                                                              tracker.collapsedTrackletsDir,
                                                              raTol=parameters.raTol,
                                                              decTol=parameters.decTol,
                                                              angTol=parameters.angTol,
                                                              vTol=parameters.vTol,
                                                              method=parameters.method,
                                                              useRMSfilt=parameters.useRMSfilt,
                                                              trackletRMSmax=parameters.trackletRMSmax,
                                                              verbose=verbose)
            tracker.collapsedTrackletsById = runIndicesToIds(tracker.collapsedTracklets,
                                                             tracker.diasources,
                                                             tracker.collapsedTrackletsDir,
                                                             COLLAPSED_TRACKLET_SUFFIX,
                                                             verbose=verbose)
            tracker.ranCollapseTracklets = True
            inputTrackletsDir = tracker.collapsedTrackletsDir
            inputTrackletSuffix = COLLAPSED_TRACKLET_SUFFIX + TRACKLET_BY_ID_SUFFIX
            tracker.toYaml(outDir=runDir)
        else:
            print("collapseTracklets has already completed, moving on...")

        print("")

    if purifyTracklets:
        # Run purifyTracklets
        if tracker.ranPurifyTracklets is False:
            tracker.purifiedTracklets = runPurifyTracklets(tracker.collapsedTracklets,
                                                           tracker.diasources,
                                                           tracker.purifiedTrackletsDir,
                                                           trackletRMSmax=parameters.trackletRMSmax,
                                                           verbose=verbose)
            tracker.purifiedTrackletsById = runIndicesToIds(tracker.purifiedTracklets,
                                                            tracker.diasources,
                                                            tracker.purifiedTrackletsDir,
                                                            PURIFIED_TRACKLET_SUFFIX,
                                                            verbose=verbose)
            tracker.ranPurifyTracklets = True
            inputTrackletsDir = tracker.purifiedTrackletsDir
            inputTrackletSuffix = PURIFIED_TRACKLET_SUFFIX + TRACKLET_BY_ID_SUFFIX
            tracker.toYaml(outDir=runDir)
        else:
            print("purifyTracklets has already completed, moving on...")

        print("")

    if removeSubsetTracklets:
        # Run removeSubsets
        if tracker.ranRemoveSubsetTracklets is False:
            tracker.finalTracklets = runRemoveSubsets(tracker.purifiedTracklets,
                                                      tracker.diasources,
                                                      tracker.finalTrackletsDir,
                                                      rmSubsets=parameters.rmSubsetTracklets,
                                                      keepOnlyLongest=parameters.keepOnlyLongestTracklets,
                                                      verbose=verbose)
            tracker.ranRemoveSubsetTracklets = True
            tracker.toYaml(outDir=runDir)
        else:
            print("removeSubsets (tracklets) has already completed, moving on...")

        print("")

        # Run indicesToIds
        if tracker.ranIndicesToIds is False:
            tracker.finalTrackletsById = runIndicesToIds(tracker.finalTracklets,
                                                         tracker.diasources,
                                                         tracker.finalTrackletsDir,
                                                         FINAL_TRACKLET_SUFFIX,
                                                         verbose=verbose)
            tracker.ranIndicesToIds = True
            inputTrackletsDir = tracker.finalTrackletsDir
            inputTrackletSuffix = FINAL_TRACKLET_SUFFIX + TRACKLET_BY_ID_SUFFIX
            tracker.toYaml(outDir=runDir)
        else:
            print("indicesToIds has already completed, moving on...")
        
        print("")

    if linkTracklets:
        # Run makeLinkTrackletsInputByNight
        if tracker.ranMakeLinkTrackletsInputByNight is False:
            tracker.dets, tracker.ids = runMakeLinkTrackletsInputByNight(tracker.diasourcesDir,
                                                                         inputTrackletsDir,
                                                                         tracker.trackletsByNightDir,
                                                                         trackletSuffix=inputTrackletSuffix,
                                                                         windowSize=parameters.windowSize,
                                                                         verbose=verbose)
            tracker.ranMakeLinkTrackletsInputByNight = True
            tracker.toYaml(outDir=runDir)
        else:
            print("makeLinkTrackletsInput_byNight has already completed, moving on...")

        print("")

        # Run linkTracklets
        if tracker.ranLinkTracklets is False:
            tracker.tracks, tracker.trackOuts, tracker.trackErrs = runLinkTracklets(tracker.dets,
                                                                                    tracker.ids,
                                                                                    tracker.tracksDir,
                                                                                    enableMultiprocessing=enableMultiprocessing,
                                                                                    processes=processes,
                                                                                    detErrThresh=parameters.detErrThresh,
                                                                                    decAccelMax=parameters.decAccelMax,
                                                                                    raAccelMax=parameters.raAccelMax,
                                                                                    nightMin=parameters.nightMin,
                                                                                    detectMin=parameters.detectMin,
                                                                                    bufferSize=parameters.bufferSize,
                                                                                    latestFirstEnd=parameters.latestFirstEnd,
                                                                                    earliestLastEnd=parameters.earliestLastEnd,
                                                                                    leafNodeSizeMax=parameters.leafNodeSizeMax,
                                                                                    trackRMSmax=parameters.trackRMSmax, 
                                                                                    trackAdditionThresh=parameters.trackAdditionThresh,
                                                                                    defaultAstromErr=parameters.defaultAstromErr,
                                                                                    trackChiSqMin=parameters.trackChiSqMin,
                                                                                    skyCenterRA=parameters.skyCenterRA,
                                                                                    skyCenterDec=parameters.skyCenterDec,
                                                                                    obsLat=parameters.obsLat,
                                                                                    obsLon=parameters.obsLon,
                                                                                    verbose=verbose)
            tracker.ranLinkTracklets = True
            tracker.toYaml(outDir=runDir)
        else:
            print("linkTracklets has already completed, moving on...")

        print("")

    if removeSubsetTracks:
        # Run removeSubsets (tracks)
        if tracker.ranRemoveSubsetTracks is False:
            tracker.finalTracks = runRemoveSubsets(tracker.tracks,
                                                   tracker.diasources,
                                                   tracker.finalTracksDir,
                                                   rmSubsets=parameters.rmSubsetTracks,
                                                   keepOnlyLongest=parameters.keepOnlyLongestTracks,
                                                   suffix=FINAL_TRACK_SUFFIX,
                                                   verbose=verbose)
            tracker.ranRemoveSubsetTracks = True
            tracker.toYaml(outDir=runDir)
        else:
            print("removeSubsets (tracks) has already completed, moving on...")

        print("")

    # Print status and save tracker
    print(tracker)
    tracker.toYaml(outDir=runDir)

    return parameters, tracker


def _status(function, current):
    """
    Simple function that prints the current MOPS function running.

    """
    if current:
        print("------- Run MOPS -------")
        print("Running %s..." % (function))
    else:
        print("Completed running %s." % (function))
        print("")
    return


def _log(function, outDir):
    """
    Creates two log files capturing MOPS output printed to stdout and stderr.

    """
    # Split function name to get rid of possible .py
    function = os.path.splitext(function)[0]

    # Create outfile and errfile streams
    outfile = open(os.path.join(outDir, function + ".out"), "w")
    errfile = open(os.path.join(outDir, function + ".err"), "w")

    return outfile, errfile


def _out(outDir, filename, suffix):
    """
    Makes an outfile based off of the name of the input files for different 
    MOPS functions. 

    """
    # Retrieve base file name
    base = os.path.basename(filename)
    # Remove all suffixes from filename and add new
    outName = base.split(".")[0] + suffix
    # Create path 
    outFile = os.path.join(outDir, outName)
    return outFile


def _runWindow(call):
    """
    Simple hacky function that will create the same log files as _log but for the case
    where we are running multiprocessing on linkTracklets and are running windows.

    """
    # Unfortunately pool.map() can"t map a function call of multiple arguments
    # so we have to extract the trackOut name from the function call.
    # When python 3.3 is accepted as standard, pool.starmap() will be used instead.
    trackOut = call[-1]
    outfile = open(trackOut + ".out", "w")
    errfile = open(trackOut + ".err", "w")
    subprocess.call(call, stdout=outfile, stderr=errfile)
    return

def _runArgs():
    """
    Helper function that runs commandline arguments.

    """
    default = Parameters(verbose=False)

    parser = argparse.ArgumentParser(
        prog="runMops",
        description="Given a set of nightly or obshist DIA sources, will run LSST's Moving Object Pipeline (MOPs)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("diasourcesDir", help="Directory containing nightly diasources (.dias)")
    parser.add_argument("outputDir", help="Output directory to be created for file output (must not exist)")

    # Config file, load parameters from config file if given
    parser.add_argument("-cfg", "--config_file", default=None,
        help="""If given, will read parameter values from file to overwrite default values defined in Parameters. 
        Parameter values not-defined in config file will be set to default. See default.cfg for sample config file.""")

    # Verbosity 
    parser.add_argument("-v","--verbose", action="store_false",
        help="Enables/disables print output")

    # findTracklets
    parser.add_argument("-vM", "--velocity_max", default=default.vMax, 
        help="Maximum velocity (used in findTracklets)")
    parser.add_argument("-vm", "--velocity_min", default=default.vMin, 
        help="Minimum velocity (used in findTracklets)")

    # collapseTracklets, purifyTracklets
    parser.add_argument("-rT", "--ra_tolerance", default=default.raTol, 
        help="RA tolerance (used in collapseTracklets)")
    parser.add_argument("-dT", "--dec_tolerance", default=default.decTol, 
        help="Dec tolerance (used in collapseTracklets)")
    parser.add_argument("-aT", "--angular_tolerance", default=default.angTol,
        help="Angular tolerance (used in collapseTracklets)")
    parser.add_argument("-vT", "--velocity_tolerance", default=default.vTol, 
        help="Velocity tolerance (used in collapseTracklets)")
    parser.add_argument("-m","--method", default=default.method,
        help="""Method to collapse tracklets, can be one of: greedy | minimumRMS | bestFit.
        If greedy, then we choose as many compatible tracklets as possible, as returned by the tree search. 
        If minimumRMS, we take the results of the tree search and repeatedly find the tracklet which would 
        have the lowest resulting RMS value if added, then add it. If bestFit, we repeatedly choose the tracklet 
        which is closest to the current approximate line first, rather than re-calculating best-fit line for 
        each possible tracklet. (used in collapseTracklets)""")
    parser.add_argument("-rF","--use_rms_filter", default=default.useRMSfilt,
        help="Enforce a maximum RMS distance for any tracklet which is the product of collapsing (used in collapseTracklets)")
    parser.add_argument("-rM", "--tracklet_rms_max", default=default.trackletRMS_max,
        help="""Only used if useRMSfilt == true. Describes the function for RMS filtering.  
        Tracklets will not be collapsed unless the resulting tracklet would have RMS <= maxRMSm * average magnitude + maxRMSb 
        (used in collapseTracklets and purifyTracklets""")

    # removeSubsets (tracklets)
    parser.add_argument("-S","--remove_subset_tracklets", default=default.rmSubsetTracklets,
        help="Remove subsets (used in removeSubsets)")
    parser.add_argument("-k","--keep_only_longest_tracklets", default=default.keepOnlyLongestTracklets,
        help="Keep only the longest collinear tracklets in a set (used in removeSubsets)")

    # makeLinkTrackletsInput_byNight
    parser.add_argument("-w", "--window_size", default=default.windowSize,
        help="Number of nights in sliding window (used in makeLinkTrackletsInput_byNight.py")

    # linkTracklets
    parser.add_argument("-e", "--detection_error_threshold", default=default.detErrThresh,
        help="Maximum allowed observational error (used in linkTracklets)")
    parser.add_argument("-D", "--dec_acceleration_max", default=default.decAccelMax,
        help="Maximum sky-plane acceleration in Dec (used in linkTracklets)")
    parser.add_argument("-R", "--ra_acceleration_max", default=default.raAccelMax,
        help="Maximum sky-plane acceleration in RA (used in linkTracklets)")
    parser.add_argument("-u", "--nights_min", default=default.nightMin,
        help="Require tracks to contain detections from at least this many nights (used in linkTracklets)")
    parser.add_argument("-s", "--detections_min", default=default.detectMin,
        help="Require tracks to contain at least this many detections (used in linkTracklets)")
    parser.add_argument("-b", "--output_buffer_size", default=default.bufferSize,
        help="Number of tracks to buffer in memory before flushing output (used in linkTracklets)")
    parser.add_argument("-F", "--latest_first_endpoint", default=default.latestFirstEnd,
        help="If specified, only search for tracks with first endpoint before time specified (used in linkTracklets)")
    parser.add_argument("-L", "--earliest_last_endpoint", default=default.earliestLastEnd,
        help="If specified, only search for tracks with last endpoint after time specified (used in linkTracklets)")
    parser.add_argument("-n", "--leaf_node_size_max", default=default.leafNodeSizeMax,
        help="Set max leaf node size for nodes in KDTree (used in linkTracklets)")
    parser.add_arugment("-r", "--track_RMS_max", default=default.trackRMSmax,
        help="Maximum RMS for adding individual track detections to a track (used in linkTracklets)")
    parser.add_arugment("-T", "--track_addition_threshold", default=default.trackAdditionThresh,
        help="[purpose not clear] in radians (used in linkTracklets)")
    parser.add_arugment("-a", "--default_astrometric_error", default=default.defaultAstromErr,
        help="[purpose not clear] in degrees (used in linkTracklets)")
    parser.add_arugment("-q", "--track_chi_square_minimum", default=default.trackChiSqMin,
        help="Minimum chi-squared fit for track to be accepted (used in linkTracklets)")
    parser.add_arugment("-x", "--sky_center_RA", default=default.skyCenterRA,
        help="Topocentric recentering RA in degrees (used in linkTracklets)")
    parser.add_arugment("-y", "--sky_center_Dec", default=default.skyCenterDec,
        help="Topocentric recentering Dec in degrees (used in linkTracklets)")
    parser.add_arugment("-z", "--observatory_lat", default=default.obsLat,
        help="Observatory latitude in degrees (used in linkTracklets)")
    parser.add_arugment("-w", "--observatory_lon", default=default.obsLon,
        help="Observatory East longitude in degrees (used in linkTracklets)")

    # removeSubsets (tracks)
    parser.add_argument("-St","--remove_subset_tracks", default=default.rmSubsetTracks,
        help="Remove subsets (used in removeSubsets)")
    parser.add_argument("-kt","--keep_only_longest_tracks", default=default.keepOnlyLongestTracks,
        help="Keep only the longest collinear tracks in a set (used in removeSubsets)")

    args = parser.parse_args()

    return args


if __name__ == "__main__":

    # Run command line arg parser and retrieve args
    args = _runArgs()
    verbose = args.verbose

    # Retrieve output directory and nightly DIA Sources directory
    runDir = os.path.join(os.path.abspath(args.outputDir), "")
    diasourcesDir = os.path.join(os.path.abspath(args.diasourcesDir), "")

    # Initialize Parameters and Tracker
    if args.config_file == None:
        parameters = Parameters(
                        velocity_max=args.velocity_max,
                        velocity_min=args.velocity_min,
                        ra_tolerance=args.ra_tolerance,
                        dec_tolerance=args.dec_tolerance,
                        angular_tolerance=args.angular_tolerance,
                        velocity_tolerance=args.velocity_tolerance,
                        method=args.method,
                        use_rms_filter=args.use_rms_filter,
                        rms_max=args.rms_max,
                        remove_subset_tracklets=args.remove_subset_tracklets,
                        keep_only_longest_tracklets=args.keep_only_longest_tracklets,
                        window_size=args.window_size,
                        detection_error_threshold=args.detection_error_threshold,
                        dec_acceleration_max=args.dec_acceleration_max,
                        ra_acceleration_max=args.ra_acceleration_max,
                        latest_first_endpoint=args.latest_first_endpoint,
                        earliest_last_endpoint=args.earliest_last_endpoint,
                        nights_min=args.nights_min,
                        detections_min=args.detections_min,
                        output_buffer_size=args.output_buffer_size,
                        leaf_node_size_max=args.leaf_node_size_max,
                        track_rms_max=args.track_RMS_max,
                        track_addition_threshold=args.track_addition_threshold,
                        default_astrometric_error=args.default_astrometric_error,
                        track_chi_square_minimum=args.track_chi_square_minimum,
                        sky_center_ra=args.sky_center_ra,
                        sky_center_dec=args.sky_center_dec,
                        observatory_lat=args.observatory_lat,
                        observatory_lon=args.observatory_lon,
                        remove_subset_tracks=args.remove_subset_tracks,
                        keep_only_longest_tracks=args.keep_only_longest_tracks)
    else:
        if verbose:
            print("Config file given. Reading parameters from file...")
            print("")
        cfg = yaml.load(open(args.config_file, "r"))
        parameters = Parameters(**cfg)

    # Initialize tracker
    tracker = Tracker(runDir)
    tracker.getDetections(diasourcesDir)

    if verbose is True:
        print(parameters)
        print(tracker)

    # Run MOPs
    parameters, tracker = runMops(parameters, tracker, verbose=verbose)
