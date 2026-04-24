"""Contains the Game class for the game Audition Absurdity"""
import pygame
from tile_class import Tile
from infantryman_class import Infantryman
from sniper_class import Sniper
from ruby_class import Ruby



class Game:
    """A class to control and update gameplay"""
    def __init__(self, tile_map, window_width, window_height, FPS, clock, display_surface, player, player_bullet_group,
                 enemy_group, enemy_bullet_group, main_group, platform_group,
                 barrier_group, ruby_group):
        """Initialize the Game class"""

        # Attaching sprite groups and initializing attributes
        self.tile_map = tile_map
        self.window_width = window_width
        self.window_height = window_height
        self.FPS = FPS
        self.clock = clock
        self.display_surface = display_surface
        self.player = player
        self.player_bullet_group = player_bullet_group
        self.enemy_group = enemy_group
        self.enemy_bullet_group = enemy_bullet_group
        self.main_group = main_group
        self.platform_group = platform_group
        self.barrier_group = barrier_group
        self.ruby_group = ruby_group

        # Setting constant variables
        self.STARTING_ROUND_NUMBER = 1
        self.STARTING_FORTRESS_INTEGRITY = 100
        self.STARTING_ROUND_TIME = 30

        self.STARTING_INFANTRYMAN_CREATION_TIME = 3
        self.STARTING_SNIPER_CREATION_TIME = 6

        self.STARTING_RUBY_ADD_ELIMINATIONS = 3

        # Setting game values
        self.round_number = self.STARTING_ROUND_NUMBER
        self.frame_count = 0
        self.fortress_integrity = self.STARTING_FORTRESS_INTEGRITY
        self.round_time = self.STARTING_ROUND_TIME
        self.infantryman_creation_time = self.STARTING_INFANTRYMAN_CREATION_TIME
        self.sniper_creation_time = self.STARTING_SNIPER_CREATION_TIME
        self.ruby_add_eliminations = self.STARTING_RUBY_ADD_ELIMINATIONS

        # Setting gameplay booleans
        self.added_ruby = False

        # Setting fonts
        self.title_font = pygame.font.Font("fonts/Tekno.ttf", 48)
        self.credits_font = pygame.font.Font("fonts/Tekno.ttf", 18)
        self.name_font = pygame.font.Font("fonts/Tekno.ttf", 18)
        self.HUD_font = pygame.font.Font("fonts/Facon.ttf", 24)

        # Setting sounds
        self.ruby_pickup_sound = pygame.mixer.Sound("sounds/ruby/ruby_pickup.wav")

    def update(self):
        """Update the game by calling methods inside the Game class"""

        # Updating the round time every second
        self.frame_count += 1
        if self.frame_count % self.FPS == 0:
            self.round_time -= 1
            self.frame_count = 0

        self.add_infantryman()
        self.add_sniper()
        self.add_ruby()
        self.check_ruby_collisions()
        self.check_round_completion()
        self.check_game_over_health()
        self.check_game_over_fortress()

    def draw(self):
        """Draw the game"""

        # Defining colors
        WHITE = (255, 255, 255)
        ORANGE = (255, 165, 0)

        # GAME HUD - setting text
        round_text = self.HUD_font.render(f"Wave: {str(self.round_number)}", True, WHITE)
        round_rect = round_text.get_rect()
        round_rect.topleft = (10, 10)

        round_time_text = self.HUD_font.render(f"Duration: {str(self.round_time)}", True, WHITE)
        round_time_rect = round_time_text.get_rect()
        round_time_rect.topleft = (10, 35)

        fortress_integrity_text = self.HUD_font.render(f"Fortress Integrity: {str(self.fortress_integrity)}", True, WHITE)
        fortress_integrity_rect = fortress_integrity_text.get_rect()
        fortress_integrity_rect.topright = (self.window_width - 80, 5)

        # CREDITS HUD - setting text
        made_by_text = self.credits_font.render("MADE BY", True, ORANGE)
        made_by_rect = made_by_text.get_rect()
        made_by_rect.bottomright = (self.window_width - 10, self.window_height - 40)

        name_by_text = self.name_font.render("ALEJANDRO BEGARA CRIADO", True, ORANGE)
        name_by_rect = name_by_text.get_rect()
        name_by_rect.bottomright = (self.window_width - 8, self.window_height - 10)

        # PLAYER HUD - setting text
        player_score_text = self.HUD_font.render(f"Score: {str(self.player.player_score)}", True, WHITE)
        player_score_rect = player_score_text.get_rect()
        player_score_rect.topleft = (8, 62)

        player_eliminations_text = self.HUD_font.render(f"Kills: {str(self.player.player_eliminations)}", True, WHITE)
        player_eliminations_rect = player_eliminations_text.get_rect()
        player_eliminations_rect.bottomleft = (150, self.window_height - 80)

        player_health_text = self.HUD_font.render(f"Health: {str(self.player.player_health)}", True, WHITE)
        player_health_rect = player_health_text.get_rect()
        player_health_rect.bottomleft = (150, self.window_height - 45)

        player_ammo_text = self.HUD_font.render(f"Ammo: {str(self.player.player_ammo)}", True, WHITE)
        player_ammo_rect = player_ammo_text.get_rect()
        player_ammo_rect.bottomleft = (150, self.window_height - 10)

        # PLAYER HUD - setting face image
        player_face = pygame.transform.scale(pygame.image.load("images/player/player_face.png"), (130, 100))
        player_face_rect = player_face.get_rect()
        player_face_rect.bottomleft = (10, self.window_height - 12)

        # Drawing the HUD lines
        pygame.draw.line(self.display_surface, WHITE, (0, self.window_height - 125), (self.window_width, self.window_height - 125), 4)
        pygame.draw.line(self.display_surface, WHITE, (340, self.window_height - 125), (340, self.window_height), 4)
        pygame.draw.line(self.display_surface, WHITE, (690, self.window_height - 125), (690, self.window_height), 4)

        # Drawing the GAME HUD
        self.display_surface.blit(made_by_text, made_by_rect)
        self.display_surface.blit(name_by_text, name_by_rect)
        self.display_surface.blit(round_text, round_rect)
        self.display_surface.blit(round_time_text, round_time_rect)
        self.display_surface.blit(fortress_integrity_text, fortress_integrity_rect)

        # Drawing the PLAYER HUD
        self.display_surface.blit(player_score_text, player_score_rect)
        self.display_surface.blit(player_eliminations_text, player_eliminations_rect)
        self.display_surface.blit(player_health_text, player_health_rect)
        self.display_surface.blit(player_ammo_text, player_ammo_rect)
        self.display_surface.blit(player_face, player_face_rect)

    def add_infantryman(self):
        """Add an infantryman to the game"""

        # Checking to add an infantryman every second
        if self.frame_count % self.FPS == 0:
            # Only add an infantryman if the infantry_creation_time has passed
            if self.round_time % self.infantryman_creation_time == 0:
                for i in range(len(self.tile_map)):
                    for j in range(len(self.tile_map[i])):
                        if self.tile_map[i][j] == -2 and len(self.enemy_group) < 5:
                            infantryman = Infantryman(self.player, self, j * 32 - 32, i * 32 + 32, self.window_width,
                                                      self.window_height, self.FPS, self.clock,
                                                      self.platform_group, self.barrier_group, self.enemy_bullet_group,
                                                      self.player_bullet_group, self.player_bullet_group,
                                                      self.enemy_group, 0, 1)
                            self.enemy_group.add(infantryman)
                            Tile(j * 32, i * 32, 6, self.main_group)

    def add_sniper(self):
        """Add a sniper to the game"""

        # Checking to add a sniper every second
        if self.frame_count % self.FPS == 0:
            # Only add a sniper if the sniper_creation_time has passed
            if self.round_time % self.sniper_creation_time == 0:
                for i in range(len(self.tile_map)):
                    for j in range(len(self.tile_map[i])):
                        if self.tile_map[i][j] == -3 and len(self.enemy_group) < 5:
                            sniper = Sniper(self.player, self, j * 32 - 32, i * 32 + 32, self.window_width,
                                            self.window_height, self.FPS, self.clock,
                                            self.platform_group, self.barrier_group, self.enemy_bullet_group,
                                            self.player_bullet_group, self.player_bullet_group,
                                            self.enemy_group, 0, 1)
                            self.enemy_group.add(sniper)
                            Tile(j * 32, i * 32, 6, self.main_group)


    def add_ruby(self):
        """Add a ruby to the game"""

        # Checking to add a ruby when the player has eliminated three enemies
        if self.player.player_eliminations == self.ruby_add_eliminations:
            self.added_ruby = True
            if self.added_ruby:
                ruby = Ruby(self.window_width, self.window_height, self.platform_group)
                self.ruby_group.add(ruby)
                self.added_ruby = False
                self.ruby_add_eliminations += 3

    def check_ruby_collisions(self):
        """Check if player collided with a ruby"""

        if pygame.sprite.spritecollide(self.player, self.ruby_group, True):
            self.ruby_pickup_sound.play()
            self.player.player_score += 100
            self.player.player_health += 10
            if self.player.player_health > self.player.STARTING_PLAYER_HEALTH:
                self.player.player_health = self.player.STARTING_PLAYER_HEALTH

           
    def check_round_completion(self):
        """Check if the player survived a wave"""

        if self.round_time == 0:
            self.player.player_score += 50
            self.start_new_round()

    def check_game_over_health(self):
        """Check to see if the player lost the game"""

        if self.player.player_health <= 0:
            self.pause_game(f"Game Over! Final Score: {str(self.player.player_score)}", "Press 'Enter' to play again...")
            self.reset_game()

    def check_game_over_fortress(self):
        """Check to see if the player lost the game from failing to defend the fortress"""

        if self.fortress_integrity <= 0:
            self.pause_game(f"Game Over! Final Score: {str(self.player.player_score)}", "Press 'Enter' to play again...")
            self.reset_game()

    def start_new_round(self):
        """Starts a new night"""

        self.round_number += 1

        # Resetting round values
        self.round_time = self.STARTING_ROUND_TIME
        

        # Resetting player values
        self.player.player_eliminations = self.player.STARTING_PLAYER_ELIMINATIONS
        self.player.reset()


        self.ruby_add_eliminations = self.STARTING_RUBY_ADD_ELIMINATIONS

        # Emptying sprite groups
        self.enemy_group.empty()
        self.enemy_bullet_group.empty()
        self.ruby_group.empty()
        self.player_bullet_group.empty()
        self.ally_bullet_group.empty()

        self.pause_game("You survived the wave!", "Press 'Enter' to continue")

    def pause_game(self, main_text, sub_text):
        """Pauses the game"""

        global running

        # Setting colors
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GREEN = (25, 200, 25)

        # Creating main pause text
        main_text = self.HUD_font.render(main_text, True, GREEN)
        main_rect = main_text.get_rect()
        main_rect.center = (self.window_width // 2, self.window_height // 2)

        # Creating sub pause text
        sub_text = self.HUD_font.render(sub_text, True, WHITE)
        sub_rect = sub_text.get_rect()
        sub_rect.center = (self.window_width // 2, self.window_height // 2 + 64)

        # Displaying the pause text
        self.display_surface.fill(BLACK)
        self.display_surface.blit(main_text, main_rect)
        self.display_surface.blit(sub_text, sub_rect)
        pygame.display.update()

        # Pausing the game until the user hits enter or quits
        is_paused = True
        while is_paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # User wants to continue
                    if event.key == pygame.K_RETURN:
                        is_paused = False
                # Users wants to quit
                if event.type == pygame.QUIT:
                    is_paused = False
                    running = False

    def reset_game(self):
        """Resets the game"""

        # Resetting game values
        self.fortress_integrity = self.STARTING_FORTRESS_INTEGRITY
        self.round_number = self.STARTING_ROUND_NUMBER
        self.round_time = self.STARTING_ROUND_TIME

        # Resetting creation times
        self.infantryman_creation_time = self.STARTING_INFANTRYMAN_CREATION_TIME
        self.sniper_creation_time = self.STARTING_SNIPER_CREATION_TIME
        self.ruby_add_eliminations = self.STARTING_RUBY_ADD_ELIMINATIONS

        # Resetting the player
        self.player.player_score = self.player.STARTING_PLAYER_SCORE
        self.player.player_health = self.player.STARTING_PLAYER_HEALTH
        self.player.player_ammo = self.player.STARTING_PLAYER_AMMO
        self.player.player_eliminations = self.player.STARTING_PLAYER_ELIMINATIONS
        self.player.reset()


        # Emptying sprite groups
        self.enemy_group.empty()
        self.enemy_bullet_group.empty()
        self.ruby_group.empty()
        self.player_bullet_group.empty()
        self.ally_bullet_group.empty()
