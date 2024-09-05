from pydantic import BaseModel, Field
import pygame
from typing import List, Tuple

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

# * Represents of the game World<map + entities>
# Field(...) means that the field is required, and the value cannot be None
from components.rendering.camera import Camera
import pygame
from pydantic import BaseModel, Field
from typing import Tuple, Optional
import pytmx
import pyscroll
from pyscroll.data import TiledMapData
from utils.resource_loader import get_map_abs

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
            
            # Debug: Draw a small green rectangle to show the map is being rendered
            pygame.draw.rect(surface, (0, 255, 0), pygame.Rect(0, 0, 20, 20))
        else:
            # Debug: Draw a small red rectangle if no map is loaded
            pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(0, 0, 20, 20))

        # Debug: Print detailed map information
        font = pygame.font.Font(None, 24)
        debug_info = [
            f"Map Size: {self.size}",
            f"Tile Size: {self.tile_size}",
            f"Tiled Map: {'Loaded' if self.tiled_map else 'Not Loaded'}",
            f"Camera Position: ({int(camera.position.x)}, {int(camera.position.y)})",
        ]

        # Safely get layer information
        if self.tiled_map:
            try:
                if callable(self.tiled_map.group.layers):
                    layers_info = "Layers method exists"
                else:
                    layers_info = f"Visible Layers: {len(self.tiled_map.group.layers)}"
            except AttributeError:
                layers_info = "Unable to access layers"
        else:
            layers_info = "N/A"

        debug_info.append(f"Layers: {layers_info}")

        for i, info in enumerate(debug_info):
            debug_surface = font.render(info, True, (255, 255, 255))
            surface.blit(debug_surface, (10, 40 + i * 25))
