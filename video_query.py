#!/usr/bin/env python
import argparse
import video_search
import numpy as np
import cv2
import glob
from video_tools import *
import feature_extraction as ft    
import sys
    
parser = argparse.ArgumentParser(description="Video Query tool")
parser.add_argument("training_set", help="Path to training videos and wav files")
parser.add_argument("query", help="query video")
parser.add_argument("-s", help="Timestamp for start of query in seconds", default=0.0)
parser.add_argument("-e", help="Timestamp for end of query in seconds", default=0.0)
parser.add_argument("-f", help="Select features to do the query with", default='all')
args = parser.parse_args()


cap = cv2.VideoCapture(args.query)
frame_count = get_frame_count(args.query, util='ffprobe') + 1
frame_rate = get_frame_rate(args.query, util='ffprobe')
q_duration = get_duration(args.query, util='ffprobe')

if not float(args.s) < float(args.e) < q_duration:
    print 'Timestamp for end of query set to:', q_duration
    args.e = q_duration

cap.set(cv2.CAP_PROP_POS_MSEC, int(args.s)*1000)
query_hists = []
while(cap.isOpened() and cap.get(cv2.CAP_PROP_POS_MSEC) < (int(args.e)*1000)):
    ret, frame = cap.read()
    if frame == None:
        break

    h = ft.colorhist(frame)
    query_hists.append(h)
    # show frame
#    cv2.imshow('Video', frame)

    # break out of loop by pressing 'q'
 #   if cv2.waitKey(1) & 0xFF == ord('q'):
 #      break





# Compare with database

video_types = ('*.mp4', '*.MP4')
audio_types = ('*.wav', '*.WAV')

# grab all video file names
video_list = []
for type_ in video_types:
    files = args.training_set + '/' +  type_
    video_list.extend(glob.glob(files))	

db_name = 'db/video_database.db'
search = video_search.Searcher(db_name)

def sliding_window(x, w, compare_func):
    """ Slide window w over signal x. 
    """
    wl = len(w)
    minimum = sys.maxint
    for i in range(len(x) - wl):
        diff = compare_func(w, x[i:(i+wl)]
        if diff<minimum:
            minimum = diff
            frame   = i
    return frame, minimum
   
def euclidean_norm(x,y):
    mean_x = np.mean(x, axis=0)
    mean_y = np.mean(y, axis=0)
    return np.linalg.norm(x-y)

for video in video_list:
    print video
    dur = get_duration(video, util='ffprobe')
    w = np.array(query_hists)
    x = search.get_features_for(video)
    if dur < q_duration:
        # use db clip as sliding window as it is shorter than the query clip
        x,w = w,x
    print 'x:', x.shape 
    print 'w:', w.shape 
    print sliding_window(x,w, euclidean_norm)
 
