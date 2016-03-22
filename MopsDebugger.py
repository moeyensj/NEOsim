import os
import shutil
import subprocess
import sqlite3 as sql
import pandas as pd
 
import runMops
import MopsAnalysis
from MopsTracker import MopsTracker
from MopsParameters import MopsParameters

OUTPUT_DIR = "debug/debugSources/"
DATABASE = "/Volumes/DataCenter/neosimData/ldm156/fullsky5year.db"
TABLE_NAME = "noAstromErr"

def runObject(objectId, database=DATABASE, tableName=TABLE_NAME, outputDir=OUTPUT_DIR, delete=False, deleteExisting=False):

    new_data_dir = os.path.join(outputDir, str(objectId))

    if deleteExisting:
        if os.path.exists(new_data_dir):
            shutil.rmtree(new_data_dir)
    os.makedirs(new_data_dir)

    con = sql.connect(database)
    
    dets = pd.read_sql_query("""
    SELECT * FROM %s
    WHERE objectId == %s
    """ % (tableName, objectId), con, index_col="diaId") 

    if len(dets) == 0:
        raise ValueError("ObjectId doesn't exist.")

    detsOut = os.path.join(new_data_dir, "%s.txt" % (objectId))
    dets.to_csv(detsOut, sep=" ", header=False, index="diaId")
    
    nightly = os.path.join(new_data_dir, "nightly/")
    os.mkdir(nightly)
    
    call = ["python", os.getenv("MOPS_DIR") + "/bin/splitByNight.py", "-n", nightly, detsOut]
    subprocess.call(call);
    
    run_dir = os.path.join(new_data_dir, "run")
    parameters = MopsParameters(verbose=True)
    tracker = MopsTracker(run_dir, verbose=True)
    tracker.getDetections(nightly)
    runMops.runMops(parameters, tracker)

    results = MopsAnalysis.analyze(parameters, tracker, outDir=outputDir)

    if delete:
        shutil.rmtree(run_dir)

    return parameters, tracker, results

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Runs MOPS on a single source")
    parser.add_argument("objectId", type=str, help="Object ID to run through MOPs.")
    parser.add_argument("-o", "--outputDir", default=OUTPUT_DIR, help="Parent directory where to store output files.")
    parser.add_argument("-db", "--database", default=DATABASE, help="File path to database.")
    parser.add_argument("-t", "--tableName", default=TABLE_NAME, help="Name of table containing detections.")
    parser.add_argument("-d", "--delete", action="store_true", help="Deletes MOPs output.")
    parser.add_argument("-O", "--overwrite", action="store_true", help="Overwrites existing test output.")

    args = parser.parse_args()

    parameters, tracker = runObject(args.objectId, database=args.database, tableName=args.tableName, outputDir=args.outputDir, delete=args.delete, deleteExisting=args.overwrite)
