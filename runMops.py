#!/usr/bin/env python

import os
import sys
import subprocess

from MopsParameters import MopsParameters
from MopsTracker import MopsTracker

# File suffixes
diaSourceSuffix = '.dias'
trackletSuffix = '.tracklet'
trackletByIndSuffix = trackletSuffix + '.byInd'
collapsedSuffix = trackletSuffix + '.collapsed'
purifiedSuffix = collapsedSuffix + '.purified'
trackSuffix = '.tracks'

# Directories
trackletsDir = 'tracklets' 
collapsedDir = 'trackletsCollapsed'
purifyDir = 'trackletsPurified' 
tracksDir = 'tracks'

def directoryBuilder(name):

    runDir = name + '/'

    try:
        os.stat(runDir)
        print runDir + ' already exists.'
    except:
        os.mkdir(runDir)
        print 'Created %s directory.' % (runDir)

    dirs = [trackletsDir, collapsedDir, purifyDir, tracksDir]
   
    for d in dirs:
        try:
            os.stat(runDir +  d)
            print d + ' already exists.'
        except:
            os.mkdir(runDir + d)
            print '\tCreated %s directory.' % (d)
            
    return runDir, dirs

def runFindTracklets(diaSourceDir, runDir):

    diaSources = os.listdir(diaSourceDir)

    for diaSource in diaSources:

        trackletsOut = runDir + trackletsDir + diaSource + trackletSuffix
        diaSourceIn = diaSourceDir + diaSource

        call = ['findTracklets', '-i', diaSourceIn, '-o', trackletsOut, '-v', str(MopsParameters.vmax), '-m', str(MopsParameters.vmin)]
        subprocess.call(call)

    return 


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
    runDir, dirs = directoryBuilder(name)

    # Run findTracklets
    tracklets = runFindTracklets(diaSourceDir, runDir)
    tracker.ranFindTracklets = True











        
        

