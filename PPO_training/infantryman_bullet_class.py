"""Contains the InfantrymanBullet class for the game Audition Absurdity"""
import pygame


class InfantrymanBullet(pygame.sprite.Sprite):
    """A projectile fired by the infantryman"""

    def __init__(self, x, y, team_bullet_group, barrier_group, player, player_integer):
        """Initialize the bullet"""

        super().__init__()

        # Attaching sprite groups
        self.barrier_group = barrier_group
        self.team_bullet_group = team_bullet_group

        # Setting constant variables
        self.VELOCITY = 8
        self.RANGE = 1280

        # Loading image and getting rect
        # If the player integer is 2, we load the infantryman's red laser
        if (player.velocity.x > 0 or player.velocity.x == 0) and player_integer == 2:
            self.image = pygame.transform.scale(pygame.image.load("images/infantryman/red_laser.png"), (32, 32))

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.starting_x = x
        self.team_bullet_group.add(self)

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
        pygame.sprite.groupcollide(self.team_bullet_group, self.barrier_group, True, False)
