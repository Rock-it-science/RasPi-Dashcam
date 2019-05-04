import sys
import os

#Camera setup
import picamera
camera = picamera.PiCamera()
camera.resolution = (1280, 720)

counter = 0  # counts number of video files
# TODO Read/write counter from/to file so it doesn't reset every time the program is ran

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
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)