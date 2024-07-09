import glob,os,sys
import cv2 
import math
import cv2
import numpy as np
import serial
import time
from stitching import stitch 
scannedlist = []
scanningPlan = []
os.chdir("C:/Users/kamci/Desktop/Microwizard_software/micoscope_code")
#call for taking 1x magnification

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
        ser.timeout=None
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
        
        def waitforcommand(input):
            output = ser.readline().decode().strip()
            while output != input :
                if output:
                    print(output)
                output = ser.readline().decode().strip()
                time.sleep(0.1)
            print("Waiting for command: done")
            return input

        #ser.write(bytes("M114", 'utf-8'))
        #tmp = ser.readline().decode().strip()
        # print(tmp)
        # if tmp.find("XY:0"):
        #     ser.write(bytes("G28 X Y;", 'utf-8'))
        #     waitforcommand("Done")
        #     print("Zeroed X & Y")   
        # else:
        #     print("X & Y already zeroed")       
        command = "G0 X: " + str(-150000) + " Y: " + str(-200000) + " Z: " + str(0) + " ;"
        ser.write(bytes(command, 'utf-8'))
        waitforcommand(command + " Done")
        print("reading camera")
        time.sleep(1)
        readCamera("Right")
        command = "G0 X: " + str(-20000) + " Y: " + str(-200000) + " Z: " + str(0) + " ;"
        ser.write(bytes(command, 'utf-8'))
        waitforcommand(command + " Done")
        time.sleep(1)
        readCamera("Left")
def fadeIn (img1, img2): #pass images here to fade between
        #while True:
        for IN in range(0,10):
                fadein = IN/10.0
                dst = cv2.addWeighted( img1, fadein, img2, fadein, 0)#linear $
                cv2.imshow('window', dst)
                cv2.waitKey(1)
                time.sleep(0.05)
                if fadein == 1.0: #blendmode mover
                        fadein = 1.0
        return # exit function


def Glue1xMag():
    # take1Xscan()
    Left1x=cv2.imread("data/Left.jpg", cv2.IMREAD_ANYCOLOR) 
    Right1x=cv2.imread("data/Right.jpg", cv2.IMREAD_ANYCOLOR) 
    Left1x = cv2.undistort(Left1x, mtx, dist, None, newcameramtx)
    Right1x = cv2.undistort(Right1x, mtx, dist, None, newcameramtx)
    # Left1x =  cv2.equalizeHist(Left1x)
    # Right1x = cv2.equalizeHist(Right1x)
    # crop the image
    h, w = Left1x.shape[:2]
    x, y, w, h = roi
    Left1x = Left1x[y:y+h, x:x+w]
    h, w = Right1x.shape[:2]
    x, y, w, h = roi
    Right1x = Right1x[y:y+h, x:x+w]
    cv2.imwrite( "undistorted left.jpg", Left1x)
    cv2.imwrite( "undistorted right.jpg", Right1x)
    glueing_x = 634
    cut_line_x = 1024 - glueing_x # 1184
    glueing_y = 0
    glue_alpha=0.75
    fill_color = (0,0,0)
    #extend left to match right after resize
    filler = np.full((Left1x.shape[0] + glueing_y,Left1x.shape[1] + glueing_x, Left1x.shape[2]), fill_color, dtype=Left1x.dtype)
    filler[glueing_y:glueing_y+Left1x.shape[0], 0:Left1x.shape[1]] = Left1x[0:,0:]
    # Left1x = left_filler.copy()
    #extend right to match left after resize
    # right_filler = np.full((Right1x.shape[0] + glueing_y,Right1x.shape[1] + glueing_x, Right1x.shape[2]), fill_color, dtype=Right1x.dtype)
    filler[0:Right1x.shape[0], glueing_x + cut_line_x:] = Right1x[:, cut_line_x:]
    # Right1x = right_filler.copy()
    # print(Right1x.shape, Left1x.shape)
    # return Left1x
    # Left1x = cv2.resize(Left1x, (Right1x.shape[0],Right1x.shape[1]))
    Left_fade = Left1x[:,glueing_x:]
    Left_alpha = cv2.cvtColor(Left_fade, cv2.COLOR_RGB2RGBA)
    alpha_mask_left = np.zeros([Left_fade.shape[0],Left_fade.shape[1]])
    # print(alpha_mask_left)
    alpha_mask_coefficient = 255
    for i in range(0,Left_fade.shape[1] - 1):
        # print(i, Left_fade.shape[0] - 1)
        for x in range(0,Left_fade.shape[0] - 1):
            
            alpha_mask_left[Left_fade.shape[0] - 1 - x][Left_fade.shape[1] - 1 - i] = round(alpha_mask_coefficient * float(i / Left_fade.shape[1]))  
            

    Left_alpha[:, :, 3] = alpha_mask_left
    # print(alpha_mask_left[:][100], round(255 * float(100 / Left_fade.shape[0])))

    Right_fade = Right1x[:, :Right1x.shape[1] - glueing_x]
    Right_alpha = cv2.cvtColor(Right_fade, cv2.COLOR_RGB2RGBA)
    alpha_mask_right = np.zeros([Right_alpha.shape[0],Right_alpha.shape[1]])
    # print(alpha_mask_right)
    for i in range(0,Right_fade.shape[1] - 1):
        # print(i, Right_fade.shape[0] - 1)
        for x in range(0,Right_fade.shape[0] - 1):
            alpha_mask_right[x][i] = round(alpha_mask_coefficient * (i / Right_fade.shape[0]))
    Right_alpha[:, :, 3] = alpha_mask_right

