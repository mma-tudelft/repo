import numpy as np
import cv2
import matplotlib.pyplot as plt
from video_tools import *
import feature_extraction as ft
from scikits.talkbox.features import mfcc

# Path to video file to analyse 
video = '../Videos/video_07.mp4'

# Retrieve frame count. We need to add one to the frame count because cv2 somehow 
# has one extra frame compared to the number returned by avprobe.
frame_count = get_frame_count(video) + 1
frame_rate = get_frame_rate(video)

# create an cv2 capture object
cap = cv2.VideoCapture(video)

# initialize a figure to do interactive plotting
plt.figure()
plt.ion()
plt.show()
# store previous frame
prev_frame = None
while(cap.isOpened()):

    # 
    retVal, frame = cap.read()
    # 
    if retVal == False:
        break

    #== Do your processing here ==#


    # 
    cv2.imshow('Video', frame)


    # 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    prev_frame = frame

#
cap.release()
cv2.destroyAllWindows()
