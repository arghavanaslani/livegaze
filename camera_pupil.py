import os
import cv2 as cv
from base_camera import BaseCamera

from pupil_labs.realtime_api.simple import discover_one_device, discover_devices
from pupil_labs.realtime_api.simple import Device
import time

class Camera(BaseCamera):
    video_source = None

    def __init__(self, camera_device = None):
        self.set_video_source(camera_device)
        super(Camera, self).__init__(camera_device.phone_id)


    @staticmethod
    def set_video_source(camera_device = None):
        print(f"Connecting to {camera_device}...")      
        Camera.video_source = camera_device
        if Camera.video_source is None:
            print("No device found.")
            raise SystemExit(-1)
        print(f"Successful! Platform is connected to {Camera.video_source}...")      


    @staticmethod
    def frames():
        while True:
            start_time = time.time()
            frame, gaze = Camera.video_source.receive_matched_scene_video_frame_and_gaze()
            image = frame.bgr_pixels
            yield (image, gaze)
