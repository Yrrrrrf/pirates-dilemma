import pygame
import pytmx
import pyscroll
from pydantic import BaseModel, Field
from typing import Optional

from utils.resource_loader import AssetManager


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

        # Create a BufferedRenderer with the map's full size
        map_layer = pyscroll.BufferedRenderer(map_data, (
            tmx_data.width * tmx_data.tilewidth,
            tmx_data.height * tmx_data.tileheight
        ))
        # todo: Impl on the Engine or Camera Some(Zoom-In/Out)
        # map_layer.zoom = 1  # default zoom

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
        except Exception as e:
            print(f"Error loading map: {e}")
            self.tiled_map = None

    def update(self, dt: float):
        if self.tiled_map: self.tiled_map.group.update(dt)
