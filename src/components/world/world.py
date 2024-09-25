import pygame
import pytmx
import pyscroll
from pydantic import BaseModel, Field
from typing import List, Tuple, Optional

from utils.resource_loader import AssetManager


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
    def load_from_file(cls, filename: str):
        tmx_data = pytmx.load_pygame(filename)
        map_data = pyscroll.data.TiledMapData(tmx_data)
        
        # Calculate the map size in pixels
        map_width = tmx_data.width * tmx_data.tilewidth
        map_height = tmx_data.height * tmx_data.tileheight
        
        # Create a BufferedRenderer with the map's full size
        map_layer = pyscroll.BufferedRenderer(map_data, (map_width, map_height))
        
        group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=0)
        return cls(tmx_data=tmx_data, map_data=map_data, group=group)


# * Represents of the game World<map + entities>
class World(BaseModel):
    map_file: str
    tiled_map: Optional[TiledMap] = Field(default=None)
    size: pygame.math.Vector2 = Field(default_factory=lambda: pygame.math.Vector2(0, 0))
    tile_size: pygame.math.Vector2 = Field(default_factory=lambda: pygame.math.Vector2(32, 32))

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.load_map()

    def load_map(self):
        try:
            self.tiled_map = TiledMap.load_from_file(AssetManager.get_map_abs(self.map_file))
            print(f"Loading map: {self.map_file}")
            self.size = pygame.math.Vector2(self.tiled_map.tmx_data.width, self.tiled_map.tmx_data.height)
            self.tile_size = pygame.math.Vector2(self.tiled_map.tmx_data.tilewidth, self.tiled_map.tmx_data.tileheight)
            print(f"Map size: {self.size}, Tile size: {self.tile_size}")
        except Exception as e:
            print(f"Error loading map: {e}")
            self.tiled_map = None

    def update(self, dt: float):
        if self.tiled_map: self.tiled_map.group.update(dt)
