import random
from enum import Enum
import pygame
from pydantic import Field

from app.core.camera import Camera
from app.core.entities import *
from app.core.entities.sprites import AnimatedSprite, AnimationState
from utils import AssetManager

class NPCType(Enum):
    MALE = "male"
    FEMALE = "female"
    ELDER = "elder"

class NPC(Actor):
    npc_type: NPCType = Field(default=NPCType.MALE)
    dialogue: str = Field(default="Hello, I'm an NPC!")
    # todo: Fix the asset loader...
    sprite_sheet_path: str = Field(default="static\\npc\\Femalse1.png")
    sprite_type_index: int = Field(default=0)  # 0-3 for each type
    scale_factor: float = Field(default=3.0)

    def __init__(self, **data):
        super().__init__(**data)
        self.sprite = AnimatedSprite()
        self._initialize_random_npc()

    def _initialize_random_npc(self) -> None:
        """Initialize NPC with random appearance from available types"""
        try:
            # Select random NPC type and corresponding sprite row
            self.npc_type = random.choice(list(NPCType))
            type_index = list(NPCType).index(self.npc_type)
            
            # Each NPC type has 3 variants, each taking 3 rows
            variant = random.randint(0, 2)  # Choose random variant
            base_row = type_index * 9 + variant * 3  # Calculate starting row
            
            # Load sprite sheet
            img_path = AssetManager.get_image(self.sprite_sheet_path)
            sprite_sheet = pygame.image.load(img_path).convert_alpha()
            
            # Frame size is consistent for all characters
            frame_width = frame_height = 24  # Standard frame size
            
            self.sprite.sprite_sheet = sprite_sheet
            self.sprite.frame_size = (frame_width, frame_height)
            self.sprite.current_state = AnimationState.IDLE
            self.sprite.animation_speed = 0.2
            
            # Set up animations using the correct rows
            self.sprite.animations = {
                AnimationState.IDLE: [(i, base_row) for i in range(4)],
                AnimationState.MOVE: [(i, base_row + 1) for i in range(4)],
            }
            
            print(f"Initialized {self.npc_type.value} NPC (variant {variant})")
            
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
        
    def interact(self) -> str:
        """Handle interaction with the NPC"""
        self.sprite.current_state = AnimationState.IDLE
        return self.dialogue

def create_random_npc(position: pygame.math.Vector2) -> NPC:
    """Factory function to create a random NPC at the specified position"""
    dialogues = {
        NPCType.MALE: [
            "Ahoy, matey! Fine weather for sailing, eh?",
            "Watch yer step around these parts, stranger.",
            "Care to hear a tale of the high seas?"
        ],
        NPCType.FEMALE: [
            "Welcome to our humble port, traveler.",
            "The market's just around the corner.",
            "Mind your manners in this establishment."
        ],
        NPCType.ELDER: [
            "I've seen many a ship come and go in my time...",
            "The old legends speak of a great treasure...",
            "In all my years, I've never seen such strange times."
        ]
    }

    npc = NPC(position=position)
    npc.dialogue = random.choice(dialogues[npc.npc_type])
    return npc