import copy
import os
import random
import cv2
import numpy as np

from flask import current_app
from artworks.models import Artwork
from gaze_manager import gaze_manager
from settings.models import Settings
from gaze_manager.models import GazeData

# TODO: what to do with it??


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
    scaled_size = int(min_img_l * tag_rel_size)
    return int(scaled_size / 2)


def add_tags(ref_img):
    img_h, img_w, c = ref_img.shape
    min_img_l = min(img_h, img_w)
    scaled_size = int(min_img_l * tag_rel_size)
    resized_images = []
    for tag_image in tag_images:
        resized_images.append(cv2.resize(tag_image, (scaled_size, scaled_size), cv2.INTER_LINEAR))
    ref_img[0:scaled_size, 0:scaled_size] = resized_images[0]
    ref_img[0:scaled_size, img_w - scaled_size: img_w] = resized_images[1]
    ref_img[img_h - scaled_size: img_h, 0: scaled_size] = resized_images[2]
    ref_img[img_h - scaled_size: img_h, img_w - scaled_size:img_w] = resized_images[3]
    return ref_img, int(scaled_size / 2)





def set_simple_pointer(settings: Settings, gaze_data: list[float], reference_img, pointer_img):
    # print(np.max(selected_image[:, :, 3]))
    img_h, img_w, c = reference_img.shape

    pointer_size_pixel, _, _ = pointer_img.shape
    # resized_pointer = cv2.resize(pointer_img, (int(pointer_size_pixel), int(pointer_size_pixel)),
    #                              interpolation=cv2.INTER_NEAREST)
    alpha_channel = pointer_img[:, :, 3] / 255.0
    inverse_alpha = 1.0 - alpha_channel
    resized_pointer = pointer_img[:, :, 0:3]
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
    a = (resized_pointer[:, :, 0] * alpha_channel)
    for i in range(0, 3):
        reference_img[start_pos[0]: end_pos[0], start_pos[1]: end_pos[1], i] = \
            ((resized_pointer[overlay_start_pos[0]:overlay_end_pos[0], overlay_start_pos[1]:overlay_end_pos[1], i] *
              alpha_channel[overlay_start_pos[0]:overlay_end_pos[0], overlay_start_pos[1]:overlay_end_pos[1]]) +
             (reference_img[start_pos[0]: end_pos[0], start_pos[1]: end_pos[1], i] *
              inverse_alpha[overlay_start_pos[0]:overlay_end_pos[0], overlay_start_pos[1]:overlay_end_pos[1]]))
    return reference_img


pointer_imgs = [cv2.imread("static/crosshairWhite.png", cv2.IMREAD_UNCHANGED),
                cv2.imread("static/circleWireWhite.png", cv2.IMREAD_UNCHANGED),
                cv2.imread("static/circleFullWhite.png", cv2.IMREAD_UNCHANGED),
                cv2.imread("static/circleGradientWhite.png", cv2.IMREAD_UNCHANGED)]
pointer_rel_size = 0.5


def gen_artwork_img(mode: str, screen_height: int, screen_width: int, artwork: Artwork, settings: Settings):

    eye_tracker_pointer = dict()

    gaze_dict: dict[int, dict[str, GazeData]] = gaze_manager.show_data

    image_path = artwork.image_path
    ref_img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    ref_img = cv2.resize(ref_img, (screen_width, screen_height), interpolation=cv2.INTER_NEAREST)

    # ref_img, tag_half_l = add_tags(ref_img)
    img_h, img_w, c = ref_img.shape
    min_img_l = min(img_h, img_w)
    pointer_size_pixel = int(settings.pointer_size * pointer_rel_size * min_img_l)
    pointer_img = pointer_imgs[settings.pointer_id]
    while True:
        reference_image = copy.deepcopy(ref_img)
        if artwork.tag_id in gaze_dict:
            gaze_data_dict = gaze_dict[artwork.tag_id]
            for pointer in gaze_data_dict:
                gaze_data = gaze_data_dict[pointer]
                if gaze_data.camera_id in eye_tracker_pointer:
                    pointer_img = eye_tracker_pointer[gaze_data.camera_id]
                else:
                    # color_int = random.randint(0, 255)
                    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 1)
                    color_np = np.array(color, dtype=np.uint8)
                    pointer_img = cv2.resize(pointer_img, (int(pointer_size_pixel), int(pointer_size_pixel)),
                                                                              interpolation=cv2.INTER_NEAREST)
                    pointer_img *= color_np
                    eye_tracker_pointer[gaze_data.camera_id] = pointer_img

                gaze_coord = [gaze_data.pos_x * screen_width, gaze_data.pos_y * screen_height]
                if mode == 'simple':
                    reference_image = set_simple_pointer(settings, gaze_coord, reference_image, pointer_img)
                elif mode == 'torch':
                    # TODO: torch
                    pass
                elif mode == 'tag_test' and image is not None:
                    # TODO: tag test
                    pass
        reference_image, _ = add_tags(reference_image)

        params = [cv2.IMWRITE_JPEG_QUALITY, 50, cv2.IMWRITE_JPEG_OPTIMIZE, 1]
        image = cv2.imencode('.jpg', reference_image, params)[1].tobytes()

        yield b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n--frame\r\n'