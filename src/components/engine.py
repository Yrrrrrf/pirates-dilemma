import sys
import pygame
from dataclasses import dataclass
import random


class Tree(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.image: pygame.Surface = pygame.image.load(f"assets/images/static/tree-{random.randint(1, 5):02d}.png").convert_alpha()
        self.image: pygame.Surface = pygame.transform.scale(self.image, (128, 128))
        self.rect: pygame.Rect = self.image.get_rect(topleft=(x, y))


@dataclass
class Engine:
    """Editor class. This class contains the logic for the GUI"""
    # display_surface: pygame.Surface = pygame.display.get_surface()

    def __init__(self):
        """Initialize the app"""
        self.display_surface: pygame.Surface = pygame.display.get_surface()


        w, h = self.display_surface.get_size()
        trees = pygame.sprite.Group([Tree(random.randint(0, w), random.randint(0, h)) for _ in range(20)])

        # add the trees to the display surface
        trees.draw(self.display_surface)

        





    def event_loop(self):
        for event in pygame.event.get():  # get all events
            if event.type == pygame.QUIT:  # if the user closes the window
                pygame.quit()  # quit pygame
                sys.exit()  # exit the program

    def run(self, dt: float) -> None:
        """
        Initialize the Editor (GUI)

        ### Parameters:
            dt (float): time in seconds since the last tick
        """
        # print("Running the G-Engine")
        self.event_loop()  # handle events

        # self.display_surface.fill('blue')
