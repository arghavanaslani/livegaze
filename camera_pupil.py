import os
import cv2 as cv
from base_camera import BaseCamera

from pupil_labs.realtime_api.simple import discover_one_device, discover_devices
from pupil_labs.realtime_api.simple import Device
import time

class Camera(BaseCamera):
    video_source = None

    def __init__(self):
        self.set_video_source()
        super(Camera, self).__init__()


    @staticmethod
    def set_video_source(phone_ip):
        print("Looking for a device")
        # Camera.video_source = Device("pi.local", 8080)
        # devicesFound = discover_devices(10)
        device1 = Device(phone_ip, 8080)
        Camera.video_source = discover_devices(10)
        if Camera.video_source is None:
            print("No device found.")
            raise SystemExit(-1)
        print(f"Connecting to {Camera.video_source}...")      


    @staticmethod
    def frames():
        while True:
            #start_time = time.time()
            frame, gaze = Camera.video_source.receive_matched_scene_video_frame_and_gaze()
            image = frame.bgr_pixels
            yield (image, gaze)
