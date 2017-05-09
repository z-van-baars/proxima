import pygame
import tile
import colors
import entity


class Dungeon(object):
    def __init__(self):
        pass


class Room(object):
    def __init__(self, x_tiles, y_tiles):
        self.x_tiles = x_tiles
        self.y_tiles = y_tiles
        self.tiles = {}
        for y in range(0, y_tiles):
            for x in range(0, x_tiles):
                self.tiles[(x, y)] = tile.Tile(x * 20, y * 20)

        self.background = pygame.Surface((x_tiles * 20, y_tiles * 20))
        self.background.fill(colors.black)

        self.static_entities = set()
        self.static_display_layer = None
        self.dynamic_entities = set()

        self.display_shift_x = 0
        self.display_shift_y = 0

    def update_static_layer(self):
        self.static_display_layer = pygame.Surface((self.x_tiles * 20, self.y_tiles * 20))
        self.static_display_layer.fill(colors.key)
        for each in self.static_entities:
            self.static_display_layer.blit(each.sprite.image, [each.pos_x, each.pos_y])
        self.static_display_layer.set_colorkey(colors.key)
        self.static_display_layer = self.static_display_layer.convert_alpha()

    def add_wall(self, x, y):
        """ X and Y args are tile coordinates, Not pixels"""
        new_wall = entity.Wall(x * 20, y * 20)
        new_wall.tile_checkin(self.tiles[x, y])
        self.static_entities.add(new_wall)


