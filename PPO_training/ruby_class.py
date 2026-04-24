"""Contains the Ruby class for the game Audition Absurdity"""
import pygame
import random

# Creating a 2D vector to use in the future
vector = pygame.math.Vector2


class Ruby(pygame.sprite.Sprite):
    """A class to control rubies the player must collect to earn points and health"""
    def __init__(self, window_width, window_height, platform_group):
        """Initialize the ruby"""
        super().__init__()

        # Attaching sprite groups
        self.window_width = window_width
        self.window_height = window_height
        self.platform_group = platform_group

        # Setting constant variables
        self.HORIZONTAL_VELOCITY = 1
        self.VERTICAL_VELOCITY = 1

        # Animation frames
        self.ruby_sprites = []

        # Rotating
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile000.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile001.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile002.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile003.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile004.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile005.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile006.png"), (64, 64)))

        # Loading image and getting the rect
        self.current_sprite = 0
        self.image = self.ruby_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.center = (self.window_width // 2 + 500, self.window_height // 2 + 100)

        # Random velocities
        self.random_horizontal = random.choice([-1 * self.HORIZONTAL_VELOCITY, self.HORIZONTAL_VELOCITY])
        self.random_vertical = random.choice([-1 * self.VERTICAL_VELOCITY, self.VERTICAL_VELOCITY])

        # Kinematic vectors
        self.position = vector(self.rect.x, self.rect.y)
        self.velocity = vector(self.random_horizontal, self.random_vertical)
        self.acceleration = vector(0, 0)

    def update(self):
        """Update the ruby"""
        self.animate(self.ruby_sprites, 0.25)
        self.move()
        self.check_collisions()

    def move(self):
        """Move the ruby"""

        # Don't need to update the acceleration vector because it NEVER changes
        # Calculating kinematics values
        self.velocity += self.acceleration
        self.position += self.velocity + (0.5 * self.acceleration)

        # Updating rect based on kinematic calculations and adding wrap-around movement
        if self.position.x < 0:
            self.position.x = self.window_width
        elif self.position.x > self.window_width:
            self.position.x = 0

        self.rect.bottomleft = self.position

    def check_collisions(self):
        """Check for collisions with platforms"""

        # Checking for collisions while moving horizontally to the left (x-direction)
        if self.velocity.x < 0:
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
            if collided_platforms:
                self.position.x += 3
                self.velocity.x = -1 * self.velocity.x
                self.rect.bottomleft = self.position

        # Checking for collisions while moving horizontally to the right (x-direction)
        if self.velocity.x > 0:
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
            if collided_platforms:
                self.position.x -= 3
                self.velocity.x = -1 * self.velocity.x
                self.rect.bottomleft = self.position

        # Checking for collisions while moving vertically up (y-direction)
        if self.velocity.y < 0:
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
            if collided_platforms:
                self.position.y += 3
                self.velocity.y = -1 * self.velocity.y
                self.rect.bottomleft = self.position

        # Checking for collisions while moving vertically down (y-direction)
        if self.velocity.y > 0:
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
            if collided_platforms:
                self.position.y -= 3
                self.velocity.y = -1 * self.velocity.y
                self.rect.bottomleft = self.position

    def animate(self, sprite_list, speed):
        """Animate the ruby"""
        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

        self.image = sprite_list[int(self.current_sprite)]
