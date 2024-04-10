from multiprocessing import Manager
from multiprocessing import Process
from calc_center import Calc_Center
from pid import PID
import signal
import time
import sys
import cv2
import socket

servoRange = (-90, 90)
def signal_handler(sig, frame):
    # print a status message
    print("[INFO] You pressed `ctrl + c`! Exiting...")

    # exit
    sys.exit()
    
def obj_center(objX, objY, centerX, centerY):
    # signal trap to handle keyboard interrupt
    signal.signal(signal.SIGINT, signal_handler)

    #Open the first webcame device
    capture = cv2.VideoCapture(1)
    
    # initialize the object center finder
    obj = Calc_Center()

    
    # loop indefinitely
    while True:
        # grab the frame from the threaded video stream
        rc, fullSizeBaseImage = capture.read()
        # calculate the center of the frame as this is where we will
        # try to keep the object
        (H, W) = fullSizeBaseImage.shape[:2]
        centerX.value = W // 2
        centerY.value = H // 2
        
        # find the object's location
        objectLoc = obj.update(fullSizeBaseImage, (centerX.value, centerY.value))
        ((temp_x, temp_y), rect) = objectLoc

        # extract the bounding box and draw it
        if rect is not None:
            objX.value = int(temp_x)
            objY.value = int(temp_y)

            (x, y, w, h) = rect
            cv2.rectangle(fullSizeBaseImage, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # display the frame to the screen
        
        cv2.imshow("Body Tracking", fullSizeBaseImage)
        cv2.waitKey(1)
        
def pid_process (output, p, i, d, obj_coord, center_coord):
    # signal trap to handle keyboard interrupt
    signal.signal(signal.SIGINT, signal_handler)
    
    # initialize PID
    p = PID(p.value, i.value, d.value)
    
    while True:
        if (obj_coord.value != 0):
            error = center_coord.value - obj_coord.value
            output.value = int(p.update(error))
        
def in_range (angle, start, end):
    return (start <= angle) and (angle <= end)

def send_servo_data (pan, tlt):
    signal.signal(signal.SIGINT, signal_handler)

    server_ip = '192.168.4.204'
    port = 5000  # Choose a port number (above 1024)
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object
    client_socket.connect((server_ip, port))

    while True:
        time.sleep(0.2)
        # the pan and tilt angles are reversed
        panAngle = pan.value
        tltAngle = tlt.value
        
        if in_range(panAngle, servoRange[0], servoRange[1]) and in_range(tltAngle, servoRange[0], servoRange[1]):
            angles = f'{panAngle} {tltAngle}'
            client_socket.send(bytes(angles, "utf-8"))


if __name__ == '__main__':
    
    # Adding process safe variable, "i" denotes that value is integer, "f" -> float
    with Manager() as manager:
        # enable the servos
                
        # set integer values for the object center (x, y)-coordinates
        centerX = manager.Value("i", 0)
        centerY = manager.Value("i", 0)
        
        # set integer values for the object's (x, y)-coordinates
        objX = manager.Value("i", 0)
        objY = manager.Value("i", 0)

        # pan and tilt values will be managed by independed PIDs
        pan = manager.Value("i", 0)
        tlt = manager.Value("i", 0)
        
        # set PID values for panning, these are the constants
        panP = manager.Value("f", 0.07)
        panI = manager.Value("f", 0.008)
        panD = manager.Value("f", 0.00006)
        
        # set PID values for tilting
        tiltP = manager.Value("f", 0.06)
        tiltI = manager.Value("f", 0.007)
        tiltD = manager.Value("f", 0.00005)
        

        processObjectCenter = Process(target=obj_center,
            args=(objX, objY, centerX, centerY))
        processPanning = Process(target=pid_process,
            args=(pan, panP, panI, panD, objX, centerX))
        processTilting = Process(target=pid_process,
            args=(tlt, tiltP, tiltI, tiltD, objY, centerY))
        processSetServos = Process(target=send_servo_data, args=(pan, tlt))
        # start all 4 processes
        processObjectCenter.start()
        processPanning.start()
        processTilting.start()
        processSetServos.start()
        # join all 4 processes
        processObjectCenter.join()
        processPanning.join()
        processTilting.join()
        processSetServos.join()
        

