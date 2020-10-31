# 本脚本仅适合在jetson平台上用opencv-python采集并显示图像，适用csi或者usb摄像头
# 参考1：https://github.com/JetsonHacksNano/CSI-Camera
#参考2：https://gist.github.com/jkjung-avt/86b60a7723b97da19f7bfa3cb7d2690e

# MIT License
# Copyright (c) 2019 JetsonHacks
# See license
# Using a CSI camera (such as the Raspberry Pi Version 2) connected to a
# NVIDIA Jetson Nano Developer Kit using OpenCV
# Drivers for the camera and OpenCV are included in the base image

import argparse
import cv2
import time
# gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
# Defaults to 1280x720 @ 60fps
# Flip the image by setting the flip_method (most common values: 0 and 2)
# display_width and display_height determine the size of the window on the screen


def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=60,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


def show_csi_camera():
    # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
    print(gstreamer_pipeline(flip_method=0))
    cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    t1 = time.time()
    numframe = 0
    if cap.isOpened():
        window_handle = cv2.namedWindow("CSI Camera", cv2.WINDOW_AUTOSIZE)
        # Window
        while cv2.getWindowProperty("CSI Camera", 0) >= 0:
            numframe+=1
            ret_val, img = cap.read()
            
            # Stop the program on the ESC key
            t2 = time.time()
            Elapsetime = t2-t1
            fps = numframe/Elapsetime
            cv2.putText(img,"fps:{:.1f}".format(fps),(200,50),0,1,(0,0,255),2)
            cv2.imshow("CSI Camera", img)
            keyCode = cv2.waitKey(1) 
            if keyCode == 27:
                break
        cap.release()
        cv2.destroyAllWindows()
    else:
        print("Unable to open camera")

def open_cam_usb(dev=1, width=1280, height=720):
    # 如果你是用USB 网络摄像头(I 使用的是罗技 C920)，这个USB摄像头通常安装在 /dev/video1, 因为 Jetson 板载摄像头已经占用了 /dev/video0.
    # 参考：https://blog.csdn.net/zong596568821xp/article/details/80306987?utm_medium=distribute.pc_relevant_t0.none-task-blog-BlogCommendFromMachineLearnPai2-1.channel_param&depth_1-utm_source=distribute.pc_relevant_t0.none-task-blog-BlogCommendFromMachineLearnPai2-1.channel_param
    gst_str = ('v4l2src device=/dev/video{} ! '
               'video/x-raw, width=(int){}, height=(int){} ! '
               'videoconvert ! appsink').format(dev, width, height)
    cap = cv2.VideoCapture(gst_str,cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        print("use /dev/video"+str(dev)+" API.")
        cap = cv2.VideoCapture("/dev/video"+str(dev))
    return cap


def show_usb_camera(dev=1):
     # inital camera
    cap = open_cam_usb(dev=dev,width=1280,height=720)
    t1 = time.time()
    numframe = 0
    while cap.isOpened():
        numframe+=1
        _,frame = cap.read()

        # Stop the program on the ESC key
        t2 = time.time()
        Elapsetime = t2-t1
        fps = numframe/Elapsetime
        cv2.putText(frame,"fps:{:.1f}".format(fps),(200,50),0,1,(0,0,255),2)
        cv2.imshow('jetson usb camera'+str(dev), frame)
        key = cv2.waitKey(1)
        if key ==27:
            break
            cap.release()
        if key ==ord(' '):
            cv2.waitKey(0)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='use all kinds of camera')
    parser.add_argument("--camera_num",help="jetson USB camera choose number,{0,1,2}分别为csi,usb1,usb2",default=1,type = int)
    args = parser.parse_args()
    
    if args.camera_num==0:
        show_csi_camera()
    else:
        show_usb_camera(dev=args.camera_num)

