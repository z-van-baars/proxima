import utilities
import math
import random


def all_room_sizes(max_width, max_height):
    for xx in range(2, max_width):
        for yy in range(2, max_height):
            aspect = min(xx, yy) / max(xx, yy)
            if aspect > 0.3:
                yield xx, yy


def room_score(width_height):
    w = width_height[0]
    h = width_height[1]
    return w * h


def buffer_from_room(room_tiles):
    top_left = room_tiles[0]
    bottom_right = room_tiles[-1]
    x1 = top_left[0] - 1
    y1 = top_left[1] - 1
    x2 = bottom_right[0] + 1
    y2 = bottom_right[1] + 1
    width = x2 - x1
    height = y2 - y1
    room_buffer_footprint = utilities.tiles_from_top_left(x1, y1, width, height)
    return room_buffer_footprint


def cardinal_neighbors(pos, cells):
    width = len(cells[0]) - 1
    height = len(cells) - 1
    x = pos[0]
    y = pos[1]
    neighbors = []
    neighbors.append((x - 1, y))  # to the left
    neighbors.append((x + 1, y))  # to the right
    neighbors.append((x, y - 1))  # above
    neighbors.append((x, y + 1))  # below
    valid_neighbors = []
    for each in neighbors:
        xx = each[0]
        yy = each[1]
        if all([xx >= 0,
                xx <= width,
                yy >= 0,
                yy <= height]):  # check to see if any neighbor is outside the map
            valid_neighbors.append(each)
    return valid_neighbors


