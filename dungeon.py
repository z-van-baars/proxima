import colors
import utilities
import pygame
import random
import math
import entity
import tile


class ProcDungeon(object):
    def __init__(self, size):
        self.id_tag = utilities.generate_id_tag()
        self.size = size
        self.rooms = {}
        self.randomize_aspect()
        preview_tile_size = 4
        self.cells = self.build_blank_cell_array()
        self.evaluated_tiles = {}

        self.paint_evaluated_tiles(preview_tile_size)

    def update_evaluated_tiles(self):
        evaluated = {}
        x = 0
        y = 0
        for row in self.cells:
            for column in row:
                evaluated[x, y] = column
                x += 1
            x = 0
            y += 1
        return evaluated

    def paint_evaluated_tiles(self, tile_size):
        evaluated_tiles = self.evaluated_tiles
        hall_image = pygame.Surface([tile_size, tile_size])
        hall_image.fill(colors.blue_grey)
        start_point_image = pygame.Surface([tile_size, tile_size])
        start_point_image.fill(colors.red)
        roomie_image = pygame.Surface([tile_size, tile_size])
        roomie_image.fill(colors.blue)
        room_image = pygame.Surface([tile_size, tile_size])
        room_image.fill(colors.room_grey)
        buffer_image = pygame.Surface([tile_size, tile_size])
        buffer_image.fill(colors.buffer_grey)

        tile_colors = {1: hall_image,
                       2: start_point_image,
                       3: roomie_image,
                       4: room_image,
                       5: buffer_image}

        self.paint_blank_preview(tile_size)

        for xy_pair, each in evaluated_tiles.items():
            if each == 0:
                pass
            else:
                self.structure_preview.blit(tile_colors[each],
                                            [xy_pair[0] * tile_size,
                                             xy_pair[1] * tile_size])

    def crawl(self, cells, pos_xy):
        print("Crawling!")

        frontier = set()
        evaluated = {pos_xy: 2}
        frontier.add(pos_xy)
        print(frontier == set())
        while not frontier == set():
            xy_pair = frontier.pop()
            neighbors = utilities.get_room_neighbors(self.width, self.height, xy_pair[0], xy_pair[1])
            for each in neighbors:

                sub_neighbors = utilities.get_room_neighbors(self.width, self.height, each[0], each[1])
                room_chance = [1]
                for subneighbor in sub_neighbors:
                    if subneighbor in evaluated and evaluated[subneighbor] == 1:
                        for x in range(1):
                            room_chance.append(0)

                if each not in evaluated:
                    evaluated[each] = random.choice(room_chance)
                    if evaluated[each] == 1:
                        frontier.add(each)
        return evaluated

    def paint_blank_preview(self, tile_size):
        self.structure_preview = pygame.Surface([self.width * tile_size, self.height * tile_size])
        self.structure_preview.fill(colors.background_blue)

    def build_blank_cell_array(self):
        cells = []
        for y in range(self.height):
            new_row = []
            for x in range(self.width):
                new_row.append(0)
            cells.append(new_row)
        return cells

    def randomize_aspect(self):
        aspect = random.randint(1, math.floor(self.size / 3))
        width = self.size
        height = self.size
        width_modifier = random.choice([aspect, -aspect])
        self.width = width + width_modifier
        self.height = height + -width_modifier

    def set_start_point(self):
        x_middle = math.floor(self.width / 2)
        y_middle = math.floor(self.height / 2)
        left_center = (0, y_middle)
        right_center = (self.width - 1, y_middle)
        top_center = (x_middle, 0)
        bottom_center = (x_middle, self.height - 1)
        starting_point = random.choice([left_center,
                                        right_center,
                                        top_center,
                                        bottom_center])

        return starting_point


class Dungeon(object):
    def __init__(self, number_of_rooms):
        self.number_of_rooms = number_of_rooms
        self.rooms = {}
        room_id_tags = []
        for room in range(number_of_rooms):
            new_room = Room(40, 40)
            self.rooms[new_room.id_tag] = new_room
            room_id_tags.append(new_room.id_tag)

        room_1_id = room_id_tags[0]
        room_2_id = room_id_tags[1]
        self.start_room = self.rooms[room_1_id]

        room_1 = self.rooms[room_1_id]
        room_2 = self.rooms[room_2_id]
        new_door = entity.Door(19, 0)
        new_door.destination_room = room_2_id
        new_door.destination_x = 19
        new_door.destination_y = 38
        room_1.static_entities[new_door.id_tag] = new_door
        new_door.tile_checkin(room_1.tiles[19, 0])
        new_door = entity.Door(19, 39)
        new_door.destination_room = room_1_id
        new_door.destination_x = 19
        new_door.destination_y = 1
        room_2.static_entities[new_door.id_tag] = new_door
        new_door.tile_checkin(room_2.tiles[19, 39])
        room_1.generate_scenery()
        room_2.generate_scenery()


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

    def generate_scenery(self):
        for ii in range(0, 40):
            self.add_wall(ii, 0)
        for ii in range(0, 40):
            self.add_wall(ii, 39)
        for ii in range(1, 39):
            self.add_wall(0, ii)
        for ii in range(1, 39):
            self.add_wall(39, ii)
        self.generate_random_walls(40)
        self.generate_random_coins(4)
        self.update_static_display_layer()

    def update_static_display_layer(self):
        self.static_display_layer = pygame.Surface((self.x_tiles * 20, self.y_tiles * 20))
        self.static_display_layer.fill(colors.key)
        for id_tag, each in self.static_entities.items():
            self.static_display_layer.blit(each.sprite.image, [each.pos_x, each.pos_y])
        self.static_display_layer.set_colorkey(colors.key)
        self.static_display_layer = self.static_display_layer.convert_alpha()

    def add_wall(self, x, y):
        """ X and Y args are tile coordinates, Not pixels"""
        if not self.tiles[x, y].is_blocked:
            new_wall = entity.Wall(x * 20, y * 20)
            new_wall.tile_checkin(self.tiles[x, y])
            self.static_entities[new_wall.id_tag] = new_wall

    def generate_random_walls(self, number_of_walls):
        def check_wall_tiles(tiles, tiles_list):
            """Returns True if all tiles in the list are vacant"""
            for each in tiles_list:
                if tiles[each].is_blocked:
                    return False
            return True

        wall_1 = [(0, 0), (0, 1), (0, 2), (0, 3)]
        wall_2 = [(0, 0), (1, 0), (2, 0), (3, 0)]
        wall_3 = [(0, 0), (-1, 1), (0, 1), (1, 1), (0, 2)]
        wall_4 = [(0, 0), (0, 1), (1, 1), (2, 1)]
        wall_5 = [(0, 0), (1, 0), (2, 0), (2, 1)]
        wall_6 = [(0, 0), (1, 0), (1, 1)]
        wall_7 = [(0, 0), (0, 1), (1, 1)]

        wall_types = [wall_1,
                      wall_2,
                      wall_3,
                      wall_4,
                      wall_5,
                      wall_6,
                      wall_7]

        for ii in range(number_of_walls):
            wall_placed = False
            while not wall_placed:
                x, y = utilities.get_random_coordinates(1,
                                                        self.x_tiles - 1,
                                                        1,
                                                        self.y_tiles - 1)
                wall_type = random.choice(wall_types)
                wall_tiles = []

                for each_tile in wall_type:
                    wall_tiles.append((x + each_tile[0], y + each_tile[1]))

                if check_wall_tiles(self.tiles, wall_tiles):
                    for each in wall_tiles:
                        self.add_wall(each[0], each[1])
                        wall_placed = True
        self.update_static_display_layer()

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



