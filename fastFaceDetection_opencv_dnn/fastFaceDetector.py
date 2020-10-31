# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:36:42 2020
轻量级的人脸检测器，参考：https://github.com/Linzaer/Ultra-Light-Fast-Generic-Face-Detector-1MB
@author: cuixingxing modify
"""
import sys
sys.path.append('..')

from math import ceil
import cv2
import time
import numpy as np
import os

from globalVar import project_path

class fastFaceDetector():
    def __init__(self,threshold=0.8,nms_threshold = 0.5,width = 320,height = 240):
        # LOAD MODELS
        model_path = os.path.join(project_path,"./models/faceDetectOnnx/version-slim-320_simplified.onnx")
        if not os.path.exists(model_path):
            raise RuntimeError(model_path +" not exist!")
        self.model = cv2.dnn.readNetFromONNX(model_path)  # onnx version
    # self.model = dnn.readNetFromCaffe("../models/faceDetectCaffe/RFB-320/RFB-320.prototxt", "../models/faceDetectCaffe/RFB-320/RFB-320.caffemodel")  # caffe model converted from onnx;
        if cv2.cuda.getCudaEnabledDeviceCount() > 0:
            print("use opencv-cuda inference face detector!")
            self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.model.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

        self.threshold = threshold
        self.nms_threshold = nms_threshold
        self.width = width #输入到检测网络的宽
        self.height = height #输入到检测网络的高
        
        self.image_std = 128.0
        self.image_mean = [127, 127, 127]
        self.center_variance = 0.1
        self.size_variance = 0.2
        self.min_boxes = [[10.0, 16.0, 24.0], [32.0, 48.0], [64.0, 96.0], [128.0, 192.0, 256.0]]
        self.strides = [8.0, 16.0, 32.0, 64.0]
        
        self.priors = self._define_img_size([self.width,self.height])
        
    def _define_img_size(self,image_size):
        shrinkage_list = []
        feature_map_w_h_list = []
        for size in image_size:
            feature_map = [int(ceil(size / stride)) for stride in self.strides]
            feature_map_w_h_list.append(feature_map)
    
        for i in range(0, len(image_size)):
            shrinkage_list.append(self.strides)
        priors = self._generate_priors(feature_map_w_h_list, shrinkage_list, image_size, self.min_boxes)
        return priors
    
    def _generate_priors(self,feature_map_list, shrinkage_list, image_size, min_boxes):
        priors = []
        for index in range(0, len(feature_map_list[0])):
            scale_w = image_size[0] / shrinkage_list[0][index]
            scale_h = image_size[1] / shrinkage_list[1][index]
            for j in range(0, feature_map_list[1][index]):
                for i in range(0, feature_map_list[0][index]):
                    x_center = (i + 0.5) / scale_w
                    y_center = (j + 0.5) / scale_h
    
                    for min_box in min_boxes[index]:
                        w = min_box / image_size[0]
                        h = min_box / image_size[1]
                        priors.append([
                            x_center,
                            y_center,
                            w,
                            h
                        ])
        # print("priors nums:{}".format(len(priors)))
        return np.clip(priors, 0.0, 1.0)

    def _predict(self,width, height, confidences, boxes, prob_threshold, iou_threshold=0.3, top_k=-1):
        boxes = boxes[0]
        confidences = confidences[0]
        picked_box_probs = []
        picked_labels = []
        for class_index in range(1, confidences.shape[1]):
            probs = confidences[:, class_index]
            mask = probs > prob_threshold
            probs = probs[mask]
            if probs.shape[0] == 0:
                continue
            subset_boxes = boxes[mask, :]
            box_probs = np.concatenate([subset_boxes, probs.reshape(-1, 1)], axis=1)
            box_probs = self._hard_nms(box_probs,
                                 iou_threshold=iou_threshold,
                                 top_k=top_k,
                                 )
            picked_box_probs.append(box_probs)
            picked_labels.extend([class_index] * box_probs.shape[0])
        if not picked_box_probs:
            return np.array([]), np.array([]), np.array([])
        picked_box_probs = np.concatenate(picked_box_probs)
        picked_box_probs[:, 0] *= width
        picked_box_probs[:, 1] *= height
        picked_box_probs[:, 2] *= width
        picked_box_probs[:, 3] *= height
        return picked_box_probs[:, :4].astype(np.int32), np.array(picked_labels), picked_box_probs[:, 4]

    def _hard_nms(self,box_scores, iou_threshold, top_k=-1, candidate_size=200):
        scores = box_scores[:, -1]
        boxes = box_scores[:, :-1]
        picked = []
        indexes = np.argsort(scores)
        indexes = indexes[-candidate_size:]
        while len(indexes) > 0:
            current = indexes[-1]
            picked.append(current)
            if 0 < top_k == len(picked) or len(indexes) == 1:
                break
            current_box = boxes[current, :]
            indexes = indexes[:-1]
            rest_boxes = boxes[indexes, :]
            iou = self._iou_of(
                rest_boxes,
                np.expand_dims(current_box, axis=0),
            )
            indexes = indexes[iou <= iou_threshold]
        return box_scores[picked, :]


    def _area_of(self,left_top, right_bottom):
        hw = np.clip(right_bottom - left_top, 0.0, None)
        return hw[..., 0] * hw[..., 1]
    
    
    def _iou_of(self,boxes0, boxes1, eps=1e-5):
        overlap_left_top = np.maximum(boxes0[..., :2], boxes1[..., :2])
        overlap_right_bottom = np.minimum(boxes0[..., 2:], boxes1[..., 2:])
    
        overlap_area = self._area_of(overlap_left_top, overlap_right_bottom)
        area0 = self._area_of(boxes0[..., :2], boxes0[..., 2:])
        area1 = self._area_of(boxes1[..., :2], boxes1[..., 2:])
        return overlap_area / (area0 + area1 - overlap_area + eps)

    
    def _convert_locations_to_boxes(self,locations, priors, center_variance,
                                   size_variance):
        if len(priors.shape) + 1 == len(locations.shape):
            priors = np.expand_dims(priors, 0)
        return np.concatenate([
            locations[..., :2] * center_variance * priors[..., 2:] + priors[..., :2],
            np.exp(locations[..., 2:] * size_variance) * priors[..., 2:]
        ], axis=len(locations.shape) - 1)
    
    
    def _center_form_to_corner_form(self,locations):
        return np.concatenate([locations[..., :2] - locations[..., 2:] / 2,
                               locations[..., :2] + locations[..., 2:] / 2], len(locations.shape) - 1)

    def detect(self, img):
        """[summary]

        Arguments:
            img : [0,255] RGB numpy，h*w*c图像

        Returns:
            bboxes {float} -- [N,4],形如[x1,y1,x2,y2]顶点坐标
            scores  {float} -- [N]
        """
        ori_width = img.shape[1]
        ori_height = img.shape[0]
        img = cv2.resize(img, (self.width, self.height))
        self.model.setInput(cv2.dnn.blobFromImage(img, 1.0 / self.image_std, (self.width, self.height), self.image_mean))
        boxes, scores = self.model.forward(["boxes", "scores"])
        boxes = np.expand_dims(np.reshape(boxes, (-1, 4)), axis=0)
        scores = np.expand_dims(np.reshape(scores, (-1, 2)), axis=0)
        boxes = self._convert_locations_to_boxes(boxes, self.priors, self.center_variance, self.size_variance)
        boxes = self._center_form_to_corner_form(boxes)
        boxes, labels, scores = self._predict(ori_width, ori_height, scores, boxes, self.threshold)
        return boxes,labels,scores
    
if __name__ == '__main__':
    faceDetector = fastFaceDetector(threshold=0.4,nms_threshold = 0.5,width = 320,height = 240)
    img_ori = cv2.imread(r'../dataSets/testImg/1.jpg')
    
    cap = cv2.VideoCapture(0+cv2.CAP_DSHOW)
    t1 = time.time()
    num = 0
    while cap.isOpened():
        num+=1
        isget,ori = cap.read()
        # ori = img_ori.copy()
        image = cv2.cvtColor(ori, cv2.COLOR_BGR2RGB)
        boxes,labels,scores = faceDetector.detect(image)
    
        for i in range(boxes.shape[0]):
            cv2.rectangle(ori, (boxes[i][0], boxes[i][1]), (boxes[i][2], boxes[i][3]), (0, 255, 0), 1)
            # cv2.putText(ori,
            #     'score:{:.2f}'.format(scores[i]),
            #     (int(boxes[i][0]), int(boxes[i][1])), 
            #     cv2.FONT_HERSHEY_SIMPLEX, 
            #     0.5,
            #     (0,255,0),
            #     1,
            #     cv2.LINE_AA)
        t2= time.time()
        elapsedT = t2-t1
        cv2.putText(ori,
                'fps:{:.2f},numFaces:{}'.format(num/elapsedT,boxes.shape[0]),
                (200,20), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1,
                (0,0,255),
                2,
                cv2.LINE_AA)
        cv2.imshow("ultra_face_ace_opencvdnn_py", ori)
        key = cv2.waitKey(1)
        if key ==27:
            break
        if key ==ord(' '):# 按空格键暂停
            cv2.waitKey(0)
    cap.release()
    cv2.destroyAllWindows()

    

