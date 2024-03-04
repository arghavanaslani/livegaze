# import imp

from flask import Flask, render_template, Response, stream_with_context, request
from gaze_manager.events import socket_io
from artworks import utils as artworks_utils

import utils
from extensions import db_config

from pupil_labs.realtime_api.simple import discover_devices, Device
import copy
import os
from pupil_apriltags import Detector
from utils import *
import json
import time
import threading
import signal
from artworks.views import artwork_blueprint
from settings.views import settings_blueprint
from flask_bootstrap import Bootstrap
from artworks.models import Artwork
from signal_handlers import signal_int_handler
from gaze_manager import GazeManager

import random

thread = None

app = Flask(__name__)
socket_io.init_app(app)
app.app_context().push()

if os.path.exists('config.py'):
    app.config.from_pyfile("config.py")
else:
    app.config.from_pyfile("config_example.py")
db_config.init_db(app)
app.register_blueprint(artwork_blueprint, url_prefix="/artworks")
app.register_blueprint(settings_blueprint, url_prefix="/settings")
bootstrap = Bootstrap(app)

print("Searching for cameras...")
cameras = discover_devices(search_duration_seconds=2.0)
# cameras = []
# cameras = [Device("192.168.204.225", 8080)]
# cameras = [Device("10.181.114.108", 8080)]

number_of_cameras = len(cameras)

print(number_of_cameras, " device(s) connected.")
signal.signal(signal.SIGINT, signal_int_handler)

frame_of_each_camera = [None] * number_of_cameras
gaze_of_each_camera = [None] * number_of_cameras
screen_height = 1080
screen_width = 1920

# for testing

print(cameras)


@app.route('/', methods=["GET"])
def index():
    return render_template('demo.html', camera_ids=number_of_cameras)


# forms
@app.route('/participant.html')
def participant():
    return render_template("participant.html")


@app.route('/stimulus.html')
def stimulus():
    return render_template("stimulus.html")


@app.route('/experiment.html')
def experiment():
    return render_template("experiment.html")


# effects
@app.route('/transformed1')
def transformed1():
    return render_template('transformed1.html', camera_ids=number_of_cameras)


@app.route('/transformed/<string:artwork_id>')
def transformed(artwork_id):
    return render_template('transformed.html', camera_ids=number_of_cameras,
                           artwork_id=int(artwork_id))


@app.route('/torch')
def torch():
    return render_template('torch.html', camera_ids=number_of_cameras)


