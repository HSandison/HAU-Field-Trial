import os
import sys
import time
from subprocess import call
from brightpi import *
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import cv2
from datetime import datetime
import subprocess
import shutil

sys.path.insert(0, '/home/pi/Camera-Control/System')
from runSystem import runSystem

t0 = time.time()

class logMode(object):
    
    def __init__(self):
        self.logsPath = '/home/pi/Camera-Control/Logs/'

    # update log
    def updateLog(self, filename, logMessage):
        cwd = os.getcwd()
        os.chdir(self.logsPath)
        timestr = time.strftime("%d%m%Y-%H%M%S")
        logfile = open(self.logsPath + filename, 'a')
        logfile.write(timestr + ": " + logMessage + "\n")
        logfile.close()
        os.chdir(cwd)
        print(logMessage)
        
class rcloneMode(object):
    
    def __init__(self):
        self.logsPath = '/home/pi/Camera-Control/Logs/'

    # copy file from dropbox
    def copyFileFromDropbox(self, dropboxPath, localPath):
        cmd = "rclone copy " + dropboxPath + " " + localPath
        call(cmd, shell=True)
        print('Copying file from dropbox')
        
    # copy file to dropbox
    def copyFileToDropbox(self, localPath, dropboxPath):
        cmd = "rclone copy " + localPath + " " + dropboxPath + " " + "--progress --log-file=/home/pi/Camera-Control/Logs/rclone-log.txt --log-level=INFO"
        print(cmd)
        call(cmd, shell=True)
        print('Copying file to dropbox')
        
class systemMode(object):

    def __init__(self):
        self.logsPath = '/home/pi/Camera-Control/Logs/'
        self.modeNum = None
        self.optionVal = None
        self.optionMessage = None
        self.pythonFile = None
    
    # get system time
    def getSystemTime(self):
        cwd = os.getcwd()
        os.chdir(self.logsPath)
        cmd = ("timedatectl >> time-log.txt")
        call(cmd, shell=True)
        os.chdir(cwd)
        print(time.strftime("%d%m%Y-%H%M%S") + ': Querying system time')
        
    # powerdown system
    def powerDown(self):
        print('Powering down Pi')
        cmd = ["/usr/bin/python /home/pi/Camera-Control/Power-Management/powerdown-new.py 60 -f 30 -r 1"]
        call(cmd, shell=True)
            
class ProcessImage(object):
    
    def __init__(self, filename, path):
        # instance attributes
        self.filename = filename
        self.path = path
        self.iwd = None
        self.roi_path = None
        self.input_data = None
        self.output_data = None
        self.masked = None
        self.thresh = None
        
    # instance method
    def create_dirs(self):
        cwd = os.getcwd()
        os.chdir(self.path)
        os.mkdir(self.filename[0:-4])
        os.chdir(self.filename[0:-4])
        self.imagedir = os.getcwd()
        print(self.imagedir)
        self.iwd = os.getcwd() # image file results path
        dir_list = ['input']
        
        for items in dir_list:
            os.mkdir(items)
            
        os.chdir(cwd)
        
    def read_image(self):
        self.input_data = cv2.imread(self.path + "/input/" + self.filename)
     
    def write_image(self):
        src_path = self.path + "/input/" + self.filename
        dst_path = self.iwd + "/input"
        shutil.copy(src_path, dst_path)
        #cv2.imwrite(self.path + self.filename  + ".jpg", self.input_data)    

# Initialise classes
logMode = logMode()
rcloneMode = rcloneMode()
systemMode = systemMode()
runSystem = runSystem()

t1 = time.time()
timetotal = t1 - t0

logMode.updateLog('system-log.txt', '\n\n')
logMode.updateLog('system-log.txt', time.strftime("%d%m%Y-%H%M%S") + ': HAU-field-trial-v1.py running')
logMode.updateLog('system-log.txt', time.strftime("%d%m%Y-%H%M%S") + ': time to initialise classes = ' + str(timetotal))


# remove input image from image capture and processing
input_dir = "/home/pi/Image-Processing/images/input/"
for f in os.listdir(input_dir):
    os.remove(os.path.join(input_dir, f))
    
input_dir = "/home/pi/Camera-Control/Image-Capture/Images/"
for f in os.listdir(input_dir):
    os.remove(os.path.join(input_dir, f))

# set system time
logMode.updateLog('system-log.txt', time.strftime("%d%m%Y-%H%M%S") + ': Setting system time')
systemMode.getSystemTime()

# take a test image
if os.path.exists("camera-test.jpg"):
    os.remove("camera-test.jpg")
else:
    print("The file doesn't exist")
    
cmd = "raspistill -o camera-test.jpg"
call(cmd, shell=True)

cwd = os.getcwd()

# does test image exist
file_name = "camera-test.jpg"

if os.path.exists(file_name):
    #print("Camera test image %s exists" %file_name)
    os.remove("camera-test.jpg")
    cam_test_log = "Camera test image successful"
    test_image = 1
else:
    #print("Camera test image %s does not exist" %file_name)
    cam_test_log = "Camera test image does not exist"
    test_image = 0

# update system log file
logfile = open('/home/pi/Camera-Control/Logs/system-log.txt', 'a')
logfile.write(time.strftime("%d%m%Y-%H%M%S") + ": CAMERA TEST: " + cam_test_log + "\n")
logfile.close()

# run system mode
runSystem.readModeNumFile()
runSystem.readSystemOptionsFile()
logMode.updateLog('system-log.txt', time.strftime("%d%m%Y-%H%M%S") + ': Initialising System Mode [' + str(runSystem.modeNum) + ']')

t0 = time.time()
runSystem.runSystemMode()
t1 = time.time()
timetotal = t1 - t0
logMode.updateLog('system-log.txt', time.strftime("%d%m%Y-%H%M%S") + ': time to runSystem.runSystemMode() = ' + str(timetotal))

# save and compress image
os.chdir('/home/pi/Image-Processing')
img_file = os.listdir('/home/pi/Image-Processing/images/input')
img_file = img_file[0]

path = "/home/pi/Image-Processing/images"
ProcessImage = ProcessImage(img_file, path)
ProcessImage.create_dirs()
ProcessImage.read_image()
ProcessImage.write_image()

#copy to dropbox
print("copying to dropbox: " + "/home/pi/Image-Processing/images/input")
call("rclone mkdir Sentomol:HAU-Trial/CAM1/" + img_file[0:-4], shell=True)
rclone_command = ['rclone', 'copy', '/home/pi/Image-Processing/images/input', 'Sentomol:HAU-Trial/CAM1/' + img_file[0:-4]]
rclone_command_as_string = ' '.join(rclone_command)
print(rclone_command_as_string)
call(rclone_command_as_string, shell=True)
# copy logs to dropbox
rcloneMode.copyFileToDropbox("/home/pi/Camera-Control/Logs/system-log.txt", "Sentomol:HAU-Trial/CAM1/Logs")

# remove input image from folder
input_dir = "/home/pi/Image-Processing/images/input/"
for f in os.listdir(input_dir):
    os.remove(os.path.join(input_dir, f))

# power down
print("Powering down")
#systemMode = systemMode()
logMode.updateLog('system-log.txt', time.strftime("%d%m%Y-%H%M%S") + ': Powering down')
time.sleep(10)
systemMode.powerDown()





