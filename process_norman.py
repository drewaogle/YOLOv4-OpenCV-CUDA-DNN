#!/bin/env python3
from to_clip import create_clips
from aperturedb.Utils import create_connector

class Options:
    offset_fr=0 # starting offset in frames
    end_fr=-1 # ending offset in frames
    initconf=50 # minimun confidence to start ( 0-100 )
    initlen=5 # minimum detection duration in frames to start a clip
    dropconf=25 # confidence to end a frame (0 -100 )
    droplen=5 # number of detection missed frames to end a clip
    detections="output/detections.csv" # path to output detections
    verbose=False
    flush=False # remove old uuids
    nosave=False # dont add data to db
    label="" # label for video
    def __init__(self,video):
        self.video=video # video file to add



opts = Options( "norman.mp4" )
opts.label="Norman_Bike"
opts.initconf=45
opts.initlen=3
opts.dropconf=20
opts.droplen=3

c = create_connector()

create_clips( opts, c )
