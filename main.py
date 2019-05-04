#Camera setup
import picamera
camera = picamera.PiCamera()
camera.resolution = (1280, 720)

counter = 0  # counts number of video files
while True:
    # Set file name for current video segment
    segName = 'dash'+str(counter)+'.h264'
    # Start recording
    camera.start_recording(segName)
    print('now recording')
    camera.wait_recording(5)  # Continue recording for 10 seconds
    # Stop recording
    camera.stop_recording()
    print('recording stopped, and segment saved as '+segName)
    counter += 1


