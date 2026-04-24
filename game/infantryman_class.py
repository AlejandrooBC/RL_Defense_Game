"""Contains the Infantryman class for the game Audition Absurdity"""
import pygame
import random
from infantryman_bullet_class import InfantrymanBullet

# Creating a 2D vector to use in the future
vector = pygame.math.Vector2


class Infantryman(pygame.sprite.Sprite):
    """An enemy class that makes infantrymen move across the screen"""

    def __init__(self, player, game, x, y, window_width, window_height, FPS, clock, platform_group, barrier_group,
                 team_bullet_group, enemy_bullet_group, player_bullet_group, team_group, min_speed, max_speed):
        """Initialize the infantryman"""

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
        self.LAST = pygame.time.get_ticks()
        self.COOLDOWN = None  # will be randomly generated each time inside the update() method
        self.HORIZONTAL_ACCELERATION = 2  # 0.5
        self.HORIZONTAL_FRICTION = 0.8
        self.STARTING_HEALTH = 40  # 100

        # Adding to team group
        self.team_group.add(self)

        # Animation frames
        self.move_right_sprites = []
        self.aim_right_sprites = []

        self.shoot_right_sprites = []
        self.melee_right_sprites = []

        self.hurt_right_sprites = []
        self.die_right_sprites = []

        # Moving (running)
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/run/11_Char_Run_Aim_000.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/run/11_Char_Run_Aim_001.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/run/11_Char_Run_Aim_002.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/run/11_Char_Run_Aim_003.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/run/11_Char_Run_Aim_004.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/run/11_Char_Run_Aim_005.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/run/11_Char_Run_Aim_006.png"), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/run/11_Char_Run_Aim_007.png"), (64, 64)))

        # Aiming
        self.aim_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/aim/11_Char_Idle_Aim_001.png"), (64, 64)))
        self.aim_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/aim/11_Char_Idle_Aim_002.png"), (64, 64)))
        self.aim_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/aim/11_Char_Idle_Aim_003.png"), (64, 64)))
        self.aim_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/aim/11_Char_Idle_Aim_004.png"), (64, 64)))
        self.aim_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/aim/11_Char_Idle_Aim_005.png"), (64, 64)))
        self.aim_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/aim/11_Char_Idle_Aim_006.png"), (64, 64)))
        self.aim_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/aim/11_Char_Idle_Aim_007.png"), (64, 64)))
        self.aim_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/aim/11_Char_Idle_Aim_008.png"), (64, 64)))
        self.aim_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/aim/11_Char_Idle_Aim_009.png"), (64, 64)))

        # Shooting
        self.shoot_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/shoot/11_Char_Shoot_001.png"), (64, 64)))
        self.shoot_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/shoot/11_Char_Shoot_002.png"), (64, 64)))
        self.shoot_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/shoot/11_Char_Shoot_003.png"), (64, 64)))
        self.shoot_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/shoot/11_Char_Shoot_004.png"), (64, 64)))

        # Meleeing (knife attack)
        self.melee_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/melee/11_Char_Melee_000.png"), (64, 64)))
        self.melee_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/melee/11_Char_Melee_001.png"), (64, 64)))
        self.melee_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/melee/11_Char_Melee_002.png"), (64, 64)))
        self.melee_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/melee/11_Char_Melee_003.png"), (64, 64)))
        self.melee_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/melee/11_Char_Melee_004.png"), (64, 64)))
        self.melee_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/melee/11_Char_Melee_005.png"), (64, 64)))
        self.melee_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/melee/11_Char_Melee_006.png"), (64, 64)))
        self.melee_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/melee/11_Char_Melee_007.png"), (64, 64)))
        self.melee_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/melee/11_Char_Melee_008.png"), (64, 64)))
        self.melee_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/melee/11_Char_Melee_009.png"), (64, 64)))

        # Hurting (when enemy is hit by a projectile)
        self.hurt_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/hurt/11_Char_Hurt_000.png"), (64, 64)))
        self.hurt_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/hurt/11_Char_Hurt_001.png"), (64, 64)))
        self.hurt_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/hurt/11_Char_Hurt_002.png"), (64, 64)))
        self.hurt_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/hurt/11_Char_Hurt_003.png"), (64, 64)))
        self.hurt_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/hurt/11_Char_Hurt_004.png"), (64, 64)))
        self.hurt_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/hurt/11_Char_Hurt_005.png"), (64, 64)))
        self.hurt_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/hurt/11_Char_Hurt_006.png"), (64, 64)))
        self.hurt_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/hurt/11_Char_Hurt_007.png"), (64, 64)))

        # Dying (when enemy health is fully drained)
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/dead/11_Char_Dead_000.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/dead/11_Char_Dead_001.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/dead/11_Char_Dead_002.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/dead/11_Char_Dead_003.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/dead/11_Char_Dead_004.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/dead/11_Char_Dead_005.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/dead/11_Char_Dead_006.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/dead/11_Char_Dead_007.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/dead/11_Char_Dead_008.png"), (64, 64)))
        self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("images/infantryman/dead/11_Char_Dead_009.png"), (64, 64)))

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
        self.can_melee = False
        self.animate_hurt = False
        self.animate_death = False
        self.animate_melee = False
        self.animate_fire = False

        # Loading sounds
        self.damage_sound = pygame.mixer.Sound("sounds/infantryman/enemy_damage.wav")
        self.fire_sound = pygame.mixer.Sound("sounds/infantryman/infantryman_fire.wav")
        self.death_sound = pygame.mixer.Sound("sounds/infantryman/headshot.wav")
        self.death_sound.set_volume(1.5)
        self.melee_sound = pygame.mixer.Sound("sounds/infantryman/enemy_melee.wav")
        self.playing_death_sound = True

        # Kinematics vectors
        self.position = vector(x, y)
        self.velocity = vector(random.randint(min_speed, max_speed), 0)
        self.acceleration = vector(0, 0)

        # Blood sprite (when enemy health is fully drained)
        self.blood_sprite = pygame.transform.scale(pygame.image.load("images/tiles/blood.png"), (15, 15))
        self.blood_sprite_rect = self.blood_sprite.get_rect()

        # Setting initial infantryman values
        self.health = self.STARTING_HEALTH
        self.starting_x = x
        self.starting_y = y

    def update(self):
        """Update the infantryman"""

        # Determining when the infantryman should fire a projectile (by generating a random cooldown)
        # Limiting the number of projectiles on the screen
        self.COOLDOWN = random.randint(1000, 3000)
        if len(self.team_bullet_group) < 3:
            now = pygame.time.get_ticks()
            if now - self.LAST >= self.COOLDOWN:
                self.LAST = now
                self.fire()

        # Checking if the infantryman's health has been fully drained
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
        # If so, we kill the infantryman from the sprite group
        if self.done_dying:
            self.player.player_eliminations += 1
            self.kill()

        if not self.is_still:
            self.move()

        self.check_platform_collisions()
        self.check_damage_collisions()
        self.check_animations()

    def move(self):
        """Move the infantryman"""

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
            # Checking for collisions between infantryman and platform group (the stone tiles)
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
            if collided_platforms:
                self.position.x -= 3
                self.velocity.x = 0
                self.rect.bottomleft = self.position
                self.melee()

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
        """Check to see if the hurt/death/melee/fire/idle animations should run"""

        # Animating the infantryman hurt animation (when hit by a bullet)
        if self.animate_hurt:
            self.animate(self.hurt_right_sprites, 0.8)

        # Animating the infantryman death animation (when killed/health drained to zero)
        if self.animate_death and self.is_still:
            self.animate(self.die_right_sprites, 0.1)

        # Animating the infantryman melee animation (when close to the fortress, begin to melee)
        if self.animate_melee:
            self.animate(self.melee_right_sprites, 0.1)

        # Animating the infantryman fire animation (shooting the weapon)
        if self.animate_fire:
            self.animate(self.shoot_right_sprites, 0.1)

        # Animating the infantryman aiming animation
        if self.is_still and not self.animate_death:
            self.animate(self.aim_right_sprites, 0.1)

    def fire(self):
        """Fire a projectile from the gun"""

        if self.can_fire:
            self.fire_sound.play()
            InfantrymanBullet(self.rect.centerx, self.rect.centery, self.team_bullet_group, self.barrier_group, self, 2)
            self.animate_fire = True

    def die(self):
        """Infantryman is killed when its health is fully drained"""

        self.can_fire = False
        self.can_melee = False
        self.is_still = True
        self.animate_death = True

        if self.playing_death_sound and self.death_sound.get_num_channels() == 0:
            self.death_sound.play()
            self.playing_death_sound = False

    def melee(self):
        """When the infantryman is close to the fortress, he attacks it to deal damage"""

        self.can_fire = False
        self.can_melee = True
        if self.can_melee:
            self.animate_melee = True
            if self.melee_sound.get_num_channels() == 0:
                self.melee_sound.play()
                self.game.fortress_integrity -= 5

    def animate(self, sprite_list, speed):
        """Animate the infantryman's actions"""

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
            # Ending the melee animation
            if self.animate_melee:
                self.animate_melee = False
            # Ending the death animation
            if self.animate_death:
                self.animate_death = False

        self.image = sprite_list[int(self.current_sprite)]
