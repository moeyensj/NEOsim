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
trackSuffix = '.tracks'
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
        diaSource = diaSourceDir + '/' + diaSource
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

        diaSource = diaSourceDir + '/' + diaSource
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

        outFile = outDir + 'tracks'
        call = ['linkTracklets', '-d', detIn, '-t', idIn,'-o', outFile]
        subprocess.call(call)

        tracks.append(outFile)

    print ''

    return tracks


if __name__=="__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("diaSourcesDir", help="Directory containing nightly diasources (.dias)")
    parser.add_argument("name", help="Name of this MOPS run")
    #parser.add_argument("-p", "--parameters", type=list, help="array of mops parameters, defaults to values set in MopsParameters.py")
    args = parser.parse_args()

    name = args.name
    diaSourceDir = args.diaSourcesDir

    # Initialize MopsParameters and MopsTracker
    parameters = MopsParameters(velocity_max=None, 
                velocity_min=None, 
                ra_tolerance=None,
                dec_tolerance=None,
                angular_tolerance=None,
                velocity_tolerance=None)
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

    #tracker.status()





        
        

