from pydantic import BaseModel, Field
import pygame
from typing import Dict, Optional
from components.world.world import World
from components.rendering.camera import Camera
from utils.resource_loader import AssetManager

class WorldManager(BaseModel):
    worlds: Dict[str, World] = Field(default_factory=dict)
    current_world: Optional[World] = Field(default=None)
    camera: Camera = Field(default_factory=Camera)
    debug_header_font: Optional[pygame.font.Font] = Field(default=None)
    debug_detail_font: Optional[pygame.font.Font] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        pygame.font.init()
        self.debug_header_font = pygame.font.Font(AssetManager.get_font("CascadiaCode.ttf"), 18)
        self.debug_detail_font = pygame.font.Font(AssetManager.get_font("CascadiaCodeItalic.ttf"), 14)

    def create_world(self, name: str, map_file: str) -> None:
        new_world = World(map_file=map_file)
        self.worlds[name] = new_world
        if self.current_world is None:
            self.current_world = new_world
            self.camera.map_size = (
                int(new_world.size.x * new_world.tile_size.x),
                int(new_world.size.y * new_world.tile_size.y)
            )

    def update(self, dt: float):
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        # Check if Shift is pressed (either left or right shift)
        speed_multiplier = 4 if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else 1.5
        # Apply the speed multiplier
        dx *= speed_multiplier
        dy *= speed_multiplier
        self.camera.move(dx, dy, dt)

        if self.current_world: self.current_world.update(dt)

    def draw(self, surface: pygame.Surface):
        # Get the size of the surface and update the BufferedRenderer's viewport
        cam_x, cam_y = self.camera.position
        cam_width, cam_height = surface.get_size()

        # Update the size of the BufferedRenderer's viewport (viewport is the visible part)
        self.current_world.tiled_map.group._map_layer.set_size((cam_width, cam_height))

        # Draw visible layers in the PyscrollGroup (with updated viewport)
        self.current_world.tiled_map.group.center((cam_x + cam_width // 2, cam_y + cam_height // 2))  # Centering the camera on the group
        self.current_world.tiled_map.group.draw(surface)

    def draw_debug(self, surface: pygame.Surface, dt: float):
        """Draw detailed debug information below the compact information."""
        if not self.current_world: return  # No world to debug

        world = self.current_world
        debug_info = [
            ("World", [
                f"Name: {world.map_file.split('.')[0]}",
                f"Size: {int(world.size[0])}x{int(world.size[1])} tiles",  # No decimals
                f"Tile Size: {int(world.tile_size[0])}x{int(world.tile_size[1])} px",  # No decimals
                f"Pixels: {int(world.size[0] * world.tile_size[0])}x{int(world.size[1] * world.tile_size[1])} px",  # No decimals
            ]),
            ("Camera", [
                f"Position: ({int(self.camera.position.x)}, {int(self.camera.position.y)})",  # No decimals for position
                f"Zoom: {self.camera.zoom:.2f}",  # Keep decimals for zoom for precision
            ])
        ]

        # Offset to account for compact info
        y_offset = 40
        for section, items in debug_info:
            header_surface = self.debug_header_font.render(section, True, (64, 128, 96))
            surface.blit(header_surface, (10, y_offset))
            y_offset += 24

            # Render details
            for item in items:
                detail_surface = self.debug_detail_font.render(item, True, (255, 255, 255))
                surface.blit(detail_surface, (20, y_offset))
                y_offset += 16

            y_offset += 5  # Add space between sections
