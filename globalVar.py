# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 10:40:54 2020

@author: cuixingxing
"""
#全局使用的变量
import torch
from torchvision import transforms as trans 
import os

embedding_size = 512
train_transform = trans.Compose([
        trans.RandomHorizontalFlip(),
        trans.ToTensor(),
        trans.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]) # [-1,1]范围内
    ])
test_transform = trans.Compose([
                    trans.ToTensor(),
                    trans.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
                ])
device = "cuda" if torch.cuda.is_available() else "cpu"

project_path = os.path.dirname(os.path.abspath(__file__))
