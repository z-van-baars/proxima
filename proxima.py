import pygame
import entity
import colors
import dungeon
import mapgen
import random


screen_width = 800  # int(input("Width?\n"))
screen_height = 800  # int(input("Height?\n"))
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

    first_dungeon = mapgen.Dungeon(2)
    current_room = first_dungeon.start_room

    player = entity.DynamicEntity(40, 40, 16, 16, colors.red, 3)
    player.id_tag = "Player"
    current_room.dynamic_entities["Player"] = player

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
                key_down(current_room, event, player)
            elif event.type == pygame.KEYUP:
                key_up(event, player)

        for id_tag, each in current_room.dynamic_entities.items():
            each.move(current_room.tiles)
            each.pickup(current_room, current_room.tiles)

        screen.blit(current_room.background, [0, 0])

        screen.blit(current_room.static_display_layer, [0, 0])
        for id_tag, each in current_room.dynamic_entities.items():
            screen.blit(each.sprite.image, [each.pos_x, each.pos_y])

        pygame.display.flip()
        clock.tick(60)


#main()

def dungeon_generation_test():
    random_dungeon = dungeon.ProcDungeon(140)
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode([screen_width, screen_height])
    start_xy = random_dungeon.set_start_point()
    random_dungeon.cells[start_xy[1]][start_xy[0]] = 2
    if start_xy[0] == 0:
        vector = (1, 0)
    elif start_xy[0] == random_dungeon.width - 1:
        vector = (-1, 0)
    if start_xy[1] == 0:
        vector = (0, 1)
    elif start_xy[1] == random_dungeon.height - 1:
        vector = (0, -1)
    corridor_width = 3
    first_tunneler = mapgen.Tunneler(start_xy[0], start_xy[1], corridor_width, 10, 0, vector)
    random_dungeon.evaluated_tiles = random_dungeon.update_evaluated_tiles()
    random_dungeon.paint_evaluated_tiles(4)
    gen1_tunnelers = [first_tunneler]
    gen2_tunnelers = []
    gen1_roomies = []
    print("Start....")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fill_count = 0
                    total_count = 0
                    for row in random_dungeon.cells:
                        for column in row:
                            total_count += 1
                            if not column == 0:
                                fill_count += 1
                    print("F: {0} / T: {1}".format(fill_count, total_count))
                    random_dungeon = dungeon.ProcDungeon(140)
                    clock = pygame.time.Clock()
                    screen = pygame.display.set_mode([screen_width, screen_height])
                    start_xy = random_dungeon.set_start_point()
                    random_dungeon.cells[start_xy[1]][start_xy[0]] = 2
                    if start_xy[0] == 0:
                        vector = (1, 0)
                    elif start_xy[0] == random_dungeon.width - 1:
                        vector = (-1, 0)
                    if start_xy[1] == 0:
                        vector = (0, 1)
                    elif start_xy[1] == random_dungeon.height - 1:
                        vector = (0, -1)
                    corridor_width = 3
                    first_tunneler = mapgen.Tunneler(start_xy[0], start_xy[1], corridor_width, 10, 0, vector)
                    random_dungeon.evaluated_tiles = random_dungeon.update_evaluated_tiles()
                    random_dungeon.paint_evaluated_tiles(4)
                    gen1_tunnelers = [first_tunneler]
                    gen2_tunnelers = []
                    gen1_roomies = []
        if len(gen1_tunnelers) < 1:
            gen1_tunnelers = gen2_tunnelers
            gen2_tunnelers = []
            for each in gen1_roomies:
                each.draw_room(random_dungeon.cells)
                if not each.active:
                    each.unmark_origin(random_dungeon.cells)
            gen1_roomies = []
        else:
            active_tunnelers = []
            for each in gen1_tunnelers:
                if each.action_timer > 0:
                    each.action_timer -= 1
                each.lifespan -= 1
                each.mark_step(random_dungeon.cells)
                if each.action_timer == 0:
                    each.vector_check(random_dungeon.cells)
                each.tunnel(random_dungeon.cells)
                if each.active:
                    if each.action_timer == 0:
                        child = each.spawn_check(random_dungeon.cells)
                        if child:
                            child_type = random.randint(0, 1)
                            if child_type == 1:
                                child = each.spawn_tunneler(random_dungeon.cells)
                                if child:
                                    gen2_tunnelers.append(child)
                            elif child_type == 0:
                                child = each.spawn_roomie(random_dungeon.cells)
                                if child:
                                    child.mark_origin(random_dungeon.cells)
                                    gen1_roomies.append(child)
                    if each.lifespan > 0:
                        active_tunnelers.append(each)
            gen1_tunnelers = active_tunnelers
        random_dungeon.evaluated_tiles = random_dungeon.update_evaluated_tiles()
        random_dungeon.paint_evaluated_tiles(4)
        screen.blit(random_dungeon.structure_preview, [0, 0])
        pygame.display.flip()
        clock.tick(200)



dungeon_generation_test()