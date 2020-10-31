import sys
sys.path.append('./MTCNN_face_detection')
sys.path.append('./fastFaceDetection_opencv_dnn')
sys.path.append('./utils')

import time
import datetime
import cv2
import argparse
import torch
import numpy as np

from net.model import Backbone, Arcface, MobileFaceNet, Am_softmax, l2_norm
from prepare_faceDatabase import load_facebank
from src.detect import FaceDetector
from fastFaceDetector import fastFaceDetector
from cameraJetson import gstreamer_pipeline,open_cam_usb
from globalVar import *

from arduinoPro.servoControl import servoControl


def classifyFace(img,model,embedingF_Database,names_Database):
    '''
    功能：提取512维特征，人脸识别，与数据库中的人脸计算欧氏距离进行比较
    输入：
    img： 输入的opencv 摄像头采集的单张人脸图像，numpy.array类型，h*w*c，[0,255]
    model: 人脸识别模型
    embedingF_Database: 数据库存储的人脸特征，N*512大小
    names_Database: 数据库存储的姓名，大小为N

    Returns
    -------
    recName: str类型，识别人的姓名
    score: float类型，最近的人脸距离
    '''
    img = cv2.resize(img,(112,112))
    img = img[:,:,::-1].copy()
    feature = model(test_transform(img).to(device).unsqueeze(0))# n*c*h*w， [0,1],rgb顺序, 输出1*512特征
    
    feature = torch.squeeze(feature)
    scores =  [torch.dot(feature,x)/(torch.norm(feature)*torch.norm(x)) for x in embedingF_Database]
    scores = torch.tensor(scores)

    score,idx = torch.max(scores,dim=0)
    return score,names_Database[idx]
   
