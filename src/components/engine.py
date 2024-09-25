from pydantic import BaseModel, Field
import pygame
from typing import Optional

from components.world.world_manager import WorldManager
from components.rendering.camera import Camera

class Engine(BaseModel):
    display_surface: Optional[pygame.Surface] = Field(default=None)
    world_manager: WorldManager = Field(default_factory=WorldManager)
    clock: pygame.time.Clock = Field(default_factory=pygame.time.Clock)
    camera: Camera = Field(default_factory=Camera)

    class Config:
        arbitrary_types_allowed = True

    def initialize_display(self, surface: pygame.Surface):
        self.display_surface = surface
        self.world_manager.create_world("main", 'some-map.tmx')
        current_world = self.world_manager.get_current_world()
        if current_world:
            map_size = current_world.get_map_size()
            self.world_manager.player.position = pygame.math.Vector2(map_size[0] // 2, map_size[1] // 2)
            self.camera.map_size = map_size
            self.camera.screen_size = surface.get_size()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        
        self.world_manager.move_player(dx, dy)
        self.camera.update(self.world_manager.player.position)

    def run(self, dt: float) -> None:
        if self.display_surface is None or self.world_manager is None:
            raise ValueError("Display surface or WorldManager not initialized. Call initialize_display() first.")
    
        self.handle_input()
        self.world_manager.update(dt)

        self.display_surface.fill((0, 0, 0))  # Clear the screen
        self.world_manager.draw(self.display_surface, self.camera)

        pygame.display.flip()
