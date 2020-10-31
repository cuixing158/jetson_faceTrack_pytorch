
%% 实现录音读入，播报
Fs = 44100; 
nBits = 16 ; 
nChannels = 2 ; 
ID = -1; % default audio input device 
recObj = audiorecorder(Fs,nBits,nChannels,ID);

disp('Start speaking.')
recordblocking(recObj,10); %录音3秒
disp('End of Recording.');

% record(recObj);
% pause(2);
% stop(recObj);

play(recObj);
y = getaudiodata(recObj);
plot(y)
audiowrite('voice_unknow.wav',y,Fs);




%% 苹果手机录音播放
filename = '001cuixingxing.m4a';
[y1,Fs] = audioread(filename,[24528,inf]);
sound(y1,Fs)
plot(y1)

