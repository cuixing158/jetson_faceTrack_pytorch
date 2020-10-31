# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 19:32:42 2020

@author: cuixingxing
"""
# 人脸图像数据库采集，采集的人脸图像保存在data\facebank文件夹下，每个人一个文件夹，文件夹名字代表姓名
import argparse
import os
import cv2
import numpy as np
import torch
from torchvision import transforms as trans

from net.model import Backbone, Arcface, MobileFaceNet, Am_softmax, l2_norm
from globalVar import *

def prepare_facebank(path, model):
    '''
    功能：对人脸数据库图像进行特征提取并保存,事先已经检测过人脸
    Parameters
    ----------
    path : str
        人脸采集图像数据库路径，该路径下每个文件夹为一个人的人脸图像，每个人的人脸图像若干张, 典型位置为：‘./data/facebank/’
    model : pytorch module类型
        人脸识别特征提取模型.
    Returns
    -------
    embeddings : torch.floattensor类型
        n*512大小
    names : list
        n,保存每个人的姓名.

    '''
    model.eval()
    embeddings =  []
    names = []
    allLists = os.listdir(path)
    folders = []
    for f in allLists:
        if os.path.isdir(os.path.join(path,f)):
            folders.append(os.path.join(path,f))
    assert len(folders),'人脸数据库为空！'
    
    with torch.no_grad():
        for folder in folders:
            imgs = os.listdir(folder)
            imgs = [x for x in imgs if x.endswith('.jpg') or x.endswith('.png')]
            _,name = os.path.split(folder)
            embs = []
            for faceimg in imgs:
                img = cv2.imread(os.path.join(folder,faceimg))
                img = cv2.resize(img,(112,112))
                img = img[:,:,::-1].copy()
                feature = model(test_transform(img).to(device).unsqueeze(0))# n*c*h*w， [0,1],rgb顺序, 1*512特征
                embs.append(feature) 
            if len(embs) == 0:
                continue
            embedding = torch.cat(embs).mean(dim=0,keepdim=True)
            embeddings.append(embedding)
            names.append(name)
    embeddings = torch.cat(embeddings,dim=0)
    names = np.array(names)
    torch.save(embeddings, os.path.join(path,'facebank.pth'))
    np.save(os.path.join(path,'names'), names) # 保存会自动加后缀.npy
    return embeddings, names
    
    

def load_facebank(path):
    '''
    功能：加载人脸数据库

    Parameters
    ----------
    path : str
        人脸采集图像数据库路径，该路径下每个文件夹为一个人的人脸图像，每个人的人脸图像若干张, 典型位置为：‘./data/facebank/’.

    Returns
    -------
    embeddings : TYPE
        DESCRIPTION.
    names : TYPE
        DESCRIPTION.

    '''
    embeddings = torch.load(os.path.join(path,'facebank.pth'))
    names = np.load(os.path.join(path,'names.npy'))
    return embeddings, names

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='for get faces')
    parser.add_argument("--faceRecModel",help="人脸识别模型选择，{mobilenetfacenet,Backbone}其一",default='mobilenetfacenet',type=str)
    parser.add_argument("--path",help="人脸数据库路径",default='./dataSets/facebank/',type = str)
    args = parser.parse_args()
    print(args)
    
    # %% 人脸数据库更新
    # embedding_out,names_out = load_facebank(args.path)
    if args.faceRecModel=='mobilenetfacenet':
        faceRecModel = MobileFaceNet(embedding_size = 512).to(device)
        faceRecModel.load_state_dict(torch.load('models/faceRecogPth/model_mobilefacenet.pth'))
    else:
        faceRecModel = Backbone(num_layers=50, drop_ratio=0.6, mode= 'ir_se').to(device)
        faceRecModel.load_state_dict(torch.load('models/faceRecogPth/model_ir_se50.pth'))
    
    
    faceRecModel.eval()
    embeddings, names = prepare_facebank(args.path,faceRecModel)
    
    print('人脸数据库已有{},embedding size:{}'.format(names,embeddings.shape))
    
    
