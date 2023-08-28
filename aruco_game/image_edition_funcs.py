import cv2
import cv2.aruco as aruco
import numpy as np


def add_image(img1, img2, y_pos, x_pos):
    height1, width1 = img1.shape[0], img1.shape[1]
    height2, width2 = img2.shape[0], img2.shape[1]

    min_height = min(height1, height2)
    min_width = min(width1, width2)

    img22 = img2[0:min_height, 0:min_width]

    img1[x_pos:min_height + x_pos, y_pos:min_width + y_pos] = img22
    return img1


def find_aruco_markers_on_image(img, marker_size=cv2.aruco.DICT_6X6_250, draw=True):
    dictionary = aruco.getPredefinedDictionary(marker_size)
    parameters = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(dictionary, parameters)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bboxs, ids, rejected = detector.detectMarkers(gray)

    # print(ids)
    if draw:
        aruco.drawDetectedMarkers(img, bboxs)
    return [bboxs, ids]


def add_warped_image(bbox, img, image_to_augments):
    tl = bbox[0][0][0], bbox[0][0][1]
    tr = bbox[0][1][0], bbox[0][1][1]
    br = bbox[0][2][0], bbox[0][2][1]
    bl = bbox[0][3][0], bbox[0][3][1]
    h, w, c = image_to_augments.shape
    pts1 = np.array([tl, tr, br, bl])
    pts2 = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    matrix, _ = cv2.findHomography(pts2, pts1)
    result_image = cv2.warpPerspective(image_to_augments, matrix, (img.shape[1], img.shape[0]))
    cv2.fillConvexPoly(img, pts1.astype(int), (0, 0, 0))
    result_image = img + result_image
    return result_image
