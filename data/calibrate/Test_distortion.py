import numpy as np
import cv2 as cv
import glob
import os
import time

os.chdir("C:/Users/kamci/Desktop/Microwizard_software/micoscope_code/data/calibrate")
# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
cam_port = 0
cam = cv.VideoCapture(cam_port, cv.CAP_DSHOW) 
cam.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((8*5,3), np.float32)
objp[:,:2] = np.mgrid[0:8,0:5].T.reshape(-1,2)
 
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
 
# images = glob.glob('*.jpg')
correct = 0
while True: 
#  ret, img = cam.read() 
 img =  cv.imread("calib.jpg")
 cv.imshow('img', img)
 cv.waitKey(100)
 imgbackup = img.copy()
 gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
 
 # Find the chess board corners
 ret, corners = cv.findChessboardCorners(gray, (8,5), None)
 
 # If found, add object points, image points (after refining them)
 if ret == True:
    objpoints.append(objp)

    
    corners2 = cv.cornerSubPix(gray,corners, (1,1), (-1,-1), criteria)
    imgpoints.append(corners2)
 

# Draw and display the corners
    # cv.imwrite(str(time.localtime()) + ".jpg", imgbackup) 
    cv.drawChessboardCorners(img, (8,5), corners2, ret)
    cv.imshow('img', img)
    cv.waitKey(100)
    
    cv.destroyAllWindows()

    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    h, w = img.shape[:2]
    newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
    max_error = 1
    # undistort
    dst = cv.undistort(img, mtx, dist, None, newcameramtx)
    h, w = img.shape[:2]
    print(mtx, dist,newcameramtx, roi)
    # crop the image
    x, y, w, h = roi
    dst = dst[y:y+h, x:x+w]
    mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)/len(imgpoints2)
    mean_error += error
    
    if max_error > mean_error/len(objpoints):
       print( "total error: {}".format(mean_error/len(objpoints)) )
       max_error = mean_error/len(objpoints)
       parameters = "Dist: " + str(dist) + "cameramtx: " + str(newcameramtx) + "ROI: " + str(roi) + "MTX: " + str(mtx)
       f = open("parameters.txt", "a")
       f.write(parameters)
       f.close()
       cv.imwrite( "calibrated" + str(time.localtime())  +".jpg", dst)