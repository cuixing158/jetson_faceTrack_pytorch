%% 说明：HC08蓝牙模块支持蓝牙4.0, HC05/06只支持2.0，matlab必须支持4.0及以上，所以不要买HC05/06,arduino上的rx,tx接口要交错连接到蓝牙模块的tx,rx

%% 测试arduiino与HC08蓝牙模块(主属端发射信号)之间的通信
% arduinoObj = arduino('HC-08','Mega2560')
% 此种方式是通过无线方式连接arduino和matlab，蓝牙模块HC08是从属端!而且要安装Instrument Control Toolbox
% +电脑还得打开蓝牙（或者装蓝牙适配器装置，麻烦！）
arduinoObj = arduino("COM3","Mega2560","Libraries",{'SPI','Serial','I2C'});% usb有限连接
serialdevObj = device(arduinoObj,'SerialPort',3,'BaudRate', 9600) %  TxPin: 'D14' RxPin: 'D15'

%% 向蓝牙引脚写入信号，然后蓝牙作为发射模块发射无线电
% 比如手机中的LightBlue APP连接到蓝牙后，当上面write数据时候，可以得到信号传过来了
nums = 1;
while true
    fprintf('write nums:%d\n',nums);
    write(serialdevObj,nums,'uint8');
    numBytes = serialdevObj.NumBytesAvailable;
    % read(serialdevObj,3) % numBytes为0，读入出错，
    nums = nums+1;
    pause(1);
end



