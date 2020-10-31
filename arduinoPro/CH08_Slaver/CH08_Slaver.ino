// 功能：arduino mega2560与HC-08蓝牙模块通信使用，思路为：jetson/pc端发起舵机转动指令，舵机转动一个epoch后就向蓝牙发送信号，蓝牙接收信号然后把信号发送为无线电，最后其他手机或电脑可以接收无线电！运行都成功！
// 参考：https://blog.csdn.net/mcgradycom2/article/details/43737117?utm_medium=distribute.pc_relevant_download.none-task-blog-baidujs-3.nonecase&depth_1-utm_source=distribute.pc_relevant_download.none-task-blog-baidujs-3.nonecase
// 参考2：https://blog.csdn.net/weixin_37272286/article/details/78016497
#include <Servo.h>
#include <SoftwareSerial.h> // 使用方法官方：https://www.arduino.cc/en/Reference/SoftwareSerial

Servo myservo1,myservo2;
int pos = 0;// variable to store the servo position

SoftwareSerial myBlueTooth(15, 14); // RX, TX 崔星星加入,代表蓝牙
int nums = 0;

void setup() {
  // 舵机
  myservo1.attach(52);
  myservo2.attach(53);

  // 蓝牙
  Serial.begin(115200); // 波特率可能引起显示乱码，当HC08模块波特率设置为115200，电平要接到arduino，手机上“LightBlue” APP上FFEO端监听传入的值，utf-8正常显示!
  myBlueTooth.begin(115200);
}

void loop() {
  // 舵机
  for (pos = 0; pos <= 180; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    myservo1.write(pos);              // tell servo to go to position in variable 'pos'
    myservo2.write(pos);
    delay(50);                       // waits 15ms for the servo to reach the position
  }
  for (pos = 180; pos >= 0; pos -= 1) { // goes from 180 degrees to 0 degrees
    myservo1.write(pos);              // tell servo to go to position in variable 'pos'
    myservo2.write(pos);
    delay(50);                       // waits 15ms for the servo to reach the position
  }

  // 此时蓝牙作为发射器，把舵机运动信号发射出去
  int number = nums++;
  char numberStr[25];
  itoa(number, numberStr, 10); //参考int转换为string, 10进制 https://blog.csdn.net/qq_25827845/article/details/50905453

 // myBlueTooth.write(numberStr);
  //myBlueTooth.write(number);  //官方参考：https://www.arduino.cc/reference/en/language/functions/communication/serial/write/ 或者下面的
  myBlueTooth.println(number);    // print as an ASCII-encoded decimal ，参考官方：https://www.arduino.cc/en/Reference/SoftwareSerialPrintln
  //myBlueTooth.println(numberStr);   // print a linefeed character
  Serial.println(number); // 在本IDE上工具->串口监视器上可以实时查看数值，注意设置好一样的波特率，否则乱码
  delay(10);
 

  // 此时蓝牙作为接收器
  myBlueTooth.listen(); // 监听蓝牙是否有信号传入进来,此时蓝牙是主属模块
  if (myBlueTooth.available())
  {
    char val = myBlueTooth.read();
    myBlueTooth.print("hah");
    Serial.println("cuixing");
    if (val == 'a')
    {
      myBlueTooth.print("123");//Set BT name
    }
    else if (val == 'b')
    {
      //Serial.println("456");
      myBlueTooth.print("456");// Set Pin
    }
    else if (val == 'c')
    {
      myBlueTooth.write("789");// Set Pin
    }
  }
}
