#!/usr/bin/env python

import os
import sys
import subprocess

WORKDIR = '/Users/joachim/repos/neosim/test/'

# Variables
vmax = 2.0
vmin = 0.0
raTol = 0.002
decTol = 0.002
angTol = 5
velTol = 0.05

# File suffixes
diaSourceSuffix = '.dias'
trackletSuffix = '.tracklet'
collapsedSuffix = trackletSuffix + '.collapsed'
purifiedSuffix = collapsedSuffix + '.purified'
trackSuffix = '.tracks'


def directoryBuilder(insideGitRepo=False):
    
    trackletsDir = 'tracklets_v%s/' % (str(vmax))
    collapsedDir = 'trackletsCollapsed_v%s/' % (str(vmax))
    purifyDir = 'trackletsPurified_v%s/' % (str(vmax))
    tracksDir = 'tracks_v%s/' % (str(vmax))
    
    dirs = [trackletsDir, collapsedDir, purifyDir, tracksDir]
    
    for d in dirs:
        try:
            os.stat(WORKDIR + d)
            print d + ' already exists'
        except:
            os.mkdir(WORKDIR + d)
            print 'Created %s directory.' % (d)
            
    return dirs

def runFindTracklets(diaSources,  nightlyDir, trackletsDir):

	for diaSource in diaSources:

		trackletsOut = WORKDIR + trackletsDir + diaSource + trackletSuffix
		diaSourceIn = WORKDIR + nightlyDir + diaSource
		call = ['findTracklets', '-i', diaSourceIn, '-o', trackletsOut, '-v', str(vmax), '-m', str(vmin)]
		subprocess.call(call)

	tracklets = os.listdir(WORKDIR + trackletsDir)

	return tracklets

if __name__=="__main__":

	nightlyDir = sys.argv[1]

	diaSources = os.listdir(nightlyDir)

	print diaSources

	dirs = directoryBuilder()

	tracklets = runFindTracklets(diaSources, nightlyDir, dirs[0])





		
		

