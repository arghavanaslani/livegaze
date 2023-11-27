import cv2
import argparse
import numpy as np

# to sort coordinates
from functools import reduce
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
               math.degrees(math.atan2(*tuple(map(operator.sub, item[1], center))[::-1]))) % 360))

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


def detect_tags(image, aruco_params=None, aruco_dict=None, at_detector=None):
    if aruco_params is not None:
        (corners, ids, rejected) = cv2.aruco.detectMarkers(image, aruco_dict, parameters=aruco_params)
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


def get_mapped_gaze(tags, gaze,height,width):
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

    output_pts = np.float32([[0, 0],
                            [0, maxHeight - 1],
                            [maxWidth - 1, maxHeight - 1],
                            [maxWidth - 1, 0]])

    M = cv2.getPerspectiveTransform(input_pts, output_pts)
    gaze_coord = np.float32([[[gaze.x, gaze.y]]])
    mapped_gaze = cv2.perspectiveTransform(gaze_coord, M)

    

    return (int(mapped_gaze[0][0][0]), int(mapped_gaze[0][0][1]))