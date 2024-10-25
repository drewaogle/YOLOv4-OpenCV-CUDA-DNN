#!/usr/bin/python3
import argparse
import pandas as pd
from hashlib import sha1
from uuid import UUID

from aperturedb import Connector
DB_HOST="127.0.0.1"
DB_PORT=55555
DB_USER="admin"
DB_PASS="admin"

def connect():
    return Connector.Connector(DB_HOST, DB_PORT, user=DB_USER, password=DB_PASS)

def load_video( vfile):
    fd = open( vfile, 'rb')
    vbuf = fd.read()
    fd.close()
    return vbuf

def create_clips( args,db_conn = None ):
   add_data = []
   f = open( args.detections , 'r' )
   l = f.readline()
   f.close()
   pf = pd.read_csv(args.detections,header=None)
   pf.columns = ["frame","label","confidence","left","top","width","height" ]
   pf.drop(pf[pf.frame < args.offset_fr].index, inplace=True)
   if args.end_fr > -1:
       pf.drop(pf[pf.frame > args.end_fr].index,inplace=True)
   print(pf)
   active = {}
   registered = {}
   finished = {}
   last_frame =0
   cur_frame = 0
   for idx,row in pf.iterrows():
       cur_frame = row['frame']
       label = row['label']
       # process events which trigger on new frame.
       if cur_frame != last_frame:
           if args.verbose:
               print(f"Processing switch from {last_frame} to {cur_frame}")
           # drop any which werent active last frame
           new_active = {}
           new_registered = {}
           for old_label in active:
               last_active = active[old_label][0] + active[old_label][1]
               if cur_frame != last_active +1:
                   if args.verbose:
                       print(f'At frame {cur_frame}, Dropped {old_label} ( last active {last_active} )')
               else:
                   if args.verbose:
                       print(f"At frame {cur_frame}, kept {old_label}")
                   new_active[old_label] = active[old_label]
           for old_label in registered:
               last_active = registered[old_label][0] + registered[old_label][1]
               total_active = registered[old_label][1]
               start_frame = registered[old_label][0]
               if cur_frame != last_active +1:
                   if args.verbose:
                       print(f'At frame {cur_frame}, Retired {old_label} frame duration: {total_active}, started {start_frame}')
                   finished[ "{}_{}".format(old_label,last_active) ] = [old_label] + registered[old_label]
               else:
                   new_registered[old_label] = registered[old_label]
           active = new_active
           registered = new_registered

           if args.verbose:
               print("Active dict: {active}")
       # all old active and registered are dropped
       if label in active:
           label_start = active[label][0]
           label_len = active[label][1] + 1
           if row['confidence'] * 100 > args.initconf:
               max_confidence = max(active[label][2], row['confidence'])
               if active[label][1] +1 >= args.initlen:
                   if args.verbose:
                       print(f"At frame {cur_frame}, moved {label} to registered")
                   registered[label] = [label_start,label_len,max_confidence]
               else:
                   if args.verbose:
                       print(f"At frame {cur_frame}, saw {label}")
                   active[label] = [label_start,label_len,max_confidence]
           else:
               if args.verbose:
                   print(f"At frame {cur_frame}, saw {label}, but confidence was too low to re-register")
       elif label in registered:
           label_start = registered[label][0]
           label_len = registered[label][1]
           max_confidence = max(registered[label][2], row['confidence'])
           # if above confidence for dropping, consider a new registered frame
           if row['confidence'] * 100 > args.dropconf:
                # allows frame to miss one and restart; duration calculated from start to current.
                registered[label] = [label_start,cur_frame-label_start,max_confidence] 
       else:
           # if label not in active list
           if row['confidence'] * 100 > args.initconf:
               if args.verbose:
                   print(f"At frame {cur_frame}, added {label}")
               active[label] = [cur_frame,0,row['confidence']]
       last_frame = cur_frame

   tdod = len(finished.keys())

   if args.verbose:
       print(f"{tdod} elements")
       for k in finished.keys():
           val = finished[k]
           print(f"{k}= {val}")

   query = []
   all_uuids = []

   sha1hash = sha1()
   sha1hash.update(str.encode(args.video))
   sha1hash.update(str.encode(args.detections))
   sha = sha1hash.digest()
   video_uuid = str(UUID( bytes=sha[:16]))
   all_uuids.append(video_uuid)
   video_add = {
       "AddVideo": {
           "if_not_found" : {
               "guid" : [ "==", video_uuid ]
           },
           "_ref": 1,
           "properties" : {
               "guid" : video_uuid
           }
       }
   }
   if args.label != "":
       video_add["AddVideo"]["properties"]["label"] = args.label

   query.append( video_add )
   

   for k in finished.keys():
       val = finished[k]
       label = val[0]
       start = val[1]
       clen = val[2]
       sha1hash = sha1()
       sha1hash.update(str.encode(args.video))
       sha1hash.update(str.encode(args.detections))
       sha1hash.update( str.encode(f"{val[0]},{val[1]},{val[2]}"))
       sha = sha1hash.digest()
       #print( f"{len(sha)} {sha}")
       clip_uuid = str(UUID( bytes=sha[:16]))
       all_uuids.append(clip_uuid)
       clip_add = {
            "AddClip": {
                "if_not_found" : {
                    "guid" : [ "==", clip_uuid ]
                },
                'label': label,
                "video_ref" : 1,
                "frame_number_range" : [ start, start+clen ],
                "properties" : { 
                    "guid" : clip_uuid,
                    "max_confidence" : val[3]
                    }
            }
        }
       query.append(clip_add)

   delete_entity = [{
       "DeleteEntity": {
                "constraints" : {
                    "guid" : [ "in" , all_uuids ]
                }
           }
   }]

   print("Queries Assembled")
   if args.verbose:
       print(query)
   db = connect() if db_conn is None else db_conn
   if args.flush:
        print(f"Delete Query: {delete_entity}")
        (del_result,data) = db.query(delete_entity)
        print(f"Delete Result: {del_result}")
   if not args.nosave:
        add_data.append(load_video(args.video))
        print(f"Add Query: {query}")
        (add_result,data) = db.query(query,add_data)
        print(f"Add Result: {add_result}")


if __name__ == '__main__':
        parser = argparse.ArgumentParser(description='Parse csv to clips')
        parser.add_argument('--offset_fr', type=int, default=0, help='Offset in video to look for frames')
        parser.add_argument('--end_fr', type=int, default=-1, help='Offset in video to look for frames')
        parser.add_argument('--initconf', type=int, default=50, help='Minimum acceptable confidence to start clip ( value 0-100 )')
        parser.add_argument('--initlen', type=int, default=5, help='Minimum frame duration to start clip')
        parser.add_argument('--dropconf', type=int, default=25, help='Confidence to consider dropping a clip with ( value 0-100 )')
        parser.add_argument('--droplen', type=int, default=50, help='Number of missed frames to consider dropping a clip with')
        parser.add_argument('--detections', type=str, default='output/detections.csv', help='Path to use detections')
        parser.add_argument('--verbose', action='store_true',  help='Verbose output')
        parser.add_argument('--flush', action='store_true',  help='Remove old uuids from database')
        parser.add_argument('--nosave', action='store_true',  help='Dont add data')
        parser.add_argument('--video', type=str, required=True, help='Path to use detections')
        parser.add_argument('--label', type=str, default="", help='Label to attach to the video')

        args = parser.parse_args()
        create_clips( args )

