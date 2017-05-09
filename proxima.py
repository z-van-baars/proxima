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


def key_down(event, player):
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


def main():
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode([screen_width, screen_height])

    room_1 = mapgen.Room(40, 40)
    for ii in range(0, 40):
        room_1.add_wall(ii, 0)
    for ii in range(0, 40):
        room_1.add_wall(ii, 39)
    for ii in range(1, 39):
        room_1.add_wall(0, ii)
    for ii in range(1, 39):
        room_1.add_wall(39, ii)

    room_1.update_static_layer()

    player = entity.DynamicEntity(40, 40, 20, 20, colors.red, 3)
    room_1.dynamic_entities.add(player)

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
                key_down(event, player)
            elif event.type == pygame.KEYUP:
                key_up(event, player)

        for each in room_1.dynamic_entities:
            each.move(room_1.tiles)

        screen.blit(room_1.background, [0, 0])

        screen.blit(room_1.static_display_layer, [0, 0])
        for each in room_1.dynamic_entities:
            screen.blit(each.sprite.image, [each.pos_x, each.pos_y])

        pygame.display.flip()
        clock.tick(60)


main()