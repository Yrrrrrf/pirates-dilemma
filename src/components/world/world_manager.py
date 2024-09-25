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
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        self.camera.move(dx, dy, dt)

        if self.current_world:
            self.current_world.update(dt)

    def draw(self, surface: pygame.Surface):
        if not self.current_world or not self.current_world.tiled_map:
            return

        world = self.current_world
        tmx_data = world.tiled_map.tmx_data
        tile_width, tile_height = tmx_data.tilewidth, tmx_data.tileheight

        # Calculate visible area in tile coordinates
        cam_x, cam_y = self.camera.position
        cam_width, cam_height = surface.get_size()
        start_x = max(0, int(cam_x / tile_width))
        start_y = max(0, int(cam_y / tile_height))
        end_x = min(tmx_data.width, int((cam_x + cam_width) / tile_width) + 1)
        end_y = min(tmx_data.height, int((cam_y + cam_height) / tile_height) + 1)

        # Render visible tiles
        for layer in tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for y in range(start_y, end_y):
                    for x in range(start_x, end_x):
                        tile_gid = layer.data[y][x]
                        if tile_gid:
                            tile_image = tmx_data.get_tile_image_by_gid(tile_gid)
                            if tile_image:
                                # Calculate screen position
                                screen_x = int((x * tile_width - cam_x) * self.camera.zoom)
                                screen_y = int((y * tile_height - cam_y) * self.camera.zoom)
                                
                                # Scale the tile image based on zoom
                                scaled_tile = pygame.transform.scale(
                                    tile_image,
                                    (int(tile_width * self.camera.zoom), int(tile_height * self.camera.zoom))
                                )
                                
                                surface.blit(scaled_tile, (screen_x, screen_y))

    def draw_debug_info(self, surface: pygame.Surface, dt: float):
        if not self.current_world:
            return

        world = self.current_world
        debug_info = [
            ("Game", [
                f"FPS: {int(1 / dt)}",
                f"Time: {pygame.time.get_ticks() / 1000:.2f}s"
            ]),
            ("World", [
                f"Name: {world.map_file.split('.')[0]}",
                f"Size: {world.size[0]}x{world.size[1]} tiles",
                f"Tile Size: {world.tile_size[0]}x{world.tile_size[1]}px",
                f"Pixels: {world.size[0] * world.tile_size[0]}x{world.size[1] * world.tile_size[1]}px",
            ]),
            ("Camera", [
                f"Position: ({self.camera.position.x:.2f}, {self.camera.position.y:.2f})",
                f"Zoom: {self.camera.zoom:.2f}"
            ])
        ]

        y_offset = 10
        for section, items in debug_info:
            header_surface = self.debug_header_font.render(section, True, (255, 255, 0))
            surface.blit(header_surface, (10, y_offset))
            y_offset += 25

            for item in items:
                detail_surface = self.debug_detail_font.render(item, True, (200, 200, 200))
                surface.blit(detail_surface, (20, y_offset))
                y_offset += 20
            
            y_offset += 5  # Add space between sections
