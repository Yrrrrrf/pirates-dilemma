from dataclasses import dataclass
import pygame

from components.world import World

@dataclass
class Engine:
    """Editor class. This class contains the logic for the GUI"""
    # display_surface: pygame.Surface = pygame.display.get_surface()

    def __init__(self):
        """Initialize the app"""
        self.display_surface: pygame.Surface = pygame.display.get_surface()
        self.world: World = World()

    def event_loop(self):
        for event in pygame.event.get():  # get all events
            match event.type:
                case pygame.K_0: print("0")


    def run(self, dt: float) -> None:
        """
        Initialize the Editor (GUI)

        ### Parameters:
            dt (float): time in seconds since the last tick
        """
        # recolor the display surface
        self.display_surface.fill((0, 0, 0))

        self.event_loop()  # * Handle events
        self.world.update(dt)
        self.world.draw(self.display_surface)
