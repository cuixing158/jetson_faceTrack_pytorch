#!/usr/bin/env python
# cuixingxing 2020.10.13 modify
import sys
import os
sys.path.append(os.pardir)

import cv2
import time
from src.detect import FaceDetector


if __name__ == "__main__":
    detector = FaceDetector()
    camera = cv2.VideoCapture(0)
    t1 = time.time()
    
    while True:
        _,frame = camera.read()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)        
        bounding_boxes,scores,landmarks = detector.detect(image,min_face_size=50,threshold=[0.6,0.6,0.6])

        for i in range(len(bounding_boxes)):
            cv2.rectangle(frame, (int(bounding_boxes[i][0]), int(bounding_boxes[i][1])),
                         (int(bounding_boxes[i][2]), int(bounding_boxes[i][3])), (255, 0, 0), 2)
            cv2.putText(frame,
                str(scores[i]),
                (int(bounding_boxes[i][0]), int(bounding_boxes[i][1])), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1,
                (0,255,0),
                1,
                cv2.LINE_AA)
            for j in range(5):
                cv2.circle(frame,(landmarks[i][j],landmarks[i][j+5]),2,(0,255,0),-1)

        t2= time.time()
        ti = t2-t1
        t1 = t2
        cv2.putText(frame,
                'fps:{:.2f}'.format(1/ti),
                (200,20), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1,
                (0,0,255),
                2,
                cv2.LINE_AA)
        enlarge = cv2.resize(frame, (0, 0),fx = 1,fy =1)  
        cv2.imshow('capture', enlarge)
        key = cv2.waitKey(1)
        if key ==27:
            break
        if key ==ord(' '):
            cv2.waitKey(0)