import pygame
import tile
import colors
import utilities
import math
import random


class Tunneler(object):
    def __init__(self, start_x, start_y, corr_width, change_dir_prob, roomie_spawn_prob, vector):
        self.pos_x = start_x
        self.pos_y = start_y
        self.id_tag = utilities.generate_id_tag()
        self.corr_width = corr_width
        self.change_dir_prob = change_dir_prob
        self.roomie_spawn_prob = roomie_spawn_prob
        self.vector = vector
        self.last_step, self.last_step_buffer = self.set_start_tiles(start_x, start_y, vector)
        self.active = True
        self.action_timer = 0
        self.reset_action_timer()
        self.lifespan = (corr_width * 40)

    def __lt__(self, other):
        return False

    def deactivate(self):
        self.active = False

    def reset_action_timer(self):
        self.action_timer = (1 + self.corr_width ** 2) * 2

    def set_start_tiles(self, start_x, start_y, vector):
        first_step = []
        first_step_buffer = []
        if vector == (0, 1) or vector == (0, -1):
            for xx in range(start_x - math.floor(self.corr_width / 2), start_x + math.floor(self.corr_width / 2) + 1):
                first_step.append((xx, start_y))
            for xx in range(start_x - math.floor((self.corr_width + 1) / 2), start_x + math.floor((self.corr_width + 1) / 2) + 1):
                first_step_buffer.append((xx, start_y))
        elif vector == (1, 0) or vector == (-1, 0):
            for yy in range(start_y - math.floor(self.corr_width / 2), start_y + math.floor(self.corr_width / 2) + 1):
                first_step.append((start_x, yy))
            for yy in range(start_y - math.floor((self.corr_width + 1) / 2), start_y + math.floor((self.corr_width + 1) / 2) + 1):
                first_step_buffer.append((start_x, yy))
        return first_step, first_step_buffer

    def spawn_check(self, cells):
        chance_to_spawn = random.randint(1, 100)
        if chance_to_spawn < 10 + (5 * self.corr_width):
            return True
        return False

    def spawn_roomie(self, cells):
        child_vector = self.roll_new_vector()
        child_x, child_y = self.get_child_start(self.vector, child_vector)
        new_roomie = Roomie(child_x, child_y, 1 + self.corr_width ** 2, child_vector)
        if new_roomie.bounds_check([new_roomie.origin], cells):
            return None
        if new_roomie.occupation_check([new_roomie.origin], cells):
            return None
        self.reset_action_timer()
        return new_roomie

    def spawn_tunneler(self, cells):
        child_vector = self.roll_new_vector()
        child_x, child_y = self.get_child_start(self.vector, child_vector)
        new_tunneler = Tunneler(child_x, child_y, random.randint(1, self.corr_width), 10, 0, child_vector)
        if new_tunneler.bounds_check(new_tunneler.last_step, cells):
            return None
        if new_tunneler.occupation_check(new_tunneler.last_step, cells):
            return None
        self.reset_action_timer()
        return new_tunneler

    def get_child_start(self, parent_vector, child_vector):
        child_x = self.pos_x - parent_vector[0] * math.floor(self.corr_width / 2)
        child_y = self.pos_y - parent_vector[1] * math.floor(self.corr_width / 2)
        child_x += child_vector[0] * (math.floor(self.corr_width / 2) + 1)
        child_y += child_vector[1] * (math.floor(self.corr_width / 2) + 1)
        return child_x, child_y

    def mark_step(self, cells):
        # for each in self.last_step_buffer:
            # cells[each[1]][each[0]] = 5
        for each in self.last_step:
            cells[each[1]][each[0]] = 1

    def vector_check(self, cells):
        chance_to_change_vector = random.randint(0, 100)
        if chance_to_change_vector < self.change_dir_prob - self.corr_width * 2:
            self.reset_action_timer()
            old_vector = self.vector
            new_vector = self.roll_new_vector()
            self.vector = new_vector
            if not self.valid_turn_check(cells, old_vector, new_vector):
                print("Debug C")
                self.deactivate()
                return

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

    def valid_turn_check(self, cells, old_vector, new_vector):
        """Checks whether the tiles one step ahead along the old vector are clear, to make sure
        the new hallway doesn't parallel an existing one, then checks to make sure the way is clear
        along the new vector.  Returns False if any one tile in the pathway along the old or new
        vector are blocked, and returns True only if all tiles are clear - [0]"""
        next_step_old = utilities.modify_tile_group(self.last_step, old_vector)
        if self.occupation_check(next_step_old, cells):
            print("Debug D")
            return False
        self.reset_last_step(cells, old_vector)
        next_step_new = utilities.modify_tile_group(self.last_step, new_vector)
        if self.occupation_check(next_step_new, cells):
            print("Debug E")
            return False
        return True

    def reset_last_step(self, cells, old_vector):
        # TODO: Fix bug where a 1x1 hallway turns right and doesn't tunnel the final tile before moving on
        self.pos_x -= old_vector[0] * math.floor(self.corr_width / 2)
        self.pos_y -= old_vector[1] * math.floor(self.corr_width / 2)
        self.pos_x += self.vector[0] * math.floor((self.corr_width - 1) / 2)
        self.pos_y += self.vector[1] * math.floor((self.corr_width - 1) / 2)
        self.last_step, self.last_step_buffer = self.set_start_tiles(self.pos_x, self.pos_y, self.vector)

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
        next_step_buffer = utilities.modify_tile_group(self.last_step_buffer, vector)
        next_step = utilities.modify_tile_group(self.last_step, vector)
        if self.bounds_check(next_step, cells):
            print("Debug A")
            self.deactivate()
            return
        if self.occupation_check(next_step, cells):
            door_spots = self.door_creation_check(next_step, cells, self.vector)
            if len(door_spots) > 0:
                self.mark_door(cells, door_spots)
            print("Debug B")
            self.deactivate()
            return

        self.last_step_buffer = next_step_buffer
        self.last_step = next_step


class Roomie(object):
    def __init__(self, x, y, size, vector):
        self.id_tag = utilities.generate_id_tag()
        self.origin = (x, y)
        self.pos_x = x + vector[0]
        self.pos_y = y + vector[1]
        self.vector = vector
        self.size = size
        self.active = True

    def mark_origin(self, cells):
        cells[self.origin[1]][self.origin[0]] = 3

    def unmark_origin(self, cells):
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

    def occupation_check(self, step, cells):
        occupied_spaces = []
        for each in step:
            if any([cells[each[1]][each[0]] == 1,
                    cells[each[1]][each[0]] == 2,
                    cells[each[1]][each[0]] == 4]):
                occupied_spaces.append(True)

        if any(occupied_spaces):
            return True
        return False

    def set_room_to_step(self, cells):
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


