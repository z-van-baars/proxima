

class Tile(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.left_border = x
        self.right_border = x + 20
        self.top_border = y
        self.bottom_border = y + 20
        self.is_occupied = False
        self.is_blocked = False
        self.entity = None

    def set_occupied(self, entity):
        self.is_occupied = True
        self.entity = entity

    def set_vacant(self):
        self.is_occupied = False
        self.is_blocked = False
        self.entity = None

    def set_blocked(self):
        self.is_blocked = True
