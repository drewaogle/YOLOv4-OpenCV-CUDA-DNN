#!/usr/bin/python3
import argparse
import pandas as pd

def create_clips( args ):
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
       if cur_frame != last_frame:
           # drop any which werent active last frame
           new_active = {}
           new_registered = {}
           for old_label in active:
               last_active = active[old_label][0] + active[old_label][1]
               if cur_frame != last_active +1:
                   print(f'Dropped {old_label}')
               else:
                   new_active[old_label] = active[old_label]
                   #del active[old_label]
           for old_label in registered:
               last_active = registered[old_label][0] + registered[old_label][1]
               total_active = registered[old_label][1]
               start_frame = registered[old_label][0]
               if cur_frame != last_active +1:
                   print(f'Retired {old_label} frame duration: {total_active}, started {start_frame}')
                   finished[ "{}_{}".format(old_label,last_active) ] = [old_label] + registered[old_label]
                   #del registered[old_label]
               else:
                   new_registered[old_label] = registered[old_label]
           active = new_active
           registered = new_registered
       if label in active:
           label_start = active[label][0]
           label_len = active[label][1] + 1
           if row['confidence'] * 100 > args.initconf:
               if active[label][1] +1 <= args.initlen:
                   registered[label] = [label_start,label_len]
               else:
                   active[label] = [label_start,label_len]
       elif label in registered:
           label_start = registered[label][0]
           label_len = registered[label][1]
           # if above confidence for dropping, consider a new registered frame
           if row['confidence'] * 100 > args.dropconf:
                # allows frame to miss one and restart; duration calculated from start to current.
                registered[label] = [label_start,cur_frame-label_start] 

       else:
           # if label not in active list
           if row['confidence'] * 100 > args.initconf:
               active[label] = [cur_frame,0]
       last_frame = cur_frame

   tdod = len(finished.keys())
   print(f"{tdod} elements")
   for k in finished.keys():
       val = finished[k]
       print(f"{k}= {val}")


if __name__ == '__main__':
        parser = argparse.ArgumentParser(description='Parse csv to clips')
        parser.add_argument('--offset_fr', type=int, default=0, help='Offset in video to look for frames')
        parser.add_argument('--end_fr', type=int, default=-1, help='Offset in video to look for frames')
        parser.add_argument('--initconf', type=int, default=50, help='Minimum acceptable confidence to start clip ( value 0-100 )')
        parser.add_argument('--initlen', type=int, default=5, help='Minimum frame duration to start clip')
        parser.add_argument('--dropconf', type=int, default=25, help='Confidence to consider dropping a clip with ( value 0-100 )')
        parser.add_argument('--droplen', type=int, default=50, help='Number of missed frames to consider dropping a clip with')
        parser.add_argument('--detections', type=str, default='output/detections.csv', help='Path to use detections')

        args = parser.parse_args()
        create_clips( args )

