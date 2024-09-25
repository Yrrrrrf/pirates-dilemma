from pydantic import BaseModel, Field
import pygame
from typing import Tuple, Union
from pygame.math import Vector2

class Entity(BaseModel):
    position: Vector2 = Field(default_factory=lambda: Vector2(0, 0))
    
    class Config:
        arbitrary_types_allowed = True

class Actor(Entity):
    speed: float = Field(default=50.0)

class Player(Actor):
    position: Vector2 = Field(default_factory=lambda: Vector2(0, 0))
    velocity: Vector2 = Field(default_factory=lambda: Vector2(0, 0))
    temp_vector: Vector2 = Field(default_factory=Vector2)

    class Config:
        arbitrary_types_allowed = True

    def update(self, map_size: Union[Vector2, Tuple[int, int]], tile_size: Union[Vector2, Tuple[int, int]]):
        # Use local variables for frequently accessed attributes
        position = self.position
        velocity = self.velocity
        speed = self.speed
        temp_vector = self.temp_vector

        # Efficiently get pressed keys
        keys = pygame.key.get_pressed()
        temp_vector.x = keys[pygame.K_d] - keys[pygame.K_a]
        temp_vector.y = keys[pygame.K_s] - keys[pygame.K_w]

        # Normalize only if necessary
        if temp_vector.x != 0 or temp_vector.y != 0:
            temp_vector.scale_to_length(1)
        
        velocity.update(temp_vector)

        # Convert tuple to Vector2 if necessary (do this once, outside the update method if possible)
        if isinstance(map_size, tuple):
            map_size = Vector2(map_size)
        if isinstance(tile_size, tuple):
            tile_size = Vector2(tile_size)

        # Update position
        position += velocity * speed

        # Constrain to map boundaries (use in-place operations)
        position.x = max(0, min(position.x, map_size.x * tile_size.x - tile_size.x))
        position.y = max(0, min(position.y, map_size.y * tile_size.y - tile_size.y))

    def set_velocity(self, dx: float, dy: float):
        self.velocity.update(dx, dy)
        length = self.velocity.length()
        if length > 0:
            self.velocity.scale_to_length(1)

class NPC(Actor):
    pass