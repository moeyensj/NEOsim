import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HW = 0.00005
HL = 0.00005
A = 1

def _plotprettymaker(fig, ax):
    ax.set_xlabel("RA", size=16);
    ax.set_ylabel("DEC", size=16);
    fig.set_size_inches(10,7);
    #ax.set_xlim(ra[0],ra[1])
    #ax.set_ylim(dec[0],dec[1]);
    ax.set_title("Random Selection: %i objects, %s nights" % (1, 1), size=20)

def _textLocation(ax):
    ymin, ymax = ax.get_ylim()
    xmin, xmax = ax.get_xlim()
    xr = np.abs(xmax - xmin)
    yr = np.abs(ymax - ymin)
    return xmin+0.1*xr, ymin+0.1*yr

def plotData(dataframe):
    fig, ax = plt.subplots(1,1)
    _plotprettymaker(fig, ax)
    ax.scatter(np.array(dataframe['ra']), np.array(dataframe['dec']));
    #fig.savefig("data.jpg")

def plotTracklets(trackletFiles, dataframe):

    fig, ax = plt.subplots(1,1)
    _plotprettymaker(fig, ax)

    ax.scatter(np.array(dataframe['ra']), np.array(dataframe['dec']), color='k', alpha=0.5);

    tracklets = []
    tracklet_num = 0

    for filein in trackletFiles:
        for line in open(filein, 'r'):
            tracklets = np.fromstring(line, sep=" ", dtype=int)
            tracklet_num += 1
        
            p1 = dataframe[dataframe['diaid'] == tracklets[0]]
            p2 = dataframe[dataframe['diaid'] == tracklets[-1]]
            
            dRa = float(p2['ra'])-float(p1['ra'])
            dDec = float(p2['dec'])-float(p1['dec'])
            
            ax.arrow(float(p1['ra']), float(p1['dec']), dRa, dDec,
                head_width=HW, head_length=HL, fc='k', ec='k', alpha=A)


    ax.text(_textLocation(ax)[0], _textLocation(ax)[1], 'Tracklets: ' + str(tracklet_num), size=18, color='r')
    #fig.savefig("tracklets.jpg")

def plotTracks(trackFiles, dataframe):

    fig, ax = plt.subplots(1,1)
    _plotprettymaker(fig, ax)

    ax.scatter(np.array(dataframe['ra']), np.array(dataframe['dec']), color='k', alpha=0.5);

    track_num = 0

    for filein in trackFiles:
        for line in open(filein, 'r'):
            track = np.fromstring(line, sep=" ", dtype=int)
            track_num += 1
            ra = []
            dec = []
            
            for d in track:
                ra.append(float(dataframe.loc[dataframe['diaid'] == d]['ra']))
                dec.append(float(dataframe.loc[dataframe['diaid'] == d]['dec']))
                
            ax.plot(ra, dec, color='k',alpha=0.7)
            
    ax.text(_textLocation(ax)[0], _textLocation(ax)[1], 'Tracks: ' + str(track_num), size=16, color='r')
    #fig.savefig("tracks.jpg")