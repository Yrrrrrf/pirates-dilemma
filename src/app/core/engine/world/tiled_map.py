# app/core/engine/world/tiled_map.py
from typing import Optional, Tuple
import pygame
import pyscroll
import pytmx
from pytmx.util_pygame import load_pygame
from pydantic import BaseModel, Field

class TiledMap(BaseModel):
    filename: str
    tmx_data: Optional[pytmx.TiledMap] = None
    map_data: Optional[pyscroll.data.TiledMapData] = None
    group: Optional[pyscroll.PyscrollGroup] = None
    sprite_group: Optional[pygame.sprite.Group] = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.sprite_group = pygame.sprite.Group()
        self.load_map()

    def load_map(self) -> None:
        """Load and process the TMX map"""
        try:
            # Load TMX data
            self.tmx_data = load_pygame(self.filename)
            self.map_data = pyscroll.data.TiledMapData(self.tmx_data)

            # Create pyscroll renderer
            map_layer = pyscroll.BufferedRenderer(
                self.map_data,
                (
                    self.tmx_data.width * self.tmx_data.tilewidth,
                    self.tmx_data.height * self.tmx_data.tileheight
                )
            )

            # Create pyscroll group
            self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=0)

            print(f"Map loaded successfully: {self.filename}")
            print(f"Size: {self.tmx_data.width}x{self.tmx_data.height} tiles")
            print(f"Tile size: {self.tmx_data.tilewidth}x{self.tmx_data.tileheight} pixels")
            
        except Exception as e:
            print(f"Error loading map: {str(e)}")
            raise

    def get_layer(self, name: str):
        """Get a specific layer by name"""
        return self.tmx_data.get_layer_by_name(name) if self.tmx_data else None

    def get_object_layer(self, name: str):
        """Get a specific object layer by name"""
        return self.tmx_data.get_layer_by_name(name) if self.tmx_data else None

    def get_tile_properties(self, x: int, y: int, layer) -> dict:
        """Get properties of a specific tile"""
        if not self.tmx_data:
            return {}
        return self.tmx_data.get_tile_properties(x, y, layer) or {}

    @property
    def width(self) -> int:
        """Get map width in tiles"""
        return self.tmx_data.width if self.tmx_data else 0

    @property
    def height(self) -> int:
        """Get map height in tiles"""
        return self.tmx_data.height if self.tmx_data else 0

    @property
    def tilewidth(self) -> int:
        """Get tile width in pixels"""
        return self.tmx_data.tilewidth if self.tmx_data else 0

    @property
    def tileheight(self) -> int:
        """Get tile height in pixels"""
        return self.tmx_data.tileheight if self.tmx_data else 0

    @property
    def pixel_width(self) -> int:
        """Get map width in pixels"""
        return self.width * self.tilewidth

    @property
    def pixel_height(self) -> int:
        """Get map height in pixels"""
        return self.height * self.tileheight
    