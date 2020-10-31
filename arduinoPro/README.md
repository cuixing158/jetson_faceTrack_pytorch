
# Overview
实现了通过端口控制arduino驱动舵机跟踪人脸位置的功能，总体思想为：在arduino控制器烧入C++控制指令，在python中实现了相关算法，通过serial端口控制库传入指令，从而完成了人脸跟踪的功能。


# arduino控制程序说明
- faceTrack/faceTrack.ino为arduino程序文件，用于控制水平和竖直两个舵机到目标位置，接收到的角度增量数据为控制条件。
- testServo/testServo.ino为简单测试舵机运动程序。
- audioRecog/audioRecog.ino为语音识别程序。
- audioRun/audioRun.ino为语音播报程序。
- CH08_Master/CH08_Master.ino为CH08型号蓝牙主属程序，手机发信号控制舵机。
- CH08_Slaver/CH08_Slaver.ino为CH08型号蓝牙从属程序，jetson/pc算法发信号到蓝牙HC08，然后HC08发信号到手机。

以上C++控制指令功能独立，供有需选择参考。<br>

**servoControl.py 为控制舵机的封装程序，板子上传`faceTrack.ino`即可在外部直接调用，`servoControl_test.py`为测试舵机运动程序。**

# How to use
1、利用arduino IDE烧入faceTrack/faceTrack.ino C++控制程序到arduino板子。<br>
2、如果使用舵机跟踪人脸位置，则必须检查舵机上的摄像头的端口序号，在`camera_faceRec.py`中务必设定好useCamType参数。<br>
3、在项目工作目录下打开终端，执行`python camera_faceRec.py --useServoTrack`<br>


**注意：烧入程序或python初始化arduino或串口监视器无法打开，是因为之前端口未释放，要及时释放close才可以使用。**

# Reference
语音识别第三方库arduino，[百度网盘](https://pan.baidu.com/s/1YCOE7Zze5N76XI0R8xnCqg )，提取码：c65t，[google drive](https://drive.google.com/file/d/1X-6dbvcS-ymhNuYnZYlYNC4d1zJ9-xdz/view?usp=sharing )<br>
[ld3320语音识别](https://www.waveshare.net/study/article-11-1.html )<br>
[Arduino-OpenCV](https://github.com/ankitdhall/Arduino-OpenCV-Human-Follower )<br>
[communicating-pyserial-arduino](https://stackoverflow.com/questions/49222435/trouble-communicating-with-pyserial-and-arduino )<br>
[faceDetectAndTrack](https://www.instructables.com/id/Face-detection-and-tracking-with-Arduino-and-OpenC/ )<br>