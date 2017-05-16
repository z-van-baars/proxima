import pygame
import math
import entity
import colors
import display
import mapgen

screen_width = 800#int(input("Width?\n"))
screen_height = 800#int(input("Height?\n"))
pygame.init()


def mouse_down(event):
    pass

def mouse_up(event):
    pass


def key_up(event, player):
    if event.key == pygame.K_w:
        player.y_speed += player.speed
    elif event.key == pygame.K_s:
        player.y_speed -= player.speed
    elif event.key == pygame.K_a:
        player.x_speed += player.speed
    elif event.key == pygame.K_d:
        player.x_speed -= player.speed


def key_down(room, event, player):
    if event.key == pygame.K_w:
        player.y_speed = -player.speed
    elif event.key == pygame.K_s:
        player.y_speed = player.speed
    elif event.key == pygame.K_a:
        player.x_speed = -player.speed
    elif event.key == pygame.K_d:
        player.x_speed = player.speed
    elif event.key == pygame.K_e:
        player.use = True
    elif event.key == pygame.K_SPACE:
        room.generate_random_coins(10)


def main():
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode([screen_width, screen_height])

    room_1 = mapgen.Room(40, 40)
    for ii in range(0, 19):
        room_1.add_wall(ii, 0)
    for ii in range(21, 40):
        room_1.add_wall(ii, 0)
    for ii in range(0, 19):
        room_1.add_wall(ii, 39)
    for ii in range(21, 40):
        room_1.add_wall(ii, 39)
    for ii in range(1, 39):
        room_1.add_wall(0, ii)
    for ii in range(1, 39):
        room_1.add_wall(39, ii)
    room_1.generate_random_walls(40)
    room_1.generate_random_coins(4)
    room_1.update_static_display_layer()

    player = entity.DynamicEntity(40, 40, 19, 19, colors.red, 3)
    player.id_tag = "Player"
    room_1.dynamic_entities["Player"] = player

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    pygame.display.quit()
                    pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down(event, player)
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_up(event, player)
            elif event.type == pygame.KEYDOWN:
                key_down(room_1, event, player)
            elif event.type == pygame.KEYUP:
                key_up(event, player)

        for id_tag, each in room_1.dynamic_entities.items():
            each.move(room_1.tiles)
            each.pickup(room_1, room_1.tiles)

        screen.blit(room_1.background, [0, 0])

        screen.blit(room_1.static_display_layer, [0, 0])
        for id_tag, each in room_1.dynamic_entities.items():
            screen.blit(each.sprite.image, [each.pos_x, each.pos_y])

        pygame.display.flip()
        clock.tick(60)


main()