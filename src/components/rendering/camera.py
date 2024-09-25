import pygame
from pydantic import BaseModel, Field
from typing import Tuple


class Camera(BaseModel):
    position: pygame.math.Vector2 = Field(default_factory=lambda: pygame.math.Vector2(0, 0))
    screen_size: Tuple[int, int] = Field(default=(1080, 720))
    map_size: Tuple[int, int] = Field(default=(0, 0))
    zoom: float = 1.0

    class Config:
        arbitrary_types_allowed = True

    def update(self, target_position: pygame.math.Vector2):
        # Center the camera on the target position
        self.position = target_position - pygame.math.Vector2(self.screen_size) / 2
        
        # Clamp the camera position to ensure it doesn't show outside the map
        self.position.x = max(0, min(self.position.x, self.map_size[0] - self.screen_size[0]))
        self.position.y = max(0, min(self.position.y, self.map_size[1] - self.screen_size[1]))

    def world_to_screen(self, world_pos: pygame.math.Vector2) -> pygame.math.Vector2:
        return world_pos - self.position

    def screen_to_world(self, screen_pos: pygame.math.Vector2) -> pygame.math.Vector2:
        return screen_pos + self.position

    def get_visible_area(self) -> pygame.Rect:
        return pygame.Rect(self.position, self.screen_size)
