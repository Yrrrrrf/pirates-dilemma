# stdlib
from typing import Optional
# third party
import pygame
from pydantic import BaseModel, Field
# local
from app.core.world import WorldManager


class Engine(BaseModel):
    display_surface: Optional[pygame.Surface] = Field(default=None)
    world_manager: WorldManager = Field(default_factory=WorldManager)
    clock: pygame.time.Clock = Field(default_factory=pygame.time.Clock)
    # ui: Optional[GameUI] = Field(default=None)  # Add GameUI field

    class Config:
        arbitrary_types_allowed = True

    def initialize_display(self, surface: pygame.Surface):
        # Initialize the display surface and the world manager
        self.display_surface = surface
        # todo: Change the map file to 'big-map.tmx' to test the big map
        self.world_manager.create_world("main", 'big-map.tmx')
        # self.world_manager.create_world("main", 'mapp.tmx')

    def run(self, dt: float):
        if self.display_surface is None or self.world_manager.current_world is None:
            raise ValueError("Display surface or World not initialized. Call initialize_display() first.")
    
        self.display_surface.fill((0, 0, 0))  # Clear the screen
        self.world_manager.update(dt)  # Update the world
        self.world_manager.draw(self.display_surface)

        pygame.display.flip()
        return True
