from datetime import datetime
import os
import picamera
import RPi.GPIO as GPIO
import sys
import shutil
import time

'''
Known issues:
 - hung on exporting files to usb

'''

# Logging setup
logFile = open("log.txt", "a")
logFile.write("\n" + str(datetime.now()) + "    Initializing\n")

# Camera setup
try:
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
except:
    logFile.write(str(datetime.now()) + "    Failure in setup\n")
    sys.exit('Failure in setup')

# Function for getting names of files in 'vids' folder
def getVids():
    path = 'vids/'  # path to 'vids' folder
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            files.append(os.path.join(r, file))
    files.sort()
    return files


# Flash LED to show program is running
GPIO.output(12, GPIO.HIGH)
time.sleep(0.5)
GPIO.output(12, GPIO.LOW)

logFile.write(str(datetime.now()) + "    Initialization complete\n")

# Main loop for recording
while True:
    # Get/update date and time for file names
    now = datetime.now()
    segName = now.strftime("%Y-%m-%d_%H-%M-%S") + '.h264'

    # Start recording to 'vids' directory
    camera.start_recording('vids/' + segName)  # Path to 'vids' folder

    # Start recording, but stop if button is pressed
    recordTime = 600  # Seconds per segment (approximately, actual time will be slightly longer)
    print('now recording')
    logFile.write(str(datetime.now()) + "    Recording started, file name: " + segName + "\n")
    while recordTime > 0:
        try:
            camera.wait_recording(1)
        except:
            camera.stop_recording()
            logFile.write(str(datetime.now()) + "    Exit due to keyboard interrupt\n")
            logFile.close()
            sys.exit('Keyboard interrupt')

        if GPIO.input(10) == GPIO.HIGH:
            logFile.write(str(datetime.now()) + "    Registered button press\n")
            print("Button pressed, saving last and current file")
            GPIO.output(12, GPIO.HIGH)  # Turn on LED
            try: # Export to usb drive
                # Split recording, saving footage up to this point to flash drive
                camera.split_recording('/media/usb/'+segName)

                # Move 2 most recent files in vids to flash drive
                files = getVids()  # Get names of files in vids

                # copy recent file into flash drive
                shutil.copy(files[-1], '/media/usb/')
                # Check if there is more than one file in 'vids' (2 kinda means 1 because one extra clip autosaves)
                if len(files) > 1:
                    shutil.copy(files[-2], '/media/usb/')
                if len(files) > 2:
                    # because of autosaving extra clip, do one more to ensure at least 1 full clip is saved
                    shutil.copy(files[-3], '/media/usb/')

                logFile.write(str(datetime.now()) + "    Saved clip " + segName + ", continuing to record\n")
                print('Saved clip ' + segName + ', continuing to record')
                
                # New segment name
                segName = now.strftime("%Y-%m-%d_%H-%M-%S") + '.h264'

                # Add a small buffer so button press doesn't overlap with next check for button check
                time.sleep(0.5)

            except Exception as e: # Error in exporting
                logFile.write(str(datetime.now()) + "    Error exporting file " + segName + e +"\n")
                print("Error exporting file")
                # Flash LED 5 times
                for x in range(5):
                    GPIO.output(12, GPIO.LOW)
                    time.sleep(0.5)
                    GPIO.output(12, GPIO.HIGH)
                    time.sleep(0.5)
                exit()

            GPIO.output(12, GPIO.LOW)  # Turn off LED

        recordTime -= 1  # Decrement recordTime

    # Segment time-out, stop recording
    camera.stop_recording()
    print('segment time-out, saving as '+segName)
    logFile.write(str(datetime.now()) + "    Segment time-out saving " + segName + "\n")

    # If there are more than 3 files in the vids folder, delete the oldest one
    files = getVids()
    if len(files) > 3:
        logFile.write(str(datetime.now()) + "    Removing file " + str(files[0]) + "\n")
        print('removing '+str(files[0]))
        os.remove(files[0])

    # Make sure LED is off
    GPIO.output(12, GPIO.LOW)

    # Repeat loop
