from multiprocessing import Manager
from multiprocessing import Process
from calc_center import Calc_Center
from pid import PID
import signal
import time
import sys
import cv2
import socket


def signal_handler(sig, frame):
    # print a status message
    print("[INFO] You pressed `ctrl + c`! Exiting...")

    # exit
    sys.exit()
    
def obj_center(objX, objY, centerX, centerY, pull_trigger):
    # signal trap to handle keyboard interrupt
    signal.signal(signal.SIGINT, signal_handler)

    #Open the first webcame device
    capture = cv2.VideoCapture(1)
    
    # initialize the object center finder
    obj = Calc_Center()
    pull_trigger.value = 0

    # loop indefinitely
    while True:
        # grab the frame from the threaded video stream
        rc, fullSizeBaseImage = capture.read()
        # calculate the center of the frame as this is where we will
        # try to keep the object
        (H, W) = fullSizeBaseImage.shape[:2]
        centerX.value = W // 2
        centerY.value = H // 2
        if objX.value == 0 and objY.value == 0:
            objX.value = centerX.value
            objY.value = centerY.value
        
        # find the object's location
        objectLoc = obj.update(fullSizeBaseImage, (centerX.value, centerY.value))
        ((objX.value, objY.value), rect) = objectLoc

        # extract the bounding box and draw it
        if rect is not None:
            (x, y, w, h) = rect
            cv2.rectangle(fullSizeBaseImage, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if objX.value - centerX.value < W * 0.05 and objY.value - centerY.value < H * 0.05 and rect is not None:
                pull_trigger.value = 1
        else:
                pull_trigger.value = 0
        # display the frame to the screen
        
        cv2.imshow("Body Tracking", fullSizeBaseImage)
        cv2.waitKey(1)
        
def pid_process (output, p, i, d, obj_coord, center_coord):
    # signal trap to handle keyboard interrupt
    signal.signal(signal.SIGINT, signal_handler)
    
    # initialize PID
    p = PID(p.value, i.value, d.value)
    
    while True:
        error = center_coord.value - obj_coord.value
        output.value = int(p.update(error))


def send_servo_data (pan, tlt, pull_trigger):
    signal.signal(signal.SIGINT, signal_handler)

    server_ip = '192.168.4.204'
    port = 5000  # Choose a port number (above 1024)
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object
    client_socket.connect((server_ip, port))

    while True:
        time.sleep(0.1)
        panAngle = pan.value
        tltAngle = tlt.value
        
        angles = f'{panAngle} {tltAngle} {pull_trigger.value}'
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
        panP = manager.Value("f", 0.015)
        panI = manager.Value("f", 0.01)
        panD = manager.Value("f", 0.001)
        
        # set PID values for tilting
        tiltP = manager.Value("f", 0.0125)
        tiltI = manager.Value("f", 0.009)
        tiltD = manager.Value("f", 0.001)
        
        pull_trigger = manager.Value("i", 0)

        processObjectCenter = Process(target=obj_center,
            args=(objX, objY, centerX, centerY, pull_trigger))
        processPanning = Process(target=pid_process,
            args=(pan, panP, panI, panD, objX, centerX))
        processTilting = Process(target=pid_process,
            args=(tlt, tiltP, tiltI, tiltD, objY, centerY))
        processSetServos = Process(target=send_servo_data, args=(pan, tlt, pull_trigger))
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
        

