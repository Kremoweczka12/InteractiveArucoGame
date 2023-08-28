import random


class FlyingObject:
    def __init__(self, x_size, y_size):
        self.position_y = random.randint(0, y_size - 30)
        self.position_x = random.randint(0, x_size - 30)
        self.move_y = random.randint(-10, 10)
        self.move_x = random.randint(-10, 10)

    def move(self):
        self.position_y += self.move_y
        self.position_x += self.move_x
