# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 18:04:54 2020
功能：完成1:N face identification训练+1：1 verfication验证测试
@author: cuixingxing
"""
import numpy as np
import datetime
import argparse
import os
import shutil

import torch
from torch.utils.data import Dataset, ConcatDataset, DataLoader
from torchvision.datasets import ImageFolder
from torch.nn import CrossEntropyLoss

from dataSets.verifactionDatasets import getPair
from net.model import Backbone,MobileFaceNet,Arcface,Am_softmax
from evaluate.verification import get_best_threshold
from globalVar import *

 
def schedule_lr(optimizer):
    for params in optimizer.param_groups:
        params['lr'] /= 10
        
def separate_bn_paras(modules):
    if not isinstance(modules, list):
        modules = [*modules.modules()]
    paras_only_bn = []
    paras_wo_bn = []
    for layer in modules:
        if 'model' in str(layer.__class__):
            continue
        if 'container' in str(layer.__class__):
            continue
        else:
            if 'batchnorm' in str(layer.__class__):
                paras_only_bn.extend([*layer.parameters()])
            else:
                paras_wo_bn.extend([*layer.parameters()])
    return paras_only_bn, paras_wo_bn

def train_model(args):
    # %% model
    if args.net_mode == 'mobilefacenet':
        model = MobileFaceNet(embedding_size = embedding_size).to(device)
    else:
        model = Backbone(num_layers=args.net_depth, drop_ratio=0.6, mode= args.net_mode).to(device)
    if args.resume:
        print('use resume model!\n')
        chkpt = torch.load('./save/net_last.pth', map_location=device)
        model.load_state_dict(chkpt['model'])
    
    # %% datasets
    milestones = [12,15,18]
    faceDataset = ImageFolder(args.train_data_root, train_transform)
    faceLoader = DataLoader(faceDataset, batch_size=args.batch_size, shuffle=True)
    class_num = faceDataset[-1][1] + 1  
    
    testdata = getPair(path = args.evaluate_data_root,img_size=(112,112))

    # %% train options
    head = Arcface(embedding_size=embedding_size, classnum=class_num).to(device) # head.kernel是学习的参数
    paras_only_bn, paras_wo_bn = separate_bn_paras(model)
    if args.net_mode == 'mobilefacenet':
        optimizer = torch.optim.SGD([
                            {'params': paras_wo_bn[:-1], 'weight_decay': 4e-5},
                            {'params': [paras_wo_bn[-1]] + [head.kernel], 'weight_decay': 4e-4},
                            {'params': paras_only_bn}
                        ], lr = args.lr, momentum = 0.9)
    else:
        optimizer = torch.optim.SGD([
                            {'params': paras_wo_bn + [head.kernel], 'weight_decay': 5e-4},
                            {'params': paras_only_bn}
                        ], lr = args.lr, momentum = 0.9)
    if args.resume:
        optimizer.load_state_dict(chkpt['optimizer'])
    # scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=40, verbose=True)

            
    # %% train
    iter_time = 0
    train_loss_list = []
    train_correct_num = 0
    ce_loss = CrossEntropyLoss()
    for epoch in range(args.epochs):
        if epoch == milestones[0]:
            schedule_lr(optimizer)
        if epoch == milestones[1]:
            schedule_lr(optimizer)      
        if epoch == milestones[2]:
            schedule_lr(optimizer) 
                                
        for i_batch,(imgs, labels) in enumerate(faceLoader):
            model.train()
            imgs = imgs.to(device)
            labels = labels.to(device)
            embeddings = model(imgs) # bs*512
            thetas = head(embeddings, labels) # bs*classnum
            _, inds = torch.max(thetas, 1)
            loss = ce_loss(thetas, labels)
            loss.backward()
            train_loss_list.append(loss.item())
            optimizer.step()
            optimizer.zero_grad()
            
            train_correct_num += torch.sum(inds==labels).item()
            acc = train_correct_num/((iter_time+1)*args.batch_size)
            iter_time+=1
            print('[{}]/The {}/{} iter ,lr:{:.7f},all train Loss: {:.6f},all train acc:{:.6f}, batchSize:{},model istrain:{}'.format(
                epoch,i_batch,len(faceLoader),optimizer.param_groups[0]['lr'],np.mean(train_loss_list),acc,args.batch_size ,model.training))
            
            # 保存模型
            if ((iter_time % 100 == 0) or (epoch==args.epochs-1)):  
                # 先save，防止验证过程中out of memory
                strTime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f_')
                save_filename = 'net_iter_{}_mode_{}_{}.pth'.format( iter_time,args.net_mode,strTime)
                save_path = os.path.join('./save',save_filename)
                
                chkpt = {'model':  model.state_dict(),
                     'optimizer': optimizer.state_dict()}
                torch.save(chkpt, save_path)
                shutil.copyfile(save_path,'./save/net_last.pth')

            # %%验证损失
            if ((iter_time % 1000 == 0) or (epoch==args.epochs-1)): 
                dataloader = torch.utils.data.DataLoader(testdata,
                                              batch_size=args.batch_size,
                                              num_workers=0, #min(os.cpu_count(), batch_size),
                                              shuffle=False,  # Shuffle=True unless rectangular training is used
                                              pin_memory=True)
                test_distances = []
                test_labels = []
                for ind,(batch1,batch2,issames) in enumerate(dataloader):
                    model.eval()
                    batch1 = batch1.to(device)
                    batch2 = batch2.to(device)
                    with torch.no_grad():
                        embeddings1 = model(batch1) # bs*512
                        embeddings2 = model(batch2) # bs*512
                    distances =  [torch.dot(x,y)/(torch.norm(x)*torch.norm(y)).item() for (x,y) in zip(embeddings1,embeddings2)] # (bs,)大小， 或者 torch.nn.functional.normalize(embeddings1,p=2,dim=1)比较欧式距离
                    test_distances.extend(distances)
                    test_labels.extend(issames)
                best_acc, best_threshold,_,_ = get_best_threshold(test_distances,test_labels)
                print('The {} iter , val acc:{:.2f}, best threshold:{:.2f}\n'.format(iter_time, best_acc,best_threshold))
   
    
# %% 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='for face verification')
    parser.add_argument( "--epochs", help="training epochs", default=20, type=int)
    parser.add_argument("--resume", help="use resume to train model",default=False,type=bool)
    parser.add_argument("--net_mode", help="which network, [ir, ir_se, mobilefacenet]",default='mobilefacenet', type=str)
    parser.add_argument("--net_depth", help="how many layers [50,100,152]", default=50, type=int)
    parser.add_argument('--lr',help='learning rate',default=1e-3, type=float)
    parser.add_argument("--batch_size", help="batch_size", default=24, type=int)
    parser.add_argument("--train_data_root", help="人脸数据root路径，该路径下每个文件夹存储每个人的人脸图像",default=r'E:\faces_emore\mysubTrainTemp', type=str)
    parser.add_argument("--evaluate_data_root", help="人脸评估数据root路径，该路径下有'same','diff'两个folder，每个folder下有若干对图像",
                        default=r'E:\faces_emore\evaluate_datasets\lfw_evaluate', type=str)
    args = parser.parse_args()
    print(args)
    # In the following, parameter ``scheduler`` is an LR scheduler object from
    # ``torch.optim.lr_scheduler``.
    train_model(args)