# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 10:40:54 2020
evaluate verifacation accuracy

@author: cuixingxing
"""
import numpy as np

def get_best_threshold(test_distances,test_labels):
    '''
    功能：获取1：1比对，余弦距离最高准确率情况下的最佳阈值，[0,1]范围内
    Reference: https://ww2.mathworks.cn/help/stats/perfcurve.html
    Parameters
    ----------
    test_distances : list
        里面每项存储余弦距离.
    test_labels : list
        里面每项存储真值，相似就是1，否则为0.

    Returns
    -------
    best_acc, best_threshold, tpr,fpr.
    
    '''
    candiateS = np.linspace(0,1,50)
    best_acc = 0.
    best_threshold = 0.5
    tpr = []
    fpr = []
    for threshold in candiateS:
        predict_issame = np.array(test_distances)>threshold
        true_labels = np.array(test_labels).astype('bool')
        correct_nums = np.sum(predict_issame==true_labels)
        val_acc = correct_nums/len(test_labels)
        if val_acc>=best_acc:
            best_acc = val_acc
            best_threshold = threshold
        tpr.append(np.sum(predict_issame & true_labels)/np.sum(true_labels)) # True positive rate, or sensitivity, or recall. 参考：https://ww2.mathworks.cn/help/stats/perfcurve.html
        fpr.append(np.sum(predict_issame & ~true_labels)/np.sum(~true_labels)) # False positive rate, or fallout, or 1 – specificity. 参考：https://ww2.mathworks.cn/help/stats/perfcurve.html
    return best_acc, best_threshold, tpr,fpr
    