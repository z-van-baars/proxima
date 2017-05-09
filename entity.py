import pygame
import utilities
import colors


class Entity(object):
    dynamic = False
    blocks_tile = False
    name = "N/A"

    def __init__(self, pos_x, pos_y, width, height, color):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface([width, height])
        self.sprite.image.fill(color)
        self.rect = self.sprite.image.get_rect()
        self.current_tile = (int(pos_x / 20), int(pos_y / 20))

    def tile_checkout(self, tile):
        tile.set_vacant()

    def tile_checkin(self, tile):
        assert not tile.is_blocked
        tile.set_occupied(self)
        if self.blocks_tile:
            tile.set_blocked()


class StaticEntity(Entity):
    def __init__(self, pos_x, pos_y, width, height, color):
        super().__init__(pos_x, pos_y, width, height, color)


class DynamicEntity(Entity):
    def __init__(self, pos_x, pos_y, width, height, color, speed):
        super().__init__(pos_x, pos_y, width, height, color)
        self.x_speed = 0
        self.y_speed = 0
        self.use = False
        self.speed = speed


    def block_check(self, modified_coordinates, tiles):
        top_left = int(modified_coordinates[0] / 20), int(modified_coordinates[1] / 20)
        top_right = (int((modified_coordinates[0] + 20) / 20), int(modified_coordinates[1] / 20))
        bottom_left = (int(modified_coordinates[0] / 20), int((modified_coordinates[1] + 20) / 20))
        bottom_right = (int((modified_coordinates[0] + 20) / 20), int((modified_coordinates[1] + 20) / 20))

        if tiles[top_left].is_blocked:
            return True
        if tiles[top_right].is_blocked:
            return True
        if tiles[bottom_left].is_blocked:
            return True
        if tiles[bottom_right].is_blocked:
            return True
        return False


    def move(self, tiles):
        current_tile = self.current_tile
        if self.x_speed != 0:
            modified_x = self.pos_x + self.x_speed
            if not self.block_check((modified_x, self.pos_y), tiles):
                self.pos_x += self.x_speed
            else:
                if self.x_speed > 0:
                    self.pos_x = int(modified_x / 20) * 20 - 1
                elif self.x_speed < 0:
                    self.pos_x = int(modified_x / 20) * 20 + 20
        if self.y_speed != 0:
            modified_y = self.pos_y + self.y_speed
            if not self.block_check((self.pos_x, modified_y), tiles):
                self.pos_y += self.y_speed
            else:
                if self.y_speed > 0:
                    self.pos_y = int(modified_y / 20) * 20 - 1
                elif self.y_speed < 0:
                    self.pos_y = int(modified_y / 20) * 20 + 20
        if not utilities.check_within(self.pos_x,
                                      self.pos_y,
                                      current_tile[0] * 20,
                                      current_tile[1] * 20,
                                      current_tile[0] * 20 + 20,
                                      current_tile[1] * 20 + 20):
            self.tile_checkout(tiles[current_tile])
            rounded_coordinates = (int(self.pos_x / 20), int(self.pos_y / 20))
            self.tile_checkin(tiles[rounded_coordinates])



class Wall(StaticEntity):
    blocks_tile = True

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, 20, 20, colors.blue)