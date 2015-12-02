#!/usr/bin/env python

"""

A simple script to run MOPS. (Work in progress)

Command-line call:
python runMops.py {nightly DIA source directory ending with '/'} {run name} 

Requirements:
MOPS setup (with MOPS_DIR path variable pointing to bin mops_daymops)

Contact moeyensj@uw.edu with questions and / or concerns.

"""

import os
import sys
import subprocess
import glob
import argparse

from MopsParameters import MopsParameters
from MopsTracker import MopsTracker

# File suffixes
diaSourceSuffix = '.dias'
trackletSuffix = '.tracklet'
byIndexSuffix = trackletSuffix + '.byIndices'
collapsedSuffix = trackletSuffix + '.collapsed'
purifiedSuffix = trackletSuffix + '.purified'
finalSuffix = trackletSuffix + '.final'
byIdSuffix = finalSuffix + '.byIds'
trackSuffix = '.track'

# Directories
trackletsDir = 'tracklets/' 
collapsedDir = 'trackletsCollapsed/'
purifyDir = 'trackletsPurified/' 
finalDir = 'trackletsFinal/'
trackletsByNightDir = 'trackletsByNight/'
tracksDir = 'tracks/'

def directoryBuilder(name):
    """
    Builds the directory structure for MOPS output files.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    name: (string), name of the top folder (same as run name)
    ----------------------
    """

    runDir = name + '/'

    try:
        os.stat(runDir)
    except:
        os.mkdir(runDir)

    dirs = [trackletsDir, collapsedDir, purifyDir, finalDir, trackletsByNightDir, tracksDir]
    dirsOut = []
   
    for d in dirs:
        try:
            os.stat(runDir +  d)
        except:
            os.mkdir(runDir + d)

        dirsOut.append(runDir +  d)
            
    return runDir, dirsOut

def runFindTracklets(parameters, diaSources, diaSourceDir, outDir):
    """
    Runs findTracklets. 

    Generates tracklets given a set of DIA sources.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    parameters: (MopsParameters object), user or default defined MOPS parameter object
    diaSources: (list), list of diaSources
    diaSourceDir: (string), directory containing diaSources
    outDir: (string), tracklet output directory
    ----------------------
    """

    tracklets = []

    outfile = file(outDir + '/findTracklets.out', 'w')
    outerr = file(outDir + '/findTracklets.err', 'w')

    for diaSource in diaSources:
        diaSourceIn = diaSourceDir + diaSource
        trackletsOut = outDir + diaSource.split('.')[0] + trackletSuffix

        call = ['findTracklets', '-i', diaSourceIn, '-o', trackletsOut, '-v', str(parameters.vMax), '-m', str(parameters.vMin)]
        subprocess.call(call, stdout=outfile, stderr=outerr)

        tracklets.append(trackletsOut)

    return tracklets

def runIdsToIndices(tracklets, diaSources, diaSourceDir, outDir):
    """
    Runs idsToIndices.py.

    Rearranges tracklets by index as opposed to id. This format is required 
    by collapseTracklets, purifyTracklets and removeSubsets.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    tracklets: (list), list of tracklets
    diaSources: (list), list of diaSources
    diaSourceDir: (string), directory containing diaSources
    outDir: (string), tracklet by index output directory
    ----------------------
    """

    byIndex = []

    outfile = file(outDir + '/idsToIndices.out', 'w')
    outerr = file(outDir + '/idsToIndices.err', 'w')

    for tracklet, diaSource in zip(tracklets, diaSources):
        diaSourceIn = diaSourceDir + diaSource
        byIndexOut = outDir + diaSource.split('.')[0] + byIndexSuffix

        script = str(os.getenv('MOPS_DIR')) + '/idsToIndices.py'
        call = ['python', script, tracklet, diaSourceIn, byIndexOut]
        subprocess.call(call, stdout=outfile, stderr=outerr)

        byIndex.append(byIndexOut)

    return byIndex

