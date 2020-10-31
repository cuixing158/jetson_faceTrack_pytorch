# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 18:04:54 2020
功能：定义1：1验证数据集,用于inference
@author: cuixingxing
"""
import sys
sys.path.append('..')
from globalVar import * # test_transform

import cv2
import os
import torch
import numpy as np
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from torchvision import datasets
import torchvision.transforms as transforms
import math
import matplotlib.pyplot as plt


def cv2_loader_Totensor(path):  
    img = cv2.imdecode(np.fromfile(path,dtype=np.uint8),-1)
    if img is None:
        raise RuntimeError('image is None')
    mat = img[:,:,::-1].copy() # H*W*C RGB,注意必须copy后才可以传进torch中
#    print('mat shape:{0},mat type:{1}'.format(mat.shape,mat.dtype))
    mat_tensor = test_transform(mat)
    return mat_tensor # c*h*w  RGB顺序， [-1,1]范围

class getPair(Dataset):
    def __init__(self,path = r'E:\faces_emore\evaluate_datasets\lfw_evaluate',img_size=(112,112)):
        """
        固定的评估1：1数据集,path路径下必须要有same,diff两个文件夹，其中每个文件夹下分别有若干对图片，2张图片为一个子文件夹，名字无要求
        """
        same_folders = os.path.join(path,'same')
        diff_folders = os.path.join(path,'diff')
        if not os.path.exists(same_folders) or not os.path.exists(diff_folders):
            raise RuntimeError("Invalid folders:{}!".format(path))
        
        self.same_full_folders = [os.path.join(same_folders,x) for x in os.listdir(same_folders)]
        self.diff_full_folders = [os.path.join(diff_folders,x) for x in os.listdir(diff_folders)]
        
        
    def __getitem__(self,index):
        if index<len(self.same_full_folders):
            image_pair_folder = self.same_full_folders[index]
            img_pairs_list = os.listdir(image_pair_folder)
            is_same = 1
        else:
            image_pair_folder = self.diff_full_folders[index-len(self.same_full_folders)]
            img_pairs_list = os.listdir(image_pair_folder)
            is_same = 0
        assert len(img_pairs_list)==2,'this folder {} not pair images!'.format(image_pair_folder)
        
        img1 = cv2_loader_Totensor(os.path.join(image_pair_folder,img_pairs_list[0]))
        img2 = cv2_loader_Totensor(os.path.join(image_pair_folder,img_pairs_list[1]))
        return (img1,img2,is_same)
        
    def __len__(self):
        return len(self.same_full_folders)+len(self.diff_full_folders) 
    

if __name__ =='__main__':
    mydata = getPair(path = r'E:\faces_emore\evaluate_datasets\cfp_fp_evaluate',img_size=(112,112))
    dataloader = torch.utils.data.DataLoader(mydata,
                                              batch_size=9,
                                              num_workers=0, #min(os.cpu_count(), batch_size),
                                              shuffle=True,  # Shuffle=True unless rectangular training is used
                                              pin_memory=True)
    
    for ind,data in enumerate(dataloader):
        img1 = data[0].numpy().transpose(2,3,1,0) # h*w*c*n
        img2 = data[1].numpy().transpose(2,3,1,0)
        labels = ['same' if x==1 else 'diff'  for x in data[2]]
        
        
        # %% show image pair ,预览查看数据
        imgs = np.concatenate((img1,img2),1) #h*2w*c*n numpy 数组
        n = math.ceil(math.sqrt(imgs.shape[-1]))
        
        fig = plt.figure(figsize=(10,10))
        for i in range(len(labels)):
            currentImg = imgs[...,i] # h*w*c
            currentLabel = labels[i]
            plt.subplot(n,n,i+1).imshow((currentImg+1)/2)
            plt.title(currentLabel)
        plt.show()
        # fig.savefig(str(i)+'.jpg', dpi=400)
        # plt.close()
        if ind==0:
            break

