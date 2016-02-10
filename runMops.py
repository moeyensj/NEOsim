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
import sys
import subprocess
import glob
import argparse
import yaml

from MopsParameters import MopsParameters
from MopsTracker import MopsTracker

# File suffixes
DIASOURCE_SUFFIX = ".dias"
TRACKLET_SUFFIX = ".tracklets"
BY_INDEX_SUFFIX = TRACKLET_SUFFIX + ".byIndices"
COLLAPSED_SUFFIX = TRACKLET_SUFFIX + ".collapsed"
PURIFIED_SUFFIX = TRACKLET_SUFFIX + ".purified"
FINAL_SUFFIX = TRACKLET_SUFFIX + ".final"
BY_ID_SUFFIX = ".byDiaIds"
TRACK_SUFFIX = ".track"

# Directories
TRACKLETS_DIR = "tracklets/" 
COLLAPSED_DIR = "trackletsCollapsed/"
PURIFIED_DIR = "trackletsPurified/" 
FINAL_TRACKLETS_DIR = "trackletsFinal/"
TRACKLETS_BY_NIGHT_DIR = "trackletsByNight/"
TRACKS_DIR = "tracks/"
FINAL_TRACKS_DIR = "tracksFinal/"

VERBOSE = True

def directoryBuilder(runDir, collapse=True, purify=True, removeSubsetTracklets=True, removeSubsetTracks=True, verbose=VERBOSE):
    """
    Builds the directory structure for MOPS output files.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    runDir: (string), name of the top folder
    ----------------------
    """

    try:
        os.mkdir(runDir)
    except:
        raise NameError("Directory exists! Cannot continue!")

    dirs = [TRACKLETS_DIR, COLLAPSED_DIR, PURIFIED_DIR, FINAL_TRACKLETS_DIR, TRACKLETS_BY_NIGHT_DIR, TRACKS_DIR, FINAL_TRACKS_DIR]
    dirsOut = []
   
    for d in dirs:
        newDir = os.path.join(runDir, d)
        os.mkdir(newDir)
        dirsOut.append(newDir)
            
    return dirsOut

def runFindTracklets(parameters, diasources, outDir, verbose=VERBOSE):
    """
    Runs findTracklets. 

    Generates tracklets given a set of DIA sources.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    parameters: (MopsParameters object), user or default defined MOPS parameter object
    diasources: (list), list of diasources
    outDir: (string), tracklet output directory
    ----------------------
    """
    function = "findTracklets"
    tracklets = []

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    for diasource in diasources:
        trackletsOut = _out(outDir, diasource, TRACKLET_SUFFIX)

        call = ['findTracklets', '-i', diasource, '-o', trackletsOut, '-v', parameters.vMax, '-m', parameters.vMin]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        tracklets.append(trackletsOut)

    if verbose:
        _status(function, False)

    return tracklets

def runIdsToIndices(tracklets, diasources, outDir, verbose=VERBOSE):
    """
    Runs idsToIndices.py.

    Rearranges tracklets by index as opposed to id. This format is required 
    by collapseTracklets, purifyTracklets and removeSubsets.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    tracklets: (list), list of tracklets
    diasources: (list), list of diasources
    outDir: (string), tracklet by index output directory
    ----------------------
    """
    function = "idsToIndices.py"
    byIndex = []

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    for tracklet, diasource in zip(tracklets, diasources):
        byIndexOut = _out(outDir, diasource, BY_INDEX_SUFFIX)

        script = str(os.getenv('MOPS_DIR')) + '/bin/idsToIndices.py'
        call = ['python', script, tracklet, diasource, byIndexOut]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        byIndex.append(byIndexOut)

    if verbose:
        _status(function, False)

    return byIndex

def runCollapseTracklets(parameters, trackletsByIndex, diasources, outDir, verbose=VERBOSE):
    """
    Runs collapseTracklets.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    parameters: (MopsParameters object), user or default defined MOPS parameter object
    trackletsByIndex: (list), list of tracklets
    diasources: (list), list of diasources
    outDir: (string), collapsed tracklet output directory
    ----------------------
    """
    function = "collapseTracklets"
    collapsedTracklets = []

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    for tracklet, diasource in zip(trackletsByIndex, diasources):
        collapsedTracklet = _out(outDir, diasource, COLLAPSED_SUFFIX)

        call = ['collapseTracklets', diasource, tracklet, parameters.raTol, 
            parameters.decTol, parameters.angTol, parameters.vTol, collapsedTracklet,
            '--method', parameters.method,
            '--useRMSFilt', parameters.useRMSfilt,
            '--maxRMS', parameters.rmsMax]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        collapsedTracklets.append(collapsedTracklet)

    if verbose:
        _status(function, False)

    return collapsedTracklets

