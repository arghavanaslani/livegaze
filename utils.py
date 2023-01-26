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


def perspective_mapper(tags, source_img, gaze, maxWidth=300, maxHeight=200):
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




def get_mapped_gaze(tags, gaze):
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

    maxHeight = 300
    maxWidth = 400

    output_pts = np.float32([[0, 0],
                            [0, maxHeight - 1],
                            [maxWidth - 1, maxHeight - 1],
                            [maxWidth - 1, 0]])

    M = cv2.getPerspectiveTransform(input_pts, output_pts)
    gaze_coord = np.float32([[[gaze.x, gaze.y]]])
    mapped_gaze = cv2.perspectiveTransform(gaze_coord, M)

    

    return (int(mapped_gaze[0][0][0]), int(mapped_gaze[0][0][1]))