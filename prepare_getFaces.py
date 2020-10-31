# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 10:40:54 2020
2020.10.13 Registered face,注册人脸
@author: cuixingxing
"""

import sys
sys.path.append('./MTCNN_face_detection')
sys.path.append('./fastFaceDetection_opencv_dnn')
sys.path.append('./utils')

import cv2
import os
import time
import datetime
import argparse
import numpy as np

from src.detect import FaceDetector #mtcnn
from fastFaceDetector import fastFaceDetector
from cameraJetson import gstreamer_pipeline,open_cam_usb

def getCameraFaces(args):
    # 初始化摄像头
    if args.useCamType==0: # jetson-csi
        cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    elif args.useCamType==1: # jetson usb
        cap = open_cam_usb(dev=1,width=1280,height=720)
    elif args.useCamType==2: # pc usb
        cap = cv2.VideoCapture(0+cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280 )
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720 )
    elif args.useCamType==3: # video file
        cap = cv2.VideoCapture(args.video_path)
    else:
        raise RuntimeError('input camera number is error!')
    
    # cap = cv2.VideoCapture(0)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    # cap.set(cv2.CAP_PROP_FOURCC, 0x32595559)
    foldername = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    save_path = 'dataSets/facebank/'+foldername
    if not os.path.exists(save_path):
        os.makedirs(save_path,exist_ok=True)
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    wri = cv2.VideoWriter(save_path+'/'+foldername+'.avi',fourcc, 30.0,
                          (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                           int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))),True)
    if args.useMTCNN:
        faceDetector = FaceDetector()
    else:
        faceDetector = fastFaceDetector() # ultra_face_ace_opencv_dnn
    t1= time.time()
    num = 0;
    loopnum=0

    while cap.isOpened():
        loopnum+=1
        # 采集一帧一帧的图像数据
        is_get,ori = cap.read()
        if not is_get:
            break
        draw = ori.copy()
        
        image = cv2.cvtColor(ori, cv2.COLOR_BGR2RGB)       
        if args.useMTCNN:
            bounding_boxes,scores,landmarks = faceDetector.detect(image,min_face_size=100,threshold=[0.6,0.6,0.6],nms_threshold=[0.5,0.5,0.5])
        else:
            bounding_boxes,_,scores = faceDetector.detect(image) # # ultra_face_ace_opencv_dnn
        
            
        for i in range(len(bounding_boxes)):
            ori_x1 = bounding_boxes[i,0]
            ori_y1 = bounding_boxes[i,1]
            ori_x2 = bounding_boxes[i,2]
            ori_y2 = bounding_boxes[i,3]
            # 人脸横向扩展，以竖直为基准,宽高一致
            x_middle = (ori_x2+ori_x1)/2
            h = ori_y2-ori_y1
            x1 = x_middle-h/2
            x2 = x_middle+h/2
            y1 = ori_y1
            y2 = ori_y2
            
            x1 = int(0) if x1<0 else int(x1)
            y1 = int(0) if y1<0 else int(y1)
            x2 = ori.shape[1] if x2>ori.shape[1] else int(x2)
            y2 = ori.shape[0] if y2>ori.shape[0] else int(y2)
            
            cv2.rectangle(draw, (x1,y1),
                          (x2,y2), (255, 0, 0), 2)
            cv2.putText(draw,
                'score:{:.2f}'.format(scores[i]),
                (int(bounding_boxes[i][0]), int(bounding_boxes[i][1])), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1,
                (0,255,0),
                1,
                cv2.LINE_AA)
            # for j in range(5):
            #     cv2.circle(draw,(landmarks[i][j],landmarks[i][j+5]),2,(0,255,0),-1)

        t2= time.time()
        ti = t2-t1
        cv2.putText(draw,
                'fps:{:.2f}'.format(loopnum/ti),
                (200,20), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1,
                (0,0,255),
                2,
                cv2.LINE_AA)

        wri.write(ori)
        cv2.imshow('capture', draw)
        key = cv2.waitKey(1)
        if key ==27:
            break
        if key ==ord(' '):# 按空格键拍照
            if len(bounding_boxes):
                num+=1
                warped_face = ori[int(y1):int(y2),int(x1):int(x2),:].copy()
                cv2.imwrite(os.path.join(save_path,str(num)+datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')+'.jpg'), warped_face)
                #cv2.imwrite(os.path.join(save_path,str(num)+'.png'), ori)
    wri.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='for get faces')
    parser.add_argument("--useCamType",help="使用摄像头类型，0，1，2,3分别对应jetson csi、jetson USB camera、pc usb camera,本地视频",default=3,type = int)
    parser.add_argument("--video_path",help="useCamType为3时，需要指定此选项视频路径",default=r"./dataSets/facebank/cuixingxing/20201014101140840253.avi",type=str)
    parser.add_argument("--useMTCNN",help="是否使用MTCNN检测人脸，否则用轻量级的人脸检测器",action='store_true')
    args = parser.parse_args()
    print(args)
    getCameraFaces(args)

