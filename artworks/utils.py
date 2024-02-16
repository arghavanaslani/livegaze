import copy
import os

import cv2

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


pointer_imgs = [cv2.imread("static/crosshair.png", cv2.IMREAD_UNCHANGED),
                cv2.imread("static/circleWire.png", cv2.IMREAD_UNCHANGED),
                cv2.imread("static/circleFull.png", cv2.IMREAD_UNCHANGED),
                cv2.imread("static/circleGradient.png", cv2.IMREAD_UNCHANGED)]
pointer_rel_size = 0.5


def set_simple_pointer(settings: Settings, gaze_data: list[float], reference_img):
    selected_image = pointer_imgs[settings.pointer_id]
    # print(np.max(selected_image[:, :, 3]))
    img_h, img_w, c = reference_img.shape
    min_img_l = min(img_h, img_w)
    pointer_size_pixel = int((settings.pointer_size) * pointer_rel_size * min_img_l)

    resized_pointer = cv2.resize(selected_image, (int(pointer_size_pixel), int(pointer_size_pixel)),
                                 interpolation=cv2.INTER_NEAREST)
    alpha_channel = resized_pointer[:, :, 3] / 255.0
    inverse_alpha = 1.0 - alpha_channel
    resized_pointer = resized_pointer[:, :, 0:3]
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


def gen_artwork_img(artwork_id: int, mode: str, screen_height: int, screen_width: int, artwork: Artwork, settings: Settings):
    gaze_dict: dict[int, dict[int, GazeData]] = gaze_manager.show_data

    image_path = artwork.image_path
    ref_img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    print("screen", screen_height, screen_width)
    ref_img = cv2.resize(ref_img, (screen_width, screen_height), interpolation=cv2.INTER_NEAREST)

    ref_img, tag_half_l = add_tags(ref_img)
    while True:
        reference_image = copy.deepcopy(ref_img)
        if artwork_id in gaze_dict:
            gaze_data_dict = gaze_dict[artwork_id]
            for pointer in gaze_data_dict:
                gaze_data = gaze_data_dict[pointer]
                gaze_coord = [gaze_data.pos_x * screen_width, gaze_data.pos_y * screen_height]
                if mode == 'simple':
                    reference_image = set_simple_pointer(settings, gaze_data, reference_image)
                elif mode == 'torch':
                    # TODO: torch
                    pass
                elif mode == 'tag_test' and image is not None:
                    # TODO: tag test
                    pass

        params = [cv2.IMWRITE_JPEG_QUALITY, 50, cv2.IMWRITE_JPEG_OPTIMIZE, 1]
        image = cv2.imencode('.jpg', reference_image, params)[1].tobytes()

        yield b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n--frame\r\n'
