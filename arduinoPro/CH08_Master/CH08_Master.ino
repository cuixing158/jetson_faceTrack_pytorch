// 参考：https://forum.arduino.cc/index.php?topic=486177.0
// 功能：蓝牙作为接收装置，在手机上发送信号控制舵机运动
// 蓝牙模块连接参数架设置模块参数，AT指令设置波特率等，现在改为9600了，波特率不匹配会乱码

#include <Servo.h>
#include <SoftwareSerial.h> // 使用方法官方：https://www.arduino.cc/en/Reference/SoftwareSerial

#define DEGREE1 0 // 手机发送0，代表2个舵机都转动到30度
#define DEGREE2 1 // 手机发送1，代表2个舵机都转动到90度
#define DEGREE3 2 // 手机发送2，代表2个舵机都转动到120度

Servo myservo1,myservo2;
int nums = 0;
int degree =0; // 每次舵机转动的位置（角度，0-180）

SoftwareSerial hc_08(15,14); // 15RX, 14TX 或者17RX，16TX

void servoRunTest(int degree)
{
      Serial.println(degree);
       hc_08.println(degree);
       myservo1.write(degree);
       myservo2.write(degree);
}

  
void setup() {
  myservo1.attach(52);
  myservo2.attach(53);
  
  //pinMode(15, OUTPUT);
 // pinMode(14, INPUT);
  Serial.begin(9600); //原来为115200
  hc_08.begin(9600);
 while(!hc_08){}
}


void loop() {
  nums++;
//  Serial.listen();
  hc_08.listen();
  if (hc_08.available()) {
    delay(5000);
    Serial.println("available");
    hc_08.println("available");
    delay(5000);
    char c = hc_08.read(); // https://www.arduino.cc/en/Reference/SoftwareSerialRead , // 读入手机来的数据
    switch(c){
      case 0:
        degree = 30;
        servoRunTest(degree);
        break;
       case 1:
        degree = 90;
        servoRunTest(degree);
        break;
       case 2:
        degree = 120;
        servoRunTest(degree);
        break;
      }
   // digitalWrite(availableLEDpin, HIGH);
   // digitalWrite(notAvailableLEDpin, LOW);

  }
  else
  {
    Serial.println("un available");
    hc_08.listen();
    Serial.println(hc_08.isListening());
    hc_08.println("hc08 un available"); // 手机上可以收到信号
   // digitalWrite(availableLEDpin, LOW);
   // digitalWrite(notAvailableLEDpin, HIGH);
  }
 delay(1000);
}
