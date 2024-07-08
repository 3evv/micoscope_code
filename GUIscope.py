import glob,os,sys
import cv2 
import math
import numpy as np
import serial
import time

scannedlist = []
scanningPlan = []
os.chdir("C:/Users/kamci/Desktop/Microwizard_software/micoscope_code")
#call for taking 1x magingication

cam_port = 0
cam = cv2.VideoCapture(cam_port, cv2.CAP_DSHOW) 
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
roi =  (6, 19, 1268, 676)
dist = np.array([[ 1.39879869e-03 ,-2.87123247e-05 ,-3.72218939e-04 ,1.53930449e-03,1.42653796e-07]])
newcameramtx = np.array([[ 70.81217412  , 0.    ,     668.49756177],[  0. ,         67.07437998 ,355.24155489],[  0.    ,       0.     ,      1.        ]])
mtx = np.array([[ 71.59824469,   0.00000000e+00    ,     639.49607517],[  0.00000000e+00,69.15288899,359.50427439],[  0.00000000e+00 ,0.00000000e+00 ,1.00000000e+00]])
def readCamera(name):
    result, image = cam.read() 
    if result: 
        cv2.imwrite("data/" + name + ".jpg", image) 
    else: 
        print("No image detected. Please! try again") 

def take1Xscan():
    with serial.Serial() as ser:
        #readCamera("Tst")
        # ser.port = '/dev/ttyACM0'
        ser.port = 'COM3'
        ser.baudrate = 9600
        ser.timeout=0.1
        #ser.parity=serial.PARITY_EVEN
        #ser.rtscts=1
        ser.open()
        # while True:
        #     time.sleep(5)
        #     #ser.write(bytes("G28 X Y;", 'utf-8'))
        #     output = ser.readline().decode().strip()
        #     while output != "Ready" :
        #         if output:
        #             print(output)
        #         output = ser.readline().decode().strip()
        #     print(output)
     
        def waitforcommand(command):
            output = ser.readline().decode().strip()
            while output != command :
                if output:
                    print(output)
                output = ser.readline().decode().strip()
                time.sleep(0.1)

        #ser.write(bytes("M114", 'utf-8'))
        #tmp = ser.readline().decode().strip()
        # print(tmp)
        # if tmp.find("XY:0"):
        #     ser.write(bytes("G28 X Y;", 'utf-8'))
        #     waitforcommand("Done")
        #     print("Zeroed X & Y")   
        # else:
        #     print("X & Y already zeroed")       
        command = "G0 X: " + str(-120000) + " Y: " + str(-200000) + " Z: " + str(0) + " ;"
        ser.write(bytes(command, 'utf-8'))
        waitforcommand(command + " Done")
        readCamera("Right")
        command = "G0 X: " + str(-40000) + " Y: " + str(-200000) + " Z: " + str(0) + " ;"
        ser.write(bytes(command, 'utf-8'))
        waitforcommand(command + " Done")
        readCamera("Left")

def Glue1xMag():
    Left1x=cv2.imread("data/Left.jpg", cv2.IMREAD_ANYCOLOR) 
    Right1x=cv2.imread("data/Right.jpg", cv2.IMREAD_ANYCOLOR) 
    Left1x = cv2.undistort(Left1x, mtx, dist, None, newcameramtx)
    Right1x = cv2.undistort(Right1x, mtx, dist, None, newcameramtx)
    cv2.imwrite( "undistorted left.jpg", Left1x)
    cv2.imwrite( "undistorted right.jpg", Right1x)
    glueing_x = 486
    cut_line_x = 1160 - glueing_x # 1184
    glueing_y = 15
    glue_alpha=0.5
    fill_color = (0,0,0)
    #extend left to match right after resize
    left_filler = np.full((Left1x.shape[0] + glueing_y,Left1x.shape[1] + glueing_x, Left1x.shape[2]), fill_color, dtype=Left1x.dtype)
    left_filler[5:5+Left1x.shape[0], 0:Left1x.shape[1]] = Left1x
    Left1x = left_filler.copy()
    
    #extend right to match left after resize

    right_filler = np.full((Right1x.shape[0] + glueing_y,Right1x.shape[1] + glueing_x, Right1x.shape[2]), fill_color, dtype=Right1x.dtype)
    right_filler[0:Right1x.shape[0], glueing_x + cut_line_x:] = Right1x[:, cut_line_x:]
    Right1x = right_filler.copy()
    # print(Right1x.shape, Left1x.shape)
    # return Left1x
    stitched = cv2.addWeighted(Left1x, glue_alpha, Right1x, 1-glue_alpha, 0)
    cv2.imwrite( "stitched.jpg", stitched)
    return stitched


for file in glob.glob("data/scanned/*.jpg"):
    scannedlist.append(file)
