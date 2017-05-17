import random
import math

letters = ["A", "B", "C", "D",
           "E", "F", "G", "H",
           "I", "J", "K", "L",
           "M", "N", "O", "P",
           "Q", "R", "S", "T",
           "U", "V", "W", "X",
           "Y", "Z"]
numbers = ['0', '1', '2', '3',
           '4', '5', '6', '7',
           '8', '9']


def generate_id_tag():
    id_string = "{0}{1}{2}{3}{4}".format(random.choice(letters),
                                         random.choice(letters),
                                         random.choice(letters),
                                         random.choice(numbers),
                                         random.choice(numbers))
    return id_string


def check_within(x, y, a1, b1, a2, b2):
    if not a1 <= x <= a2:
        return False
    if not b1 <= y <= b2:
        return False
    return True


def get_random_coordinates(x_lower, x_upper, y_lower, y_upper):
    x_position = random.randint(x_lower, x_upper)
    y_position = random.randint(y_lower, y_upper)
    return (x_position, y_position)


def corners(pos, width, height):
    top_left = pixel_to_tile((pos))
    top_right = pixel_to_tile((pos[0] + width, pos[1]))
    bottom_left = pixel_to_tile((pos[0], pos[1] + height))
    bottom_right = pixel_to_tile((pos[0] + width, pos[1] + height))
    return top_left, top_right, bottom_left, bottom_right


def pixel_to_tile(pixel_coordinates):
    tile_width = 20
    tile_height = 20
    return (math.floor(pixel_coordinates[0] / tile_width), math.floor(pixel_coordinates[1] / tile_height))


def get_room_neighbors(width, height, x, y):
    potential_neighbors = [(x, y - 1),
                           (x - 1, y),
                           (x + 1, y),
                           (x, y + 1)]
    valid_neighbors = set()
    for each in potential_neighbors:
        if not each[0] < 0 and not each[1] < 0:
            if not each[0] > width - 1 and not each[1] > height - 1:
                valid_neighbors.add(each)
    return valid_neighbors


def get_adjacent_tiles(width, height, x, y):
    potential_neighbors = [(x - 1, y - 1),
                           (x, y - 1),
                           (x + 1, y - 1),
                           (x - 1, y),
                           (x, y),
                           (x + 1, y),
                           (x - 1, y + 1),
                           (x, y + 1),
                           (x + 1, y + 1)]
    valid_neighbors = set()
    for each in potential_neighbors:
        if not each[0] < 0 and not each[1] < 0:
            if not each[0] > width - 1 and not each[1] > height - 1:
                valid_neighbors.add(each)
    return valid_neighbors
