

# program to capture single image from webcam in python 
  
# importing OpenCV library 
import serial
import time
import cv2 as cv
# initialize the camera 
# If you have multiple camera connected with  
# current device, assign a value in cam_port  
# variable according to that 
cam_port = 0
cam = cv.VideoCapture(cam_port) 
def readCamera(coordinates):
    # reading the input using the camera 
    result, image = cam.read() 
    
    # If image will detected without any error,  
    # show result 
    if result: 
        
        # cv.rectangle(image, (33,33), (531,453), (255,0,0),2)
        # showing result, it take frame name and image  
        # output 
        image = image[21:501, 21:501]
        #cv.imshow("capture", image) 
    
        # saving image in local storage 
        cv.imwrite("pic/" + coordinates + ".png", image) 
    
        # If keyboard interrupt occurs, destroy image  
        # window  
        #cv.destroyWindow("capture") 
    
    # If captured image is corrupted, moving to else part 
    else: 
        print("No image detected. Please! try again") 

glass_Y_top = 6000
glass_Y_bottom = -89000
glass_X_min = -418500
glass_X_max = -197500
scan_step = 1500
current_Z = 0
where = "test"


with serial.Serial() as ser:
    #readCamera("Tst")
    ser.port = '/dev/ttyACM0'
    ser.baudrate = 9600
    ser.timeout=0.1
    #ser.parity=serial.PARITY_EVEN
    #ser.rtscts=1
    ser.open()
    while True:
        time.sleep(5)
        #ser.write(bytes("G28 X Y;", 'utf-8'))
        output = ser.readline().decode().strip()
        while output != "00Ready" :
            if output:
                print(output)
            output = ser.readline().decode().strip()
        print(output)

        #ser.write(b'M114')
        def waitforcommand(command):
            output = ser.readline().decode().strip()
            while output != command :
                if output:
                    print(output)
                output = ser.readline().decode().strip()
                time.sleep(0.1)

        #waitforcommand("ok")

        ser.write(bytes("G28 X Y;", 'utf-8'))
        waitforcommand("Done")
        print("Zeroed X & Y")

        glass_X_temp = glass_X_min

        while glass_X_temp < glass_X_max:
            glass_Y_temp = glass_Y_top
            print("To the bottom")
            while glass_Y_temp > glass_Y_bottom:
                command = "G0 X: " + str(glass_X_temp) + " Y: " + str(glass_Y_temp) + " Z: " + str(current_Z) + " ;"
                ser.write(bytes(command, 'utf-8'))
                waitforcommand(command + " Done")
                readCamera(command)
                glass_Y_temp -= scan_step
            print("To the top")
            glass_X_temp += scan_step
            while glass_Y_temp < glass_Y_top:
                command = "G0 X: " + str(glass_X_temp) + " Y: " + str(glass_Y_temp) + " Z: " + str(current_Z) + " ;"
                ser.write(bytes(command, 'utf-8'))
                waitforcommand(command + " Done")
                readCamera(command)
                glass_Y_temp += scan_step
            
            glass_X_temp += scan_step
        print("Scan done")


