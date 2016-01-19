import os
import numpy as np
import pandas as pd
import sqlite3 as sql

def readTracklet(tracklet):
    return np.fromstring(tracklet, sep=" ", dtype=int) 

def readTrack(track):
    return np.fromstring(track, sep=" ", dtype=int)

def readIds(ids):
    return np.fromstring(track, sep=" ", dtype=int)

def readDetectionsIntoDataframe(detsFile):
    return pd.read_csv(detsFile, header=None, names=['diaid', 'obshistid', 'ssmid', 'ra', 'dec', 'mjd', 'mag', 'snr'], index_col='diaid', delim_whitespace=True)

def readDetectionsIntoDatabase(detsFile, database, table):
    con = sql.connect(database)
    con.execute("""
    CREATE TABLE %s (
        diaid INTEGER,
        obshistid INTEGER,
        ssmid INTEGER,
        ra REAL,
        dec REAL,
        mjd REAL,
        mag REAL,
        snr REAL
    );
    """ % (table))

    df = readDetectionsIntoDataframe(detsFile)
    df.to_sql(table, con, if_exists="append")

    con.close()
    del df

    return