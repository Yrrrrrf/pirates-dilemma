from pydantic import BaseModel, Field
import pygame
from typing import Callable, Optional

from components.game_state import GameState
from components.world.world_manager import WorldManager
from components.rendering.camera import Camera
from utils.resource_loader import AssetManager

class Engine(BaseModel):
    game_state: GameState = Field(default_factory=GameState)
    display_surface: Optional[pygame.Surface] = Field(default=None)
    world_manager: WorldManager = Field(default_factory=WorldManager)
    clock: pygame.time.Clock = Field(default_factory=pygame.time.Clock)
    camera: Camera = Field(default_factory=Camera)

    class Config:
        arbitrary_types_allowed = True

    def initialize_display(self, surface: pygame.Surface):
        self.display_surface = surface

        world_size = (10, 20)  # blocks
        tile_size = self.game_state.settings.tile_size  # pixels
        self.world_manager.create_world("main", world_size, tile_size)
        self.world_manager.set_water_row(1)

    def event_loop(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.KEYDOWN:
                    match event.key:
                        case _: pass  # do anything ...


    # todo: Move this fn to the camera class
    def handle_input(self):
        keys = pygame.key.get_pressed()  # Get the state of all keys
        # d: Callable = lambda k1, k2: keys[k1] - keys[k2]
        # self.camera.move(d(pygame.K_d, pygame.K_a), d(pygame.K_s, pygame.K_w))
        # * Same as above w/ a more readable format (commented out for reference)
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        self.camera.move(dx, dy)

    def run(self, dt: float) -> None:
        if self.display_surface is None or self.world_manager is None:
            raise ValueError("Display surface or WorldManager not initialized. Call initialize_display() first.")
        
        self.handle_input()
        self.world_manager.update(dt)

        self.display_surface.fill((0, 0, 0))  # Clear the screen
        self.world_manager.draw(self.display_surface, self.camera)
        
        pygame.display.flip()

        # pygame.quit()

    def draw_debug_info(self) -> None:
        if self.display_surface is None:
            return
        font = pygame.font.Font(None, 30)
        # Add debug info drawing logic here