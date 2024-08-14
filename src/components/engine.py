from dataclasses import dataclass
import pygame

from components.world import World
from components.camera import YSortCamera

@dataclass
class Engine:
    """Engine class. This class contains the logic for the game engine and GUI."""

    def __init__(self):
        """Initialize the engine."""
        self.display_surface: pygame.Surface = pygame.display.get_surface()
        self.world: World = World()
        # * Add a YSortCamera instance to the engine
        self.camera: YSortCamera = YSortCamera(self.world.player, self.display_surface.get_size())

    def event_loop(self):
        """Handle game events."""
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    print("0")

    def run(self, dt: float) -> None:
        # Update
        self.event_loop()
        self.world.update(dt)

        # Draw
        self.display_surface.fill((0, 0, 0))  # Clear the screen

        # Draw the background (water animation)
        self.world.draw_background()

        all_sprites = self.world.get_all_sprites()
        self.camera.draw_sprites(self.display_surface, all_sprites)

        # # Draw any UI elements that should be fixed on the screen
        # self.world.draw_ui(self.display_surface)

        self.draw_debug_info()

    def draw_debug_info(self):
        """Draw debug information on the screen."""
        font = pygame.font.Font(None, 30)


# * personaje.dice("HOLA")
# * -> saludo = {"es": "Hola", "en": "Hello"}
# * -> personaje.dice(saludo[GameInfo.idioma])