def runCollapseTracklets(parameters, trackletsByIndex, diaSources, diaSourceDir, outDir):
    """
    Runs collapseTracklets.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    parameters: (MopsParameters object), user or default defined MOPS parameter object
    trackletsByIndex: (list), list of tracklets
    diaSources: (list), list of diaSources
    diaSourceDir: (string), directory containing diaSources
    outDir: (string), collapsed tracklet output directory
    ----------------------
    """

    collapsedTracklets = []

    outfile = file(outDir + '/collapseTracklets.out', 'w')
    outerr = file(outDir + '/collapseTracklets.err', 'w')

    for tracklet, diaSource in zip(trackletsByIndex, diaSources):
        diaSourceIn = diaSourceDir + diaSource
        trackletName = diaSource.split('.')[0]
        collapsedTracklet = outDir + trackletName + collapsedSuffix

        call = ['collapseTracklets', diaSourceIn, tracklet, str(parameters.raTol), 
        str(parameters.decTol), str(parameters.angTol), str(parameters.vTol), collapsedTracklet]
        subprocess.call(call, stdout=outfile, stderr=outerr)

        collapsedTracklets.append(collapsedTracklet)

    return collapsedTracklets

def runPurifyTracklets(parameters, collapsedTracklets, diaSources, diaSourceDir, outDir):
    """
    Runs purifyTracklets.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    parameters: (MopsParameters object), user or default defined MOPS parameter object
    collapsedTrackets: (list), list of collapsed tracklets
    diaSources: (list), list of diaSources
    diaSourceDir: (string), directory containing diaSources
    outDir: (string), purified tracklet output directory
    ----------------------
    """

    purifiedTracklets = []

    outfile = file(outDir + '/purifyTracklets.out', 'w')
    outerr = file(outDir + '/purifyTracklets.err', 'w')

    for tracklet, diaSource in zip(collapsedTracklets, diaSources):
        diaSourceIn = diaSourceDir + diaSource
        trackletName = diaSource.split('.')[0]
        purifiedTracklet = outDir + trackletName + purifiedSuffix

        call = ['purifyTracklets', '--detsFile', diaSourceIn, '--pairsFile', tracklet, 
        '--maxRMS', str(parameters.rmsMax),'--outFile', purifiedTracklet]
        subprocess.call(call, stdout=outfile, stderr=outerr)

        purifiedTracklets.append(purifiedTracklet)

    return purifiedTracklets

def runRemoveSubsets(parameters, purifiedTracklets, diaSources, diaSourceDir, outDir):
    """
    Runs removeSubsets.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    parameters: (MopsParameters object), user or default defined MOPS parameter object
    purifiedTracklets: (list), list of purified tracklets
    diaSources: (list), list of diaSources
    diaSourceDir: (string), directory containing diaSources
    outDir: (string), final tracklet output directory
    ----------------------
    """

    finalTracklets = []

    outfile = file(outDir + '/removeSubsets.out', 'w')
    outerr = file(outDir + '/removeSubsets.err', 'w')

    for tracklet, diaSource in zip(purifiedTracklets, diaSources):
        trackletName = diaSource.split('.')[0]
        finalTracklet = outDir + trackletName + finalSuffix

        call = ['removeSubsets', '--inFile', tracklet, '--outFile', finalTracklet]
        subprocess.call(call, stdout=outfile, stderr=outerr)

        finalTracklets.append(finalTracklet)

    return finalTracklets

def runIndicesToIds(finalTracklets, diaSources, diaSourceDir, outDir):
    """
    Runs indicesToIds.py.

    Convert back to original tracklet format. 

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    finalTracklets: (list), list of final (subset removed) tracklets
    diaSources: (list), list of diaSources
    diaSourceDir: (string), directory containing diaSources
    outDir: (string), tracklet by ID output directory
    ----------------------
    """

    byId = []

    outfile = file(outDir + '/indicesToIds.out', 'w')
    outerr = file(outDir + '/indicesToIds.err', 'w')

    for tracklet, diaSource in zip(finalTracklets, diaSources):
        diaSourceIn = diaSourceDir + diaSource
        byIdOut = outDir + diaSource.split('.')[0] + byIdSuffix

        script = str(os.getenv('MOPS_DIR')) + '/indicesToIds.py'
        call = ['python', script, tracklet, diaSourceIn, byIdOut]
        subprocess.call(call, stdout=outfile, stderr=outerr)

        byId.append(byIdOut)

    return byId

