# import imp
from flask import Flask, render_template, Response, stream_with_context

from pupil_labs.realtime_api.simple import discover_devices
import cv2 as cv
import copy
from pupil_apriltags import Detector
from utils import *
import json
import time
import threading
import random

thread = None

app = Flask(__name__)

print("Searching for cameras...")
cameras = discover_devices(search_duration_seconds=5.0)


number_of_cameras = len(cameras)

print(number_of_cameras , " device(s) connected.")

frame_of_each_camera = [None] * number_of_cameras
gaze_of_each_camera = [None] * number_of_cameras


# for testing

print(cameras)

@app.route('/', methods=["GET"])
def index():
    return render_template('demo.html', camera_ids = number_of_cameras)


# @app.route('/scene')
# def scene():
#     """world view page"""
#     return render_template("scene.html", camera_ids = number_of_cameras)


# @app.route('/transformed')
# def transformed():
#     """Mapped view page"""
#     return render_template("transformed.html", camera_ids = number_of_cameras)


# @app.route('/livcanv')
# def livcanv():
#     """Living canvas"""
#     return render_template("livcanv.html")


# @app.route('/main.js')
# def script():
#     return render_template('main.js')

@app.route('/devices_info/<string:id>/')
def devices_info_feed(id):
    def send_devices_info(id):
        device = cameras[int(id)]

        info_data = json.dumps({"phone_name": device.phone_name, "battery_level": device.battery_level_percent})
        yield f"id: {id}\ndata: {info_data}\nevent: device_info\n\n"
        time.sleep(60)
    return Response(send_devices_info(id), mimetype='text/event-stream')


@app.route('/video_feed/<string:id>/', methods=["GET"])
def video_feed(id):
    return Response(gen_frames(id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/mapped_gaze_feed/<string:id>/')
def mapped_gaze_feed(id):
    return Response(gen_mapped_gaze(int(id)), mimetype='text/event-stream')



# def detect_april_tags(frame):
#     at_detector = Detector(
#         families='tag36h11',
#         nthreads=2,
#         quad_decimate=2.0,
#         quad_sigma=0.0,
#         refine_edges=1,
#         decode_sharpening=0.25,
#         debug=0)
#     image = frame.bgr_pixels
#     img_copy = copy.deepcopy(image)
#     img_copy = cv.cvtColor(img_copy, cv.COLOR_BGR2GRAY)
#     tags = at_detector.detect(
#         img_copy,
#         estimate_tag_pose=False,
#         camera_params=None,
#         tag_size=None
#         )
#     return tags

at_detector = Detector(
        families='tag36h11',
        nthreads=4,
        quad_decimate=2.0,
        quad_sigma=0.0,
        refine_edges=1,
        decode_sharpening=0.25,
        debug=0)

sem = threading.Semaphore()
def gen_mapped_gaze(camera_id):
    while True:
        tags = []
        try:
            sem.acquire()
            frame = frame_of_each_camera[int(camera_id)]
            gaze = gaze_of_each_camera[int(camera_id)]

            image = frame.bgr_pixels

            img_copy = copy.deepcopy(image)
            img_copy = cv.cvtColor(img_copy, cv.COLOR_BGR2GRAY)
            tags = at_detector.detect(
                img_copy,
                estimate_tag_pose=False,
                camera_params=None,
                tag_size=None,
        )
        except:
            print("Error in April tags detection")
        
        finally:
            sem.release()
            if(len(tags) == 4):
                print("4 april tags are detected camera id: " + str(camera_id) )
                mapped_gaze = get_mapped_gaze(tags, gaze)
                gaze_data = json.dumps({"x":mapped_gaze[0], "y":mapped_gaze[1]})
                print(gaze_data)

                yield f"id: {camera_id}\ndata: {gaze_data}\nevent: mapped_gaze\n\n"
            else:
                gaze_data = json.dumps({"x":-30, "y":-30})

                yield f"id: {camera_id}\ndata: {gaze_data}\nevent: mapped_gaze\n\n"


            time.sleep(0.03333)
        





def gen_frames(camera_id):
     
    device = cameras[int(camera_id)]
 
    while True:
        frame, gaze = device.receive_matched_scene_video_frame_and_gaze()
        frame_of_each_camera[int(camera_id)] = frame
        gaze_of_each_camera[int(camera_id)] = gaze
        cv.circle(
                frame.bgr_pixels,
                (int(gaze.x), int(gaze.y)),
                radius=80,
                color=(0, 0, 255),
                thickness=15,
            )
        image = frame.bgr_pixels
        params = [cv.IMWRITE_JPEG_QUALITY, 50,  cv.IMWRITE_JPEG_OPTIMIZE, 1]
        image = cv.imencode('.jpg', image, params)[1].tobytes()
        yield b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n--frame\r\n'  # concat frame one by one and show result



# def gen_gaze_test(id):
#     while True:
#         gaze = (gaze_of_each_camera[int(id)])

#         gaze_data = json.dumps({"x":gaze.x, "y":gaze.y})
#         yield f"id: {id}\ndata: {gaze_data}\nevent: gaze_world\n\n"
#         time.sleep(0.03333)


# def gen_gaze_mapped(camera_id):
#     """Video streaming generator function."""

#     frame = frame_of_each_camera[int(camera_id)]
#     gaze = gaze_of_each_camera[int(camera_id)]

#     image = frame.bgr_pixels

#     img_copy = copy.deepcopy(image)
#     img_copy = cv.cvtColor(img_copy, cv.COLOR_BGR2GRAY)
#     tags = at_detector.detect(
#             img_copy,
#             estimate_tag_pose=False,
#             camera_params=None,
#             tag_size=None,
#         )

#     print("Detected april tags: " + str(len(tags) ) )

#     if(len(tags) == 4):
#         try:
#             mapped_gaze = get_mapped_gaze(tags, frame, gaze)

#             print(mapped_gaze)
#             print(type(mapped_gaze))

#             return mapped_gaze

#         except:
#             print("Couldn't find 4 april tags")
#             return (0,0)

#     else:
#         print("Couldn't find 4 april tags")
#         return (0,0)




if __name__ == '__main__':
    app.run()