def cameraRec(args):
    if args.useServoTrack:
        controlObj = servoControl(com=args.com,baudRate=9600,rangeHcam1 = 18,rangeVcam1 = 10,rangeHservo = 180,rangeVservo = 180)
    path = args.path
    if args.useMTCNN:
        faceDetector = FaceDetector() # mtcnn
    else:
        faceDetector = fastFaceDetector(threshold=0.3,nms_threshold = 0.5,width = 320,height = 240) # ultra_face_ace_opencv_dnn 
    
    if args.faceRecModel == 'mobilenetfacenet':
        faceRecModel = MobileFaceNet(embedding_size = 512).to(device)
        faceRecModel.load_state_dict(torch.load('models/faceRecogPth/model_mobilefacenet.pth'))
    else:
        faceRecModel = Backbone(num_layers=50, drop_ratio=0.6, mode= 'ir_se').to(device)
        faceRecModel.load_state_dict(torch.load('models/faceRecogPth/model_ir_se50.pth'))
    faceRecModel.eval()
    
    if args.useAudio:
        from playAudio import AudioFile
        player = AudioFile("dataSets/demo.wav")
        
    # load face embedding features
    embedding_out,names_out = load_facebank(path)
    print('人脸数据库已有{},embedding size:{}'.format(names_out,embedding_out.shape))


    # 初始化摄像头
    if (args.usejetsonCam and (args.camnum==0)): # jetson-csi
        cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
        print("use jeton-csi camera!")
    elif (args.usejetsonCam and args.camnum): # jetson usb
        cap = open_cam_usb(dev=args.camnum,width=1280,height=720)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280 )
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720 )
        print("use jetson usb camera,camera num:"+str(args.camnum))
    elif args.usepcCam: # pc usb
        cap = cv2.VideoCapture(args.camnum+cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280 )
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720 )
        print("use pc usb camera,camera num:"+str(args.camnum))
    elif args.usepcVideo: # video file
        cap = cv2.VideoCapture(args.video_path)
        print("use video file!")
    else:
        raise RuntimeError('input  error!')
   
    # 
    if args.save:
        video_writer = cv2.VideoWriter('results/'+datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')+'.avi', cv2.VideoWriter_fourcc(*'XVID'), 20, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        
    print('start recognitize...')
    num = 0
    t1 = time.time()
    while cap.isOpened():
        num+=1
        isget,ori = cap.read()
        if not isget:
            print("Can't get camera image! please check args.useCamType!")
            break
        draw = ori.copy()
        image = cv2.cvtColor(ori, cv2.COLOR_BGR2RGB)
        if args.useMTCNN:
            bounding_boxes,scores,landmarks = faceDetector.detect(image,min_face_size=100,threshold=[0.6,0.6,0.6],nms_threshold=[0.5,0.5,0.5]) # mtcnn
        else:
            bounding_boxes,_,scores = faceDetector.detect(image) # # ultra_face_ace_opencv_dnn
        bounding_boxes = bounding_boxes.astype(int)
        
        max_bounding_box = np.empty((0,4),dtype='int')# x1,y1,x2,y2方式
        max_area=0
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
            
            if (y2-y1)*(x2-x1)>max_area:
                max_area = (y2-y1)*(x2-x1)
                max_bounding_box = np.array([x1,y1,x2,y2]).reshape((1,4)) # 保证shape为(1,4)二维矩阵
                
            # 人脸识别
            faceImg = ori[y1:y2,x1:x2,:].copy()
            t_s = time.time()
            score,predictname = classifyFace(faceImg,faceRecModel,embedding_out,names_out)
            t_e = time.time()
            # print("extract face feature predict take time:{:.2f} ms".format((t_e-t_s)*1000)) # GTX1050-gpu 耗时8ms左右
            if score<args.threshold:
                predictname = 'unknow'
                score = torch.tensor(-1.0)
            cv2.rectangle(draw, (x1,y1),(x2,y2), (255, 0, 0), 2)
            cv2.putText(draw,
                        predictname+','+'{:.2f}'.format(score.item()),
                        (x1,y1), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7,
                        (0,255,0),
                        1,
                        cv2.LINE_AA)
             
            # %% another way to play audio
            if args.useAudio: 
                player.play()
        
        if args.useServoTrack and len(max_bounding_box):
            # print(max_bounding_box)
            controlObj.controlServo(max_bounding_box,ori.shape[0],ori.shape[1])
            
        # %% show 
        t2= time.time()
        ti = t2-t1
        cv2.putText(draw,
                'fps:{:.2f}'.format(num/ti),
                (200,20), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1,
                (0,0,255),
                2,
                cv2.LINE_AA)
        #print('fps:{:.2f}'.format(1/ti))
        cv2.imshow('face recognition', draw)
        key = cv2.waitKey(1)
        if key ==27:
            cv2.destroyAllWindows()
            break
            
        if key ==ord(' '):
            cv2.waitKey(0)
        if args.save:
            video_writer.write(draw)
    if args.save:
        video_writer.release()
    if args.useServoTrack:
        controlObj.arduino.close() # 释放端口占用
    if args.useAudio:
        player.close()

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='for face identification')
    parser.add_argument("--camnum",help="使用摄像头序号，0，1，2,...，jetson上有csi摄像头为0，usb随后排;pc上摄像头序号从0开始排",default=0,type = int) 
    parser.add_argument("--com",help="硬件设备端口，如接arduino，win上为COM*，ubuntu上为/dev/ttyACM*",default="/dev/ttyACM0",type=str)

    parser.add_argument("--usejetsonCam",help="是否取用jetson camera",action='store_true')
    parser.add_argument("--usepcCam",help="是否取用pc camera",action='store_true')
    parser.add_argument("--usepcVideo",help="是否取用视频文件输入",action='store_true')
    parser.add_argument("--useServoTrack",help="是否取用舵机跟踪最大人脸位置",action='store_true')

    parser.add_argument("--useAudio",help="是否语音播报",action='store_true')
    parser.add_argument("--video_path",help="usepcVideo为true时，需要指定此选项视频路径",default="",type=str)
    parser.add_argument("--faceRecModel",help="人脸识别模型选择，{mobilenetfacenet,Backbone}其一",default='mobilenetfacenet',type=str)
    parser.add_argument("--useMTCNN",help="是否使用MTCNN检测人脸，否则用轻量级的人脸检测器",action='store_true')
    parser.add_argument("--path",help="人脸数据库路径",default='./dataSets/facebank/',type = str)
    parser.add_argument('--threshold',help='threshold to decide identical faces',default=0.5, type=float)
    parser.add_argument("--save", help="whether save video",action="store_true")
    args = parser.parse_args()
    print(args)
    cameraRec(args)
    
   
