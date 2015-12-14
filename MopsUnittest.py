import yaml
import unittest
import shutil
import os

import runMops
from MopsTracker import MopsTracker
from MopsParameters import MopsParameters

TESTDIR = "unittest/testRun/"
DATADIR = "unittest/testData/nightly/"
CONTROLDIR = "unittest/controlRun/"

VERBOSE = True

class MopsTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.testTracker = MopsTracker(TESTDIR)
        self.testParameters = MopsParameters(verbose=VERBOSE)

        self.controlParameters = yaml.load(file("unittest/controlRun/parameters.yaml", "r"))
        self.controlTracker = yaml.load(file("unittest/controlRun/tracker.yaml", "r"))

        runMops.runMops(self.testParameters, self.testTracker, DATADIR, TESTDIR, verbose=VERBOSE)

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(TESTDIR)

    def test_directoryBuilder(self):
        controlDirs = [self.controlTracker.trackletsDir, self.controlTracker.trackletsByIndexDir,
        self.controlTracker.collapsedTrackletsDir, self.controlTracker.purifiedTrackletsDir, 
        self.controlTracker.finalTrackletsDir, self.controlTracker.tracksDir]

        testDirs = [self.testTracker.trackletsDir, self.testTracker.trackletsByIndexDir,
        self.testTracker.collapsedTrackletsDir, self.testTracker.purifiedTrackletsDir, 
        self.testTracker.finalTrackletsDir, self.testTracker.tracksDir]

        for td, cd in zip(testDirs, controlDirs):
            self.assertEqual(os.path.basename(td), os.path.basename(cd))

    def test_findTracklets(self):
        testTracklets = self.testTracker.tracklets
        controlTracklets = self.controlTracker.tracklets

        for tt, ct in zip(testTracklets, controlTracklets):

            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_idsToIndices(self):
        testTrackletsByIndex = self.testTracker.trackletsByIndex
        controlTrackletsByIndex = self.controlTracker.trackletsByIndex

        for tt, ct in zip(testTrackletsByIndex, controlTrackletsByIndex):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_collapseTracklets(self):
        testCollapsedTracklets = self.testTracker.collapsedTracklets
        controlCollapsedTracklets = self.controlTracker.collapsedTracklets

        for tt, ct in zip(testCollapsedTracklets, controlCollapsedTracklets):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_purifyTrackets(self):
        testPurifiedTracklets = self.testTracker.purifiedTracklets
        controlPurifiedTracklets = self.controlTracker.purifiedTracklets

        for tt, ct in zip(testPurifiedTracklets, controlPurifiedTracklets):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_removeSubsets(self):
        testFinalTracklets = self.testTracker.finalTracklets
        controlFinalTracklets = self.controlTracker.finalTracklets

        for tt, ct in zip(testFinalTracklets, controlFinalTracklets):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_indicesToIds(self):
        testTrackletsByIndex = self.testTracker.trackletsByIndex
        controlTrackletsByIndex = self.controlTracker.trackletsByIndex

        for tt, ct in zip(testTrackletsByIndex, controlTrackletsByIndex):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_linkTracklets(self):
        testTracks = self.testTracker.tracks
        controlTracks = self.controlTracker.tracks

        for tt, ct in zip(testTracks, controlTracks):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

if __name__ == '__main__':
    unittest.main()