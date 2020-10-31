// 测试只能播报28，29，30，其他数字无法播报出来！
// 语音识别功能参考：https://www.waveshare.net/study/article-11-1.html
// 语音播放功能参考：参考：https://item.taobao.com/item.htm?spm=a1z09.2.0.0.53a62e8dfL5xw7&id=612887678709&_u=71nargtrc654
// https://blog.csdn.net/qq_36955622/article/details/103512824

#include <Arduino.h>
#include <Wire.h>
#include <Servo.h>
#include <SoftwareSerial.h>

void setup() {
  // put your setup code here, to run once:
int A1 = 22;
int A2 = 24;
int A3 = 26;
int A4 = 28;
int A5 = 30;

  pinMode(A1,OUTPUT);
  pinMode(A2,OUTPUT);
  pinMode(A3,OUTPUT);
  pinMode(A4,OUTPUT);
  pinMode(A5,OUTPUT);

int A6 = 32;
int A7 = 34;
int A8 = 36;
int A9 = 38;
  pinMode(A6,OUTPUT);
  pinMode(A7,OUTPUT);
  pinMode(A8,OUTPUT);
  pinMode(A9,OUTPUT);
}

void loop() {
    // put your main code here, to run repeatedly:
  

  //delay(1000);
  while(true)
  {
    digitalWrite(A1,1);
    delay(2000);
    digitalWrite(A2,1);
    delay(2000);
    digitalWrite(A3,1);
    digitalWrite(A4,0);
    digitalWrite(A5,0);
    digitalWrite(A6,1);
    digitalWrite(A7,1);
    digitalWrite(A8,1);
    digitalWrite(A9,1);

//    delay(600);
//  
//    digitalWrite(A1,1);
//    digitalWrite(A2,0);
//    digitalWrite(A3,1);
//    digitalWrite(A4,1);
//    digitalWrite(A5,1);
    delay(700);
   }
}