class Tunneler(object):
    def __init__(self, start_x, start_y, corr_width, vector, max_child_width):
        self.pos_x = start_x
        self.pos_y = start_y
        self.id_tag = utilities.generate_id_tag()
        self.corr_width = max(1, corr_width)
        self.max_child_width = max_child_width
        self.vector = vector
        self.last_step = self.set_start_tiles(start_x, start_y, vector)
        self.active = True
        self.action_timer = 0
        self.reset_action_timer()
        self.lifespan = (self.corr_width * 40)

    def __lt__(self, other):
        return False

    def deactivate(self):
        self.active = False

    def reset_action_timer(self):
        self.action_timer = (1 + self.corr_width * 3)

    def set_start_tiles(self, start_x, start_y, vector):
        first_step = []
        if vector == (0, 1) or vector == (0, -1):
            for xx in range(start_x - math.floor(self.corr_width / 2),
                            start_x + math.floor(self.corr_width / 2) + 1):
                first_step.append((xx, start_y))
        elif vector == (1, 0) or vector == (-1, 0):
            for yy in range(start_y - math.floor(self.corr_width / 2),
                            start_y + math.floor(self.corr_width / 2) + 1):
                first_step.append((start_x, yy))
        return first_step

    def spawn_check(self, cells):
        chance_to_spawn = random.randint(1, 100)
        if chance_to_spawn < 10 + (5 * self.corr_width):
            return True
        return False

    def spawn_roomie(self, cells):
        child_vector = self.roll_new_vector()
        child_x, child_y = self.get_child_start(self.vector, child_vector)
        new_roomie = Roomie(child_x,
                            child_y,
                            1 + self.corr_width ** 2,  # room size based on tunnel size
                            child_vector)
        if new_roomie.bounds_check([new_roomie.origin], cells):
            return None
        if new_roomie.occupation_check([new_roomie.origin], cells):
            return None
        self.reset_action_timer()
        return new_roomie

    def spawn_tunneler(self, cells):
        child_vector = self.roll_new_vector()
        child_x, child_y = self.get_child_start(self.vector, child_vector)
        child_width = random.choice([self.corr_width - 2,
                                     self.max_child_width])
        new_tunneler = Tunneler(child_x,
                                child_y,
                                child_width,
                                child_vector,
                                self.corr_width + 2)
        if new_tunneler.bounds_check(new_tunneler.last_step, cells):
            return None
        if new_tunneler.occupation_check(new_tunneler.last_step, cells):
            return None
        self.reset_action_timer()
        return new_tunneler

    def get_child_start(self, parent_vector, child_vector):
        child_x = self.pos_x - parent_vector[0] * (math.floor(self.corr_width / 2) + 1)
        child_y = self.pos_y - parent_vector[1] * (math.floor(self.corr_width / 2) + 1)
        child_x += child_vector[0] * (math.floor(self.corr_width / 2) + 1)
        child_y += child_vector[1] * (math.floor(self.corr_width / 2) + 1)
        return child_x, child_y

    def mark_step(self, cells):
        for each in self.last_step:
            cells[each[1]][each[0]] = 1

    def vector_check(self, cells, turn_frequency):
        chance_to_change_vector = random.randint(0, 100)
        if chance_to_change_vector < turn_frequency:
            self.reset_action_timer()
            old_vector = self.vector
            new_vector = self.roll_new_vector()
            self.vector = new_vector
            if not self.valid_turn_check(cells, old_vector, new_vector):
                self.deactivate()
                return

    def roll_new_vector(self):
        new_vectors = utilities.flip_vector(self.vector)
        return random.choice(new_vectors)

    def valid_turn_check(self, cells, old_vector, new_vector):
        """Checks whether the tiles one step ahead along the old vector are clear, to make sure
        the new hallway doesn't parallel an existing one, then checks to make sure the way is clear
        along the new vector.  Returns False if any one tile in the pathway along the old or new
        vector are blocked, and returns True only if all tiles are clear - [0]"""
        next_step_old = utilities.modify_tile_group(self.last_step, old_vector)
        if self.occupation_check(next_step_old, cells):
            return False
        self.reset_last_step(cells, old_vector)
        next_step_new = utilities.modify_tile_group(self.last_step, new_vector)
        if self.occupation_check(next_step_new, cells):
            return False
        return True

    def reset_last_step(self, cells, old_vector):
        self.pos_x -= old_vector[0] * math.floor(self.corr_width / 2)
        self.pos_y -= old_vector[1] * math.floor(self.corr_width / 2)  # Back up the centerpoint

        self.pos_x += self.vector[0] * math.floor(self.corr_width / 2)  # Move centerpoint ahead to the edge of the current tunnel
        self.pos_y += self.vector[1] * math.floor(self.corr_width / 2)
        self.last_step = self.set_start_tiles(self.pos_x, self.pos_y, self.vector)

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

    def occupation_check(self, tile_group, cells):
        occupied_spaces = []
        for each in tile_group:
            if any([cells[each[1]][each[0]] == 1,
                    cells[each[1]][each[0]] == 2,
                    cells[each[1]][each[0]] == 3,
                    cells[each[1]][each[0]] == 4,
                    cells[each[1]][each[0]] == 5]):
                occupied_spaces.append(True)
        if any(occupied_spaces):
            return True
        return False

    def mark_door(self, cells, door_spots):
        door_location = random.choice(door_spots)
        cells[door_location[1]][door_location[0]] = 3

    def door_creation_check(self, step, cells, vector):
        valid_door_spots = []
        for each in step:
            if cells[each[1] + vector[1]][each[0] + vector[0]] == 4:
                valid_door_spots.append((each[0], each[1]))
        return valid_door_spots

    def tunnel(self, cells):
        vector = self.vector
        self.pos_x += vector[0]
        self.pos_y += vector[1]
        next_step = utilities.modify_tile_group(self.last_step, vector)
        if self.bounds_check(next_step, cells):
            self.deactivate()
            return
        if self.occupation_check(next_step, cells):
            door_spots = self.door_creation_check(next_step, cells, self.vector)
            if len(door_spots) > 0:
                self.mark_door(cells, door_spots)
            self.deactivate()
            return

        self.last_step = next_step


