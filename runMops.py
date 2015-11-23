#!/usr/bin/env python

import os
import sys
import subprocess
import glob

from MopsParameters import MopsParameters
from MopsTracker import MopsTracker

# File suffixes
diaSourceSuffix = '.dias'
trackletSuffix = '.tracklet'
collapsedSuffix = '.collapsed'
purifiedSuffix = '.purified'
trackSuffix = '.track'
byIndexSuffix = '.byIndices'
byIdSuffix = '.byIds'

# Directories
trackletsDir = 'tracklets/' 
collapsedDir = 'trackletsCollapsed/'
purifyDir = 'trackletsPurified/' 
trackletsByNightDir = 'trackletsByNight/'
tracksDir = 'tracks/'

def directoryBuilder(name):

    print '---- directoryBuilder ----'

    runDir = name + '/'

    try:
        os.stat(runDir)
        print runDir + ' already exists.'
    except:
        os.mkdir(runDir)
        print 'Created %s directory.' % (runDir)

    dirs = [trackletsDir, collapsedDir, purifyDir, trackletsByNightDir, tracksDir]
    dirsOut = []
   
    for d in dirs:
        try:
            os.stat(runDir +  d)
            print d + ' already exists.'
        except:
            os.mkdir(runDir + d)
            print '\tCreated %s directory.' % (d)

        dirsOut.append(runDir +  d)

    print ''
            
    return dirsOut

def runFindTracklets(parameters, diaSources, diaSourceDir, outDir):

    print '---- findTracklets ----'

    tracklets = []

    for diaSource in diaSources:

        trackletsOut = outDir + diaSource + trackletSuffix
        diaSourceIn = diaSourceDir + diaSource

        call = ['findTracklets', '-i', diaSourceIn, '-o', trackletsOut, '-v', str(parameters.vMax), '-m', str(parameters.vMin)]
        subprocess.call(call, stdin=None, stdout=None, stderr=None, shell=False)

        tracklets.append(trackletsOut)

    print ''

    return tracklets

def runIdsToIndices(tracklets, diaSources, diaSourceDir):

    print '---- idsToIndices.py ----'

    byIndex = []

    for tracklet, diaSource in zip(tracklets, diaSources):
        diaSource = diaSourceDir + diaSource
        byIndexOut = tracklet + byIndexSuffix

        script = str(os.getenv('MOPS_DIR')) + '/idsToIndices.py'
        call = ['python', script, tracklet, diaSource, byIndexOut]
        subprocess.call(call)

        byIndex.append(byIndexOut)

    print ''

    return byIndex

def runCollapseTracklets(parameters, trackletsByIndex, diaSources, diaSourceDir, outDir):

    print '---- collapseTracklets ----'

    collapsedTracklets = []

    for tracklet, diaSource in zip(trackletsByIndex, diaSources):
        diaSource = diaSourceDir + diaSource

        trackletName = tracklet.split('/')[2]
        collapsedTracklet = outDir + trackletName + collapsedSuffix

        call = ['collapseTracklets', diaSource, tracklet, str(parameters.raTol), 
        str(parameters.decTol), str(parameters.angTol), str(parameters.vTol), collapsedTracklet]
        subprocess.call(call)

        collapsedTracklets.append(collapsedTracklet)

    print ''

    return collapsedTracklets

def runPurifyTracklets(parameters, collapsedTracklets, diaSources, diaSourceDir, outDir):

    print '---- purifyTracklets ----'

    purifiedTracklets = []

    for tracklet, diaSource in zip(collapsedTracklets, diaSources):
        diaSource = diaSourceDir + diaSource

        trackletName = tracklet.split('/')[2]
        purifiedTracklet = outDir + trackletName + purifiedSuffix

        call = ['purifyTracklets', '--detsFile', diaSource, '--pairsFile', tracklet, 
        '--maxRMS', str(parameters.rmsMax),'--outFile', purifiedTracklet]
        subprocess.call(call)

        purifiedTracklets.append(purifiedTracklet)

    print ''

    return purifiedTracklets

def runIndicesToIds(tracklets, diaSources, diaSourceDir):

    print '---- indicesToIds.py ----'

    byId = []

    for tracklet, diaSource in zip(tracklets, diaSources):

        diaSource = diaSourceDir + diaSource
        byIdOut = tracklet + byIdSuffix

        script = str(os.getenv('MOPS_DIR')) + '/indicesToIds.py'
        call = ['python', script, tracklet, diaSource, byIdOut]
        subprocess.call(call)

        byId.append(byIdOut)

    print ''

    return byId

def runMakeLinkTrackletsInputByNight(parameters, diaSourcesDir, trackletsDir, outDir):

    print '---- makeLinkTrackletsInput_byNight.py ----'
    
    script = str(os.getenv('MOPS_DIR')) + '/makeLinkTrackletsInput_byNight.py'
    call = ['python', script, str(parameters.windowSize), diaSourcesDir, trackletsDir, outDir]
    subprocess.call(call)

    ids = glob.glob(outDir + '*.ids')
    dets = glob.glob(outDir + '*.dets')

    print ''

    return dets, ids

def runLinkTracklets(dets, ids, outDir):

    print '---- linkTracklets ----'

    tracks = []

    for detIn, idIn in zip(dets,ids):

        trackName = detIn.split('/')[2].split('.')[0]
        outFile = outDir +  trackName + trackSuffix

        print outFile
        call = ['linkTracklets', '-d', detIn, '-t', idIn,'-o', outFile]
        subprocess.call(call)

        tracks.append(outFile)

    print ''

    return tracks

def runArgs():

    import argparse

    defaultParameters = MopsParameters()

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

    # Build directory structure
    dirs = directoryBuilder(name)

    # Find DIASources
    diaSources = os.listdir(diaSourceDir)
    tracker.diaSources = diaSources
    tracker.diaSourceDir = diaSourceDir

    # Run findTracklets
    tracklets = runFindTracklets(parameters, diaSources, diaSourceDir, dirs[0])
    tracker.ranFindTracklets = True
    tracker.tracklets = tracklets
    tracker.trackletsDir = dirs[0]

    # Run idsToIndices
    trackletsByIndex = runIdsToIndices(tracklets, diaSources, diaSourceDir)
    tracker.ranIdsToIndices = True
    tracker.trackletsByIndex = trackletsByIndex

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

    # Run indicesToIds
    trackletsById = runIndicesToIds(purifiedTracklets, diaSources, diaSourceDir)
    tracker.ranIndicesToIds = True
    tracker.trackletsById = trackletsById

    # Run makeLinkTrackletsInputByNight
    dets, ids = runMakeLinkTrackletsInputByNight(parameters, diaSourceDir, dirs[2], dirs[3])
    tracker.ranMakeLinkTrackletsInputByNight = True
    tracker.trackletsByNightDets = dets
    tracker.trackletsByNightIds = ids
    tracker.trackletsByNightDir = dirs[3]

    # Run linkTracklets
    tracks = runLinkTracklets(dets, ids, dirs[4])
    tracker.ranLinkTracklets = True
    tracker.tracks = tracks
    tracker.tracksDir = dirs[4]

    tracker.status()

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
    tracker = MopsTracker(name, parameters)

    # Run MOPs
    runMops(parameters, tracker, diaSourceDir, name)

    
