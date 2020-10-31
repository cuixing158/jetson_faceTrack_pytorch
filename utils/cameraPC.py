# 简单测试相机平均帧率
import cv2
import time

width = 1280
height = 720

cam = cv2.VideoCapture(0+cv2.CAP_DSHOW) # '/dev/video1'
cam.set(cv2.CAP_PROP_FRAME_WIDTH, width )
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height )
t1 = time.time()

# show
num = 0
while cam.isOpened():
    num+=1
    ret, frame = cam.read()
    if not ret:
        print("Can't get image")
        continue
    #frame_rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA).astype(np.float32)
    
    
    t2 = time.time()
    Elapsetime = t2-t1
    fps = num/Elapsetime
    cv2.putText(frame,"fps:{:.1f}".format(fps),(200,50),0,1,(0,0,255),2)

    # show
    cv2.imshow("",frame)
    key = cv2.waitKey(1)
    if key==27:
        break
    if key==ord(' '):
        cv2.waitKey()

cam.release()
cv2.destroyAllWindows()