def runMakeLinkTrackletsInputByNight(parameters, diaSourcesDir, trackletsDir, outDir):
    """
    Runs makeLinkTrackletsInput_byNight.py.

    Reads tracklet files into dets and ids as required by linkTracklets.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    parameters: (MopsParameters object), user or default defined MOPS parameter object
    diaSourceDir: (string), directory containing diaSources
    trackletsDir: (string), directory containing final (subset removed) tracklets
    outDir: (string), dets and ids file output directory
    ----------------------
    """

    outfile = file(outDir + '/makeLinkTrackletsInput_byNight.out', 'w')
    outerr = file(outDir + '/makeLinkTrackletsInput_byNight.err', 'w')
    script = str(os.getenv('MOPS_DIR')) + '/makeLinkTrackletsInput_byNight.py'
    call = ['python', script, str(parameters.windowSize), diaSourcesDir, trackletsDir, outDir]
    subprocess.call(call, stdout=outfile, stderr=outerr)

    ids = glob.glob(outDir + '*.ids')
    dets = glob.glob(outDir + '*.dets')

    return dets, ids

def runLinkTracklets(dets, ids, outDir):
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

    tracks = []

    outfile = file(outDir + '/linkTracklets.out', 'w')
    outerr = file(outDir + '/linkTracklets.err', 'w')

    for detIn, idIn in zip(dets,ids):
        trackName = detIn.split('/')[2].split('.')[0]
        trackOut = outDir +  trackName + trackSuffix

        call = ['linkTracklets', '-d', detIn, '-t', idIn,'-o', trackOut]
        subprocess.call(call, stdout=outfile, stderr=outerr)

        tracks.append(trackOut)

    return tracks

