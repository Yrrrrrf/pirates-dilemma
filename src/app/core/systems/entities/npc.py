import random
from enum import Enum
from typing import List
from pydantic import Field

from app.core.systems.entities import *
from app.core.systems.entities.sprites import *
from tools import AssetManager

class NPCType(Enum):
    # SOME COMMON GUY...
    CIVILIAN = "Civilian"

    MERCHANT = "Merchant"
    HARBOR_MASTER = "Harbor Master"
    TAVERN_KEEPER = "Tavern Keeper"
    WANDERING_MERCHANT = "Wandering Merchant"

def get_random_asset() -> str:
    """Get a random asset path for the NPC sprite"""
    gender = random.choice(["Male", "Female"])
    return f"static\\npc\\{gender}{random.randint(1, 2 if gender == "Female" else 4)}.png"



class NPC(Actor):
    npc_type: NPCType = Field(...)  # Required field
    name: str = Field(default="Some NPC")
    dialogue_keys: List[str] = Field(default_factory=list)  # Default empty list if not provided
    current_dialogue_index: int = Field(default=0)

    sprite_sheet_path: str = Field(default_factory=get_random_asset)
    sprite_type_index: int = Field(default=0)
    scale_factor: float = Field(default=3.0)

    def __init__(self, **data):
        super().__init__(**data)
        self.sprite = AnimatedSprite()
        self._initialize_random_npc()
        
        # Set name based on NPC type if not provided
        if self.name == "Some NPC":
            self.name = f"{self.npc_type.name.title()}-{random.randint(1, 100):02d}"

    def __init__(self, **data):
        super().__init__(**data)
        self.sprite = AnimatedSprite()
        self._initialize_random_npc()

        self.npc_type = data.get("npc_type", NPCType.CIVILIAN)

        # self.name = f"{self.sprite_sheet_path.split('\\')[-1].split('.')[0].title()}-{random.randint(1, 100):02d}"
        self.name = f"{self.npc_type.name.title()}-{random.randint(1, 100):02d}"


    def _initialize_random_npc(self) -> None:
        """Initialize NPC with random appearance from available types"""
        try:
            # Load sprite sheet
            img_path = AssetManager.get_image(self.sprite_sheet_path)
            sprite_sheet = pygame.image.load(img_path).convert_alpha()
            
            # Set up sprite properties
            self.sprite.sprite_sheet = sprite_sheet
            self.sprite.frame_size = (32, 48)  # Updated frame size
            self.sprite.current_state = AnimationState.IDLE
            self.sprite.animation_speed = 0.2
            
            # Set up animations based on direction
            self.sprite.setup_directional_animations()
            
            print(f"NPC initialized successfully with sprite sheet: {img_path}")
            
        except Exception as e:
            print(f"Error initializing NPC: {e}")
            self._create_fallback_sprite()
    
    def _create_fallback_sprite(self) -> None:
        """Create a basic fallback sprite if loading fails"""
        fallback = pygame.Surface((24, 24), pygame.SRCALPHA)
        fallback.fill((255, 0, 0, 180))
        
        self.sprite.sprite_sheet = fallback
        self.sprite.frame_size = (24, 24)
        self.sprite.animations = {
            state: [(0, 0)] for state in AnimationState
        }

    def update(self, dt: float) -> None:
        """Update NPC state and animations"""
        if not self.sprite: return
        self.sprite.update(dt)  # Update animation

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Draw NPC with proper scaling"""
        if not self.sprite or not self.sprite.sprite_sheet:
            return
            
        current_frame = self.sprite.get_current_frame()
        scaled_size = (
            int(current_frame.get_width() * self.scale_factor),
            int(current_frame.get_height() * self.scale_factor)
        )
        scaled_frame = pygame.transform.scale(current_frame, scaled_size)

        screen_pos = camera.world_to_screen(self.position)
        draw_pos = (
            screen_pos[0] - scaled_size[0] // 2,
            screen_pos[1] - scaled_size[1] // 2
        )
        
        surface.blit(scaled_frame, draw_pos)

