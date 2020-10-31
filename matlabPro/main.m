%% 云台人脸检测跟踪+HC08蓝牙模块发射信号+语音播报+行人/人脸识别
% 2020.9.6日更改，SPI语音识别模块，Serial蓝牙模块，Servo舵机模块
addpath('./mtcnn')
arduinoObj = arduino("COM3","Mega2560","Libraries",{'SPI','Serial','I2C','Servo'});% arduino通过usb有限连接

% 定义蓝牙，检测到人脸就发送信号1，没有就发送0
BLEsserial = device(arduinoObj,'SerialPort',3,'BaudRate', 9600); %  TxPin: 'D14' RxPin: 'D15'

% 定义语音播放模块对应板子上接的引脚
[y,Fs] = audioread('demo.wav');
player = audioplayer(y,Fs);

A1 = 'D38';
A2 = 'D36';
A3 = 'D34';
A4 = 'D32';
A5 = 'D30';
% 语音播报检测到人脸
% configDigOutput(arduinoObj,A1,A2,A3,A4,A5);
% writeDigitalPin(arduinoObj,A1,1);
% writeDigitalPin(arduinoObj,A2,0);
% writeDigitalPin(arduinoObj,A3,1);
% writeDigitalPin(arduinoObj,A4,1);
% writeDigitalPin(arduinoObj,A5,1);
% dispalyVot(arduinoObj,A1,A2,A3,A4,A5);
    
% 舵机位置初始化
s1 = servo(arduinoObj,'D52'); % 云台下面舵机
s2 = servo(arduinoObj,'D53'); % 云台上面舵机
degree_y = 0.3;% 54/180;
degree_x = 0.6;% 108/180;
writePosition(s1,degree_x);% 初始化角度位置
writePosition(s2,degree_y);% 初始化角度位置

%% 设置参数
cap = webcam('LRCP USB2.0 500W');
cap.Resolution = '1280x800';
% preview(cap);
rangeHcam1 = 18;% 摄像头水平方向范围,度数, 也可以理解为调节灵敏度
rangeVcam1 = 10;% 摄像头竖直方向范围,度数, 也可以理解为调节灵敏度
rangeHservo = 180;% 舵机水平方向范围
rangeVservo = 180;% 舵机竖直方向范围
scalar= 0.25; %图像缩放系数
ratioHorizontal = rangeHcam1/rangeHservo; % 相机与舵机水平方向转动比例
ratioVertical = rangeVcam1/rangeVservo; % 相机与舵机竖直方向转动比例

%%
facedetector = mtcnn.Detector("MinSize", 15, "MaxSize", 70,'UseGPU',true);
frame = snapshot(cap);
videoObj = vision.DeployableVideoPlayer();
step(videoObj,frame)
[H,W,~] = size(frame);
imgCenter = [W/2,H/2]; % 图像固有中心坐标，如[640/2,480/2]
numPts = 0;
FPS = 0;
while(videoObj.isOpen())
    t_all = tic;
    writePosition(s1,degree_x);
    writePosition(s2,degree_y);
    fprintf("degree_x:%.2f,degree_y:%.2f\n",degree_x*180,degree_y*180);
    frame = snapshot(cap);
    detectImg = imresize(frame,scalar);
    
    % 检测人脸
    [bboxes, scores, landmarks] = facedetector.detect(detectImg);
    if isempty(bboxes)
        step(videoObj,frame);
         write(BLEsserial,uint8(0));
        continue; 
    end
    [~,ind] = max(bboxes(:,3).*bboxes(:,4));
    bboxes(bboxes<0)=1;
    bbox = bboxes(ind,:)./scalar;
    score = scores(ind);
    landmark = landmarks(ind,:,:)./scalar;
    
    % 发送蓝牙信号
    write(BLEsserial,uint8(1));
    
    % 语音播报
    play(player); % Play without blocking，无阻塞方式播报

    %绘图
    RGB = insertObjectAnnotation(frame, "rectangle", bbox, score, "LineWidth", 2);
    RGB = insertMarker(RGB,squeeze(landmark),"square",...
        "Color","green");
    RGB = insertText(RGB,[10,20],FPS);
    step(videoObj,RGB);
    
    %% 调整角度，假设相机无畸变
    center = [bbox(1)+bbox(3)/2,bbox(2)+bbox(4)/2]; % [x,y]
    if center(1)<=imgCenter(1) % 人脸在图像左边
        distance_x = imgCenter(1)-center(1);
        degree_x = readPosition(s1)+ (distance_x./W).*ratioHorizontal;
    else
        distance_x = center(1)-imgCenter(1);
        degree_x = readPosition(s1)-(distance_x./W).*ratioHorizontal;
    end
    if center(2)<=imgCenter(2) % 人脸在图像上方
        distance_y = imgCenter(2)-center(2);
        degree_y = readPosition(s2)+(distance_y/H).*ratioVertical;
    else
        distance_y = center(2)-imgCenter(2);
        degree_y = readPosition(s2)-(distance_y/H).*ratioVertical;
    end
    
    %% 限定范围内
    degree_x(degree_x<0)=0;
    degree_y(degree_y<0)=0;
    degree_x(degree_x>1)=1;
    degree_y(degree_y>1)=1;

    FPS = 1/toc(t_all);
end


