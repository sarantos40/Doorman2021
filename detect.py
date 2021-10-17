#!/usr/bin/python3
from imutils import face_utils
import numpy as np
import argparse
import imutils
import dlib
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 5
rawCapture = PiRGBArray(camera, size=(640, 480))
 
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=True,
help="facial landmark predictor path")
args = vars(ap.parse_args())
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(args["shape_predictor"])
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    if key == ord("s"):
       image = imutils.resize(image, width=300)
       gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
       rects = detector(gray, 1)
 
# loop over the face detections
       for (i, rect) in enumerate(rects):
 
# determine the facial landmarks for the face region
          shape = predictor(gray, rect)
          shape = face_utils.shape_to_np(shape)
 
# loop over the face parts individually
          for (name, (i, j)) in face_utils.FACIAL_LANDMARKS_IDXS.items():
 
# display the name of the face part on the image
                clone = image.copy()
                cv2.putText(clone, name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
0.7, (0, 0, 255), 2)
 
# Draw Circles on specific face part
                for (x, y) in shape[i:j]:
                       cv2.circle(clone, (x, y), 1, (0, 0, 255), -1)
 
# extract the ROI of the face region as a separate image
                (x, y, w, h) = cv2.boundingRect(np.array([shape[i:j]]))
                roi = image[y:y + h, x:x + w]
                roi = imutils.resize(roi, width=250, inter=cv2.INTER_CUBIC)
 
# show the particular face part
                cv2.imshow("ROI", roi)
                cv2.imshow("Image", clone)
                cv2.waitKey(0)
 
# visualize all facial landmarks 
          for (x, y) in shape:
              cv2.circle(image, (x, y), 1, (0, 0, 255), -1)
              cv2.imshow("Image",image)
          cv2.waitKey(0)
