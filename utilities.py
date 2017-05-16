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


def get_adjacent_tiles(room, x, y):
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
            if not each[0] > room.x_tiles - 1 and not each[1] > room.y_tiles - 1:
                valid_neighbors.add(each)
    return valid_neighbors
