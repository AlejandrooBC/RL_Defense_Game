"""Contains the Player class for the game Audition Absurdity"""
import pygame
from player_bullet_class import PlayerBullet

# Creating a 2D vector to use in the future
vector = pygame.math.Vector2


class Player(pygame.sprite.Sprite):
    """A class the user can control"""

    def __init__(self, window_width, window_height, x, y, platform_group, barrier_group, personal_bullet_group, enemy_bullet_group):
        """Initialize the player"""

        super().__init__()

        # Attaching sprite groups
        self.window_width = window_width
        self.window_height = window_height
        self.platform_group = platform_group
        self.barrier_group = barrier_group
        self.personal_bullet_group = personal_bullet_group
        self.enemy_bullet_group = enemy_bullet_group

        # Setting constant variables
        self.HORIZONTAL_ACCELERATION = 2
        self.HORIZONTAL_FRICTION = 0.4

        self.VERTICAL_ACCELERATION = 2
        self.VERTICAL_FRICTION = 0.4

        self.STARTING_PLAYER_ELIMINATIONS = 0
        self.STARTING_PLAYER_SCORE = 0
        self.STARTING_PLAYER_HEALTH = 1000
        self.STARTING_PLAYER_AMMO = 1000

        # Animation frames
        self.move_right_sprites = []
        self.move_left_sprites = []

        self.aim_right_sprites = []
        self.aim_left_sprites = []

        self.shoot_right_sprites = []
        self.shoot_left_sprites = []

        self.revive_right_sprites = []
        self.revive_left_sprites = []

        # Moving (running)
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/7_Char_Run_000.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/7_Char_Run_001.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/7_Char_Run_002.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/7_Char_Run_003.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/7_Char_Run_004.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/7_Char_Run_005.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/7_Char_Run_006.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/run/7_Char_Run_007.png"), (64, 64)))
        for sprite in self.move_right_sprites:
            self.move_left_sprites.append(pygame.transform.flip(sprite, True, False))

        # Aiming
        self.aim_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/aim/7_Char_Idle_Aim_000.png"), (64, 64)))
        self.aim_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/aim/7_Char_Idle_Aim_001.png"), (64, 64)))
        self.aim_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/aim/7_Char_Idle_Aim_002.png"), (64, 64)))
        self.aim_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/aim/7_Char_Idle_Aim_003.png"), (64, 64)))
        self.aim_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/aim/7_Char_Idle_Aim_004.png"), (64, 64)))
        self.aim_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/aim/7_Char_Idle_Aim_005.png"), (64, 64)))
        self.aim_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/aim/7_Char_Idle_Aim_006.png"), (64, 64)))
        self.aim_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/aim/7_Char_Idle_Aim_007.png"), (64, 64)))
        for sprite in self.aim_right_sprites:
            self.aim_left_sprites.append(pygame.transform.flip(sprite, True, False))

        # Shooting
        self.shoot_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/shoot/7_Char_Shoot_000.png"), (64, 64)))
        self.shoot_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/shoot/7_Char_Shoot_001.png"), (64, 64)))
        self.shoot_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/shoot/7_Char_Shoot_002.png"), (64, 64)))
        self.shoot_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/shoot/7_Char_Shoot_003.png"), (64, 64)))
        self.shoot_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/shoot/7_Char_Shoot_004.png"), (64, 64)))
        for sprite in self.shoot_right_sprites:
            self.shoot_left_sprites.append(pygame.transform.flip(sprite, True, False))

        # Reviving
        self.revive_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/revive/7_Char_Crouch_Throw_000.png"), (64, 64)))
        self.revive_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/revive/7_Char_Crouch_Throw_001.png"), (64, 64)))
        self.revive_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/revive/7_Char_Crouch_Throw_002.png"), (64, 64)))
        self.revive_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/revive/7_Char_Crouch_Throw_003.png"), (64, 64)))
        self.revive_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/revive/7_Char_Crouch_Throw_004.png"), (64, 64)))
        self.revive_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/revive/7_Char_Crouch_Throw_005.png"), (64, 64)))
        self.revive_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/revive/7_Char_Crouch_Throw_006.png"), (64, 64)))
        self.revive_right_sprites.append(pygame.transform.scale(pygame.image.load("images/player/revive/7_Char_Crouch_Throw_007.png"), (64, 64)))
        for sprite in self.revive_right_sprites:
            self.revive_left_sprites.append(pygame.transform.flip(sprite, True, False))

        # Loading image and getting rect
        self.current_sprite = 0
        self.image = self.aim_left_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        # Animation/sound booleans
        self.is_still = True
        self.animate_revive = False
        self.animate_fire = False

        # Loading sounds
        self.damage_sound = pygame.mixer.Sound("sounds/player/damage_sound.wav")
        self.fire_sound = pygame.mixer.Sound("sounds/player/player_fire.wav")
        self.revive_sound = pygame.mixer.Sound("sounds/player/bandage_sound.wav")
        self.running_sound = pygame.mixer.Sound("sounds/player/footstep.wav")

        # Kinematics vectors
        self.position = vector(x, y)
        self.velocity = vector(0, 0)
        self.acceleration = vector(0, 0)

        # Setting initial player values
        self.player_eliminations = self.STARTING_PLAYER_ELIMINATIONS
        self.player_score = self.STARTING_PLAYER_SCORE
        self.player_health = self.STARTING_PLAYER_HEALTH
        self.player_ammo = self.STARTING_PLAYER_AMMO
        self.starting_x = x
        self.starting_y = y

    def update(self):
        """Update the player"""

        self.move()
        self.check_platform_collisions()
        self.check_damage_collisions()
        self.check_animations()

    def move(self):
        """Move the player"""

        # Setting the acceleration vector
        self.acceleration = vector(0, 0)

        # If the user is pressing a key, we set the x-component of the acceleration to be nonzero
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            if self.running_sound.get_num_channels() == 0:
                self.running_sound.play()
            self.is_still = False
            self.acceleration.x = -1 * self.HORIZONTAL_ACCELERATION
            self.animate(self.move_left_sprites, 0.25)
        elif keys[pygame.K_RIGHT]:
            if self.running_sound.get_num_channels() == 0:
                self.running_sound.play()
            self.is_still = False
            self.acceleration.x = self.HORIZONTAL_ACCELERATION
            self.animate(self.move_right_sprites, 0.25)
        elif keys[pygame.K_UP]:
            if self.running_sound.get_num_channels() == 0:
                self.running_sound.play()
            self.is_still = False
            self.acceleration.y = -1 * self.VERTICAL_ACCELERATION
            self.animate(self.move_right_sprites, 0.25)  # arbitrary, just need animations for moving up
        elif keys[pygame.K_DOWN]:
            if self.running_sound.get_num_channels() == 0:
                self.running_sound.play()
            self.is_still = False
            self.acceleration.y = self.VERTICAL_ACCELERATION
            self.animate(self.move_left_sprites, 0.25)  # arbitrary, just need animations for moving down
        else:
            self.is_still = True
            if self.velocity.x > 0:
                self.animate(self.aim_right_sprites, 0.5)
            else:
                self.animate(self.aim_left_sprites, 0.5)

        # Calculating new kinematics values
        self.acceleration.x -= self.velocity.x * self.HORIZONTAL_FRICTION
        self.acceleration.y -= self.velocity.y * self.VERTICAL_FRICTION
        self.velocity += self.acceleration
        self.position += self.velocity + (0.5 * self.acceleration)

        self.rect.bottomleft = self.position

    def check_platform_collisions(self):
        """Check for collisions with platforms"""

        # Checking for collisions while moving horizontally to the left (x-direction)
        if self.velocity.x < 0:
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
            if collided_platforms:
                self.position.x += 3
                self.velocity.x = 0
                self.rect.bottomleft = self.position

        # Checking for collisions while moving horizontally to the right (x-direction)
        if self.velocity.x > 0:
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
            if collided_platforms:
                self.position.x -= 3
                self.velocity.x = 0
                self.rect.bottomleft = self.position

        # Checking for collisions while moving vertically up (y-direction)
        if self.velocity.y < 0:
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
            if collided_platforms:
                self.position.y += 3
                self.velocity.y = 0
                self.rect.bottomleft = self.position

        # Checking for collisions while moving vertically down (y-direction)
        if self.velocity.y > 0:
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
            if collided_platforms:
                self.position.y -= 3
                self.velocity.y = 0
                self.rect.bottomleft = self.position

    def check_damage_collisions(self):
        """Check for collisions with enemy bullets"""

        # Checking for collisions with enemy bullets that hit the player
        shot_by_enemies = pygame.sprite.spritecollide(self, self.enemy_bullet_group, True)
        if shot_by_enemies:
            self.damage_sound.play()
            self.damage_sound.set_volume(2)
            self.player_health -= 10

    def check_animations(self):
        """Check to see if the revive/fire animations should run"""

        # Animating the player revive
        if self.animate_revive:
            # If the player is moving right
            if self.velocity.x > 0:
                self.animate(self.revive_right_sprites, 0.1)
            else:
                self.animate(self.revive_left_sprites, 0.1)

        # Animating the player fire
        if self.animate_fire:
            # If the player is moving right
            if self.velocity.x > 0:
                self.animate(self.shoot_right_sprites, 0.1)
            else:
                self.animate(self.shoot_left_sprites, 0.1)

    def fire(self):
        """Fire a projectile from the gun"""

        # Restrict the number of bullets on the screen at a time
        # Only allow the player to shoot while standing still
        if len(self.personal_bullet_group) < 2 and self.is_still:
            self.fire_sound.play()
            PlayerBullet(self.rect.centerx, self.rect.centery, self.personal_bullet_group, self.barrier_group, self, 1)
            self.player_ammo -= 10
            self.animate_fire = True

    def reset(self):
        """Reset the player's position"""

        self.velocity = vector(0, 0)
        self.position = vector(self.starting_x, self.starting_y)
        self.rect.bottomleft = self.position

    def animate(self, sprite_list, speed):
        """Animate the player's actions"""

        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0
            if self.animate_fire:
                self.animate_fire = False

        self.image = sprite_list[int(self.current_sprite)]
