from pydantic import BaseModel, Field
import pygame
from typing import Dict, Tuple

from components.world.world import World
from components.rendering.camera import Camera
from utils.resource_loader import AssetManager

class WorldManager(BaseModel):
    worlds: Dict[str, World] = Field(default_factory=dict)
    current_world: str = Field(default="main")
    debug_font: pygame.font.Font = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        pygame.font.init()
        self.debug_font = pygame.font.Font(None, 24)

    def get_current_world(self) -> World:
        return self.worlds.get(self.current_world)

    def create_world(self, name: str, map_file: str) -> None:
        self.worlds[name] = World(map_file)

    def set_water_row(self, row: int):
        if self.current_world in self.worlds:
            self.worlds[self.current_world].water.set_row(row)        

    def update(self, dt: float):
        if self.current_world in self.worlds:
            self.worlds[self.current_world].update(dt)

    def draw(self, surface: pygame.Surface, camera: Camera):
        if self.current_world in self.worlds:
            self.worlds[self.current_world].draw(surface, camera)
            self.draw_debug_info(surface, self.worlds[self.current_world], 1/60)  # Assuming 60 FPS, adjust as needed
        else:
            # If somehow the current world is not in the worlds dict, draw a red rectangle
            pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(0, 0, 128, 128))
            debug_info = f"Current World '{self.current_world}' not found"
            debug_surface = self.debug_font.render(debug_info, True, (255, 255, 255))
            surface.blit(debug_surface, (10, 140))

    def draw_debug_info(self, surface: pygame.Surface, world: World, dt: float):
        debug_info = [
            f"FPS: {int(1 / dt)}",
            # f"Camera: ({int(camera.position.x)}, {int(camera.position.y)})",
            f"Map Size: {world.size if world else 'N/A'}",
            f"Tile Size: {world.tile_size if world else 'N/A'}",
            f"Tiled Map: {'Loaded' if world and world.tiled_map else 'Not Loaded'}",
        ]

        match world and world.tiled_map:
            case True:
                try:
                    if callable(world.tiled_map.group.layers): layers_info = "Layers method exists"
                    else: layers_info = f"Visible Layers: {len(world.tiled_map.group.layers)}"
                except AttributeError: layers_info = "Unable to access layers"
            case False: layers_info = "N/A"

        # debug_info.append(f"Layers: {layers_info}")

        for i, info in enumerate(debug_info):
            debug_surface = self.debug_font.render(info, True, (255, 255, 255))
            surface.blit(debug_surface, (10, 10 + i * 25))

        # Draw indicator rectangles
        match world and world.tiled_map:
            case True: pygame.draw.rect(surface, (0, 255, 0), pygame.Rect(0, 0, 20, 20))
            case False: pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(0, 0, 20, 20))
