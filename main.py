import os
import RPi.GPIO as GPIO
import shutil
import sys
import time

#Camera setup
import picamera
camera = picamera.PiCamera()
camera.resolution = (1280, 720)
camera.rotation = 180

# GPIO setup for button and LED
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.OUT)


# Get counter from counter.txt
file = open("counter.txt", "r")
counter = int(file.read())+1  # counts number of video files
file.close()

while True:
    # Set file name for current video segment
    segName = 'vids/dash'+str(counter)+'.h264'
    # Start recording
    camera.start_recording(segName)
    print('now recording')

    # Record, but stop if button is pressed
    recordTime = 600  # Set this to how many seconds to make each segment
    while recordTime > 0:

        camera.wait_recording(1)

        if GPIO.input(10) == GPIO.HIGH:
            print("Button pressed, saving last and current file to usb drive")
            GPIO.output(12, GPIO.HIGH)  # Turn on LED
            camera.stop_recording()  # Stop recording

            # Lock in current file and last one
            files = os.listdir('vids')
            try:
                for f in files:
                    shutil.move('vids/' + f, '../../../../media/usb')
            except:
                print('Video already saved')

            time.sleep(0.5)  # Add a small buffer so button press doesn't overlap with next check for button check
            GPIO.output(12, GPIO.LOW)  # Turn off LED

            # Start recording again
            camera.start_recording(segName)
            print('now recording')

        recordTime -= 1  # Decrement recordTime

    # Stop recording
    camera.stop_recording()
    print('recording stopped, and segment saved as '+segName)

    # Delete file counter-2 if it exists
    try:
        os.remove("vids/dash"+str(counter-2)+".h264")
        print("removed: vids/dash"+str(counter-2)+".h264")
    except OSError:
        pass
    counter += 1  # Increment counter

    # write counter to file
    file = open("counter.txt", "w")
    file.write(str(counter))
    file.close()

    # Make sure LED is off
    GPIO.output(12, GPIO.LOW)

