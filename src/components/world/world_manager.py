from pydantic import BaseModel, Field
import pygame
from typing import Dict, Tuple

from components.world.world import World, Water
from components.rendering.camera import Camera
from utils.resource_loader import AssetManager  # Assume this exists to load assets

class WorldManager(BaseModel):
    worlds: Dict[str, World] = Field(default_factory=dict)
    current_world: str = "main"

    class Config:
        arbitrary_types_allowed = True

    def create_world(self, name: str, size: Tuple[int, int], tile_size: int = 32) -> None:
        water_sprite_sheet = pygame.image.load(AssetManager.get_image("static/water-demo.png"))

        water = Water(
            sprite_sheet=water_sprite_sheet,
            tile_size=tile_size,
            animation_speed=0.2  # Adjust this value as needed
        )
        self.worlds[name] = World(size=size, tile_size=tile_size, water=water)

    def set_water_row(self, row: int):
        if self.current_world in self.worlds:
            self.worlds[self.current_world].water.set_row(row)

    def update(self, dt: float):
        if self.current_world in self.worlds:
            self.worlds[self.current_world].update(dt)

    def draw(self, surface: pygame.Surface, camera: Camera):
        if self.current_world in self.worlds:
            self.worlds[self.current_world].draw(surface, camera)
