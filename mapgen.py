import pygame
import tile
import colors
import entity
import utilities
import math
import random


class Tunneler(object):
    def __init__(self, start_x, start_y, corr_width, change_dir_prob, roomie_spawn_prob, vector):
        self.id_tag = utilities.generate_id_tag()
        self.corr_width = corr_width
        self.change_dir_prob = change_dir_prob
        self.roomie_spawn_prob = roomie_spawn_prob
        self.vector = vector
        self.last_step = self.set_start_tiles(start_x, start_y, vector)
        self.active = True

    def __lt__(self, other):
        return False

    def deactivate(self):
        self.active = False

    def set_start_tiles(self, start_x, start_y, vector):
        first_step = [(start_x, start_y)]
        if vector == (0, 1) or vector == (0, -1):
            for x_width in range(self.corr_width):
                first_step.append((start_x + x_width, start_y))
        elif vector == (1, 0) or vector == (-1, 0):
            for y_height in range(self.corr_width):
                first_step.append((start_x, start_y + y_height))
        return first_step

    def spawn_check(self, cells):
        chance_to_spawn = random.randint(1, 100)
        if chance_to_spawn < 8:
            child_vector = self.roll_new_vector()
            child_x, child_y = self.get_child_start(child_vector)
            new_tunneler = Tunneler(child_x, child_y, random.randint(self.corr_width - 1, self.corr_width + 1), 1, 0, child_vector)
            if new_tunneler.bounds_check(new_tunneler.last_step, cells):
                return None
            if new_tunneler.occupation_check(new_tunneler.last_step, cells):
                return None
            return new_tunneler
        return None

    def get_child_start(self, child_vector):
        if child_vector[0] > 0:
            child_x = self.last_step[0][0] + self.corr_width
            child_y = self.last_step[0][1]
        elif child_vector[0] < 0:
            child_x = self.last_step[0][0] - 1
            child_y = self.last_step[0][1]
        if child_vector[1] > 0:
            child_x = self.last_step[0][0]
            child_y = self.last_step[0][1] + self.corr_width
        elif child_vector[1] < 0:
            child_x = self.last_step[0][0]
            child_y = self.last_step[0][1] - 1
        return child_x, child_y

    def mark_step(self, cells):
        for each in self.last_step:
            cells[each[1]][each[0]] = 1

    def vector_check(self, cells):
        chance_to_change_vector = random.randint(0, 100)
        if chance_to_change_vector < self.change_dir_prob:
            self.vector = self.roll_new_vector()
            self.reset_last_step(cells)

    def reset_last_step(self, cells):
        x, y = self.get_child_start(self.vector)
        x -= self.vector[0]
        y -= self.vector[1]
        self.last_step = self.set_start_tiles(x, y, self.vector)

    def roll_new_vector(self):
        vectors = [(0, 1),
                   (1, 0),
                   (0, -1),
                   (-1, 0)]
        old_vector = self.vector
        reverse_vector = (old_vector[0] * -1, old_vector[1] * -1)
        new_vector_chosen = False
        while not new_vector_chosen:
            new_vector = random.choice(vectors)
            if new_vector != old_vector and new_vector != reverse_vector:
                return new_vector

    def bounds_check(self, step, cells):
        out_of_bounds = [False]
        for each in step:
            if each[0] >= len(cells[0]) - 1 or each[0] <= 0:
                out_of_bounds.append(True)
            if each[1] >= len(cells) - 1 or each[1] <= 0:
                out_of_bounds.append(True)
        if any(out_of_bounds):
            return True
        return False

    def occupation_check(self, step, cells):
        occupied_spaces = []
        for each in step:
            occupied_spaces.append(cells[each[1]][each[0]] == 1)

        if any(occupied_spaces):
            return True
        return False

    def tunnel(self, cells):
        vector = self.vector
        next_step = []
        for each in self.last_step:
            new_tile = (each[0] + vector[0], each[1] + vector[1])
            next_step.append(new_tile)

        if self.bounds_check(next_step, cells):
            self.deactivate()
            return

        if self.occupation_check(next_step, cells):
            self.deactivate()
            return

        self.last_step = next_step


class ProcDungeon(object):
    def __init__(self, size):
        self.id_tag = utilities.generate_id_tag()
        self.size = size
        self.rooms = {}
        self.randomize_aspect()
        preview_tile_size = 4
        self.cells = self.paint_blank_preview(preview_tile_size)
        self.evaluated_tiles = {}
        #evaluated_tiles = self.crawl(cells, start_pos_xy)
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
        room_image = pygame.Surface([tile_size, tile_size])
        room_image.fill(colors.blue_grey)
        start_point_image = pygame.Surface([tile_size, tile_size])
        start_point_image.fill(colors.red)
        for xy_pair, each in evaluated_tiles.items():
            if each == 1:
                self.structure_preview.blit(room_image, [xy_pair[0] * tile_size, xy_pair[1] * tile_size])
            elif each == 2:
                self.structure_preview.blit(start_point_image, [xy_pair[0] * tile_size, xy_pair[1] * tile_size])

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
        cells = []
        self.structure_preview = pygame.Surface([self.width * tile_size, self.height * tile_size])
        blank_tile = pygame.Surface([tile_size, tile_size])
        blank_tile.fill(colors.background_blue)
        for y in range(self.height):
            new_row = []
            for x in range(self.width):
                new_row.append(0)
                self.structure_preview.blit(blank_tile, [x * tile_size, y * tile_size])
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





