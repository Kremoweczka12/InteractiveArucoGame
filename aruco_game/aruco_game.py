from typing import List

from playsound import playsound
from screeninfo import get_monitors

from aruco_game.constants import FilesPaths
from aruco_game.image_edition_funcs import find_aruco_markers_on_image, add_warped_image, add_image

import cv2

from aruco_game.in_game_objects import FlyingObject


class ArucoGame:
    augmented_player_ufo_image = cv2.imread(r'%s' % FilesPaths.play_ufo)
    enemy_ufo_image = cv2.imread(r'%s' % FilesPaths.evil_ufo, cv2.IMREAD_UNCHANGED)
    coin_image = cv2.imread(r'%s' % FilesPaths.money, cv2.IMREAD_UNCHANGED)

    def __init__(self, number_of_ufo: int, number_of_coins: int, shall_play_music: bool):
        monitors = get_monitors()
        self.x, self.y = monitors[0].width, monitors[0].height
        self.enemy_ufo_image = cv2.resize(self.enemy_ufo_image, (0, 0), None, 2, 2)
        self.score = {}
        self.evil_ufos = [FlyingObject(self.x, self.y) for _ in range(number_of_ufo)]
        self.coins = [FlyingObject(self.x, self.y) for _ in range(number_of_coins)]
        if shall_play_music:
            playsound(FilesPaths.music, False)

        self.cap = cv2.VideoCapture(0)
        # set size
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.x)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.y)

        self.game_loop()

    @staticmethod
    def draw_images_of_moving_objects(result_image, object_image, objects_list: List[FlyingObject]):
        for single_object in objects_list:
            try:
                result_image = add_image(result_image, object_image, single_object.position_x,
                                         single_object.position_y)
            except ValueError:
                # if object touches frame border - it will force them to move in another direction
                single_object.move_x = -1 * single_object.move_x
                single_object.move_y = -1 * single_object.move_y
        return result_image

    def check_for_collisions(self, objects_list: List[FlyingObject], center_x: int, center_y: int,
                             collision_result: int, player_id: int):
        for single_object in objects_list:
            is_collision_with_object_center = (single_object.position_y < center_y < single_object.position_y + 50) \
                                              and (single_object.position_x < center_x < single_object.position_x + 50)

            if is_collision_with_object_center:
                objects_list.remove(single_object)
                self.score[player_id] += collision_result

    def apply_aruco_marker_for_single_frame(self, aruco_markers, aruco_copy):
        if aruco_markers[0] is not None and aruco_markers[1] is not None:

            for aruco_elem, aruco_id in zip(aruco_markers[0], aruco_markers[1]):
                aruco_copy = add_warped_image(aruco_elem, aruco_copy, self.augmented_player_ufo_image)

            # check collisions

            for aruco_elem, aruco_id in zip(aruco_markers[0], aruco_markers[1]):
                if not self.score.get(aruco_id[0], ""):
                    self.score[aruco_id[0]] = 0

                moments = cv2.moments(aruco_elem)
                center_x = int(moments["m10"] / moments["m00"])
                center_y = int(moments["m01"] / moments["m00"])
                # ufos collisions
                self.check_for_collisions(self.evil_ufos, center_x=center_x, center_y=center_y, collision_result=-1,
                                          player_id=aruco_id[0])
                # coins collisions
                self.check_for_collisions(self.coins, center_x=center_x, center_y=center_y, collision_result=1,
                                          player_id=aruco_id[0])

        return aruco_copy

    def game_loop(self):

        # loop until all coin are taken
        while len(self.coins) != 0:
            result, base_image = self.cap.read()
            aruco_copy = base_image.copy()
            aruco_found = find_aruco_markers_on_image(aruco_copy)

            aruco_copy = self.apply_aruco_marker_for_single_frame(aruco_found, aruco_copy)

            [evil_ufo.move() for evil_ufo in self.evil_ufos]
            [coin.move() for coin in self.coins]

            result_image = aruco_copy.copy()
            # draw ufo objects
            result_image = self.draw_images_of_moving_objects(result_image, self.enemy_ufo_image, self.evil_ufos)
            # draw coins objects
            result_image = self.draw_images_of_moving_objects(result_image, self.coin_image, self.coins)

            result_image = cv2.flip(result_image, 1)
            cv2.imshow(f'Aruco Game', result_image)
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break

        self.display_results()

    def display_results(self):
        cv2.destroyAllWindows()
        font = cv2.FONT_HERSHEY_SIMPLEX

        font_scale = 1
        color = (255, 0, 0)
        thickness = 2
        try:
            winner = max(list(self.score.keys()), key=lambda key: self.score[key])
        except ValueError:
            winner = "no_player"

        while True:
            result, frame = self.cap.read()
            label_position = (50, 50)
            frame = cv2.flip(frame, 1)
            for k, v in self.score.items():
                frame = cv2.putText(frame, f'player {k} scored {v} points', label_position, font,
                                    font_scale, color, thickness, cv2.LINE_AA)
                label_position = (label_position[0], label_position[1] + 50)
            cv2.imshow(f'the winner is player: {winner}', frame)
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                self.cap.release()
                cv2.destroyAllWindows()
                break


if __name__ == "__main__":
    ArucoGame(10, 100, False)
