import pygame
import tile
import colors
import entity
import utilities
import math
import random


class Dungeon(object):
    def __init__(self):
        pass


class Room(object):
    def __init__(self, x_tiles, y_tiles):
        self.id_tag = utilities.generate_id_tag()
        self.x_tiles = x_tiles
        self.y_tiles = y_tiles
        self.tiles = self.generate_empty_tiles()
        self.background = pygame.Surface((x_tiles * 20, y_tiles * 20))
        self.background.fill(colors.black)

        self.static_entities = {}
        self.update_static_display_layer()
        self.dynamic_entities = {}

    def generate_empty_tiles(self):
        tiles = {}
        for y in range(0, self.y_tiles):
            for x in range(0, self.x_tiles):
                tiles[(x, y)] = tile.Tile(x * 20, y * 20)
        return tiles

    def update_static_display_layer(self):
        self.static_display_layer = pygame.Surface((self.x_tiles * 20, self.y_tiles * 20))
        self.static_display_layer.fill(colors.key)
        for id_tag, each in self.static_entities.items():
            self.static_display_layer.blit(each.sprite.image, [each.pos_x, each.pos_y])
        self.static_display_layer.set_colorkey(colors.key)
        self.static_display_layer = self.static_display_layer.convert_alpha()

    def add_wall(self, x, y):
        """ X and Y args are tile coordinates, Not pixels"""
        new_wall = entity.Wall(x * 20, y * 20)
        new_wall.tile_checkin(self.tiles[x, y])
        self.static_entities[new_wall.id_tag] = new_wall

    def generate_random_coins(self, number_of_coins):
        number_of_coins = random.randint(3, number_of_coins)
        for coin in range(number_of_coins):
            coin_placed = False
            while not coin_placed:
                x, y = utilities.get_random_coordinates(1, self.x_tiles - 2, 1, self.y_tiles - 2)
                if not self.tiles[(x, y)].is_occupied:
                    new_coin = entity.Coin(x * 20, y * 20)
                    self.static_entities[new_coin.id_tag] = new_coin
                    new_coin.tile_checkin(self.tiles[x, y])
                    coin_placed = True
        self.update_static_display_layer()


