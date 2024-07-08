import glob,os,sys
import cv2 
import math
import numpy as np

scannedlist = []
scanningPlan = []
NoMagScan  = cv2.imread("data/zlepione.jpg", cv2.IMREAD_ANYCOLOR) 
img = NoMagScan.copy()
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
        x_coord = int(scan[scan.rfind("X:") + 2:scan.rfind("Y:")]) - math.floor(tmp.shape[1]/2)
        y_coord = int(scan[scan.rfind("Y:") + 2:scan.rfind("C:")]) - math.floor(tmp.shape[0]/2)
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
        x_coord = int(scan[scan.rfind("X:") + 2:scan.rfind("Y:")]) - math.floor(8)
        y_coord = int(scan[scan.rfind("Y:") + 2:scan.rfind("C:")]) - math.floor(4)
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
        
 
cv2.destroyAllWindows() # destroy all windows

# 16x9 -> rescaled 
# 3840 x 2160 orginal -> 240x magnification
# 623 x  middle 1415, 166
# 5,63 -> lacks factor of 6 times?  1408,162 -> upper right corner of scan 1422,170 -> lower left
