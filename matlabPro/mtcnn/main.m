   %% 测试人脸检测在GPU上运行
   facedetector = mtcnn.Detector("MinSize", 15, "MaxSize", 70,'UseGPU',true);
   im = imread("visionteam.jpg");
   [bboxes, scores, landmarks] = facedetector.detect(im);
    
