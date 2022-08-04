import copy
import time

import os
import cv2 as cv
from base_camera import BaseCamera

from pupil_apriltags import Detector

from pupil_labs.realtime_api.simple import discover_one_device
from pupil_labs.realtime_api.simple import Device

from utils import *

at_detector = Detector(
    families='tag36h11',
    nthreads=1,
    quad_decimate=2.0,
    quad_sigma=0.0,
    refine_edges=1,
    decode_sharpening=0.25,
    debug=0,
)

class Camera(BaseCamera):
    video_source = None

    def __init__(self):
        self.set_video_source()
        super(Camera, self).__init__()


    @staticmethod
    def set_video_source():
        print("Looking for a device")
        Camera.video_source = Device("pi.local", 8080)
        if Camera.video_source is None:
            print("No device found.")
            raise SystemExit(-1)
        print(f"Connecting to {Camera.video_source}...")      


    @staticmethod
    def frames():

        while True:

            frame, gaze = Camera.video_source.receive_matched_scene_video_frame_and_gaze()
            image = frame.bgr_pixels

            # main part of code
            img_copy = copy.deepcopy(image)

            img_copy = cv.cvtColor(img_copy, cv.COLOR_BGR2GRAY)
            tags = at_detector.detect(
                img_copy,
                estimate_tag_pose=False,
                camera_params=None,
                tag_size=None,
            )
            if(len(tags) != 4):
                continue

            mapped_image, mapped_gaze = perspective_mapper(
                tags, image, gaze, maxWidth=500, maxHeight=400)

            #print(mapped_gaze)
            cv.circle(
                mapped_image,
                (int(mapped_gaze[0][0][0]), int(mapped_gaze[0][0][1])),
                # (50, 50),
                radius=30,
                color=(0, 0, 255),
                thickness=10,
            )

            yield cv.imencode('.jpg', mapped_image)[1].tobytes()

