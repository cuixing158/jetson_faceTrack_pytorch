# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 14:51:42 2020
功能：输入人脸位置和原始图像宽高，控制舵机跟踪人脸位置
@author: cuixingxing
"""
import time
import numpy as np
import serial

class servoControl():
    def __init__(self,com='COM6',baudRate=9600,rangeHcam1 = 18,rangeVcam1 = 10,rangeHservo = 180,rangeVservo = 180):
        '''
        功能：初始化工作
        输入：
        Returns
        --------
        无
        '''
        self.arduino = serial.Serial(com, baudRate)
        time.sleep(1) # 等待1秒
    
        # %% 舵机和图像固有的一些参数设置
        rangeHcam1 = rangeHcam1;# 摄像头水平方向范围,度数, 也可以理解为调节灵敏度
        rangeVcam1 = rangeVcam1;# 摄像头竖直方向范围,度数, 也可以理解为调节灵敏度
        self.rangeHservo = rangeHservo;# 舵机水平方向范围
        self.rangeVservo = rangeVservo;# 舵机竖直方向范围
        self.ratioHorizontal = rangeHcam1/rangeHservo; # 相机与舵机水平方向转动比例
        self.ratioVertical = rangeVcam1/rangeVservo; # 相机与舵机竖直方向转动比例

    def controlServo(self,max_bounding_box, ori_H,ori_W):
        '''
        功能：由检测到的人脸，控制舵机跟踪最大的人脸位置
        输入：
        max_bounding_box： np.array类型，1*4大小，保存形式为[x1,y1,x2,y2]顶点原图坐标
        ori_H: 原始图像的高
        ori_W: 原始图像的宽
        Returns
        --------
        无
        '''
        # 输入图像的中心坐标
        imgCenter = [ori_W/2,ori_H/2]; # 图像固有中心坐标，如[640/2,480/2]
        bbox = [max_bounding_box[0,0],
                max_bounding_box[0,1],
                max_bounding_box[0,2]-max_bounding_box[0,0],
                max_bounding_box[0,3]-max_bounding_box[0,1]] # [x,y,w,h]
        
        # %% 调整角度，假设相机无畸变,对读入arduino板子上舵机的位置相对较困难，故把相对角度传递到arduino板子程序里面,代替matlab中函数readPosition()功能
        center = [bbox[0]+bbox[2]/2,bbox[1]+bbox[3]/2]; # [x,y]
        if center[0]<=imgCenter[0]: # 人脸在图像左边
            distance_x = imgCenter[0]-center[0];
            delta_degree_x = (distance_x/ori_W)*self.ratioHorizontal; # 传递到arduino板子上,即当前水平舵机上角度需要相加的量
        else:
            distance_x = center[0]-imgCenter[0];
            delta_degree_x = -(distance_x/ori_W)*self.ratioHorizontal;# 传递到arduino板子上,即当前水平舵机上角度需要相加的量

        if center[1]<=imgCenter[1]: # 人脸在图像上方
            distance_y = imgCenter[1]-center[1];
            delta_degree_y = (distance_y/ori_H)*self.ratioVertical;# 传递到arduino板子上,即当前竖直舵机上角度需要相加的量
        else:
            distance_y = center[1]-imgCenter[1];
            delta_degree_y = -(distance_y/ori_H)*self.ratioVertical;

        # %% 写到arduino板子里的相对角度,单位：度数
        wriInfo = str(round(delta_degree_x*self.rangeHservo))+","+str(round(delta_degree_y*self.rangeVservo))+"\n" # 如："22,15"
        print("wriInfo:{}".format(wriInfo))
        
        self.arduino.write(wriInfo.encode('utf-8')) # 
        
        inComing = self.arduino.readline().decode()
        print('解码serial为：{}\n'.format(inComing))   ## Debug
      
        
        
if __name__=='__main__':
    # 只需初始化一次
    myServo = servoControl(com='/dev/ttyACM0',baudRate=9600,rangeHcam1 = 18,rangeVcam1 = 10,rangeHservo = 180,rangeVservo = 180)
    
    # 可多次循环执行
    max_bounding_box = np.array([[10,10,120,120]])
    myServo.controlServo(max_bounding_box,ori_H=480,ori_W=640)
    
    # 释放端口占用
    myServo.arduino.close()

        
        