#img = cv2.resize(img, (0,0), fx = 240, f = 09_42_58_Pro.jpg", cv2.IMREAD_ANYCOLOR) cancer idea
posList = []
def GetSquare(x,y):
    h, w, _ = NoMagScan.shape
    planned_x = (round(x/16)) * 16 + 8
    planned_y = (round(y/9) - 1) * 9 + 4
    return (planned_x,planned_y)

def getcoords(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if GetSquare(x,y) in scanningPlan: 
            scanningPlan.remove(GetSquare(x,y))
        else:
            scanningPlan.append(GetSquare(x,y))
        print(x,y)
        print(scanningPlan)
    #drawGrid(img)
    # if event != cv2.EVENT_MBUTTONUP:
    #    if (x,y) != posList[-1]: 
           

def generateScan():
    finishedScan = NoMagScan.copy()
    print(scannedlist)
    for scan in scannedlist:
        tmp = cv2.imread(scan, cv2.IMREAD_ANYCOLOR)
        tmp = cv2.resize(tmp, (16,9))
        x_coord = int(scan[scan.rfind("X") + 3:scan.rfind("Y")]) - math.floor(tmp.shape[1]/2)
        y_coord = int(scan[scan.rfind("Y") + 3:scan.rfind("C")]) - math.floor(tmp.shape[0]/2)
        print(x_coord,y_coord)
        finishedScan[y_coord:y_coord+tmp.shape[0], x_coord:x_coord+tmp.shape[1]] = tmp
    return finishedScan   
    
def drawGrid(color1=(180, 180, 180)):
    color2=(125, 125, 125)
    img = NoMagScan.copy()
    h,w, _ = img.shape
    alpha = 0.75
    alpha2 = 0.25
    x_denisty = 16 # 1, 5, 9th of 9 line cluster? 
    y_denisty = 9 # 1, 7, 16th line clusters ?
    for x in np.linspace(start=x_denisty, stop= w - x_denisty, num=(round(w/x_denisty))-1):
        x = int(round(x))
        cv2.line(img, (x,0), (x, h), color=color1, thickness=1)
        cv2.line(img, (x+8,0), (x+8, h), color=color2, thickness=1)
    
    for y in np.linspace(start=y_denisty, stop= h - y_denisty, num=(round(h/y_denisty))-1):
        y = int(round(y))
        cv2.line(img, (0, y), (w, y), color=color1, thickness=1)
        #cv2.line(img, (0, y+4), (w, y+4), color=color1, thickness=2)
        #cv2.line(img, (0, y+9), (w, y+9), color=color1, thickness=1)

    img = cv2.addWeighted(NoMagScan.copy(), alpha, img, 1-alpha, 0)

    img2 = img.copy()
     #Draw rectangles on scanned areas: 
    for scan in scannedlist:
        x_coord = int(scan[scan.rfind("X") + 3:scan.rfind("Y")]) - math.floor(8)
        y_coord = int(scan[scan.rfind("Y") + 3:scan.rfind("C")]) - math.floor(4)
        cv2.rectangle(img2, (x_coord, y_coord), (x_coord+16,y_coord+8), color=(0, 180, 0), thickness=-1)

    for planned in scanningPlan:
        # x_coord = int(planned[planned.rfind("X:") + 2:planned.rfind("Y:")]) - math.floor(8)
        # y_coord = int(planned[planned.rfind("Y:") + 2:planned.rfind("C:")]) - math.floor(4)
        x_coord, y_coord = planned
        #print(planned)
        cv2.rectangle(img2, (x_coord-8, y_coord-4), (x_coord+8,y_coord+5), color=(150, 0, 0), thickness=-1)

    img = cv2.addWeighted(img, alpha2, img2, 1-alpha2, 0)

    return img

cv2.namedWindow('image')
cv2.setMouseCallback('image',getcoords)
NoMagScan = Glue1xMag()
img = NoMagScan.copy()
while True:
    cv2.imshow('image',img)
    k = cv2.waitKey(0) & 0xFF
    if k == 27:
       break
    elif k == ord('n'):
        print("no maginification")
        #img = cv2.imread("data/zlepione.jpg", cv2.IMREAD_ANYCOLOR) 
        img = NoMagScan.copy()
    elif k == ord('m'): 
        print("generating")
        img = generateScan()
    elif k == ord('b'):
        img = drawGrid()
    elif k == ord('p'):
        take1Xscan()
        NoMagScan = Glue1xMag()
        
 
cv2.destroyAllWindows() # destroy all windows

# 16x9 -> rescaled 
# 3840 x 2160 orginal -> 240x magnification
# 623 x  middle 1415, 166
# 5,63 -> lacks factor of 6 times?  1408,162 -> upper right corner of scan 1422,170 -> lower left