def runArgs():

    defaultParameters = MopsParameters(verbose=False)

    parser = argparse.ArgumentParser(
        prog="runMops",
        description="Given a set of nightly or obshist DIA sources, will run LSST's Moving Object Pipeline (MOPs)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("diaSourcesDir", help="directory containing nightly diasources (.dias)")
    parser.add_argument("name", help="name of this MOPS run, used as top directory folder")
    parser.add_argument("-vMax", "--velocity_max", metavar="", default=defaultParameters.vMax, 
        help="Maximum velocity (used in findTracklets)")
    parser.add_argument("-vMin", "--velocity_min", metavar="", default=defaultParameters.vMin, 
        help="Minimum velocity (used in findTracklets)")
    parser.add_argument("-raTol", "--ra_tolerance", metavar="", default=defaultParameters.raTol, 
        help="RA tolerance (used in collapseTracklets)")
    parser.add_argument("-decTol", "--dec_tolerance", metavar="", default=defaultParameters.decTol, 
        help="Dec tolerance (used in collapseTracklets)")
    parser.add_argument("-angTol", "--angular_tolerance", metavar="", default=defaultParameters.angTol,
        help="Angular tolerance (used in collapseTracklets)")
    parser.add_argument("-vTol", "--velocity_tolerance", metavar="", default=defaultParameters.vTol, 
        help="Velocity tolerance (used in collapseTracklets)")
    parser.add_argument("-rmsMax", "--rms_max", metavar="", default=defaultParameters.rmsMax,
        help="Maximum RMS (used in purifyTracklets")
    parser.add_argument("-windowSize", "--window_size", metavar="", default=defaultParameters.windowSize,
        help="Windows size (used in makeLinkTrackletsInput_byNight.py")

    args = parser.parse_args()

    return args

def runMops(parameters, tracker, diaSourceDir, name):
    """
    Runs Moving Object Pipeline.

    Parameters:
    ----------------------
    parameter: (dtype) [default (if optional)], information

    parameters: (MopsParameters object), user or default defined MOPS parameter object
    tracker: (MopsTracker object), object keeps track of output files and directories
    diaSourceDir: (string), directory containing diaSources
    name: (string), run name
    ----------------------
    """
    # Build directory structure
    runDir, dirs = directoryBuilder(name)

    # Save parameters
    parameters.save(outDir=runDir)

    # Find DIASources
    diaSources = os.listdir(diaSourceDir)
    tracker.diaSources = diaSources
    tracker.diaSourcesDir = diaSourceDir

    # Run findTracklets
    tracklets = runFindTracklets(parameters, diaSources, diaSourceDir, dirs[0])
    tracker.ranFindTracklets = True
    tracker.tracklets = tracklets
    tracker.trackletsDir = dirs[0]

    # Run idsToIndices
    trackletsByIndex = runIdsToIndices(tracklets, diaSources, diaSourceDir, dirs[0])
    tracker.ranIdsToIndices = True
    tracker.trackletsByIndex = trackletsByIndex
    tracker.trackletsByIndexDir = dirs[0]

    # Run collapseTracklets
    collapsedTracklets = runCollapseTracklets(parameters, trackletsByIndex, diaSources, diaSourceDir, dirs[1])
    tracker.ranCollapseTracklets = True
    tracker.collapsedTracklets = collapsedTracklets
    tracker.collapsedTrackletsDir = dirs[1]

    # Run purifyTracklets
    purifiedTracklets = runPurifyTracklets(parameters, collapsedTracklets, diaSources, diaSourceDir, dirs[2])
    tracker.ranPurifyTracklets = True
    tracker.purifiedTracklets = purifiedTracklets
    tracker.purifiedTrackletsDir = dirs[2]

    # Run removeSubsets
    finalTracklets = runRemoveSubsets(parameters, purifiedTracklets, diaSources, diaSourceDir, dirs[3])
    tracker.ranRemoveSubsets = True
    tracker.finalTracklets = finalTracklets
    tracker.finalTrackletsDir = dirs[3]

    # Run indicesToIds
    trackletsById = runIndicesToIds(finalTracklets, diaSources, diaSourceDir, dirs[3])
    tracker.ranIndicesToIds = True
    tracker.trackletsById = trackletsById
    tracker.trackletsByIdDir = dirs[3]

    # Run makeLinkTrackletsInputByNight
    dets, ids = runMakeLinkTrackletsInputByNight(parameters, diaSourceDir, dirs[3], dirs[4])
    tracker.ranMakeLinkTrackletsInputByNight = True
    tracker.trackletsByNightDets = dets
    tracker.trackletsByNightIds = ids
    tracker.trackletsByNightDir = dirs[4]

    # Run linkTracklets
    tracks = runLinkTracklets(dets, ids, dirs[5])
    tracker.ranLinkTracklets = True
    tracker.tracks = tracks
    tracker.tracksDir = dirs[5]

    # Print status and save tracker
    tracker.status()
    tracker.save(outDir=runDir)

    return

if __name__=="__main__":

    # Run command line arg parser and retrieve args
    args = runArgs()

    # Retrieve name and nightly DIA Sources directory
    name = args.name
    diaSourceDir = args.diaSourcesDir

    # Initialize MopsParameters and MopsTracker
    parameters = MopsParameters(
                velocity_max=args.velocity_max, 
                velocity_min=args.velocity_min, 
                ra_tolerance=args.ra_tolerance,
                dec_tolerance=args.dec_tolerance,
                angular_tolerance=args.angular_tolerance,
                velocity_tolerance=args.velocity_tolerance,
                rms_max=args.rms_max,
                window_size=args.window_size)

     # Initialize tracker
    tracker = MopsTracker(name)

    # Run MOPs
    runMops(parameters, tracker, diaSourceDir, name)
