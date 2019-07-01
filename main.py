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

# Function for getting names of files in 'vids' folder
def getVids():
    path = 'vids/'
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            files.append(os.path.join(r, file))
    files.sort()
    return files


# Flash LED to show program is running
GPIO.output(12, GPIO.HIGH)
time.sleep(0.2)
GPIO.output(12, GPIO.LOW)

# Main loop for recording
while True:
    # Get/update date and time for file names
    now = datetime.datetime.now()
    segName = now.strftime("%Y-%m-%d_%H-%M-%S") + '.h264'

    # Start recording to 'vids' directory
    camera.start_recording("vids/"+segName)
    print('now recording')

    # Start recording, but stop if button is pressed
    recordTime = 10  # Seconds per segment (approximately, actual time will be slightly longer)
    while recordTime > 0:

        try:
            camera.wait_recording(1)
        except:
            camera.stop_recording()
            sys.exit('Keyboard interrupt')

        if GPIO.input(10) == GPIO.HIGH:
            print("Button pressed, saving last and current file")
            GPIO.output(12, GPIO.HIGH)  # Turn on LED

            # Split recording, saving footage up to this point to flash drive
            camera.split_recording('/media/usb/'+segName)

            # Move 2 most recent files in vids to flash drive
            files = getVids()  # Get names of files in vids

            # move recent file into flash drive
            shutil.move(files[-1], r'/media/usb/')
            # Check if there is more than one file in 'vids' (2 kinda means 1 because one extra clip autosaves)
            if len(files) > 2:
                shutil.move(files[-2], r'/media/usb/')
                # because of autosaving extra clip, do one more to ensure at least 1 full clip is saved
                shutil.move(files[-3], r'/media/usb/')

            time.sleep(0.5)  # Add a small buffer so button press doesn't overlap with next check for button check

            GPIO.output(12, GPIO.LOW)  # Turn off LED

        recordTime -= 1  # Decrement recordTime

    # Segment time-out, stop recording
    camera.stop_recording()
    print('segment time-out, saving as '+segName)

    # If there are more than 3 files in the vids folder, delete the oldest one
    files = getVids()
    if len(files) > 3:
        os.remove(files[0])

    # Make sure LED is off
    GPIO.output(12, GPIO.LOW)
