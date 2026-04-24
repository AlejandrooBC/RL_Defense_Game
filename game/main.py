import pygame
from game_class import Game
from tile_class import Tile
from player_class import Player
from ruby_maker_class import RubyMaker

# Initializing pygame
pygame.init()

# Setting the display surface dimensions
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 736

# Setting the display surface
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Audition Absurdity")

# Setting FPS and clock
FPS = 60
clock = pygame.time.Clock()


def main():
    # Creating sprite groups
    my_main_tile_group = pygame.sprite.Group()
    my_platform_group = pygame.sprite.Group()
    my_barrier_group = pygame.sprite.Group()

    my_player_group = pygame.sprite.Group()
    my_player_bullet_group = pygame.sprite.Group()



    my_enemy_group = pygame.sprite.Group()
    my_enemy_bullet_group = pygame.sprite.Group()

    my_ruby_group = pygame.sprite.Group()

    # Creating the tile map
    # -1 --> player tile
    # 0 --> no tile, 1 --> stone tile, 2 --> chest tile, 3 --> barrel tile, 4 --> torch tile, 5 --> wood tile
    # 6 --> concrete tile, 7 --> barrier tile, 8 --> carpet tile, 9 --> chandelier tile
    # -2 --> infantryman tile, -3 --> sniper tile, -4 --> ruby maker tile, -5 --> ally_one tile, -6 --> ally_two tile
    # 19 rows, 40 columns
    tile_map = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4, 2, 2, 8, 8, 8, 8, 8, 8, 8, 8, 8, 2, 2, 4, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 8, 5, 5, 9, 5, 5, 5, 5, 5, 5, 5, 9, 5, 5, 3, 1],
        [-2, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 1, 8, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 3, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 8, 5, 5, 5, 5, 5, 5, 5, 7, 5, 5, 5, 5, 5, 3, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 8, 5, 5, 5, 5, 5, 5, 5, 7, 5, 5, 5, 5, 5, 2, 1],
        [-3, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 1, 8, 5, 5, 5, 5, 5, -1, 5, 7, 5, 5, 5, 5, 5, 3, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 8, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 2, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 8, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 8, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 8, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 8, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 8, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 8, 1],
        [-3, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 1, 8, 5, 5, 5, 5, 5, 5, 5, 7, 5, 5, 5, 5, 5, 8, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 8, 5, 5, 5, 5, 5, 5, 5, 7, 5, 5, 5, 5, 5, 8, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 8, 5, 5, 5, 5, 5, 5, 5, 7, 5, 5, 5, 5, 5, 8, 1],
        [-2, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 1, 8, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 8, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 8, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 8, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 8, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, -4, 5, 8, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 4, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ]

    # Generating Tile objects from the tile map
    # Loop through the 19 lists (rows) in the tile map ("i" moves down the map)
    for i in range(len(tile_map)):
        # Loop through the 40 elements in a given list ("j" moves across the map)
        for j in range(len(tile_map[i])):
            # Stone tile
            if tile_map[i][j] == 1:
                Tile(j * 32, i * 32, 1, my_main_tile_group, my_platform_group)
            # Chest tile
            elif tile_map[i][j] == 2:
                Tile(j * 32, i * 32, 5, my_main_tile_group)
                Tile(j * 32, i * 32, 2, my_main_tile_group)
            # Barrel tile
            elif tile_map[i][j] == 3:
                Tile(j * 32, i * 32, 5, my_main_tile_group)
                Tile(j * 32, i * 32, 3, my_main_tile_group, my_platform_group)
            # Torch tile
            elif tile_map[i][j] == 4:
                Tile(j * 32, i * 32, 5, my_main_tile_group)
                Tile(j * 32, i * 32, 4, my_main_tile_group)
            # Wood tile
            elif tile_map[i][j] == 5:
                Tile(j * 32, i * 32, 5, my_main_tile_group)
            # Concrete tile
            elif tile_map[i][j] == 6:
                Tile(j * 32, i * 32, 6, my_main_tile_group)
            # Barrier tile
            elif tile_map[i][j] == 7:
                Tile(j * 32, i * 32, 7, my_main_tile_group, my_platform_group, my_barrier_group)
            # Carpet tile
            elif tile_map[i][j] == 8:
                Tile(j * 32, i * 32, 5, my_main_tile_group)
                Tile(j * 32, i * 32, 8, my_main_tile_group)
            # Chandelier tile
            elif tile_map[i][j] == 9:
                Tile(j * 32, i * 32, 5, my_main_tile_group)
                Tile(j * 32, i * 32, 9, my_main_tile_group)
            # Player tile
            elif tile_map[i][j] == -1:
                my_player = Player(WINDOW_WIDTH, WINDOW_HEIGHT, j * 32 - 32, i * 32 + 32, my_platform_group,
                                   my_barrier_group, my_player_bullet_group, my_enemy_bullet_group)
                my_player_group.add(my_player)
                Tile(j * 32, i * 32, 5, my_main_tile_group)
            # Player tile
            elif tile_map[i][j] == -4:
                Tile(j * 32, i * 32, 5, my_main_tile_group)
                RubyMaker(j * 32, i * 32, my_main_tile_group)

    # Loading in a background image (resized to fit the screen)
    background_image_one = pygame.transform.scale(pygame.image.load("images/background.png"), (1280, 736))  # 615
    background_image_one_rect = background_image_one.get_rect()
    background_image_one_rect.topleft = (0, 0)

    # Creating a game
    my_game = Game(tile_map, WINDOW_WIDTH, WINDOW_HEIGHT, FPS, clock, display_surface, my_player,
                   my_player_bullet_group, my_enemy_group, my_enemy_bullet_group, my_main_tile_group, my_platform_group,
                   my_barrier_group, my_ruby_group)
    my_game.pause_game("AUDITION ABSURDITY", "Press 'Enter' to Begin")

    # The main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    my_player.fire()
            

        # Blitting the background image
        display_surface.blit(background_image_one, background_image_one_rect)

        # Drawing tiles
        my_main_tile_group.update()
        my_main_tile_group.draw(display_surface)

        my_platform_group.update()
        my_platform_group.draw(display_surface)

        my_barrier_group.update()
        my_barrier_group.draw(display_surface)

        # Updating and drawing sprite groups
        my_player_group.update()
        my_player_group.draw(display_surface)

        my_player_bullet_group.update()
        my_player_bullet_group.draw(display_surface)

        my_enemy_group.update()
        my_enemy_group.draw(display_surface)

        my_enemy_bullet_group.update()
        my_enemy_bullet_group.draw(display_surface)

        my_ruby_group.update()
        my_ruby_group.draw(display_surface)

        # Updating and drawing the game
        my_game.update()
        my_game.draw()

        # Updating the display and ticking the clock
        pygame.display.update()
        clock.tick(FPS)

    # Ending the game
    pygame.quit()


if __name__ == "__main__":
    main()
