from pydantic import BaseModel, Field
import pygame
from typing import Dict, Optional
from components.world.world import World
from components.world import Player
from components.rendering.camera import Camera
from utils.resource_loader import AssetManager

class WorldManager(BaseModel):
    worlds: Dict[str, World] = Field(default_factory=dict)
    current_world: str = Field(default="main")
    debug_header_font: Optional[pygame.font.Font] = Field(default=None)
    debug_detail_font: Optional[pygame.font.Font] = Field(default=None)
    player: Player = Field(default_factory=Player)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        pygame.font.init()
        # self.debug_header_font = pygame.font.Font(AssetManager.get_font("Roboto-Bold.ttf"), 18)
        # self.debug_detail_font = pygame.font.Font(AssetManager.get_font("Roboto-Regular.ttf"), 14)
        self.debug_header_font = pygame.font.Font(AssetManager.get_font("CascadiaCode.ttf"), 18)
        self.debug_detail_font = pygame.font.Font(AssetManager.get_font("CascadiaCodeItalic.ttf"), 14)

    def create_world(self, name: str, map_file: str) -> None:
        self.worlds[name] = World(map_file=map_file)
    
    def move_player(self, dx: float, dy: float):
        current_world = self.get_current_world()
        if current_world:
            scaled_dx = dx * current_world.tile_size[0]
            scaled_dy = dy * current_world.tile_size[1]
            
            new_pos = self.player.position + pygame.math.Vector2(scaled_dx, scaled_dy)
            
            max_x = current_world.size[0] * current_world.tile_size[0]
            max_y = current_world.size[1] * current_world.tile_size[1]
            
            new_pos.x = max(0, min(new_pos.x, max_x - current_world.tile_size[0]))
            new_pos.y = max(0, min(new_pos.y, max_y - current_world.tile_size[1]))
            
            self.player.position = new_pos

    def get_current_world(self) -> World:
        return self.worlds.get(self.current_world)

    def update(self, dt: float):
        if self.current_world in self.worlds:
            self.worlds[self.current_world].update(dt)

    def draw(self, surface: pygame.Surface, camera: Camera):
        if self.current_world in self.worlds:
            self.worlds[self.current_world].draw(surface, camera)
            
            # Draw the player
            player_surface = pygame.Surface((32, 32))
            player_surface.fill((255, 0, 0))  # Red square for the player
            player_rect = player_surface.get_rect(center=camera.world_to_screen(self.player.position))
            surface.blit(player_surface, player_rect)
            
            self.draw_debug_info(surface, self.worlds[self.current_world], camera, 1/60)  # Assuming 60 FPS, adjust as needed

    def draw_debug_info(self, surface: pygame.Surface, world: World, camera: Camera, dt: float):
        debug_info = [
            ("Game", [
                f"FPS: {int(1 / dt)}",
                f"Time: {pygame.time.get_ticks() / 1000:.2f}s"
            ]),
            ("World", [
                f"Name: {self.current_world}",
                f"Size: {world.size[0]}x{world.size[1]} tiles",
                f"Tile Size: {world.tile_size[0]}x{world.tile_size[1]}px",
                f"Pixel Size: {world.size[0] * world.tile_size[0]}x{world.size[1] * world.tile_size[1]}px",
                f"Tiled Map: {'Loaded' if world and world.tiled_map else 'Not Loaded'}"
            ]),
            ("Player", [
                f"Position: ({self.player.position.x:.2f}, {self.player.position.y:.2f})",
                f"Tile: ({int(self.player.position.x / world.tile_size[0])}, {int(self.player.position.y / world.tile_size[1])})"
            ]),
            ("Camera", [
                f"Position: ({camera.position.x:.2f}, {camera.position.y:.2f})",
                f"Zoom: {camera.zoom:.2f}"
            ])
        ]

        y_offset = 10
        for section, items in debug_info:
            # Draw section header
            header_surface = self.debug_header_font.render(section, True, (255, 255, 0))
            surface.blit(header_surface, (10, y_offset))
            y_offset += 25

            # Draw section details
            for item in items:
                detail_surface = self.debug_detail_font.render(item, True, (200, 200, 200))
                surface.blit(detail_surface, (20, y_offset))
                y_offset += 20
            
            y_offset += 5  # Add space between sections