@app.route('/torch_new/<string:artwork_id>')
def torch_new(artwork_id):
    return render_template('torch_new.html', camera_ids=number_of_cameras,
                           artwork_id=int(artwork_id))


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
    print("id", id)
    return Response(gen_frames(id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/mapped_gaze_feed/<string:artwork_id>/')
def mapped_gaze_feed(artwork_id):
    return Response(gen_mapped_gaze(int(artwork_id), mode='simple'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/mapped_gaze_torch_feed/<string:artwork_id>/')
def mapped_gaze_torch_feed(artwork_id):
    return Response(gen_mapped_gaze(int(artwork_id), mode='torch'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/tag_test/<string:artwork_id>/')
def tag_test_feed(artwork_id):
    return Response(gen_mapped_gaze(int(artwork_id), mode="tag_test"), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/screen_resolution', methods=['POST'])
def set_screen_resolution():
    global screen_width, screen_height
    data = request.get_json()
    screen_width = data['width']
    screen_height = data['height']
    print("screen height", screen_height, screen_width)
    return 'Screen resolution set successfully'


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
#     img_copy = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
#     tags = at_detector.detect(
#         img_copy,
#         estimate_tag_pose=False,
#         camera_params=None,
#         tag_size=None
#         )
#     return tags


sem = threading.Semaphore()


# gaze_data = {"x":100, "y":100}

pointer_imgs = [cv2.imread("static/crosshair.png", cv2.IMREAD_UNCHANGED),
                cv2.imread("static/circleWire.png", cv2.IMREAD_UNCHANGED),
                cv2.imread("static/circleFull.png", cv2.IMREAD_UNCHANGED),
                cv2.imread("static/circleGradient.png", cv2.IMREAD_UNCHANGED)]


def gen_mapped_gaze(artwork_id, mode='simple', tag_type='aruco'):
    last_gaze = None
    last_torch_mask = None
    with app.app_context():
        artwork = db_config.db.session.query(Artwork).get(int(artwork_id))
        settings = db_config.db.session.query(Settings).first()

    image_path = artwork.image_path
    ref_img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    ref_img = cv2.resize(ref_img, (screen_width, screen_height), interpolation=cv2.INTER_NEAREST)

    ref_img, tag_half_l = artworks_utils.add_tags(ref_img)
    shape_ref_img = ref_img.shape
    height_ref_img = shape_ref_img[0]
    width_ref_img = shape_ref_img[1]
    at_detector = None
    aruco_detector = None
    uncommited_gaze_data_count = 0
    if tag_type == 'april':
        at_detector = Detector(
            families='tag36h11',
            nthreads=4,
            quad_decimate=2.0,
            quad_sigma=0.0,
            refine_edges=1,
            decode_sharpening=0.25,
            debug=0)
    elif tag_type == 'aruco':
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_ARUCO_ORIGINAL)
        aruco_params = cv2.aruco.DetectorParameters()
        aruco_detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

    if number_of_cameras == 0:
        params = [cv2.IMWRITE_JPEG_QUALITY, 50, cv2.IMWRITE_JPEG_OPTIMIZE, 1]
        image = cv2.imencode('.jpg', ref_img, params)[1].tobytes()
        yield b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n--frame\r\n'

    image = None
    # reference_img = copy.deepcopy(ref_img)
    # reference_img = utils.set_simple_pointer(settings, {"x": 400, "y": 500}, reference_img, pointer_imgs)
    # reference_img = utils.set_simple_pointer(settings, {"x": 0.5, "y": 0.5}, reference_img, pointer_imgs)
    while True:
        tags = []
        try:
            sem.acquire()
            frame = frame_of_each_camera[0]
            gaze = gaze_of_each_camera[0]

            image = frame.bgr_pixels

            img_copy = copy.deepcopy(image)
            img_copy = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
            tags = utils.detect_tags(img_copy, aruco_detector, at_detector)
            #
            # tags = at_detector.detect(
            #     img_copy,
            #     estimate_tag_pose=False,
            #     camera_params=None,
            #     tag_size=None,
            # )
        except:
            pass
            # print("No Apriltag Detected")

        finally:
            sem.release()
            if len(tags) == 4:
                print("4 april tags are detected camera id: " + str(0))
                height_ref_img = shape_ref_img[0]
                width_ref_img = shape_ref_img[1]
                mapped_gaze = get_mapped_gaze(tags, gaze, height_ref_img, width_ref_img, tag_half_l)

                gaze_data = {"x": mapped_gaze[0], "y": mapped_gaze[1]}
                # gaze_data_object = GazeData()
                # gaze_data_object.artwork_id = artwork_id
                # gaze_data_object.gaze_position_x = gaze_data['x'] / width_ref_img
                # gaze_data_object.gaze_position_y = gaze_data['y'] / height_ref_img
                # gaze_data_object.eyetracker_id = 0
                # gaze_data_object.gaze_type = GazeType.simple if mode == 'simple' else GazeType.torch
                # with app.app_context():
                #     db_config.db.session.add(gaze_data_object)
                #     uncommited_gaze_data_count += 1
                #     if uncommited_gaze_data_count > 5:
                #         db_config.db.session.commit()
                #         uncommited_gaze_data_count = 0
                reference_img = copy.deepcopy(ref_img)

                if gaze_data['x'] > 0 and gaze_data['y'] > 0 and gaze_data['x'] < width_ref_img and \
                        gaze_data['y'] < height_ref_img:
                    last_gaze = gaze_data

                if mode == 'simple':
                    # print(gaze_data)
                    # cv2.circle(reference_img,  # red gaze
                    #           (int(gaze_data['x']), int(gaze_data['y'])),
                    #           radius=100,
                    #           color=(0, 0, 255),
                    #           thickness=15)
                    reference_img = utils.set_simple_pointer(settings, gaze_data, reference_img, pointer_imgs)
                elif mode == 'torch':
                    new_mask = np.zeros_like(reference_img)
                    new_mask = cv2.circle(new_mask,  # torch light
                                          (int(gaze_data['x']), int(gaze_data['y'])),
                                          100,
                                          (255, 255, 255),
                                          -1)
                    if last_torch_mask is not None:
                        last_torch_mask = cv2.bitwise_or(new_mask, last_torch_mask)
                    else:
                        last_torch_mask = new_mask
                    reference_img = cv2.bitwise_and(reference_img, last_torch_mask)
                elif mode == 'tag_test' and image is not None:
                    reference_img = image
                    for tag in tags:
                        cv2.rectangle(reference_img, tag.corners[0], tag.corners[2], color=(0, 255, 0),
                                                 thickness=10)

                params = [cv2.IMWRITE_JPEG_QUALITY, 50, cv2.IMWRITE_JPEG_OPTIMIZE, 1]
                image = cv2.imencode('.jpg', reference_img, params)[1].tobytes()

                yield b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n--frame\r\n'

            else:
                reference_img = copy.deepcopy(ref_img)
                if mode == 'simple' and last_gaze is not None:
                    reference_img = utils.set_simple_pointer(settings, last_gaze, reference_img, pointer_imgs)

                if mode == 'torch':
                    mask = last_torch_mask if last_torch_mask is not None else np.zeros_like(reference_img)
                    reference_img = cv2.bitwise_and(reference_img, mask)

                elif mode == 'tag_test':
                    reference_img = image

                params = [cv2.IMWRITE_JPEG_QUALITY, 50, cv2.IMWRITE_JPEG_OPTIMIZE, 1]
                image = cv2.imencode('.jpg', reference_img, params)[1].tobytes()

                yield b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n--frame\r\n'

            time.sleep(0.03333)


def gen_frames(camera_id):
    device = cameras[int(camera_id)]

    while True:
        frame, gaze = device.receive_matched_scene_video_frame_and_gaze()

        frame_of_each_camera[int(camera_id)] = frame
        gaze_of_each_camera[int(camera_id)] = gaze
        cv2.circle(
            frame.bgr_pixels,
            (int(gaze.x), int(gaze.y)),
            radius=80,
            color=(0, 0, 255),
            thickness=15,
        )
        image = frame.bgr_pixels
        params = [cv2.IMWRITE_JPEG_QUALITY, 50, cv2.IMWRITE_JPEG_OPTIMIZE, 1]
        image = cv2.imencode('.jpg', image, params)[1].tobytes()
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
#     img_copy = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
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
