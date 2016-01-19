import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import MopsReader

HW = 0.00005
HL = 0.00005
A = 1

def _plotprettymaker(fig, ax):
    ax.set_xlabel("RA", size=16);
    ax.set_ylabel("DEC", size=16);
    fig.set_size_inches(10,7);

def _textLocation(ax):
    ymin, ymax = ax.get_ylim()
    xmin, xmax = ax.get_xlim()
    xr = np.abs(xmax - xmin)
    yr = np.abs(ymax - ymin)
    return xmin+0.1*xr, ymin+0.1*yr

def plotData(detFile):
    fig, ax = plt.subplots(1,1)
    _plotprettymaker(fig, ax)
    ax.scatter(np.array(dataframe['ra']), np.array(dataframe['dec']));

def plotTracklets(detFiles, trackletFiles):

    fig, ax = plt.subplots(1,1)
    _plotprettymaker(fig, ax)

    tracklets = []
    tracklet_num = 0

    for detFile, trackletFile in zip(detFiles, trackletFiles):
        df = MopsReader.readDetectionsIntoDataframe(detFile)
        ax.scatter(np.array(df['ra']), np.array(df['dec']), color='k', s=0.005);

        for line in open(trackletFile, "r"):
            tracklets = MopsReader.readTracklet(line)
            tracklet_num += 1
        
            p1 = df.loc[tracklets[0]]
            p2 = df.loc[tracklets[-1]]
            
            dRa = float(p2['ra'])-float(p1['ra'])
            dDec = float(p2['dec'])-float(p1['dec'])
            
            ax.arrow(float(p1['ra']), float(p1['dec']), dRa, dDec,
                head_width=HW, head_length=HL, fc='k', ec='k', alpha=A)

        del df

    ax.text(_textLocation(ax)[0], _textLocation(ax)[1], 'Tracklets: ' + str(tracklet_num), size=18, color='r')

def plotTracks(detFiles, trackFiles):

    fig, ax = plt.subplots(1,1)
    _plotprettymaker(fig, ax)

    track = []
    track_num = 0

    for detFile, trackFile in zip(detFiles, trackFiles):
        df = MopsReader.readDetectionsIntoDataframe(detFile)
        ax.scatter(np.array(df['ra']), np.array(df['dec']), color='k', s=0.005);

        for line in open(trackFile, 'r'):
            track = MopsReader.readTrack(line)
            track_num += 1
            ra = []
            dec = []
            
            for d in track:
                ra.append(df.loc[d]['ra'])
                dec.append(df.loc[d]['dec'])
                
            ax.plot(ra, dec, color='k',alpha=0.7)

        del df
            
    ax.text(_textLocation(ax)[0], _textLocation(ax)[1], 'Tracks: ' + str(track_num), size=16, color='r')
