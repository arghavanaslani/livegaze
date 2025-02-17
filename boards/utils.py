import copy
import os
import random
import cv2
import numpy as np

from flask import current_app
from boards.models import Board
from gaze_manager import gaze_manager
from settings.models import Settings
from gaze_manager.models import GazeData


class RollingAverageList:
    def __init__(self, n):
        self.list: list[int] = [0] * n
        self.update_index = 0

    def set_value(self, val: int):
        self.list[self.update_index] = val
        self.update_index += 1
        self.update_index %= len(self.list)

    def get_average(self):
        return sum(self.list) / len(self.list)


def get_unique_filename(path):
    name = os.path.basename(path)
    directory = os.path.dirname(path)
    print(name, directory, path)
    if not os.path.exists(path):
        return path
    else:
        base, extension = os.path.splitext(name)
        i = 1
        while os.path.exists(os.path.join(directory, '{}_{}{}'.format(base, i, extension))):
            i += 1
        return os.path.join(directory, '{}_{}{}'.format(base, i, extension))


# View Utils

tag_images = [cv2.imread("static/tags/aruco0.png"), cv2.imread("static/tags/aruco1.png"),
              cv2.imread("static/tags/aruco2.png"), cv2.imread("static/tags/aruco3.png")]
tag_rel_size = 0.25


def get_tag_scaled_size(ref_img):
    img_h, img_w, c = ref_img.shape
    min_img_l = min(img_h, img_w)
    return int(min_img_l * tag_rel_size)


def add_tags(ref_img, scaled_size: int, tag_images_index=0):
    img_h, img_w, c = ref_img.shape
    resized_images = []
    tag_images_len = len(tag_images)
    for i in range(tag_images_len):
        tag_image = tag_images[(i + tag_images_index) % tag_images_len]
        resized_images.append(cv2.resize(tag_image, (scaled_size, scaled_size), cv2.INTER_LINEAR))
    ref_img[0:scaled_size, 0:scaled_size] = resized_images[0]
    ref_img[0:scaled_size, img_w - scaled_size: img_w] = resized_images[1]
    ref_img[img_h - scaled_size: img_h, 0: scaled_size] = resized_images[2]
    ref_img[img_h - scaled_size: img_h, img_w - scaled_size:img_w] = resized_images[3]
    return ref_img


def set_pointer(gaze_data: list[float], reference_img, pointer_img, mode='simple', orig_image=None):
    # print(np.max(selected_image[:, :, 3]))
    img_h, img_w, c = reference_img.shape

    pointer_size_pixel, _, _ = pointer_img.shape
    # resized_pointer = cv2.resize(pointer_img, (int(pointer_size_pixel), int(pointer_size_pixel)),
    #                              interpolation=cv2.INTER_NEAREST)
    alpha_channel = pointer_img[:, :, 3] / 255.0
    inverse_alpha = 1.0 - alpha_channel
    # resized_pointer = pointer_img[:, :, 0:3]
    start_pos = [int(gaze_data[1] - pointer_size_pixel / 2), int(gaze_data[0] - pointer_size_pixel / 2)]
    overlay_start_pos = [0, 0]
    overlay_end_pos = [pointer_size_pixel, pointer_size_pixel]
    overlay_size = [pointer_size_pixel, pointer_size_pixel]
    if (start_pos[0] <= - pointer_size_pixel or start_pos[1] <= - pointer_size_pixel or
            start_pos[0] >= img_h or start_pos[1] >= img_w):
        return reference_img
    if start_pos[0] < 0:
        overlay_start_pos[0] = -start_pos[0]
        overlay_size[0] += start_pos[0]
        start_pos[0] = 0
    if start_pos[1] < 0:
        overlay_start_pos[1] = -start_pos[1]
        overlay_size[1] += start_pos[1]
        start_pos[1] = 0
    if start_pos[0] > img_h - pointer_size_pixel:
        overlay_end_pos[0] = img_h - start_pos[0]
        overlay_size[0] = overlay_end_pos[0]
    if start_pos[1] > img_w - pointer_size_pixel:
        overlay_end_pos[1] = img_w - start_pos[1]
        overlay_size[1] = overlay_end_pos[1]
    end_pos = [int(start_pos[0] + overlay_size[0]), int(start_pos[1] + overlay_size[1])]
    # print(pointer_size_pixel, start_pos, end_pos)
    # end_pos = [int(gaze_data['x'] + pointer_size_pixel / 2), int(gaze_data['y'] + pointer_size_pixel / 2)]
    # a = (resized_pointer[:, :, 0] * alpha_channel)
    selected_image = (pointer_img[overlay_start_pos[0]:overlay_end_pos[0], overlay_start_pos[1]:overlay_end_pos[1], :] if mode in ['simple', 'waldo']
                      else orig_image[start_pos[0]: end_pos[0], start_pos[1]: end_pos[1], :])
    for i in range(0, 3):
        reference_img[start_pos[0]: end_pos[0], start_pos[1]: end_pos[1], i] = \
            ( (selected_image [:,:, i] * alpha_channel[overlay_start_pos[0]:overlay_end_pos[0], overlay_start_pos[1]:overlay_end_pos[1]]) +
             (reference_img[start_pos[0]: end_pos[0], start_pos[1]: end_pos[1], i] *
              inverse_alpha[overlay_start_pos[0]:overlay_end_pos[0], overlay_start_pos[1]:overlay_end_pos[1]]))
    return reference_img


