import pygame
from pydantic import BaseModel, Field
from typing import Tuple, Union

from app.camera import Camera

# ========================== Entity Class ==========================
class Entity(BaseModel):
    position: pygame.math.Vector2 = Field(default_factory=lambda: pygame.math.Vector2(0, 0))
    
    class Config:
        arbitrary_types_allowed = True

# ========================== Actor Class ==========================
class Actor(Entity):
    speed: float = Field(default=200.0)
    size: pygame.math.Vector2 = Field(default_factory=lambda: pygame.math.Vector2(32, 32))

    def move(self, dx: float, dy: float, dt: float):
        self.position.x += dx * self.speed * dt
        self.position.y += dy * self.speed * dt

    def draw(self, surface: pygame.Surface, camera: Camera):
        screen_pos = camera.world_to_screen(self.position)
        pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(screen_pos, self.size))

# ========================== NPC Class ==========================
class NPC(Actor):
    dialogue: str = Field(default="Hello, I'm an NPC!")

# ========================== Player Class ==========================
class Player(Actor):
    health: int = Field(default=100)
    max_health: int = Field(default=100)

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper):
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        self.move(dx, dy, dt)

    def draw(self, surface: pygame.Surface, camera: Camera):
        super().draw(surface, camera)
        # Add player-specific rendering here, like a health bar
        screen_pos = camera.world_to_screen(self.position)
        health_bar_width = self.size.x * (self.health / self.max_health)
        pygame.draw.rect(surface, (0, 255, 0), (screen_pos.x, screen_pos.y - 10, health_bar_width, 5))
