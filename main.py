import datetime
import os
import picamera
import RPi.GPIO as GPIO
import sys
import shutil
import time

# Camera setup
camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.rotation = 180

# GPIO setup for button and LED
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.OUT)
# Make sure LED starts off (sometimes when program exits unexpectedly LED will stay on after program terminates)
GPIO.output(12, GPIO.LOW)

# Get date and time for file names
now = datetime.datetime.now()
segName = now.strftime("%Y-%m-%d %H:%M")+'.h264'

# Function for getting names of files in 'vids' folder
def getVids():
    path = 'vids/'
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            files.append(os.path.join(r, file))
    return files

# Main loop for recording
while True:
    # Start recording to 'vids' directory
    camera.start_recording("vids/"+segName)
    print('now recording')

    # Start recording, but stop if button is pressed
    recordTime = 600  # Seconds per segment (approximately, actual time will be slightly longer)
    while recordTime > 0:

        try:
            camera.wait_recording(1)
        except:
            camera.stop_recording()
            sys.exit('Keyboard interrupt')

        if GPIO.input(10) == GPIO.HIGH:
            print("Button pressed, saving last and current file")
            GPIO.output(12, GPIO.HIGH)  # Turn on LED

            # Split recording, saving footage up to this point to 'saved' directory
            camera.split_recording('vids/saved/'+segName)

            # Move most recent file in vids to 'saved' folder
            files = getVids()  # Get names of files in vids
            recent = files[-1]  # Get most recent file
            shutil.move("/home/pi/projects/RasPi-Dashcam/vids/"+recent, "/home/pi/projects/RasPi-Dashcam/vids/saved/"+recent)  # move file into 'saved' directory (TODO change this to relative path)

            time.sleep(0.5)  # Add a small buffer so button press doesn't overlap with next check for button check

        recordTime -= 1  # Decrement recordTime

    # Segment time-out, stop recording
    camera.stop_recording()
    print('segment time-out, saving as '+segName)

    # If there are more than 2 files in the vids folder, delete the oldest one
    files = getVids()
    os.remove(files[0])

    # Make sure LED is off
    GPIO.output(12, GPIO.LOW)