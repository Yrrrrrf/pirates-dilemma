import pygame
import pytmx
import pyscroll
from pydantic import BaseModel, Field
from pyscroll.data import TiledMapData
from typing import List, Tuple, Optional

from components.rendering.camera import Camera
from utils.resource_loader import AssetManager, get_map_abs


# * Represents of a water tile (used for the background)
class Water(BaseModel):
    sprite_sheet: pygame.Surface = Field(default=None)
    tile_size: int = Field(default=32)
    animation_speed: float = Field(default=0.5)
    animation_time: float = Field(default=0)
    current_frame: int = Field(default=0)
    frames: List[List[pygame.Surface]] = Field(default_factory=list)
    selected_row: int = Field(default=0)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.sprite_sheet = pygame.image.load(AssetManager.get_image("static/water-demo.png"))
        self.frames = self.split_sprite_sheet()

    def split_sprite_sheet(self) -> List[List[pygame.Surface]]:
        frames = []
        sheet_width = self.sprite_sheet.get_width()
        sheet_height = self.sprite_sheet.get_height()
        for y in range(0, sheet_height, self.tile_size):
            row = []
            for x in range(0, sheet_width, self.tile_size):
                frame = self.sprite_sheet.subsurface((x, y, self.tile_size, self.tile_size))
                row.append(frame)
            frames.append(row)
        return frames

    def update(self, dt: float) -> None:
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(self.frames[0])
            self.animation_time = 0

    def get_tile(self) -> pygame.Surface:
        return self.frames[self.selected_row][self.current_frame]

    def draw(self, surface: pygame.Surface, position: Tuple[int, int]) -> None:
        surface.blit(self.get_tile(), position)

    def set_row(self, row: int) -> None:
        if 0 <= row < len(self.frames):
            self.selected_row = row

class TiledMap(BaseModel):
    tmx_data: pytmx.TiledMap
    map_data: pyscroll.data.TiledMapData
    group: pyscroll.PyscrollGroup

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def load_from_file(cls, filename: str, screen_size: Tuple[int, int]):
        tmx_data = pytmx.load_pygame(filename)
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.BufferedRenderer(map_data, screen_size)
        group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=0)
        return cls(tmx_data=tmx_data, map_data=map_data, group=group)

# * Represents of the game World<map + entities>
class World(BaseModel):
    water: Water = Field(default=None)
    tile_size: Tuple[int, int] = Field(default=(32, 32))
    size: Tuple[int, int] = Field(default=(64, 64))
    tiled_map: Optional[TiledMap] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, map_file: Optional[str] = None):
        super().__init__()
        self.water: Water = Water()

        if map_file:
            self.load_map(map_file)

    def load_map(self, map_file: str, screen_size: Tuple[int, int] = (1080, 720)):
        try:
            map_path = get_map_abs(map_file)
            self.tiled_map = TiledMap.load_from_file(map_path, screen_size)
            print(f"Loaded map from file: {map_path}")
            self.size = (self.tiled_map.tmx_data.width, self.tiled_map.tmx_data.height)
            self.tile_size = (self.tiled_map.tmx_data.tilewidth, self.tiled_map.tmx_data.tileheight)
        except Exception as e:
            print(f"Error loading map: {e}")
            self.tiled_map = None

    def update(self, dt: float):
        self.water.update(dt)
        if self.tiled_map:
            self.tiled_map.group.update(dt)

    def draw(self, surface: pygame.Surface, camera: Camera):
        if self.tiled_map:
            # Update the map view
            self.tiled_map.group.center((int(camera.position.x), int(camera.position.y)))

            # Draw the Tiled map
            self.tiled_map.group.draw(surface)
        else:
            # Fall back to drawing water background if no map is loaded
            visible_area = pygame.Rect(camera.position, surface.get_size())
            start_x = max(0, int(camera.position.x // self.tile_size[0]))
            start_y = max(0, int(camera.position.y // self.tile_size[1]))
            end_x = min(self.size[0], start_x + surface.get_width() // self.tile_size[0] + 2)
            end_y = min(self.size[1], start_y + surface.get_height() // self.tile_size[1] + 2)

            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                    tile_rect = pygame.Rect(x * self.tile_size[0], y * self.tile_size[1], self.tile_size[0], self.tile_size[1])
                    if visible_area.colliderect(tile_rect):
                        screen_pos = camera.apply(tile_rect)
                        self.water.draw(surface, screen_pos.topleft)
