from pydantic import BaseModel, Field
import pygame
from typing import Tuple


class Entity(BaseModel):
    position: pygame.math.Vector2 = Field(default_factory=lambda: pygame.math.Vector2(0, 0))
    
    class Config:
        arbitrary_types_allowed = True

class Actor(Entity):
    speed: float = 5.0

class Player(Actor):
    def move(self, dx: float, dy: float, map_size: Tuple[int, int]):
        new_x = max(0, min(self.position.x + dx * self.speed, map_size[0] - 1))
        new_y = max(0, min(self.position.y + dy * self.speed, map_size[1] - 1))
        self.position = pygame.math.Vector2(new_x, new_y)

class NPC(Actor):
    pass
