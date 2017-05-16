import pygame
import utilities
import colors


class Entity(object):
    dynamic = False
    blocks_tile = False
    name = "N/A"

    def __init__(self, pos_x, pos_y, width, height, color):
        self.id_tag = utilities.generate_id_tag()
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface([width, height])
        self.sprite.image.fill(color)
        self.rect = self.sprite.image.get_rect()
        self.current_tile = (int(pos_x / 20), int(pos_y / 20))
        self.rect.x = self.pos_x
        self.rect.y = self.pos_y


class StaticEntity(Entity):
    def __init__(self, pos_x, pos_y, width, height, color):
        super().__init__(pos_x, pos_y, width, height, color)


class Scenery(StaticEntity):
    def __init__(self, pos_x, pos_y, width, height, color):
        super().__init__(pos_x, pos_y, width, height, color)

    def tile_checkout(self, tile):
        tile.scenery = None
        tile.is_occupied = False
        tile.is_blocked = False

    def tile_checkin(self, tile):
        assert not tile.is_blocked
        tile.scenery = self
        tile.is_occupied = True
        tile.is_blocked = True


class Item(StaticEntity):
    def __init__(self, pos_x, pos_y, width, height, color):
        super().__init__(pos_x, pos_y, width, height, color)

    def tile_checkout(self, tile):
        tile.is_occupied = False
        tile.item = None

    def tile_checkin(self, tile):
        assert not tile.is_blocked
        tile.is_occupied = True
        tile.item = self


class DynamicEntity(Entity):
    def __init__(self, pos_x, pos_y, width, height, color, speed):
        super().__init__(pos_x, pos_y, width, height, color)
        self.x_speed = 0
        self.y_speed = 0
        self.use = False
        self.speed = speed
        self.coins = 0

    def tile_checkout(self, tile):
        tile.is_occupied = False
        tile.entity = None

    def tile_checkin(self, tile):
        assert not tile.is_blocked
        tile.is_occupied = True
        tile.entity = self

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
        if self.x_speed == 0 and self.y_speed == 0:
            return
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
            self.current_tile = rounded_coordinates
            self.tile_checkin(tiles[rounded_coordinates])
        self.rect.x = self.pos_x
        self.rect.y = self.pos_y

    def pickup(self, room, tiles):
        current_tile = self.current_tile
        neighbors = utilities.get_adjacent_tiles(room, current_tile[0], current_tile[1])
        for each in neighbors:
            if tiles[each].item is not None:
                player_rect = self.rect
                coin_rect = tiles[each].item.rect
                if player_rect.colliderect(coin_rect):
                    self.coins += 1
                    coin_id = tiles[each].item.id_tag
                    tiles[each].item.tile_checkout(tiles[each])
                    del room.static_entities[coin_id]
                    room.update_static_display_layer()


class Wall(Scenery):
    blocks_tile = True

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, 20, 20, colors.blue)


class Coin(Item):
    name = "Coin"

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y, 6, 6, colors.gold)
