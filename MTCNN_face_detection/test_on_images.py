#!/usr/bin/env python
# coding: utf-8
# cuixingxing 2020.10.13 modify

import sys, os
sys.path.append(os.pardir)

import matplotlib.pyplot as plt
import time
from PIL import Image
import cv2
from src.detect import FaceDetector

frame = cv2.imread('./assets/office1.jpg')
detectImg = frame[:,:,::-1].copy()
detector = FaceDetector()

start = time.time()
bounding_boxes,scores,landmarks = detector.detect(detectImg)
print("time %.2f sec" % (time.time() - start))

# %% draw
for i in range(len(bounding_boxes)):
    cv2.rectangle(detectImg, (int(bounding_boxes[i][0]), int(bounding_boxes[i][1])),
                 (int(bounding_boxes[i][2]), int(bounding_boxes[i][3])), (255, 0, 0), 2)
    cv2.putText(detectImg,
        str(scores[i]),
        (int(bounding_boxes[i][0]), int(bounding_boxes[i][1])), 
        cv2.FONT_HERSHEY_SIMPLEX, 
        0.4,
        (0,255,0),
        1,
        cv2.LINE_AA)
    for j in range(5):
        cv2.circle(detectImg,(landmarks[i][j],landmarks[i][j+5]),2,(0,255,0),-1)
plt.figure()
plt.imshow(detectImg)
plt.savefig('../results/mtcnn.png', dpi=1000)


