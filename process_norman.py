#!/bin/env python3
from to_clip import create_clips
from dnn_inference import YOLOv4
from remote import RemoteYOLOv4
from aperturedb.Utils import create_connector
import sys

class ClipOptions:
    offset_fr=0 # starting offset in frames
    end_fr=-1 # ending offset in frames
    initconf=50 # minimun confidence to start ( 0-100 )
    initlen=5 # minimum detection duration in frames to start a clip
    dropconf=25 # confidence to end a frame (0 -100 )
    droplen=5 # number of detection missed frames to end a clip
    detections="output/noman/detections.csv" # path to output detections
    verbose=False
    flush=False # remove old uuids
    nosave=False # dont add data to db
    label="" # label for video
    def __init__(self,video):
        self.video=video # video file to add

class DetectorOptions:
    image='' # path for images
    stream='' # path for stream
    cfg="models/yolov4.cfg" # path to config
    weights="models/yolov4.weights" # path to weights
    namesfile="models/coco.names" # path for output to name mapping
    input_size=416
    use_gpu=False # use GPU or not
    outdir="output/norman"
    def __init__(self, image='',stream=''):
        self.image = image
        self.stream=stream # 'webcam' to open webcam w/ OpenCV

dopts = DetectorOptions( stream="norman.mp4")
yolo = RemoteYOLOv4.__new__(RemoteYOLOv4)
yolo.__init__(dopts)
sys.exit(0)

opts = ClipOptions( "norman.mp4" )
opts.label="Norman_Bike"
opts.initconf=45
opts.initlen=3
opts.dropconf=20
opts.droplen=3

c = create_connector()

create_clips( opts, c )