#   cv2.addWeighted(Right_alpha, glue_alpha, Left_alpha, 1-glue_alpha, 0)
    # fadeIn (Right_alpha, Left_alpha)

        # get image dimensions
    imgHeight, imgWidth = Right_alpha.shape[:2]

    # create empty overlay layer with 4 channels
    overlay = np.zeros((imgHeight, imgWidth, 4), dtype = "uint8")

    # draw semi-transparent red rectangle
    overlay[200:300, 0:imgWidth] = (0, 0, 255, 200)

    # Extract the RGB channels
    srcRGB = Left_alpha[...,:3]
    dstRGB = Right_alpha[...,:3]

    # Extract the alpha channels and normalise to range 0..1
    srcA = Left_alpha[...,3]/255.0
    dstA = Right_alpha[...,3]/255.0

    # Work out resultant alpha channel
    outA = srcA + dstA*(1-srcA)

    # Work out resultant RGB
    outRGB = (srcRGB*srcA[...,np.newaxis] + dstRGB*dstA[...,np.newaxis]*(1-srcA[...,np.newaxis])) / outA[...,np.newaxis]

    # Merge RGB and alpha (scaled back up to 0..255) back into single image
    midline = np.dstack((outRGB,outA*255)).astype(np.uint8)

    # midline = cv2.addWeighted(Right_alpha, glue_alpha, Left_alpha, 1-glue_alpha, 0)
    # cv2.imwrite( "mask.png", Right_alpha)
    midline = cv2.cvtColor(midline, cv2.COLOR_RGBA2RGB)
    # cv2.imshow("midline", midline)
    
    cv2.imwrite( "mask.png", midline)
    filler[:, Left1x.shape[1] - glueing_x + 2 :Left1x.shape[1] - glueing_x + midline.shape[1] - 2] = midline[:,2:-2]
    # try: 
    #     stitched = stitch(Left1x,Right1x).copy()
    # except Exception as e:
    #     print("Retaking scan")
    #     take1Xscan()
    #     Left1x=cv2.imread("data/Left.jpg", cv2.IMREAD_ANYCOLOR) 
    #     Right1x=cv2.imread("data/Right.jpg", cv2.IMREAD_ANYCOLOR) 
    #     stitched = stitch(Left1x,Right1x).copy()
    
    cv2.imwrite( "stitched.jpg", filler)
    # stitched = np.uint8(stitched)
    # height, width = stitched.shape[:-1]   
    # dst = cv2.cv.CreateMat(height, width, cv2.IMREAD_COLOR)
    return filler


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
