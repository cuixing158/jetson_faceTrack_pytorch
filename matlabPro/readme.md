# Overview
The code on this page implements the functions of face detection + tracking + HC08 Bluetooth module transmission signal + voice broadcast and other functions equivalent to the matlab2020a version. The code implementation is relatively simple, condensed arduino control program + matlab algorithm design, and has a strong understanding.<br>
本页实现了matlab2020a版本等价的人脸检测+追踪+HC08蓝牙模块发射信号+语音播报等功能，代码实现较为简洁，浓缩arduino控制程序+matlab算法设计，理解性强。<br>

# Advantages
- Simple code, integrated control + algorithm.
- It is easy to debug the verification algorithm repeatedly.
- Fast development cycle.

# 优点
- 代码简洁，集成控制+算法。
- 易于反复调试验证算法。
- 开发周期快。

# Disadvantages
- Compared with C++, the execution efficiency is lower
- Not easy to transplant
- SOTA algorithm unified integration into matlab is slow

# 缺点
- 相比C++,执行效率较低
- 不易移植
- SOTA算法统一集成到matlab中较慢

# How to use
1. Download [arduino support package](https://ww2.mathworks.cn/matlabcentral/fileexchange/47522-matlab-support-package-for-arduino-hardware?s_tid=srchtitle );<br>
2. Configure the hardware environment, such as arduino wiring, steering gear wiring, jetson maximum power supply use short-circuit plug, the default is usb power supply, etc.;<br>
3. run `main.m` <br>

# 怎样使用
1、下载[arduino支持包](https://ww2.mathworks.cn/matlabcentral/fileexchange/47522-matlab-support-package-for-arduino-hardware?s_tid=srchtitle )；<br>
2、配置好硬件环境，如arduino接线，舵机接线,jetson最大电源使用要用短接冒，默认是usb供电等；<br>
3、run `main.m` <br>


# Reference
[Arduino-matlab](https://www.mathworks.com/hardware-support/arduino-matlab.html )
