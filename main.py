import os
import RPi.GPIO as GPIO
import shutil
import sys
import time

#Camera setup
import picamera
camera = picamera.PiCamera()
camera.resolution = (1280, 720)

# GPIO setup for button and LED
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.OUT)

'''
# Get counter from counter.txt
file = open("counter.txt", "r")
counter = int(file.read())  # counts number of video files
file.close()
'''
counter = 0

while True:
    try:
        # Set file name for current video segment
        segName = 'vids/dash'+str(counter)+'.h264'
        # Start recording
        camera.start_recording(segName)
        print('now recording')

        # Record, but stop if button is pressed
        recordTime = 5 # Set this to how many seconds to make each segment
        while recordTime > 0:
            print("Button pressed, saving last and current file to /vids/saved")
            GPIO.output(12, GPIO.HIGH)  # Turn on LED
            camera.wait_recording(1)
            if GPIO.input(10) == GPIO.HIGH:
                print("Button pressed, saving files to /vids/saved")
                camera.stop_recording()
                # Lock in current file and last one
                files = os.listdir('vids')
                for f in files:
                    shutil.move('vids' + f, 'vids/saved')
            GPIO.output(12, GPIO.LOW)  # Turn off LED
            recordTime -= 1  # Decrement recordTime

        # Stop recording
        camera.stop_recording()
        print('recording stopped, and segment saved as '+segName)

        # Delete file counter-2 if it exists
        if counter > 1:
            os.remove("vids/dash"+str(counter-2)+".h264")
            print("removed: vids/dash"+str(counter-2)+".h264")

        counter += 1  # Decrement counter

    except KeyboardInterrupt:
        print('interrupted, saving last segment and exiting')
        camera.stop_recording()
        '''
        # write counter to file
        file = open("counter.txt", "w")
        file.write(str(counter))
        file.close()
        '''
        # Exit
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)