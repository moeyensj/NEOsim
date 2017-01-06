import os
import random
import shutil
import subprocess
import sqlite3 as sql
import pandas as pd
 
import runMops
from tracker import Tracker
from parameters import Parameters

TEST_DATA_DIR = "unittest/testData/"
CONTROL_RUN_DIR = "unittest/controlRun/"
DATABASE = "unittest/testsources.db"

def updateUnittest(database, testDataDir, controlRunDir, tableName="testsources"):
    
    # Clean up any existing files in controlRunDir and testDataDir, create directoriess
    if os.path.exists(controlRunDir):
        shutil.rmtree(controlRunDir)
    os.mkdir(controlRunDir)
        
    if os.path.exists(testDataDir):
        shutil.rmtree(testDataDir)
    os.mkdir(testDataDir)
    
    # Connect to the database
    con = sql.connect(database)
    
    # Gather detections and save them to a text file
    objs = pd.read_sql_query("""
    SELECT * FROM %s
    """ % tableName, con, index_col="diaId")
    
    # Retrieve unique ssmids and limit to 3
    ssmids = objs["ssmId"].unique()
    ssmids_sample = sorted(random.sample(ssmids, 3))
    
    createTestCase(con, testDataDir, controlRunDir, "full")
    createTestCase(con, testDataDir, controlRunDir, "source1", ssmid="1")
    createTestCase(con, testDataDir, controlRunDir, "source2", ssmid="2")
    createTestCase(con, testDataDir, controlRunDir, "source3", ssmid="3")

def createTestCase(con, testDataDir, controlRunDir, subDir, ssmid=None):
    new_data_dir = os.path.join(testDataDir, subDir)
    os.mkdir(new_data_dir)
    
    nightly = os.path.join(new_data_dir, "nightly/")
    os.mkdir(nightly)
    
    if ssmid == None:
        dets = pd.read_sql_query("""
        SELECT * FROM testsources
        """, con, index_col="diaId")
        
        detsOut = os.path.join(new_data_dir, "full.txt")
        dets.to_csv(detsOut, sep=" ", header=False, index="diaId")
    else:
        dets = pd.read_sql_query("""
        SELECT * FROM testsources
        WHERE ssmId = %s
        """ % ssmid, con, index_col="diaId")
    
        detsOut = os.path.join(new_data_dir, "source%s.txt" % (ssmid))
        dets.to_csv(detsOut, sep=" ", header=False, index="diaId")

    call = ["python", os.getenv("MOPS_DIR") + "/bin/splitByNight.py", "-n", nightly, detsOut]
    subprocess.call(call);
    
    runDir = os.path.join(controlRunDir, subDir)
    parameters = Parameters(verbose=True)
    tracker = Tracker(runDir, verbose=True)
    runMops.runMops(parameters, tracker, nightly, runDir)

if __name__ == "__main__":
    updateUnittest(DATABASE, TEST_DATA_DIR, CONTROL_RUN_DIR)
