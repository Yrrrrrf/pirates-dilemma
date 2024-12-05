# app/core/engine/world.py
from typing import Dict, List, Optional, Tuple
import pygame
from pydantic import BaseModel, Field

from app.core.engine.camera import Camera
from app.core.engine.world.tiled_map import TiledMap
from app.core.systems.entities.npc_manager import NPCManager
from app.game.base.player import Player
from tools import AssetManager

class World(BaseModel):
    map_file: str
    tiled_map: Optional[TiledMap] = None
    size: pygame.math.Vector2 = Field(default_factory=lambda: pygame.math.Vector2(0, 0))
    tile_size: pygame.math.Vector2 = Field(default_factory=lambda: pygame.math.Vector2(16, 16))

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.load_map()

    def load_map(self) -> None:
        """Load the TMX map file"""
        try:
            map_path = AssetManager.get_map_abs(self.map_file)
            self.tiled_map = TiledMap(filename=map_path)
            
            # Update world size based on map
            self.size.x = self.tiled_map.width
            self.size.y = self.tiled_map.height
            
            # Update tile size
            self.tile_size.x = self.tiled_map.tilewidth
            self.tile_size.y = self.tiled_map.tileheight
            
            print(f"Map loaded: {self.map_file}")
            print(f"Size: {self.size.x}x{self.size.y} tiles")
            print(f"Pixel size: {self.tiled_map.pixel_width}x{self.tiled_map.pixel_height}")
            
        except Exception as e:
            print(f"Error loading map: {e}")
            self.tiled_map = None

    def update(self, dt: float) -> None:
        """Update world state"""
        if not self.tiled_map:
            return
        
        if self.tiled_map.group:
            self.tiled_map.group.update(dt)

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Draw the world with camera position"""
        if not self.tiled_map or not self.tiled_map.group:
            return

        # Get camera position and screen size
        cam_x, cam_y = camera.position
        cam_width, cam_height = surface.get_size()

        # Update map layer size and center position
        self.tiled_map.group._map_layer.set_size((cam_width, cam_height))
        self.tiled_map.group.center((cam_x + cam_width // 2, cam_y + cam_height // 2))
        
        # Draw the map
        self.tiled_map.group.draw(surface)

    def get_spawn_point(self) -> Tuple[float, float]:
        """Get player spawn point from map"""
        if not self.tiled_map:
            return 300.0, 300.0  # Default spawn point
            
        # Try to find spawn point in map objects
        object_layer = self.tiled_map.get_object_layer('Objects')
        if object_layer:
            for obj in object_layer:
                if obj.type == 'Spawn':
                    return float(obj.x), float(obj.y)
                    
        return 300.0, 300.0  # Default if no spawn point found

    def get_collision_rects(self) -> List[pygame.Rect]:
        """Get collision rectangles from map"""
        collision_rects = []
        
        if not self.tiled_map:
            return collision_rects
            
        # Get collision objects from map
        object_layer = self.tiled_map.get_object_layer('Collision')
        if object_layer:
            for obj in object_layer:
                if hasattr(obj, 'width') and hasattr(obj, 'height'):
                    rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                    collision_rects.append(rect)
                    
        return collision_rects

# ========================== WorldManager Class ==========================

class WorldManager(BaseModel):
    """Manages game worlds, camera, player, and debug UI"""
    worlds: Dict[str, World] = Field(default_factory=dict)
    current_world: Optional[World] = Field(default=None)
    camera: Camera = Field(default_factory=Camera)
    player: Player = Field(default_factory=Player)
    # debug_ui: Optional[DebugUI] = Field(default=None)
    npc_manager: Optional[NPCManager] = Field(default=None)
    # interaction_menu: InteractionMenu = Field(default_factory=InteractionMenu)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)

        # * Initialize debug UI
        self.npc_manager = NPCManager()

    def create_world(self, name: str, map_file: str) -> None:
        new_world = World(map_file=map_file)
        self.worlds[name] = new_world
        if self.current_world is None:
            self.current_world = new_world
            self.camera.map_size = (
                new_world.tiled_map.pixel_width,
                new_world.tiled_map.pixel_height
            )
            self.player.position = pygame.math.Vector2(300, 300)

    def update(self, dt: float):
        if not self.current_world: return

        # Handle keyboard input
        keys = pygame.key.get_pressed()
        # self.player.update(dt, keys, self.current_world.get_collision_rects())
        self.player.update(dt, keys)

        camera_dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        camera_dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        speed_multiplier = 4 if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else 1.5
        self.camera.move(camera_dx * speed_multiplier, camera_dy * speed_multiplier, dt)

        # ^ Update world
        self.current_world.update(dt)

        # Update NPC manager
        if self.npc_manager:
            self.npc_manager.update(dt, self.player.position)

    def draw(self, surface: pygame.Surface):
        if not self.current_world or not self.current_world.tiled_map:
            return

        cam_x, cam_y = self.camera.position
        cam_width, cam_height = surface.get_size()

        self.current_world.tiled_map.group._map_layer.set_size((cam_width, cam_height))
        self.current_world.tiled_map.group.center((cam_x + cam_width // 2, cam_y + cam_height // 2))
        self.current_world.tiled_map.group.draw(surface)

        # Draw NPCs and interaction hints
        if self.npc_manager: self.npc_manager.draw(surface, self.camera)

        if self.player:
            self.player.draw(surface, self.camera)
            self.player.reputation.draw(surface, (10, 10))

            # Draw inventory
            self.player.inventory.draw(surface)

    # # ? Debug UI methods ----------------------------------------------------------------------

    # def _initialize_debug_ui(self):
    #     """Initialize the debug UI with initial empty data structure"""
    #     initial_debug_data = {
    #         "world": {
    #             "Name": "",
    #             "Size": "",
    #             "Tile Size": "",
    #             "Pixels": ""
    #         },
    #         "camera": {
    #             "Position": "",
    #             "Zoom": ""
    #         },
    #         "player": {
    #             "Position": "",
    #             "Health": ""
    #         }
    #     }
    #     # self.debug_ui = create_debug_ui(initial_debug_data)

    # def _update_debug_info(self):
    #     """Update debug UI with current game state"""
    #     if not self.current_world: return
    #     # if not self.debug_ui or not self.current_world: return

    #     world = self.current_world
    #     debug_data = {
    #         "world": {
    #             "Name": world.map_file.split('.')[0],
    #             "Size": f"{int(world.size[0])}x{int(world.size[1])} tiles",
    #             "Tile Size": f"{int(world.tile_size[0])}x{int(world.tile_size[1])} px",
    #             "Pixels": f"{int(world.size[0] * world.tile_size[0])}x{int(world.size[1] * world.tile_size[1])} px"
    #         },
    #         "camera": {
    #             "Position": f"({int(self.camera.position.x)}, {int(self.camera.position.y)})",
    #             "Zoom": f"{self.camera.zoom:.2f}"
    #         },
    #         "player": {
    #             "Position": f"({int(self.player.position.x)}, {int(self.player.position.y)})",
    #             "Reputation:": f"{self.player.reputation.get_status()} ({self.player.reputation.value:.2f})"
    #         }
    #     }
    #     # self.debug_ui.update(debug_data)
