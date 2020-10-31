%% 语音识别和播放两个功能
% 语音识别功能参考：https://www.waveshare.net/study/article-11-1.html
% 语音播放功能参考：参考：https://item.taobao.com/item.htm?spm=a1z09.2.0.0.53a62e8dfL5xw7&id=612887678709&_u=71nargtrc654
%  https://blog.csdn.net/qq_36955622/article/details/103512824

%% 1、控制语音播放,目前编码形式与淘宝介绍不符！32种编码格式对应播放顺序不一致！
arduinoObj = arduino("COM6","Mega2560","Libraries",{'SPI','Serial','I2C'});% usb有限连接
% 定义语音播放模块对应板子上接的引脚
A1 = 'D38';
A2 = 'D36';
A3 = 'D34';
A4 = 'D32';
A5 = 'D30';

%% 根据语音模块上标注的A1-A5编码模式，对应播放音乐！
modes = dec2bin(1:31);
% validModes = {'10100','11001','11111'};
for i = 1:31
    mode = modes(i,:); % 1*5 char
%     mode = validModes{i};
    fprintf("当前编码数：%s\n",mode);
    v1 = str2double(mode(1));
    v2 = str2double(mode(2));
    v3 = str2double(mode(3));
    v4 = str2double(mode(4));
    v5 = str2double(mode(5));

    configDigUnset(arduinoObj,A1,A2,A3,A4,A5);
    writeDigitalPin(arduinoObj,A1,v1);
%     pause(1);
    writeDigitalPin(arduinoObj,A2,v2);
%     pause(1);
    writeDigitalPin(arduinoObj,A3,v3);
%     pause(1);
    writeDigitalPin(arduinoObj,A4,v4);
%     pause(1);
    writeDigitalPin(arduinoObj,A5,v5);
%     pause(1);
    configDigUnset(arduinoObj,A1,A2,A3,A4,A5)
    a1 = readDigitalPin(arduinoObj,A1);
    a2 = readDigitalPin(arduinoObj,A2);
    a3 = readDigitalPin(arduinoObj,A3);
    a4 = readDigitalPin(arduinoObj,A4);
    a5 = readDigitalPin(arduinoObj,A5);
    pause(1.1);
    fprintf('读入的电平A1-A5:%s\n\n',strjoin(string([a1,a2,a3,a4,a5]),''));
end

%% 语音播报
configDigUnset(arduinoObj,A1,A2,A3,A4,A5);
writeDigitalPin(arduinoObj,A1,0);
writeDigitalPin(arduinoObj,A2,1);
writeDigitalPin(arduinoObj,A3,1);
writeDigitalPin(arduinoObj,A4,1);
writeDigitalPin(arduinoObj,A5,1);
pause(2);

% 第3首
configDigUnset(arduinoObj,A1,A2,A3,A4,A5);
writeDigitalPin(arduinoObj,A1,1);
writeDigitalPin(arduinoObj,A2,0);
writeDigitalPin(arduinoObj,A3,1);
writeDigitalPin(arduinoObj,A4,1);
writeDigitalPin(arduinoObj,A5,1);
pause(2);

% 第3首
configDigUnset(arduinoObj,A1,A2,A3,A4,A5);
writeDigitalPin(arduinoObj,A1,1);
writeDigitalPin(arduinoObj,A2,1);
writeDigitalPin(arduinoObj,A3,1);
writeDigitalPin(arduinoObj,A4,0);
writeDigitalPin(arduinoObj,A5,1);
pause(2);



%% 2、语音接收模块