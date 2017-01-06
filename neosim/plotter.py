import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import neosim.reader as reader
import neosim.database as database

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
    df = reader.readDetectionsIntoDataframe(detFile)
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
        df = reader.readDetectionsIntoDataframe(detFile)
        ax.scatter(df['ra'], df['dec'], color='k', s=0.005);

        for line in open(trackletFile, "r"):
            tracklets = reader.readTracklet(line)
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
        df = reader.readDetectionsIntoDataframe(detFile)
        ax.scatter(df['ra'], df['dec'], color='k', s=0.005);

        for line in open(trackFile, 'r'):
            track = reader.readTrack(line)
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
        
    detections = database.findTrackletDetections(con, trackletId)
    info = database.findTrackletInfo(con, trackletId)
    
    ax.scatter(detections["ra"], detections["dec"], color="b", s=2)
    ax.plot(detections["ra"], detections["dec"], color="b",lw=1)
    
    ymin, ymax = ax.get_ylim()
    xmin, xmax = ax.get_xlim()
    
    nearby_detections = database.findNearbyDetections(con, xmin, ymin, xmax, ymax, detections["mjd"][0])
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
        
    detections = database.findTrackDetections(con, trackId, attachedWindow)
    info = database.findTrackInfo(con, trackId, attachedWindow)
    ax.scatter(detections["ra"], detections["dec"], color="b", s=2)
    ax.plot(detections["ra"], detections["dec"], color="b", lw=1)
    
    ymin, ymax = ax.get_ylim()
    xmin, xmax = ax.get_xlim()
    
    nearby_detections = database.findNearbyDetections(con, xmin, ymin, xmax, ymax, detections["mjd"][0], windowSize=15)
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


def plotDetections(con):
    missed_objects_detections = database.findMissedObjectsDetections(con)
    found_objects_detections = database.findFoundObjectsDetections(con)

    fig, ax = plt.subplots(1,2)
    fig.set_size_inches(14,7)

    ax[0].scatter(found_objects_detections["ra"], found_objects_detections["dec"], c="b", label="%s Found objects" % found_objects_detections["objectId"].nunique())
    ax[1].scatter(missed_objects_detections["ra"], missed_objects_detections["dec"], c="r",  label="%s Missed objects" % missed_objects_detections["objectId"].nunique())

    for a in ax:
        a.legend()
        a.set_xlabel("RA", size=16);
        a.set_ylabel("DEC", size=16);   
    
    ax[0].set_title("Found Objects and Their Detections")
    ax[1].set_title("Missed Objects and Their Detections")

    return


def plotMagHist(con):
    found_objects_detections = database.findFoundObjectsDetections(con)
    missed_objects_detections = database.findMissedObjectsDetections(con)

    total_detections = float(len(found_objects_detections) + len(missed_objects_detections))

    hist, bin_edges = np.histogram(found_objects_detections["mag"].values, bins=np.linspace(12,26,15))
    hist2, bins = np.histogram(missed_objects_detections["mag"].values, bins=bin_edges)
    width = 0.4

    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(10,7)
    ax.bar(bin_edges[1:], hist/total_detections*100.0, width, label="Found")
    ax.bar(bin_edges[1:] + width, hist2/total_detections*100.0, width, color="r", label="Missed")
    #ax.set_xticks(bin_edges[1:]);
    ax.legend(loc="upper left");
    ax.grid();
    ax.set_title("MAG Distribution as Percent of Detections");
    ax.set_xlabel("MAG");
    ax.set_ylabel("% Freq");

    return

def plotSnrHist(con):
    found_objects_detections = database.findFoundObjectsDetections(con)
    missed_objects_detections = database.findMissedObjectsDetections(con)

    total_detections = float(len(found_objects_detections) + len(missed_objects_detections))

    hist, bin_edges = np.histogram(found_objects_detections["snr"].values, bins=np.linspace(0,60,20))
    hist2, bins = np.histogram(missed_objects_detections["snr"].values, bins=bin_edges)
    width = 0.75

    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(10,7)
    ax.bar(bin_edges[1:], hist/total_detections*100.0, width, label="Found")
    ax.bar(bin_edges[1:] + width, hist2/total_detections*100.0, width, color="r", label="Missed")
    #ax.set_xticks(bin_edges[1:]);
    ax.legend(loc="upper left");
    ax.grid();
    ax.set_title("SNR Distribution as Percent of Detections");
    ax.set_xlabel("SNR");
    ax.set_ylabel("% Freq");

    return

def plotVelocityHist(con):
    missed_objects_tracklets = database.findMissedObjectsTracklets(con)
    found_objects_tracklets = database.findFoundObjectsTracklets(con)
    
    total_tracketlets_num = float(len(missed_objects_tracklets["trackletId"].unique()) + len(found_objects_tracklets["trackletId"].unique()))

    hist, bin_edges = np.histogram(found_objects_tracklets["velocity"].unique(), bins=np.linspace(0,2.5,15))
    hist2, bins = np.histogram(missed_objects_tracklets["velocity"].unique(), bins=bin_edges)
    width = 0.05

    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(10,7)
    ax.bar(bin_edges[1:], hist/total_tracketlets_num*100., width, label="Found")
    ax.bar(bin_edges[1:] + width, hist2/total_tracketlets_num*100., width, color="r", label="Missed")
    ax.legend(loc="upper right");
    ax.grid();
    ax.set_title("Velocity Distribution as Percent of Tracklets");
    ax.set_xlabel("Velocity");
    ax.set_ylabel("% Freq");

    return

def plotHists(con):
    plotDetections(con)
    plotMagHist(con)
    plotSnrHist(con)
    plotVelocityHist(con)

    return


def plotObject(con, objectId):
    fig, ax = plt.subplots(1,1)
    _plotformatter(fig, ax)
    detections = database.findObjectDetections(con, objectId)
    ax.scatter(np.array(detections['ra']), np.array(detections['dec']));
    return


def addVelocityRange(ax, ra_center, dec_center, vmax, dt=1.0):
    vrange = plt.Circle((ra_center, dec_center), vmax*dt, color='k', fill=False)
    ax.add_artist(vrange)