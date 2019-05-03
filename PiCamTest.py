from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.start_recording('')
sleep(5)
camera.stop_recording()