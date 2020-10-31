/*
  舵机的控制
*/

//导入舵机的库
#include <Servo.h>

Servo servo_pin_1;

int state=0; //初始状态
int t=10; //延时毫秒
void setup()
{
  Serial.begin(9600);
  servo_pin_1.attach(51);//使用第1号引脚为信号输出
}

void loop()
{
  while(!Serial)//检测是否有串口接通
  {} 
  if(Serial.available()>0) //判断是否具有输入
  {
    state=Serial.parseInt(); //接收数据
    servo_pin_1.write( state ); //定义舵机的转动角度
//    delay( t );//延时1000毫秒
  }
}
