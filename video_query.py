#!/usr/bin/env python
import argparse
import video_search
import numpy as np
import cv2
import glob
from video_tools import *
import feature_extraction as ft    
import sys
from video_features import *
   
features = ['colorhists', 'tempdiffs', 'audiopowers', 'mfccs']
 
parser = argparse.ArgumentParser(description="Video Query tool")
parser.add_argument("training_set", help="Path to training videos and wav files")
parser.add_argument("query", help="query video")
parser.add_argument("-s", help="Timestamp for start of query in seconds", default=0.0)
parser.add_argument("-e", help="Timestamp for end of query in seconds", default=0.0)
parser.add_argument("-f", help="Select features "+str(features)+" for the query ", default='colorhists')
args = parser.parse_args()


cap = cv2.VideoCapture(args.query)
frame_count = get_frame_count(args.query) + 1
frame_rate = get_frame_rate(args.query )
q_duration = get_duration(args.query) 

if not float(args.s) < float(args.e) < q_duration:
    print 'Timestamp for end of query set to:', q_duration
    args.e = q_duration

cap.set(cv2.CAP_PROP_POS_MSEC, int(args.s)*1000)
query_features = []
prev_frame = None
while(cap.isOpened() and cap.get(cv2.CAP_PROP_POS_MSEC) < (int(args.e)*1000)):
    ret, frame = cap.read()
    if frame == None:
        break

    if args.f == features[0]: 
        h = ft.colorhist(frame)
    elif args.f == features[1]:
        h = temporal_diff(prev_frame, frame)
    
    if h != None:
        query_features.append(h)
    prev_frame = frame


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
        diff = compare_func(w, x[i:(i+wl)])
        if diff < minimum:
            minimum = diff
            frame   = i
    return frame, minimum
   
def euclidean_norm(x,y):
    mean_x = np.mean(x, axis=0)
    mean_y = np.mean(y, axis=0)
    return np.linalg.norm(x-y)

for video in video_list:
    print video
    dur = get_duration(video)
    if args.f == features[0]: 
        x = search.get_colorhists_for(video)
    elif args.f == features[1]:
        x = search.get_temporaldiffs_for(video)
    w = np.array(query_features)
    if dur < q_duration:
        print 'Error: query is longer than database video'
        sys.exit()
    frame, score = sliding_window(x,w, euclidean_norm)
    print frame/frame_rate, score

 
