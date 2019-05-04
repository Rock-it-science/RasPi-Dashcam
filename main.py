import sys
import os

#Camera setup
import picamera
camera = picamera.PiCamera()
camera.resolution = (1280, 720)

# Get counter from counter.txt
file = open("counter.txt", "r")
counter = int(file.read())  # counts number of video files
file.close()

while True:
    try:
        # Set file name for current video segment
        segName = 'vids/dash'+str(counter)+'.h264'
        # Start recording
        camera.start_recording(segName)
        print('now recording')
        camera.wait_recording(5)  # Continue recording for 10 seconds
        # Stop recording
        camera.stop_recording()
        print('recording stopped, and segment saved as '+segName)
        counter += 1
    except KeyboardInterrupt:
        print('interrupted, saving last segment and exiting')
        camera.stop_recording()
        # write counter to file
        file = open("counter.txt", "w")
        file.write(str(counter))
        file.close()
        # Exit
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)