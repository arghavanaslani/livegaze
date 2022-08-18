#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response

from pupil_apriltags import Detector

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

# this part has been commented and will be uncommented after testing
# at_detector = Detector(
#     families='tag36h11',
#     nthreads=1,
#     quad_decimate=2.0,
#     quad_sigma=0.0,
#     refine_edges=1,
#     decode_sharpening=0.25,
#     debug=0,
# )


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


def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = camera.get_frame()
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'

# this part has been commented and will be uncommented after testing
# def gen_mapped(camera):
#     """Video streaming generator function."""
#     yield b'--frame\r\n'
#     while True:
#         frame = camera.get_frame()
#         yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(threaded=True)
