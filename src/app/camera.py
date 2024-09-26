import pygame
from pydantic import BaseModel, Field
from typing import Tuple

class Camera(BaseModel):
    position: pygame.math.Vector2 = Field(default_factory=lambda: pygame.math.Vector2(0, 0))
    map_size: Tuple[int, int] = Field(default=(0, 0))
    zoom: float = Field(default=1.0, gt=0.5, lt=2.0)
    move_speed: float = Field(default=200.0)  # pixels per second

    class Config:
        arbitrary_types_allowed = True

    def move(self, dx: float, dy: float, dt: float):
        # movement = pygame.math.Vector2(dx, dy) * self.move_speed
        movement = pygame.math.Vector2(dx, dy) * self.move_speed * dt
        new_position = self.position + movement
        
        screen_size = pygame.math.Vector2(pygame.display.get_surface().get_size())
        max_x = self.map_size[0] - screen_size.x / self.zoom
        max_y = self.map_size[1] - screen_size.y / self.zoom
        
        self.position.x = max(0, min(new_position.x, max_x))
        self.position.y = max(0, min(new_position.y, max_y))

    def get_visible_area(self) -> pygame.Rect:
        screen_size = pygame.math.Vector2(pygame.display.get_surface().get_size())
        visible_size = screen_size / self.zoom
        return pygame.Rect(self.position, visible_size)

    def world_to_screen(self, world_pos: pygame.math.Vector2) -> pygame.math.Vector2:
        return (world_pos - self.position) * self.zoom

    def screen_to_world(self, screen_pos: pygame.math.Vector2) -> pygame.math.Vector2:
        return (screen_pos / self.zoom) + self.position
