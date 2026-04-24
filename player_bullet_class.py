"""Contains the PlayerBullet class for the game Audition Absurdity"""
import pygame


class PlayerBullet(pygame.sprite.Sprite):
    """A projectile fired by the player"""

    def __init__(self, x, y, personal_bullet_group, barrier_group, player, player_integer):
        """Initialize the bullet"""

        super().__init__()

        # Attaching sprite groups
        self.personal_bullet_group = personal_bullet_group
        self.barrier_group = barrier_group

        # Setting constant variables
        self.VELOCITY = 20
        self.RANGE = 1280

        # Loading image and getting rect
        # If the player integer is 1, we load the player's purple laser
        if (player.velocity.x < 0 or player.velocity.x == 0) and player_integer == 1:
            self.image = pygame.transform.scale(pygame.image.load("images/player/purple_laser.png"), (32, 32))
            self.VELOCITY = -1 * self.VELOCITY
        elif (player.velocity.x > 0 or player.velocity.x == 0) and player_integer == 1:
            self.image = pygame.transform.scale(pygame.image.load("images/player/purple_laser.png"), (32, 32))

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.starting_x = x
        self.personal_bullet_group.add(self)

    def update(self):
        """Update the bullet"""
        self.rect.x += self.VELOCITY

        # If the bullet has passed the range, kill it
        if abs(self.rect.x - self.starting_x) > self.RANGE:
            self.kill()

        self.check_collisions()

    def check_collisions(self):
        """Check for collisions with barrier groups"""

        # Checking for collisions between infantryman bullet and barrier groups
        pygame.sprite.groupcollide(self.personal_bullet_group, self.barrier_group, True, False)
