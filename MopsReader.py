import numpy as np
import pandas as pd

def readTracklets(trackletFile):
    trackletFileIn = open(trackletFile, 'r')
    for tracklet in trackletFileIn:
        diaids = tracklet.split(" ", dtype=int)[:-1]
        return np.array(diaids)

def readTracks(trackFile):
    trackFileIn = open(trackFile, 'r')
    for tracklet in trackFileIn:
        diaids = tracklet.split(" ", dtype=int)[:-1]
        return np.array(diaids)

def readDetections(detFile):
    return pd.read_csv(detFile, sep=' ', header=None, names=['diaid', 'obshistid', 'ssmid', 'ra', 'dec', 'mjd', 'mag', 'snr'])