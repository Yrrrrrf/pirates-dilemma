# stdlib
from typing import Dict, Optional
# third party
import pygame
import pytmx
import pyscroll
from pydantic import BaseModel, Field
# local
from app.core.camera import Camera
from app.game.player import Player
from layout.ui.debug import create_debug_ui, DebugUI
from utils import AssetManager

# ========================== TiledMap Class ==========================
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
        map_layer = pyscroll.BufferedRenderer(map_data, (
            tmx_data.width * tmx_data.tilewidth,
            tmx_data.height * tmx_data.tileheight
        ))
        group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=0)
        return cls(tmx_data=tmx_data, map_data=map_data, group=group)

# ========================== World Class ==========================
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
        if self.tiled_map:
            self.tiled_map.group.update(dt)

# ========================== WorldManager Class ==========================

class WorldManager(BaseModel):
    """Manages game worlds, camera, player, and debug UI"""
    worlds: Dict[str, World] = Field(default_factory=dict)
    current_world: Optional[World] = Field(default=None)
    camera: Camera = Field(default_factory=Camera)
    player: Player = Field(default_factory=Player)
    debug_ui: Optional[DebugUI] = Field(default=None)


    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        # self._initialize_debug_ui()

    def create_world(self, name: str, map_file: str) -> None:
        new_world = World(map_file=map_file)
        self.worlds[name] = new_world
        if self.current_world is None:
            self.current_world = new_world
            self.camera.map_size = (
                int(new_world.size.x * new_world.tile_size.x),
                int(new_world.size.y * new_world.tile_size.y)
            )
            self.player.position = pygame.math.Vector2(300, 300)

    def update(self, dt: float):
        keys = pygame.key.get_pressed()
        
        self.player.update(dt, keys)

        camera_dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        camera_dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        speed_multiplier = 4 if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else 1.5
        self.camera.move(camera_dx * speed_multiplier, camera_dy * speed_multiplier, dt)

        if self.current_world: 
            self.current_world.update(dt)
            
        # self._update_debug_info()

    def draw(self, surface: pygame.Surface):
        if not self.current_world or not self.current_world.tiled_map:
            return

        cam_x, cam_y = self.camera.position
        cam_width, cam_height = surface.get_size()

        self.current_world.tiled_map.group._map_layer.set_size((cam_width, cam_height))
        self.current_world.tiled_map.group.center((cam_x + cam_width // 2, cam_y + cam_height // 2))
        self.current_world.tiled_map.group.draw(surface)

        self.player.draw(surface, self.camera)
        
        # Draw debug UI if initialized
        if self.debug_ui: self.debug_ui.draw(surface)

        self.player.reputation.draw(surface, (10, 10))
        self.player.reputation.modify(2)


    # ? Debug UI methods ----------------------------------------------------------------------

    def _initialize_debug_ui(self):
        """Initialize the debug UI with initial empty data structure"""
        initial_debug_data = {
            "world": {
                "Name": "",
                "Size": "",
                "Tile Size": "",
                "Pixels": ""
            },
            "camera": {
                "Position": "",
                "Zoom": ""
            },
            "player": {
                "Position": "",
                "Health": ""
            }
        }
        self.debug_ui = create_debug_ui(initial_debug_data)

    def _update_debug_info(self):
        """Update debug UI with current game state"""
        if not self.debug_ui or not self.current_world:
            return

        world = self.current_world
        debug_data = {
            "world": {
                "Name": world.map_file.split('.')[0],
                "Size": f"{int(world.size[0])}x{int(world.size[1])} tiles",
                "Tile Size": f"{int(world.tile_size[0])}x{int(world.tile_size[1])} px",
                "Pixels": f"{int(world.size[0] * world.tile_size[0])}x{int(world.size[1] * world.tile_size[1])} px"
            },
            "camera": {
                "Position": f"({int(self.camera.position.x)}, {int(self.camera.position.y)})",
                "Zoom": f"{self.camera.zoom:.2f}"
            },
            "player": {
                "Position": f"({int(self.player.position.x)}, {int(self.player.position.y)})",
                "Health": f"{self.player.health}/{self.player.max_health}"
            }
        }
        self.debug_ui.update(debug_data)