pointer_imgs = [cv2.imread("static/crosshairWhite.png", cv2.IMREAD_UNCHANGED),
                cv2.imread("static/circleWireWhite.png", cv2.IMREAD_UNCHANGED),
                cv2.imread("static/circleFullWhite.png", cv2.IMREAD_UNCHANGED),
                cv2.imread("static/circleGradientWhite.png", cv2.IMREAD_UNCHANGED)]
pointer_rel_size = 0.5
rolling_average_window = 10


def gen_artwork_img(mode: str, screen_height: int, screen_width: int, artwork: Board, settings: Settings):
    eye_tracker_pointer = dict()

    gaze_dict: dict[int, dict[str, GazeData]] = gaze_manager.show_data
    # print(len(gaze_manager.show_data))
    # gaze_past_pos: dict[str, list[RollingAverageList]] = dict()

    image_path = artwork.image_path
    ref_img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    # create a black image with size of screen width and height
    black_img = np.zeros((screen_height, screen_width, 3), np.uint8)
    raw_h, raw_w, c = ref_img.shape
    resize_h, resize_w = 0, 0
    if raw_h / raw_w < screen_height / screen_width:
        resize_h, resize_w = int(screen_width * raw_h / raw_w), screen_width
    else:
        resize_h, resize_w = screen_height, int(screen_height * raw_w / raw_h)
    ref_img = cv2.resize(ref_img, (resize_w, resize_h), interpolation=cv2.INTER_NEAREST)
    black_img[int((screen_height - resize_h) / 2):int((screen_height + resize_h) / 2),
    int((screen_width - resize_w) / 2):int((screen_width + resize_w) / 2)] = ref_img
    ref_img = black_img

    # ref_img, tag_half_l = add_tags(ref_img)
    img_h, img_w, c = ref_img.shape
    min_img_l = min(img_h, img_w)
    tag_scaled_size_f = min_img_l * tag_rel_size
    tag_scaled_size = int(tag_scaled_size_f)
    # tag_scaled_size = get_tag_scaled_size(ref_img)
    pointer_size_pixel = int(settings.pointer_size * pointer_rel_size * min_img_l)
    if mode == 'waldo':
        white_pointer_img = pointer_imgs[1]
        pointer_size_pixel = int(pointer_size_pixel * 0.8)
    elif mode == 'simple':
        white_pointer_img = pointer_imgs[settings.pointer_id]
    elif mode == 'torch':
        white_pointer_img = pointer_imgs[settings.pointer_id]
        reference_image = np.zeros((screen_height, screen_width, 3), np.uint8)
    while True:
        if mode in ['simple', 'waldo']:
            reference_image = copy.deepcopy(ref_img)
        if artwork.tag_id in gaze_dict:
            gaze_data_dict = gaze_dict[artwork.tag_id]
            gaze_data_dict_items = list(gaze_data_dict.items())
            for pointer, gaze_data in gaze_data_dict_items:
                if gaze_data.camera_id in eye_tracker_pointer:
                    pointer_img = eye_tracker_pointer[gaze_data.camera_id]
                else:
                    color_int = random.random()
                    # color_
                    color = (random.random(), random.random(), random.random(), 1)
                    # color = (color_int, color_int, color_int, 1)
                    # print(color_int)
                    color_np = np.array(color, dtype=np.float32)
                    pointer_img = cv2.resize(white_pointer_img, (int(pointer_size_pixel), int(pointer_size_pixel)),
                                             interpolation=cv2.INTER_NEAREST)

                    pointer_img = pointer_img.astype(np.float32)
                    pointer_img *= color_np
                    pointer_img = pointer_img.astype(np.uint8)
                    eye_tracker_pointer[gaze_data.camera_id] = pointer_img
                gaze_coord = [int(gaze_data.pos_x * (screen_width - tag_scaled_size_f) + tag_scaled_size / 2),
                              int(gaze_data.pos_y * (screen_height - tag_scaled_size_f) + tag_scaled_size / 2)]
                # if pointer in gaze_past_pos:
                #     past_poses = gaze_past_pos[pointer]
                # else:
                #     past_poses = [RollingAverageList(5), RollingAverageList(5)]
                #     gaze_past_pos[pointer] = past_poses
                # past_poses[0].set_value(gaze_coord[0])
                # past_poses[1].set_value(gaze_coord[1])
                # gaze_coord = [past_poses[0].get_average(), past_poses[1].get_average()]
                if mode in ['simple', 'waldo', 'torch']:
                    reference_image = set_pointer(gaze_coord, reference_image, pointer_img, mode=mode, orig_image= ref_img if mode == 'torch' else None)
                elif mode == 'tag_test' and image is not None:
                    # TODO: tag test
                    pass
        reference_image = add_tags(reference_image, tag_scaled_size, artwork.id)

        params = [cv2.IMWRITE_JPEG_QUALITY, 50, cv2.IMWRITE_JPEG_OPTIMIZE, 1]
        image = cv2.imencode('.jpg', reference_image, params)[1].tobytes()

        yield b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n--frame\r\n'
