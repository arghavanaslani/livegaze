import cv2
import argparse
import numpy as np
import pupil_apriltags

# to sort coordinates
from functools import reduce
from settings.models import Settings
import operator
import math


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--width", help='cap width', type=int, default=960)
    parser.add_argument("--height", help='cap height', type=int, default=540)

    parser.add_argument("--families", type=str, default='tag36h11')
    parser.add_argument("--nthreads", type=int, default=1)
    parser.add_argument("--quad_decimate", type=float, default=2.0)
    parser.add_argument("--quad_sigma", type=float, default=0.0)
    parser.add_argument("--refine_edges", type=int, default=1)
    parser.add_argument("--decode_sharpening", type=float, default=0.25)
    parser.add_argument("--debug", type=int, default=0)

    args = parser.parse_args()

    return args


def sort_poses(tags):
    center_coords = {}
    for i in range(len(tags)):
        center_coords[i] = tuple(tags[i].center)

    coords = list(center_coords.values())
    center = tuple(map(operator.truediv,
                       reduce(lambda x, y: map(operator.add, x, y), coords), [len(coords)] * 2))

    res = dict(sorted(center_coords.items(), key=lambda item: (-135 -
                                                               math.degrees(math.atan2(
                                                                   *tuple(map(operator.sub, item[1], center))[
                                                                    ::-1]))) % 360))

    return res


def perspective_mapper(tags, source_img, gaze, maxWidth=1200, maxHeight=849):
    tags_sorted_by_center = sort_poses(tags)
    sorted_coords = list(tags_sorted_by_center.values())

    pt_A = sorted_coords[0]
    pt_B = sorted_coords[1]
    pt_C = sorted_coords[2]
    pt_D = sorted_coords[3]

    width_AD = np.sqrt(((pt_A[0] - pt_D[0]) ** 2) + ((pt_A[1] - pt_D[1]) ** 2))
    width_BC = np.sqrt(((pt_B[0] - pt_C[0]) ** 2) + ((pt_B[1] - pt_C[1]) ** 2))
    #    maxWidth = max(int(width_AD), int(width_BC))
    height_AB = np.sqrt(((pt_A[0] - pt_B[0]) ** 2) +
                        ((pt_A[1] - pt_B[1]) ** 2))
    height_CD = np.sqrt(((pt_C[0] - pt_D[0]) ** 2) +
                        ((pt_C[1] - pt_D[1]) ** 2))
    #    maxHeight = max(int(height_AB), int(height_CD))
    input_pts = np.float32([pt_A, pt_B, pt_C, pt_D])
    # output_pts = np.float32([[0, 0],
    #                         [0, maxHeight - 1],
    #                         [maxWidth - 1, maxHeight - 1],
    #                         [maxWidth - 1, 0]])
    output_pts = np.float32([[0, 0],
                             [0, maxHeight - 1],
                             [maxWidth - 1, maxHeight - 1],
                             [maxWidth - 1, 0]])

    M = cv2.getPerspectiveTransform(input_pts, output_pts)
    gaze_coord = np.float32([[[gaze.x, gaze.y]]])
    mapped_gaze = cv2.perspectiveTransform(gaze_coord, M)

    out = cv2.warpPerspective(
        source_img, M, (maxWidth, maxHeight), flags=cv2.INTER_LINEAR)

    return out, mapped_gaze


class ArucoTag:
    def __init__(self):
        self.center = None
        self.corners = None
        self.tag_id = None


def detect_tags(image, aruco_detector: cv2.aruco.ArucoDetector = None, at_detector: pupil_apriltags.Detector = None):
    if aruco_detector is not None:
        (corners, ids, rejected) = aruco_detector.detectMarkers(image)
        if len(ids) <= 0:
            return []
        ids = ids.flatten()
        return_vals = []
        for (marker_corner, marker_id) in zip(corners, ids):
            corners = marker_corner.reshape((4, 2))
            (top_left, top_right, bottom_right, bottom_left) = corners
            top_right = (int(top_right[0]), int(top_right[1]))
            bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
            bottom_left = (int(bottom_left[0]), int(bottom_left[1]))
            top_left = (int(top_left[0]), int(top_left[1]))
            c_x = int((top_right[0] + bottom_left[0]) / 2.0)
            c_y = int((top_right[1] + bottom_left[1]) / 2.0)
            detected_tag = ArucoTag()
            detected_tag.center = np.array([c_x, c_y])
            detected_tag.tag_id = marker_id
            detected_tag.corners = np.array([top_left, top_right, bottom_right, bottom_left])
            return_vals.append(detected_tag)
        return return_vals

    else:
        tags = at_detector.detect(
            image, estimate_tag_pose=False,
            camera_params=None,
            tag_size=None
        )
        return tags


def get_mapped_gaze(tags, gaze, height, width, tag_half_l):
    tags_sorted_by_center = sort_poses(tags)
    sorted_coords = list(tags_sorted_by_center.values())

    pt_A = sorted_coords[0]
    pt_B = sorted_coords[1]
    pt_C = sorted_coords[2]
    pt_D = sorted_coords[3]

    width_AD = np.sqrt(((pt_A[0] - pt_D[0]) ** 2) + ((pt_A[1] - pt_D[1]) ** 2))
    width_BC = np.sqrt(((pt_B[0] - pt_C[0]) ** 2) + ((pt_B[1] - pt_C[1]) ** 2))
    # maxWidth = max(int(width_AD), int(width_BC))
    height_AB = np.sqrt(((pt_A[0] - pt_B[0]) ** 2) +
                        ((pt_A[1] - pt_B[1]) ** 2))
    height_CD = np.sqrt(((pt_C[0] - pt_D[0]) ** 2) +
                        ((pt_C[1] - pt_D[1]) ** 2))
    # maxHeight = max(int(height_AB), int(height_CD))
    input_pts = np.float32([pt_A, pt_B, pt_C, pt_D])

    maxHeight = height
    maxWidth = width

    output_pts = np.float32([[tag_half_l, tag_half_l],
                             [tag_half_l, maxHeight - 1 - tag_half_l],
                             [maxWidth - 1 - tag_half_l, maxHeight - 1 - tag_half_l],
                             [maxWidth - 1 - tag_half_l, tag_half_l]])

    M = cv2.getPerspectiveTransform(input_pts, output_pts)
    gaze_coord = np.float32([[[gaze.x, gaze.y]]])
    mapped_gaze = cv2.perspectiveTransform(gaze_coord, M)

    return (int(mapped_gaze[0][0][0]), int(mapped_gaze[0][0][1]))


pointer_rel_size = 0.5

def set_simple_pointer(settings: Settings, gaze_data: dict, reference_img, pointer_imgs: list):
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
    start_pos = [int(gaze_data['y'] - pointer_size_pixel / 2), int(gaze_data['x'] - pointer_size_pixel / 2)]
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