def runPurifyTracklets(parameters, collapsedTracklets, diasources, outDir, verbose=VERBOSE):
    """
    Runs purifyTracklets.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    parameters: (MopsParameters object), user or default defined MOPS parameter object
    collapsedTrackets: (list), list of collapsed tracklets
    diasources: (list), list of diasources
    outDir: (string), purified tracklet output directory
    ----------------------
    """
    function = "purifyTracklets"
    purifiedTracklets = []

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    for tracklet, diasource in zip(collapsedTracklets, diasources):
        purifiedTracklet = _out(outDir, diasource, PURIFIED_SUFFIX)

        call = ['purifyTracklets', '--detsFile', diasource, '--pairsFile', tracklet, 
        '--maxRMS', parameters.rmsMax,'--outFile', purifiedTracklet]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        purifiedTracklets.append(purifiedTracklet)

    if verbose:
        _status(function, False)

    return purifiedTracklets

def runRemoveSubsets(parameters, purifiedTracklets, diasources, outDir, verbose=VERBOSE):
    """
    Runs removeSubsets.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    parameters: (MopsParameters object), user or default defined MOPS parameter object
    purifiedTracklets: (list), list of purified tracklets
    diasources: (list), list of diasources
    diasourcesDir: (string), directory containing diasources
    outDir: (string), final tracklet output directory
    ----------------------
    """
    function = "removeSubsets"
    finalTracklets = []

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    for tracklet, diasource in zip(purifiedTracklets, diasources):
        finalTracklet = _out(outDir, diasource, FINAL_SUFFIX)

        call = ['removeSubsets', '--inFile', tracklet, '--outFile', finalTracklet,
            '--removeSubsets', parameters.rmSubsets,
            '--keepOnlyLongest', parameters.keepOnlyLongest]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        finalTracklets.append(finalTracklet)

    if verbose:
        _status(function, False)

    return finalTracklets

def runIndicesToIds(finalTracklets, diasources, outDir, suffix, verbose=VERBOSE):
    """
    Runs indicesToIds.py.

    Convert back to original tracklet format. 

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    finalTracklets: (list), list of final (subset removed) tracklets
    diasources: (list), list of diasources
    outDir: (string), tracklet by ID output directory
    ----------------------
    """
    function = "indicesToIds.py"
    byId = []

    outfile = file(outDir + '/indicesToIds.out', 'w')
    errfile = file(outDir + '/indicesToIds.err', 'w')

    if verbose:
        _status(function, True)

    for tracklet, diasource in zip(finalTracklets, diasources):
        byIdOut = _out(outDir, diasource, suffix + BY_ID_SUFFIX)

        script = str(os.getenv('MOPS_DIR')) + '/bin/indicesToIds.py'
        call = ['python', script, tracklet, diasource, byIdOut]
        subprocess.call(call, stdout=outfile, stderr=errfile)

        byId.append(byIdOut)

    if verbose:
        _status(function, False)

    return byId

def runMakeLinkTrackletsInputByNight(parameters, diasourcesDir, trackletsDir, outDir, verbose=VERBOSE):
    """
    Runs makeLinkTrackletsInput_byNight.py.

    Reads tracklet files into dets and ids as required by linkTracklets.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    parameters: (MopsParameters object), user or default defined MOPS parameter object
    diasourcesDir: (string), directory containing diasources
    trackletsDir: (string), directory containing final (subset removed) tracklets
    outDir: (string), dets and ids file output directory
    ----------------------
    """
    function = "makeLinkTrackletsInput_byNight.py"

    outfile, errfile = _log(function, outDir)

    if verbose:
        _status(function, True)

    script = str(os.getenv('MOPS_DIR')) + '/bin/makeLinkTrackletsInput_byNight.py'
    call = ['python', script, parameters.windowSize, diasourcesDir, trackletsDir, outDir]
    subprocess.call(call, stdout=outfile, stderr=errfile)

    ids = glob.glob(outDir + '*.ids')
    dets = glob.glob(outDir + '*.dets')

    if verbose:
        _status(function, False)

    return dets, ids

