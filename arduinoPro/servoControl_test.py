# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 00:25:48 2020
功能：测试舵机运动，前提需要上传faceTrack/faceTrack.ino到arduino控制板
@author: cuixingxing
"""

import numpy as np
import serial
import time

class servoControl():
    def __init__(self,rangeHcam1 = 18,rangeVcam1 = 10,rangeHservo = 180,rangeVservo = 180,com='COM6',baudRate=9600):
        '''
        功能：初始化工作
        输入：
        Returns
        --------
        无
        '''
        self.arduino = serial.Serial(com, baudRate, bytesize=8, parity='N', stopbits=1, timeout=1)
        time.sleep(1) # waiting the initialization
    
        # %% 舵机和图像固有的一些参数设置
        rangeHcam1 = rangeHcam1;# 摄像头水平方向范围,度数, 也可以理解为调节灵敏度
        rangeVcam1 = rangeVcam1;# 摄像头竖直方向范围,度数, 也可以理解为调节灵敏度
        self.rangeHservo = rangeHservo;# 舵机水平方向范围
        self.rangeVservo = rangeVservo;# 舵机竖直方向范围
        self.ratioHorizontal = rangeHcam1/rangeHservo; # 相机与舵机水平方向转动比例
        self.ratioVertical = rangeVcam1/rangeVservo; # 相机与舵机竖直方向转动比例

    def controlServo(self,degree_str):
        self.arduino.write(degree_str.encode('utf-8'))
        
        
if __name__=='__main__':
    mySer = servoControl(rangeHcam1 = 18,rangeVcam1 = 10,rangeHservo = 180,rangeVservo = 180,com='COM6',baudRate=9600)
    
    degree_h = np.arange(0,180,1)
    degree_v = np.arange(0,180,1)
    
    for i,j in zip(degree_h,degree_v):
        degree_str = str(i)+","+str(j)+"\n"
        print(degree_str)
        mySer.controlServo(degree_str)
        time.sleep(1)
    
