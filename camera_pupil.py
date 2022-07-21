import os
import cv2 as cv
from base_camera import BaseCamera

from pupil_labs.realtime_api.simple import discover_one_device
import time

class Camera(BaseCamera):
    video_source = 0

    def __init__(self):
        super(Camera, self).__init__()


    @staticmethod
    def set_video_source():
        print("Looking for a device")
        Camera.video_source = discover_one_device(max_search_duration_seconds=10)
        if Camera.video_source is None:
            print("No device found.")
            raise SystemExit(-1)
        print(f"Connecting to {Camera.video_source}...")      


    @staticmethod
    def frames():

        while True:

            start_time = time.time()
            frame, gaze = Camera.video_source.receive_matched_scene_video_frame_and_gaze()
            image = frame.bgr_pixels
            yield cv.imencode('.jpg', image)[1].tobytes()