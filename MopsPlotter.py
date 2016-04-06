import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import MopsReader
import MopsDatabase

HW = 0.00005
HL = 0.00005
A = 1

def _plotformatter(fig, ax):
    ax.set_xlabel("RA", size=16);
    ax.set_ylabel("DEC", size=16);
    
def _textLocation(ax):
    ymin, ymax = ax.get_ylim()
    xmin, xmax = ax.get_xlim()
    xr = np.abs(xmax - xmin)
    yr = np.abs(ymax - ymin)
    return xmax+0.05*xr, ymin+0.4*yr
    return xmin+0.1*xr, ymin+0.1*yr

def plotData(detFile):
    fig, ax = plt.subplots(1,1)
    _plotformatter(fig, ax)
    df = MopsReader.readDetectionsIntoDataframe(detFile)
    ax.scatter(np.array(df['ra']), np.array(df['dec']));
    return

def plotDataframe(dataframe):
    fig, ax = plt.subplots(1,1)
    _plotformatter(fig, ax)
    ax.scatter(np.array(dataframe['ra']), np.array(dataframe['dec']));
    return

def plotTracklets(detFiles, trackletFiles):

    fig, ax = plt.subplots(1,1)
    _plotformatter(fig, ax)

    tracklets = []
    tracklet_num = 0

    for detFile, trackletFile in zip(detFiles, trackletFiles):
        df = MopsReader.readDetectionsIntoDataframe(detFile)
        ax.scatter(df['ra'], df['dec'], color='k', s=0.005);

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
    _plotformatter(fig, ax)

    track = []
    track_num = 0

    for detFile, trackFile in zip(detFiles, trackFiles):
        df = MopsReader.readDetectionsIntoDataframe(detFile)
        ax.scatter(df['ra'], df['dec'], color='k', s=0.005);

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

def plotTracklet(con, trackletId, ax=None):
    if ax is None:
        fig, ax = plt.subplots(1,1)
        _plotformatter(fig, ax)
        
    detections = MopsDatabase.findTrackletDetections(con, trackletId)
    info = MopsDatabase.findTrackletInfo(con, trackletId)
    
    ax.scatter(detections["ra"], detections["dec"], color="b", s=2)
    ax.plot(detections["ra"], detections["dec"], color="b",lw=1)
    
    ymin, ymax = ax.get_ylim()
    xmin, xmax = ax.get_xlim()
    
    nearby_detections = MopsDatabase.findNearbyDetections(con, xmin, ymin, xmax, ymax, detections["mjd"][0])
    ax.scatter(nearby_detections["ra"], nearby_detections["dec"], color="k", s=0.3, alpha=0.3)
    
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_title("TrackletId: %s" % info["trackletId"].values[0])
    
    for i, txt in enumerate(detections["objectId"]):
        ax.annotate(txt, (detections["ra"][i], detections["dec"][i]-0.001))
    
    x, y = _textLocation(ax)
    ax.text(x,y,"linkedObjectId: %s\n"
                "numLinkedObjects: %s\n"
                "numMembers: %s\n"
                "velocity: %.4f\n" 
                "rms: %.4f\n"
                "night: %s\n"
                "createdBy: %s\n"
                "deletedBy: %s\n" % (info["linkedObjectId"].values[0], 
                                    info["numLinkedObjects"].values[0],
                                    info["numMembers"].values[0],
                                    info["velocity"].values[0],
                                    info["rms"].values[0],
                                    info["night"].values[0],
                                    info["createdBy"].values[0],
                                    info["deletedBy"].values[0]),color="k")
    
    return
   
def plotTrack(con, trackId, attachedWindow, ax=None):
    if ax is None:
        fig, ax = plt.subplots(1,1)
        _plotformatter(fig, ax)
        
    detections = MopsDatabase.findTrackDetections(con, trackId, attachedWindow)
    info = MopsDatabase.findTrackInfo(con, trackId, attachedWindow)
    ax.scatter(detections["ra"], detections["dec"], color="b", s=2)
    ax.plot(detections["ra"], detections["dec"], color="b", lw=1)
    
    ymin, ymax = ax.get_ylim()
    xmin, xmax = ax.get_xlim()
    
    nearby_detections = MopsDatabase.findNearbyDetections(con, xmin, ymin, xmax, ymax, detections["mjd"][0], windowSize=15)
    ax.scatter(nearby_detections["ra"], nearby_detections["dec"], color="k", s=0.3, alpha=0.3)
    
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_title("TrackId: %s" % info["trackId"].values[0])
        
    x, y = _textLocation(ax)
    ax.text(x,y,"linkedObjectId: %s\n"
                "numLinkedObjects: %s\n"
                "numMembers: %s\n"
                "rms: %.4f\n"
                "windowStart: %s\n"
                "startTime: %s\n"
                "endTime: %s\n" 
                "subsetOf: %s\n"
                "createdBy: %s\n"
                "deletedBy: %s\n" % (info["linkedObjectId"].values[0], 
                                    info["numLinkedObjects"].values[0],
                                    info["numMembers"].values[0],
                                    info["rms"].values[0],
                                    info["windowStart"].values[0],
                                    info["startTime"].values[0],
                                    info["endTime"].values[0],
                                    info["subsetOf"].values[0],
                                    info["createdBy"].values[0],
                                    info["deletedBy"].values[0]), color="k")
    
    return

def addVelocityRange(ax, ra_center, dec_center, vmax, dt=1.0):
    vrange = plt.Circle((ra_center, dec_center), vmax*dt, color='k', fill=False)
    ax.add_artist(vrange)