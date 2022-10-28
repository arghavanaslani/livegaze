#!/usr/bin/env python
from importlib import import_module
import os
import cv2 as cv
import copy
import time
from flask import Flask, render_template, Response
from pupil_apriltags import Detector
from utils import *

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

at_detector = Detector(
    families='tag36h11',
    nthreads=1,
    quad_decimate=2.0,
    quad_sigma=0.0,
    refine_edges=1,
    decode_sharpening=0.25,
    debug=0,
)


app = Flask(__name__)


@app.route('/')
def index():
    """Home Page."""
    return render_template("index.html")


@app.route('/world_view')
def world():
    """World view page"""
    return render_template("world_view.html")


@app.route('/mapped_view')
def mapped():
    """Mapped view page"""
    return render_template("mapped.html")

#world view 
def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame, gaze = camera.get_frame()
        image = cv.imencode('.jpg', frame)[1].tobytes()
        yield b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n--frame\r\n'

#mapped
def gen_mapped(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'

    while True:
        frame, gaze = camera.get_frame()
        img_copy = copy.deepcopy(frame)
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
            tags, frame, gaze, maxWidth=500, maxHeight=400)

        #print(mapped_gaze)
        cv.circle(
            mapped_image,
            (int(mapped_gaze[0][0][0]), int(mapped_gaze[0][0][1])),
            # (50, 50),
            radius=30,
            color=(0, 0, 255),
            thickness=10,
        )
        image = cv.imencode('.jpg', mapped_image)[1].tobytes()
        yield b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n--frame\r\n'


@app.route('/video_feed/<phone_id>')
def video_feed(phone_id):
    """Video streaming route. Put this in the src attribute of an img tag."""
    Camera.set_video_source(phone_id)
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_mapped')
def video_feed_mapped():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_mapped(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(threaded=True)
