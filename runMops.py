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
trackletByIndSuffix = trackletSuffix + '.byInd'
collapsedSuffix = trackletSuffix + '.collapsed'
purifiedSuffix = collapsedSuffix + '.purified'
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

def runFindTracklets(diaSources, diaSourceDir, parameters, outDir):

    print '---- findTracklets ----'

    tracklets = []

    for diaSource in diaSources:

        trackletsOut = outDir + diaSource + trackletSuffix
        diaSourceIn = diaSourceDir + diaSource

        call = ['findTracklets', '-i', diaSourceIn, '-o', trackletsOut, '-v', str(parameters.vmax), '-m', str(parameters.vmin)]
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

def runCollapseTracklets():

    return 

def runPurifyCollapseTracklets():

    return

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

def runMakeLinkTrackletsInputByNight(windowsize, diaSourcesDir, trackletsDir, outDir):

    print '---- makeLinkTrackletsInput_byNight.py ----'
    
    script = str(os.getenv('MOPS_DIR')) + '/makeLinkTrackletsInput_byNight.py'
    call = ['python', script, str(windowsize), diaSourcesDir, trackletsDir, outDir]
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

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("diaSourcesDir", help="directory containing nightly diasources (.dias)")
    parser.add_argument("name", help="name of this MOPS run, used as top directory folder")
    parser.add_argument("-vmax", "--velocity_max", metavar="maximum velocity", default=defaultParameters.vmax, 
        help="Maximum velocity (used in findTracklets)")
    parser.add_argument("-vmin", "--velocity_min", metavar="minimum velocity", default=defaultParameters.vmin, 
        help="Minimum velocity (used in findTracklets)")
    parser.add_argument("-raTol", "--ra_tolerance", metavar="ra tolerance", default=defaultParameters.raTol, 
        help="RA tolerance (used in collapseTracklets)")
    parser.add_argument("-decTol", "--dec_tolerance", metavar="dec tolerance", default=defaultParameters.decTol, 
        help="Dec tolerance (used in collapseTracklets)")
    parser.add_argument("-angTol", "--angular_tolerance", metavar="angular tolerance", default=defaultParameters.angTol,
        help="Angular tolerance (used in collapseTracklets)")
    parser.add_argument("-vTol", "--velocity_tolerance", metavar="velocity tolerance", default=defaultParameters.vTol, 
        help="Velocity tolerance (used in collapseTracklets)")

    args = parser.parse_args()

    return args

if __name__=="__main__":

    # Run command line arg parser and retrieve args
    args = runArgs()

    name = args.name
    diaSourceDir = args.diaSourcesDir

    # Initialize MopsParameters and MopsTracker
    parameters = MopsParameters(velocity_max=args.velocity_max, 
                velocity_min=args.velocity_min, 
                ra_tolerance=args.ra_tolerance,
                dec_tolerance=args.dec_tolerance,
                angular_tolerance=args.angular_tolerance,
                velocity_tolerance=args.velocity_tolerance)

    tracker = MopsTracker(name, parameters)

    # Build directory structure
    dirs = directoryBuilder(name)

    # Find DIASources
    diaSources = os.listdir(diaSourceDir)

    # Run findTracklets
    tracklets = runFindTracklets(diaSources, diaSourceDir, parameters, dirs[0])
    tracker.ranFindTracklets = True

    # Run idsToIndices
    trackletsByIndex = runIdsToIndices(tracklets, diaSources, diaSourceDir)
    tracker.ranIdsToIndices = True

    # Run indicesToIds
    trackletsById = runIndicesToIds(trackletsByIndex, diaSources, diaSourceDir)
    tracker.ranIndicesToIds = True

    # Run makeLinkTrackletsInputByNight
    dets, ids = runMakeLinkTrackletsInputByNight(15, diaSourceDir, dirs[0], dirs[3])
    tracker.ranMakeLinkTrackletsInputByNight = True

    # Run linkTracklets
    tracks = runLinkTracklets(dets, ids, dirs[4])
    tracker.ranLinkTracklets = True

    tracker.status()





        
        