class Roomie(object):
    def __init__(self, x, y, size, vector):
        self.id_tag = utilities.generate_id_tag()
        self.origin = (x, y)
        self.pos_x = x + vector[0]
        self.pos_y = y + vector[1]
        self.vector = vector
        self.size = max(1, size)
        self.max_dimensions = math.floor((size + 10) * 0.3)
        self.active = True

    def mark_origin(self, cells):
        cells[self.origin[1]][self.origin[0]] = 3

    def remark_origin(self, cells):
        neighboring_tiles = cardinal_neighbors(self.origin, cells)
        occupied_spaces = []
        for each in neighboring_tiles:
            xx = each[0]
            yy = each[1]
            if any([cells[yy][xx] == 1,
                    cells[yy][xx] == 4]):
                opposite_x = self.origin[0] - (xx - self.origin[0])
                opposite_y = self.origin[1] - (yy - self.origin[1])
                opposite_tile = cells[opposite_y][opposite_x]
                if any([opposite_tile == 1,
                        opposite_tile == 4]):
                    return

        occupied_spaces = []
        for each in neighboring_tiles:
            xx = each[0]
            yy = each[1]
            if any([cells[yy][xx] == 5]):
                occupied_spaces.append(True)

        if len(occupied_spaces) > 1:
            cells[self.origin[1]][self.origin[0]] = 5
            return

        cells[self.origin[1]][self.origin[0]] = 0

    def deactivate(self):
        self.active = False

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

    def occupation_check(self, tiles, cells):
        occupied_spaces = []
        for each in tiles:
            if any([cells[each[1]][each[0]] == 1,
                    cells[each[1]][each[0]] == 2,
                    cells[each[1]][each[0]] == 4]):
                occupied_spaces.append(True)

        if any(occupied_spaces):
            return True
        return False

    def draw_room(self, cells):
        room_footprint = self.get_room_footprint(cells)
        if not room_footprint:
            self.deactivate()
            return
        room_buffer_footprint = buffer_from_room(room_footprint)
        for each in room_buffer_footprint:
            if cells[each[1]][each[0]] != 3:
                cells[each[1]][each[0]] = 5
        for each in room_footprint:
            cells[each[1]][each[0]] = 4

    def get_room_footprint(self, cells):
        candidates = sorted(all_room_sizes(self.max_dimensions, self.max_dimensions), key=room_score, reverse=True)
        shifted_permutations = []
        for each in candidates:
            shape_permutations = []
            if self.vector == (0, 1) or self.vector == (0, -1):
                x = self.pos_x - each[0]
                if self.vector == (0, 1):
                    y = self.pos_y
                elif self.vector == (0, -1):
                    y = self.pos_y - each[1]
                for xx in range(each[0]):
                    tiles_in_candidate = utilities.tiles_from_top_left(x + xx,
                                                                       y,
                                                                       each[0],
                                                                       each[1])
                    buffer_tiles = buffer_from_room(tiles_in_candidate)
                    if not self.bounds_check(buffer_tiles, cells):
                        if not self.occupation_check(buffer_tiles, cells):
                            shape_permutations.append(tiles_in_candidate)
            elif self.vector == (1, 0) or self.vector == (-1, 0):
                y = self.pos_y - each[1]
                if self.vector == (1, 0):
                    x = self.pos_x
                elif self.vector == (-1, 0):
                    x = self.pos_x - each[1]
                for yy in range(each[1]):
                    tiles_in_candidate = utilities.tiles_from_top_left(x,
                                                                       y + yy,
                                                                       each[0],
                                                                       each[1])
                    buffer_tiles = buffer_from_room(tiles_in_candidate)
                    if not self.bounds_check(buffer_tiles, cells):
                        if not self.occupation_check(buffer_tiles, cells):
                            shape_permutations.append(tiles_in_candidate)
            if shape_permutations:
                shifted_permutations.append(shape_permutations)
                break

        if shifted_permutations:
            return random.choice(shifted_permutations[0])
        return None

































    def set_room_to_step_old(self, cells):
        center_x = self.pos_x + self.vector[0] * math.floor(self.size / 2)
        center_y = self.pos_y + self.vector[1] * math.floor(self.size / 2)
        room_tiles = utilities.tiles_in_range(center_x, center_y, self.size, self.size)
        room_buffer = utilities.tiles_in_range(center_x, center_y, self.size + 2, self.size + 2)
        if self.bounds_check(room_buffer, cells):
            self.deactivate()
            return
        if not self.occupation_check(room_buffer, cells):
            for each in room_buffer:
                if cells[each[1]][each[0]] != 3:
                    cells[each[1]][each[0]] = 5
            for each in room_tiles:
                cells[each[1]][each[0]] = 4
            return
        self.deactivate()
        return


