# HAU-Field-Trial
Files for HAU field trial September 2023

These files have been created following an email discussion with David Loughlin of Sentomol.
He requested to send 5 units, initially, to HAU.
The units have been programmed to capture an image every 60 minutes, archive the image, then upload via Rclone to a dropbox directory.
The 5 units have names CAM1, CAM2, ... , CAM5.
This file was created by Helen Sandison on 8th September 2023.
An overnight test was run with a battery to check that the program run correctly and the battery and power/timer switch was working.
All image processing and classification has been removed for this trial.

HOW TO RUN 
The system is programmed to wake up every 60 minutes, capture an image, upload the image to dropbox via WiFi, then shut down and sleep.
A crontab is set up to run 'HAU-field-trial-v1.py' when the system boots up.
The main python file 'HAU-field-trial-v1.py' is stored in the folder /home/pi/HAU-Field-Trial.
Images are stored in the folder: /home/pi/Image-Processing/images
The folder is named by the timestamp, e.g. img-070923-124521 - where the timestamp is interpreted as: img-DDMMYY-HHMMSS
The image will be found in this folder with the same timestamp.

DROPBOX
The images will be uploaded to a dropbox folder.
This can be accessed by going to dropbox.com
Login: cam0001.sentomol@gmail.com
Password: pineweevil0001

There is a folder 'HAU-Trial', then folders 'CAM1', 'CAM2', etc, for each of the 5 units.
In each folder, you can find the Image folders with the same timestamp as above.
There is also a 'Logs' folder which contains info on the system performance.

