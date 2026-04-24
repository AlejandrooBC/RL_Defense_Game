"""Contains the Sniper class for the game Audition Absurdity"""
import pygame
import random
from sniper_bullet_class import SniperBullet

# Creating a 2D vector to use in the future
vector = pygame.math.Vector2


class Sniper(pygame.sprite.Sprite):
    """An enemy class that makes snipers move across the screen"""

    def __init__(self, player, game, x, y, window_width, window_height, FPS, clock, platform_group, barrier_group,
                 team_bullet_group, enemy_bullet_group, player_bullet_group, team_group, min_speed, max_speed):
        """Initialize the sniper"""

        super().__init__()

        # Attaching sprite groups
        self.player = player
        self.game = game
        self.window_width = window_width
        self.window_height = window_height
        self.FPS = FPS
        self.clock = clock
        self.platform_group = platform_group
        self.barrier_group = barrier_group
        self.team_bullet_group = team_bullet_group
        self.enemy_bullet_group = enemy_bullet_group
        self.player_bullet_group = player_bullet_group
        self.team_group = team_group

        # Setting constant variables
        self.MOVE_TIME = 0
        self.STOP_TIME = random.randint(2, 4)
        self.LAST_SHOT = pygame.time.get_ticks()
        self.SHOOT_COOLDOWN = None  # will be randomly generated each time inside the update() method
        self.HORIZONTAL_ACCELERATION = 2  # 0.5
        self.HORIZONTAL_FRICTION = 0.8
        self.STARTING_HEALTH = 40  # 100

        # Adding to team group
        self.team_group.add(self)

        # Animation frames
        self.move_right_sprites = []
        self.shoot_right_sprites = []

        self.hurt_right_sprites = []
        self.die_right_sprites = []

        # Moving (running)
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/run/13_Char_Run_000.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/run/13_Char_Run_001.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/run/13_Char_Run_002.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/run/13_Char_Run_003.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/run/13_Char_Run_004.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/run/13_Char_Run_005.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/run/13_Char_Run_006.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/run/13_Char_Run_007.png"), (64, 64)))

        # Shooting
        self.shoot_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/shoot/13_Char_Shoot_000.png"), (64, 64)))
        self.shoot_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/shoot/13_Char_Shoot_001.png"), (64, 64)))
        self.shoot_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/shoot/13_Char_Shoot_002.png"), (64, 64)))
        self.shoot_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/shoot/13_Char_Shoot_003.png"), (64, 64)))
        self.shoot_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/shoot/13_Char_Shoot_004.png"), (64, 64)))

        # Hurting (when enemy is hit by a projectile)
        self.hurt_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/hurt/13_Char_Hurt_000.png"), (64, 64)))
        self.hurt_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/hurt/13_Char_Hurt_001.png"), (64, 64)))
        self.hurt_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/hurt/13_Char_Hurt_002.png"), (64, 64)))
        self.hurt_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/hurt/13_Char_Hurt_003.png"), (64, 64)))
        self.hurt_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/hurt/13_Char_Hurt_004.png"), (64, 64)))
        self.hurt_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/hurt/13_Char_Hurt_005.png"), (64, 64)))
        self.hurt_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/hurt/13_Char_Hurt_006.png"), (64, 64)))
        self.hurt_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/hurt/13_Char_Hurt_007.png"), (64, 64)))

        # Dying (when enemy health is fully drained)
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/dead/13_Char_Dead_000.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/dead/13_Char_Dead_001.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/dead/13_Char_Dead_002.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/dead/13_Char_Dead_003.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/dead/13_Char_Dead_004.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/dead/13_Char_Dead_005.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/dead/13_Char_Dead_006.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/dead/13_Char_Dead_007.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/dead/13_Char_Dead_008.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/sniper/dead/13_Char_Dead_009.png"), (64, 64)))

        # Loading image and getting rect
        self.current_sprite = 0
        self.image = self.move_right_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        # Animation booleans
        self.can_collide = True
        self.is_still = False
        self.is_dead = False
        self.done_dying = False
        self.can_fire = True
        self.animate_hurt = False
        self.animate_death = False
        self.animate_fire = False

        # Loading sounds
        self.damage_sound = pygame.mixer.Sound("sounds/sniper/enemy_damage.wav")
        self.fire_sound = pygame.mixer.Sound("sounds/sniper/sniper_fire.wav")
        self.death_sound = pygame.mixer.Sound("sounds/sniper/headshot.wav")
        self.death_sound.set_volume(1.5)
        self.playing_death_sound = True

        # Kinematics vectors
        self.position = vector(x, y)
        self.velocity = vector(random.randint(min_speed, max_speed), 0)
        self.acceleration = vector(0, 0)

        # Blood sprite (when enemy health is fully drained)
        self.blood_sprite = pygame.transform.scale(pygame.image.load("images/tiles/blood.png"), (15, 15))
        self.blood_sprite_rect = self.blood_sprite.get_rect()

        # Setting initial sniper values
        self.frame_count = 0
        self.health = self.STARTING_HEALTH
        self.starting_x = x
        self.starting_y = y

    def update(self):
        """Update the sniper"""

        # Determining when the sniper should fire a projectile (by generating a random cooldown)
        # Limiting the number of projectiles on the screen
        self.SHOOT_COOLDOWN = random.randint(1000, 3000)
        if len(self.team_bullet_group) < 3:
            now_shoot = pygame.time.get_ticks()
            if now_shoot - self.LAST_SHOT >= self.SHOOT_COOLDOWN:
                self.LAST_SHOT = now_shoot
                self.fire()

        # Checking if the sniper's health has been fully drained
        if self.health <= 0:
            # Blitting the blood image to the display surface when the enemy is killed
            self.blood_sprite_rect.bottomleft = self.position
            self.game.display_surface.blit(self.blood_sprite, self.blood_sprite_rect)
            self.can_collide = False
            self.is_dead = True
            if self.is_dead:
                self.die()
                self.is_dead = False

        # Checking if the dying animation has been fully completed
        # If so, we kill the sniper from the sprite group
        if self.done_dying:
            self.player.player_eliminations += 1
            self.kill()

        # Determining when the sniper will stop to shoot
        self.frame_count += 1
        if self.frame_count % self.FPS == 0:
            self.MOVE_TIME += 1
            self.frame_count = 0
            if self.MOVE_TIME == self.STOP_TIME:
                self.is_still = True
                self.can_fire = True

        if not self.is_still:
            self.can_fire = False
            self.move()

        self.check_platform_collisions()
        self.check_damage_collisions()
        self.check_animations()

    def move(self):
        """Move the sniper"""

        # Setting the acceleration vector
        self.acceleration = vector(0, 0)

        self.acceleration.x = self.HORIZONTAL_ACCELERATION
        self.animate(self.move_right_sprites, 0.25)

        # Calculating new kinematics values
        self.acceleration.x -= self.velocity.x * self.HORIZONTAL_FRICTION
        self.velocity += self.acceleration
        self.position += self.velocity + (0.5 * self.acceleration)

        self.rect.bottomleft = self.position

    def check_platform_collisions(self):
        """Check for collisions with platforms"""

        if self.can_collide:
            # Checking for collisions between sniper and platform group (the stone tiles)
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
            if collided_platforms:
                self.position.x -= 3
                self.velocity.x = 0
                self.rect.bottomleft = self.position

    def check_damage_collisions(self):
        """Check for collisions with ally/player projectiles"""

        if self.can_collide:
            # Check collisions for THIS enemy only
            hit_by_player = pygame.sprite.spritecollide(self, self.player_bullet_group, True)
            hit_by_enemies = pygame.sprite.spritecollide(self, self.enemy_bullet_group, True)
            if hit_by_player or hit_by_enemies:
                self.damage_sound.play()
                self.damage_sound.set_volume(2)
                self.health -= 10
                self.animate_hurt = True

    def check_animations(self):
        """Check to see if the hurt/death/fire animations should run"""

        # Animating the sniper hurt animation (when hit by a bullet)
        if self.animate_hurt:
            self.animate(self.hurt_right_sprites, 0.8)

        # Animating the sniper death animation (when killed/health drained to zero)
        if self.animate_death and self.is_still:
            self.animate(self.die_right_sprites, 0.1)

        # Animating the sniper fire animation (shooting the weapon)
        if self.is_still and self.animate_fire:
            self.animate(self.shoot_right_sprites, 0.1)

    def fire(self):
        """Fire a projectile from the gun"""

        if self.can_fire:
            self.fire_sound.play()
            SniperBullet(self.rect.centerx, self.rect.centery, self.team_bullet_group, self.barrier_group, self, 3)
            self.animate_fire = True

    def die(self):
        """Sniper is killed when its health is fully drained"""

        self.can_fire = False
        self.is_still = True
        self.animate_death = True

        if self.playing_death_sound and self.death_sound.get_num_channels() == 0:
            self.death_sound.play()
            self.playing_death_sound = False

    def animate(self, sprite_list, speed):
        """Animate the sniper's actions"""

        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        elif sprite_list == self.die_right_sprites:
            self.done_dying = True
        else:
            self.current_sprite = 0
            # Ending the hurt animation
            if self.animate_hurt:
                self.animate_hurt = False
            # Ending the fire animation
            if self.animate_fire:
                self.animate_fire = False
            # Ending the death animation
            if self.animate_death:
                self.animate_death = False

        self.image = sprite_list[int(self.current_sprite)]
