// 功能：由给定的水平和竖直舵机的角度增量，完成舵机位置移动跟踪;
// 另外，可通过蓝牙控制，1为启动跟踪，0为停止跟踪
// cuixingxing 2020.10.24

#include <Servo.h> //舵机
#include<SoftwareSerial.h> // 蓝牙
Servo servoH; //水平方向舵机
Servo servoV; // 竖直方向舵机
SoftwareSerial BT(14,15); // RX,TX，定义为接受蓝牙，手机在串口发送1开始跟踪，发送0停止跟踪
bool isTrack = 1;

void setup()
{
  //start serial communication at Baud rate of 9600
  Serial.begin(9600);
  Serial.println("Starting Cam-servo Face tracker");
  BT.begin(9600);

  servoH.attach(52); //水平方向舵机接引脚52
  servoV.attach(53); //竖直方向舵机接引脚53

  // 舵机位置初始化
  servoH.write(108); // 初始化位置108度，根据实际情况调整
  delay(200);
  servoV.write(54); // 初始化位置54度，根据实际情况调整
  delay(200);
}

void loop()
{
  
  if (BT.available())
  {
    String value = String(BT.read());
    isTrack = value.toInt(); // 非数是以0返回
    Serial.println("isTrack:"+isTrack);
  }
  BT.write(isTrack);
  
  if (Serial.available()&& isTrack)
  {
    //Check for frame control bits
    String message = Serial.readStringUntil('\n'); //https://www.arduino.cc/reference/en/language/functions/communication/serial/readstring/
    //String message = Serial.readString(); // 水平和竖直2个舵机传入的角度增量用逗号分割一起传入进来,如 "20,32"
    //Serial.println("从python传入进来的值为:" + message+"\n");
    //Serial.println( bytesSent);
    //Serial.println('\n');
    //delay(1000);
    
    int commaPosition = message.indexOf(','); // https://www.cnblogs.com/jqmtony/p/3763060.html
    int delta_degreeH = 0; // 相对当前位置的水平舵机角度增量
    int delta_degreeV = 0; // 相对当前位置的竖直舵机角度增量
    if (commaPosition != -1)
    {
      String degreeH = message.substring(0, commaPosition);
      String degreeV = message.substring(commaPosition + 1, message.length());
      delta_degreeH = degreeH.toInt(); // https://blog.csdn.net/qq_39042062/article/details/102866046
      delta_degreeV = degreeV.toInt();
    }
    Serial.println("delta_degreeH:"+String(delta_degreeH)+",delta_degreeV:"+String(delta_degreeV)); // 可以在python中利用pyserial库serial.readline().decode()调试结果

    // 读当前舵机位置,https://www.arduino.cc/reference/en/libraries/servo/read/
    int currentH = servoH.read();
    int currentV = servoV.read();

    // 写,https://www.arduino.cc/reference/en/libraries/servo/write/
    int writeH = currentH + delta_degreeH;
    int writeV = currentV + delta_degreeV;
    if (writeH < 0)
      writeH = 0;
    if (writeH > 180)
      writeH = 180;
    if (writeV < 0)
      writeV = 0;
    if (writeV > 180)
      writeV = 180;
    servoH.write(writeH);
    servoV.write(writeV);
  }
}
