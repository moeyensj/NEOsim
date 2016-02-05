import yaml
import unittest
import shutil
import os

import runMops
from MopsTracker import MopsTracker
from MopsParameters import MopsParameters

TEST_DIR = "unittest/testRun/"
DATA_DIR = "unittest/testData/nightly/"
CONTROL_DIR = "unittest/controlRun/"

VERBOSE = True

class MopsTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.testTracker = MopsTracker(TEST_DIR)
        self.testParameters = MopsParameters(verbose=VERBOSE)

        self.controlParameters = yaml.load(file("unittest/controlRun/parameters.yaml", "r"))
        self.controlTracker = yaml.load(file("unittest/controlRun/tracker.yaml", "r"))

        runMops.runMops(self.testParameters, self.testTracker, DATA_DIR, TEST_DIR, verbose=VERBOSE)

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(TEST_DIR)

    def test_directoryBuilder(self):
        controlDirs = [self.controlTracker.trackletsDir, self.controlTracker.trackletsByIndexDir,
        self.controlTracker.collapsedTrackletsDir, self.controlTracker.collapsedTrackletsByIdDir,
        self.controlTracker.purifiedTrackletsDir, self.controlTracker.purifiedTrackletsByIdDir, 
        self.controlTracker.finalTrackletsDir, self.controlTracker.finalTrackletsByIdDir,
        self.controlTracker.trackletsByNightDir, self.controlTracker.tracksDir]

        testDirs = [self.testTracker.trackletsDir, self.testTracker.trackletsByIndexDir,
        self.testTracker.collapsedTrackletsDir, self.testTracker.collapsedTrackletsByIdDir,
        self.testTracker.purifiedTrackletsDir, self.testTracker.purifiedTrackletsByIdDir, 
        self.testTracker.finalTrackletsDir, self.testTracker.finalTrackletsByIdDir,
        self.testTracker.trackletsByNightDir, self.testTracker.tracksDir]

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

    def test_collapsedTrackletsById(self):
        testCollapsedTrackletsById = self.testTracker.collapsedTrackletsById
        controlCollapsedTrackletsById = self.controlTracker.collapsedTrackletsById

        for tt, ct in zip(testCollapsedTrackletsById, controlCollapsedTrackletsById):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_purifyTrackets(self):
        testPurifiedTracklets = self.testTracker.purifiedTracklets
        controlPurifiedTracklets = self.controlTracker.purifiedTracklets

        for tt, ct in zip(testPurifiedTracklets, controlPurifiedTracklets):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_purifiedTracketsById(self):
        testPurifiedTrackletsById = self.testTracker.purifiedTrackletsById
        controlPurifiedTrackletsById = self.controlTracker.purifiedTrackletsById

        for tt, ct in zip(testPurifiedTrackletsById, controlPurifiedTrackletsById):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_removeSubsets(self):
        testFinalTracklets = self.testTracker.finalTracklets
        controlFinalTracklets = self.controlTracker.finalTracklets

        for tt, ct in zip(testFinalTracklets, controlFinalTracklets):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_finalTrackletsById(self):
        testFinalTrackletsById = self.testTracker.finalTrackletsById
        controlFinalTrackletsById = self.controlTracker.finalTrackletsById

        for tt, ct in zip(testFinalTrackletsById, controlFinalTrackletsById):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_makeLinkTrackletsInput_byNight(self):
        testDets = self.testTracker.dets
        controlDets = self.controlTracker.dets

        for tt, ct in zip(testDets, controlDets):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

        testIds = self.testTracker.ids
        controlIds = self.controlTracker.ids

        for tt, ct in zip(testIds, controlIds):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

    def test_linkTracklets(self):
        testTracks = self.testTracker.tracks
        controlTracks = self.controlTracker.tracks

        for tt, ct in zip(testTracks, controlTracks):
            self.assertEqual(file(tt, "r").read(), file(ct, "r").read())

if __name__ == '__main__':
    unittest.main()