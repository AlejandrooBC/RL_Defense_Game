"""Contains the Tile class for the game Audition Absurdity"""
import pygame

class Tile(pygame.sprite.Sprite):
    """A class to represent a 32x32 pixel area in our display"""

    def __init__(self, x, y, image_integer, main_group, sub_group_one=None, sub_group_two=None):
        """Initialize the Tile class"""

        super().__init__()
        # Loading in the correct image and adding it to the correct subgroup
        # Stone tile
        if image_integer == 1:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/stone.png"), (32, 32))
            sub_group_one.add(self)
        # Chest tile
        elif image_integer == 2:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/chest.png"), (32, 32))
        # Barrel tile
        elif image_integer == 3:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/barrel.png"), (32, 32))
        # Torch tile
        elif image_integer == 4:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/torch.png"), (32, 32))
        # Wood tile
        elif image_integer == 5:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/wood.png"), (32, 32))
        # Concrete tile
        elif image_integer == 6:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/concrete.png"), (32, 32))
        # Barrier tile --> serves as protection
        elif image_integer == 7:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/barrier.png"), (32, 32))
            sub_group_one.add(self)
            sub_group_two.add(self)
        # Carpet tile
        elif image_integer == 8:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/carpet.png"), (32, 32))
        # Chandelier tile
        elif image_integer == 9:
            self.image = pygame.transform.scale(pygame.image.load("images/tiles/chandelier.png"), (32, 32))

        # Adding every tile to the main group
        main_group.add(self)

        # Getting the rect of the image and positioning it within the grid
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)