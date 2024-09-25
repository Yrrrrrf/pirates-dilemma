from pydantic import BaseModel, Field
import pygame
from typing import Optional

from components.world.world_manager import WorldManager
from components.rendering.camera import Camera

from pydantic import BaseModel, Field
import pygame
from typing import Optional

from components.world.world_manager import WorldManager
from components.rendering.camera import Camera

class Engine(BaseModel):
    display_surface: Optional[pygame.Surface] = Field(default=None)
    world_manager: WorldManager = Field(default_factory=WorldManager)
    clock: pygame.time.Clock = Field(default_factory=pygame.time.Clock)

    class Config:
        arbitrary_types_allowed = True

    def initialize_display(self, surface: pygame.Surface):
        self.display_surface = surface
        self.world_manager.create_world("main", 'big-map.tmx')

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            self.world_manager.camera.handle_event(event)
        return True

    def run(self, dt: float):
        if self.display_surface is None or self.world_manager.current_world is None:
            raise ValueError("Display surface or World not initialized. Call initialize_display() first.")
    
        if not self.handle_events():
            return False

        self.world_manager.update(dt)

        self.display_surface.fill((0, 0, 0))  # Clear the screen
        self.world_manager.draw(self.display_surface)
        self.world_manager.draw_debug_info(self.display_surface, dt)

        pygame.display.flip()
        return True
