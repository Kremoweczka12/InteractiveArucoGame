import random

from playsound import playsound, PlaysoundException
import cv2
import cv2.aruco as aruco
import numpy as np


def add_images(img1, img2, y_pos, x_pos):
    height1, width1 = img1.shape[0], img1.shape[1]
    height2, width2 = img2.shape[0], img2.shape[1]

    min_height = min(height1, height2)
    min_width = min(width1, width2)

    img22 = img2[0:min_height, 0:min_width]

    img1[x_pos:min_height + x_pos, y_pos:min_width + y_pos] = img22
    return img1


def findArucoMarkers(img, markerSize=6, totalMarkers=250, draw=True):
    dictionary = aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(dictionary, parameters)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bboxs, ids, rejected = detector.detectMarkers(gray)

    # print(ids)
    if draw:
        aruco.drawDetectedMarkers(img, bboxs)
    return [bboxs, ids]


def arucoAug(bbox, id, img, imgAug, drawId=True):
    tl = bbox[0][0][0], bbox[0][0][1]
    tr = bbox[0][1][0], bbox[0][1][1]
    br = bbox[0][2][0], bbox[0][2][1]
    bl = bbox[0][3][0], bbox[0][3][1]
    h, w, c = imgAug.shape
    pts1 = np.array([tl, tr, br, bl])
    pts2 = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    matrix, _ = cv2.findHomography(pts2, pts1)
    imgout = cv2.warpPerspective(imgAug, matrix, (img.shape[1], img.shape[0]))
    cv2.fillConvexPoly(img, pts1.astype(int), (0, 0, 0))
    imgout = img + imgout
    return imgout


# cap = cv2.VideoCapture(0)
img = cv2.imread(r"test.png")
imgAug = cv2.imread(r"ufo.png")
EvilUfo = cv2.imread(r"evilufo.png", cv2.IMREAD_UNCHANGED)
Coin = cv2.imread(r"money.png", cv2.IMREAD_UNCHANGED)

EvilUfo = cv2.resize(EvilUfo, (0, 0), None, 2, 2)


class FlyingObject:
    def __init__(self, x_size, y_size):
        self.position_y = random.randint(0, y_size - 30)
        self.position_x = random.randint(0, x_size - 30)
        self.move_y = random.randint(-10, 10)
        self.move_x = random.randint(-10, 10)

    def move(self):
        self.position_y += self.move_y
        self.position_x += self.move_x


score = {}
evil_ufos = [FlyingObject(1200, 650) for _ in range(20)]
coins = [FlyingObject(1200, 650) for _ in range(100)]
playsound("music.mp3", False)
cap = cv2.VideoCapture(1)
# grandImg = img.copy()
while len(coins) != 0:
    result, r = cap.read()
    # r = grandImg.copy()
    img = r.copy()
    arucofound = findArucoMarkers(img)
    # img = grandImg.copy()

    if arucofound[0] is not None and arucofound[1] is not None:

        for aruco_elem, aruco_id in zip(arucofound[0], arucofound[1]):
            img = arucoAug(aruco_elem, aruco_id, img, imgAug)
            break

        # check collisions

        for aruco_elem, aruco_id in zip(arucofound[0], arucofound[1]):
            if not score.get(aruco_id[0], ""):
                score[aruco_id[0]] = 0

            M = cv2.moments(aruco_elem)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            for ufo in evil_ufos:
                if (ufo.position_y < cY < ufo.position_y + 30) and (ufo.position_x < cX < ufo.position_x + 30):
                    evil_ufos.remove(ufo)
                    score[aruco_id[0]] -= 1
            for coin in coins:
                if (coin.position_y < cY < coin.position_y + 30) and (coin.position_x < cX < coin.position_x + 30):
                    coins.remove(coin)
                    score[aruco_id[0]] += 1

    [evil_ufo.move() for evil_ufo in evil_ufos]
    [coin.move() for coin in coins]

    r = img.copy()
    for ufo in evil_ufos:
        try:
            r = add_images(r, EvilUfo, ufo.position_x, ufo.position_y)
        except ValueError:
            ufo.move_x = -1 * ufo.move_x
            ufo.move_y = -1 * ufo.move_y
            # evil_ufos.remove(ufo)
    for coin in coins:
        try:
            r = add_images(r, Coin, coin.position_x, coin.position_y)
        except ValueError:
            coin.move_x = -1 * coin.move_x
            coin.move_y = -1 * coin.move_y

    r = cv2.flip(r, 1)
    cv2.imshow(f'Aruco Game', r)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cv2.destroyAllWindows()
best = 0
winner = 0
font = cv2.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2

for k, v in score.items():
    if best < v:
        winner = k
        best = v

while True:
    result, frame = cap.read()
    org = (50, 50)

    frame = cv2.flip(frame, 1)
    for k, v in score.items():
        frame = cv2.putText(frame, f'player {k} scored {v} points', org, font,
                               fontScale, color, thickness, cv2.LINE_AA)
        org = (org[0], org[1] + 50)
    cv2.imshow(f'the winner is player: {winner}', frame)

    k = cv2.waitKey(30) & 0xff
    if k == 27:
        cap.release()
        cv2.destroyAllWindows()
        break