def runLinkTracklets(parameters, dets, ids, outDir, verbose=VERBOSE):
    """
    Runs linkTracklets.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    dets: (list), list of dets files
    ids: (list), list of ids files
    outDir: (string), tracks output directory
    ----------------------
    """
    function = "linkTracklets"
    tracks = []

    if verbose:
        _status(function, True)

    for detIn, idIn in zip(dets,ids):
        trackOut = _out(outDir, detIn, TRACK_SUFFIX)
        outfile = file(trackOut + '.out', 'w')
        errfile = file(trackOut + '.err', 'w')

        call = ['linkTracklets', 
            '-e', parameters.detErrThresh, 
            '-D', parameters.decAccelMax,
            '-R', parameters.raAccelMax,
            '-u', parameters.nightMin,
            '-s', parameters.detectMin,
            '-b', parameters.bufferSize,
            '-d', detIn, 
            '-t', idIn,
            '-o', trackOut]

        if parameters.latestFirstEnd != None:
            call.extend(['-F', parameters.latestFirstEnd])
        if parameters.earliestLastEnd != None:
            call.extend(['-L', parameters.earliestLastEnd])
        if parameters.leafNodeSizeMax != None:
            call.extend(['-n', parameters.leafNodeSizeMax])

        subprocess.call(call, stdout=outfile, stderr=errfile)

        tracks.append(trackOut)

    if verbose:
        _status(function, False)

    return tracks

