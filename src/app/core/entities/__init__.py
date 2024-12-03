import os
import pygame
from pydantic import BaseModel, Field
from typing import Optional

from app.core.camera import Camera
from .sprites import AnimatedSprite

class Entity(BaseModel):
    position: pygame.math.Vector2 = Field(default_factory=lambda: pygame.math.Vector2(0, 0))
    
    class Config:
        arbitrary_types_allowed = True

class Actor(Entity):
    speed: float = Field(default=200.0)
    size: pygame.math.Vector2 = Field(default_factory=lambda: pygame.math.Vector2(48, 48))
    sprite: Optional[AnimatedSprite] = None

    def move(self, dx: float, dy: float, dt: float):
        self.position.x += dx * self.speed * dt
        self.position.y += dy * self.speed * dt

    def draw(self, surface: pygame.Surface, camera: Camera):
        if self.sprite:
            screen_pos = camera.world_to_screen(self.position)
            surface.blit(self.sprite.get_current_frame(), screen_pos)
