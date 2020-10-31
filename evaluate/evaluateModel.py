# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 17:51:41 2020

@author: cuixingxing
"""
import sys
sys.path.append('..')

import numpy as np
import torch
import torchvision.datasets
from torch.utils.data import Dataset, ConcatDataset, DataLoader

from verifacation import get_best_threshold
from net.model import Backbone,MobileFaceNet,Arcface,Am_softmax
from dataSets.verifactionDatasets import getPair
from globalVar import * # device


testdatapath = r'E:\faces_emore\evaluate_datasets\agedb_evaluate'
modlename ='mobilefacenet'
modelweights = r'../models/faceRecogPth/model_mobilefacenet.pth'
embedding_size=512

testdata = getPair(path = testdatapath,img_size=(112,112))
dataloader = torch.utils.data.DataLoader(testdata,
                                         batch_size=12,
                                         num_workers=0, #min(os.cpu_count(), batch_size),
                                         shuffle=False,  # Shuffle=True unless rectangular training is used
                                         pin_memory=True)

if modlename == 'mobilefacenet':
    model = MobileFaceNet(embedding_size = embedding_size).to(device)
else:
    model = Backbone(num_layers=args.net_depth, drop_ratio=0.6, mode= args.net_mode).to(device)
chkpt = torch.load(modelweights, map_location=device)
model.load_state_dict(chkpt)

model.eval()        
test_distances = []
test_labels = []
for ind,(batch1,batch2,issames) in enumerate(dataloader):
    batch1 = batch1.to(device)
    batch2 = batch2.to(device)
    with torch.no_grad():
        embeddings1 = model(batch1) # bs*512
        embeddings2 = model(batch2) # bs*512
        distances =  [torch.dot(x,y)/(torch.norm(x)*torch.norm(y)).item() for (x,y) in zip(embeddings1,embeddings2)] # (bs,)大小， 或者 torch.nn.functional.normalize(embeddings1,p=2,dim=1)比较欧式距离
        test_distances.extend(distances)
        test_labels.extend(issames)
model_acc, best_threshold,tpr,fpr = get_best_threshold(test_distances,test_labels)
print('model acc:{:.2f}, best threshold:{:.2f}，tpr:{},fpr:{}\n'.format( model_acc,best_threshold,tpr,fpr))