def runArgs():

    default = MopsParameters(verbose=False)

    parser = argparse.ArgumentParser(
        prog="runMops",
        description="Given a set of nightly or obshist DIA sources, will run LSST's Moving Object Pipeline (MOPs)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("diasourcesDir", help="Directory containing nightly diasources (.dias)")
    parser.add_argument("outputDir", help="Output directory to be created for file output (must not exist)")

    # Config file, load parameters from config file if given
    parser.add_argument("-cfg", "--config_file", default=None,
        help="""If given, will read parameter values from file to overwrite default values defined in MopsParameters. 
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
    parser.add_argument("-rM", "--rms_max", default=default.rmsMax,
        help="""Only used if useRMSfilt == true. Describes the function for RMS filtering.  
        Tracklets will not be collapsed unless the resulting tracklet would have RMS <= maxRMSm * average magnitude + maxRMSb 
        (used in collapseTracklets and purifyTracklets""")

    # removeSubsets
    parser.add_argument("-S","--remove_subsets", default=default.rmSubsets,
        help="Remove subsets (used in removeSubsets)")
    parser.add_argument("-k","--keep_only_longest", default=default.keepOnlyLongest,
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

    args = parser.parse_args()

    return args

def runMops(parameters, tracker, diasourcesDir, runDir, collapse=True, purify=True, removeSubsetTracklets=True, 
    removeSubsetTracks=False, verbose=VERBOSE):
    """
    Runs Moving Object Pipeline.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    parameters: (MopsParameters object), user or default defined MOPS parameter object
    tracker: (MopsTracker object), object keeps track of output files and directories
    diasourcesDir: (string), directory containing diasources
    runDir: (string), run directory
    ----------------------
    """

    # Build directory structure
    dirs = directoryBuilder(runDir, collapse=collapse, purify=purify, removeSubsetTracklets=removeSubsetTracklets,
        removeSubsetTracks=removeSubsetTracks, verbose=verbose)

    # Save parameters
    _save(parameters, 'parameters', outDir=runDir)
    
    # Find diasources
    diasourceList = os.listdir(diasourcesDir)
    diasources = []
    for diasource in diasourceList:
        diasources.append(os.path.join(diasourcesDir, diasource))
    tracker.diasources = diasources
    tracker.diasourcesDir = diasourcesDir

    # Run findTracklets
    tracklets = runFindTracklets(parameters, diasources, dirs[0], verbose=verbose)
    tracker.ranFindTracklets = True
    tracker.tracklets = tracklets
    tracker.trackletsDir = dirs[0]

    if collapse:
        # Run idsToIndices
        trackletsByIndex = runIdsToIndices(tracklets, diasources, dirs[0], verbose=verbose)
        tracker.ranIdsToIndices = True
        tracker.trackletsByIndex = trackletsByIndex
        tracker.trackletsByIndexDir = dirs[0]

        # Run collapseTracklets
        collapsedTracklets = runCollapseTracklets(parameters, trackletsByIndex, diasources, dirs[1], verbose=verbose)
        collapsedTrackletsById = runIndicesToIds(collapsedTracklets, diasources, dirs[1], COLLAPSED_SUFFIX, verbose=verbose)
        tracker.ranCollapseTracklets = True
        tracker.collapsedTracklets = collapsedTracklets
        tracker.collapsedTrackletsDir = dirs[1]
        tracker.collapsedTrackletsById = collapsedTrackletsById
        tracker.collapsedTrackletsByIdDir = dirs[1]

    if purify: 
        # Run purifyTracklets
        purifiedTracklets = runPurifyTracklets(parameters, collapsedTracklets, diasources, dirs[2], verbose=verbose)
        purifiedTrackletsById = runIndicesToIds(purifiedTracklets, diasources, dirs[2], PURIFIED_SUFFIX, verbose=verbose)
        tracker.ranPurifyTracklets = True
        tracker.purifiedTracklets = purifiedTracklets
        tracker.purifiedTrackletsDir = dirs[2]
        tracker.purifiedTrackletsById =  purifiedTrackletsById
        tracker.purifiedTrackletsByIdDir =  dirs[2]

    if removeSubsetTracklets:
        # Run removeSubsets
        finalTracklets = runRemoveSubsets(parameters, purifiedTracklets, diasources, dirs[3], verbose=verbose)
        finalTrackletsById = runIndicesToIds(finalTracklets, diasources, dirs[3], FINAL_SUFFIX, verbose=verbose)
        tracker.ranRemoveSubsets = True
        tracker.finalTracklets = finalTracklets
        tracker.finalTrackletsDir = dirs[3]

        # Run indicesToIds
        tracker.ranIndicesToIds = True
        tracker.finalTrackletsById = finalTrackletsById
        tracker.finalTrackletsByIdDir = dirs[3]

    # Run makeLinkTrackletsInputByNight
    dets, ids = runMakeLinkTrackletsInputByNight(parameters, diasourcesDir, dirs[3], dirs[4], verbose=verbose)
    tracker.ranMakeLinkTrackletsInputByNight = True
    tracker.dets = dets
    tracker.ids = ids
    tracker.trackletsByNightDir = dirs[4]

    # Run linkTracklets
    tracks = runLinkTracklets(parameters, dets, ids, dirs[5], verbose=verbose)
    tracker.ranLinkTracklets = True
    tracker.tracks = tracks
    tracker.tracksDir = dirs[5]

    # Print status and save tracker
    tracker.info()
    _save(tracker, 'tracker', outDir=runDir)

    return

def _status(function, current):

    if current:
        print "------- Run MOPS -------"
        print "Running %s..." % (function)
    else:
        print "Completed running %s." % (function)
        print ""
    return


def _save(mopsObject, objectName, outDir=None):

    print "------- Run MOPS -------"

    if outDir == None:
        outname = "%s.yaml" % (objectName)
    else:
        outname = os.path.join(outDir, "%s.yaml" % (objectName))

    print "Saving %s to %s" % (objectName, outname)

    stream = file(outname, "w")
    yaml.dump(mopsObject, stream)   
    stream.close()

    print ""

    return

def _log(function, outDir):
    # Split function name to get rid of possible .py
    function = os.path.splitext(function)[0]

    # Create outfile and errfile streams
    outfile = file(os.path.join(outDir, function + '.out'), 'w')
    errfile = file(os.path.join(outDir, function + '.err'), 'w')

    return outfile, errfile

def _out(outDir, filename, suffix):
    # Retrieve base file name
    base = os.path.basename(filename)
    # Remove all suffixes from filename and add new
    outName = base.split('.')[0] + suffix
    # Create path 
    outFile = os.path.join(outDir, outName)
    return outFile

if __name__=="__main__":

    # Run command line arg parser and retrieve args
    args = runArgs()
    verbose = args.verbose

    # Retrieve output directory and nightly DIA Sources directory
    runDir = os.path.join(os.path.abspath(args.outputDir), "")
    diasourcesDir = os.path.join(os.path.abspath(args.diasourcesDir), "")

    if verbose:
        print "------- Run MOPS -------"
        print "Running LSST's Moving Object Pipeline"
        print ""

    # Initialize MopsParameters and MopsTracker
    if args.config_file == None:
        parameters = MopsParameters(velocity_max=args.velocity_max, 
                    velocity_min=args.velocity_min, 
                    ra_tolerance=args.ra_tolerance,
                    dec_tolerance=args.dec_tolerance,
                    angular_tolerance=args.angular_tolerance,
                    velocity_tolerance=args.velocity_tolerance,
                    method=args.method,
                    use_rms_filter=args.use_rms_filter,
                    rms_max=args.rms_max,
                    remove_subsets=args.remove_subsets,
                    keep_only_longest=args.keep_only_longest,
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
                    verbose=verbose)
    else:
        if verbose:
            print "Config file given. Reading parameters from file..."
            print ""
        cfg = yaml.load(file(args.config_file,'r'))
        parameters = MopsParameters(**cfg)

     # Initialize tracker
    tracker = MopsTracker(runDir, verbose=verbose)

    # Run MOPs
    runMops(parameters, tracker, diasourcesDir, runDir, verbose=verbose)
