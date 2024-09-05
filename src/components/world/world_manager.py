from pydantic import BaseModel, Field
import pygame
from typing import Dict, Tuple

from components.world.world import World
from components.rendering.camera import Camera

class WorldManager(BaseModel):
    worlds: Dict[str, World] = Field(default_factory=dict)
    current_world: str = Field(default="main")

    class Config:
        arbitrary_types_allowed = True

    def create_world(self, name: str, map_file: str = 'some-map.tmx', scree_size: Tuple[int, int] = None):
        match scree_size:
            case None: self.worlds[name] = World(map_file)
            case _: self.worlds[name] = World(map_file)

    def set_water_row(self, row: int):
        if self.current_world in self.worlds:
            self.worlds[self.current_world].water.set_row(row)        

    def update(self, dt: float):
        if self.current_world in self.worlds:
            self.worlds[self.current_world].update(dt)

    def draw(self, surface: pygame.Surface, camera: Camera):
        match self.current_world in self.worlds:
            case True: self.worlds[self.current_world].draw(surface, camera)
            case False:
                # If somehow the current world is not in the worlds dict, draw a red rectangle
                pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(0, 0, 128, 128))
                font = pygame.font.Font(None, 24)
                debug_info = f"Current World '{self.current_world}' not found"
                debug_surface = font.render(debug_info, True, (255, 255, 255))
                surface.blit(debug_surface, (10, 140))
