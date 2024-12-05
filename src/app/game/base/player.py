import os
from typing import Dict, Optional
import pygame
from pydantic import Field

from app.engine.camera import Camera
from app.core.entities import Actor
from app.core.entities.sprites import AnimatedSprite, AnimationState, Direction
from app.game.reputation import Reputation
from app.game.inventory import Inventory
from app.game.abilities import Ability
from tools import AssetManager

class Player(Actor):
    sprite_sheet_path: str = Field("static\\player.png")
    sprite: Optional[AnimatedSprite] = Field(default=None)
    scale_factor: float = Field(default=3.0)
    
    reputation: Reputation = Field(default_factory=Reputation)
    inventory: Inventory = Field(default_factory=Inventory)
    abilities: Dict[str, Ability] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.sprite is None:
            self.sprite = AnimatedSprite()
        self.load_sprite_sheet()
    #     self._initialize_abilities()

    # def _initialize_abilities(self) -> None:
    #     """Initialize basic abilities"""
    #     self.abilities["attack"] = Ability(
    #         name="attack",
    #         cooldown=1.0,
    #         animation_state=AnimationState.ATTACK
    #     )

    def load_sprite_sheet(self):
        try:
            img_path = AssetManager.get_image(self.sprite_sheet_path)
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"Image file not found: {img_path}")

            print(f"Image file exists: {img_path}")
            sprite_sheet = pygame.image.load(img_path).convert_alpha()  # Use convert_alpha() instead of convert()

            if not isinstance(sprite_sheet, pygame.Surface):
                raise TypeError(f"Loaded object is not a pygame.Surface. Got {type(sprite_sheet)}")

            # Get and print surface information
            print(f"\tImage size: {sprite_sheet.get_size()}")
            print(f"\tImage color key: {sprite_sheet.get_colorkey()}")
            print(f"\tImage alpha: {sprite_sheet.get_alpha()}")
            print(f"\tImage bit size: {sprite_sheet.get_bitsize()}")

            # Determine frame size and animation layout
            sheet_width, sheet_height = sprite_sheet.get_size()
            frame_width = 48  # Assuming each frame is 48x48
            frame_height = 48
            cols = sheet_width // frame_width
            rows = sheet_height // frame_height

            self.sprite.sprite_sheet = sprite_sheet
            self.sprite.frame_size = (frame_width, frame_height)
            print(f"Frame size: {self.sprite.frame_size}")
            
            # Set up animations based on available frames
            self.sprite.animations = {
                AnimationState.IDLE: [(i, 0) for i in range(min(3, cols))],
                AnimationState.MOVE: [(i, 1) for i in range(min(3, cols))],
                AnimationState.ATTACK: [(i, 2) for i in range(min(3, cols))],
                AnimationState.DEATH: [(0, 3)]
            }
            print("Animations set up successfully")
            
        except (pygame.error, FileNotFoundError, TypeError) as e:
            print(f"Error loading player sprite sheet: {e}")
            self.create_fallback_sprite()
        except Exception as e:
            print(f"Unexpected error loading player sprite sheet: {e}")
            self.create_fallback_sprite()

    def create_fallback_sprite(self):
        """Create a basic fallback sprite if loading fails"""
        self.sprite.sprite_sheet = pygame.Surface((48, 48), pygame.SRCALPHA)  # Add SRCALPHA flag
        self.sprite.sprite_sheet.fill((255, 0, 0, 128))  # Add alpha value
        self.sprite.frame_size = (48, 48)
        self.sprite.animations = {
            state: [(0, 0)] for state in AnimationState
        }

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        # Movement
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        
        if dx != 0 or dy != 0:
            self.sprite.current_state = AnimationState.MOVE
            self.sprite.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
        else:
            self.sprite.current_state = AnimationState.IDLE

        # Abilities
        if keys[pygame.K_SPACE]: self.use_ability("attack")

        self.move(dx, dy, dt)
        self.sprite.update(dt)
        
        # Update ability cooldowns
        for ability in self.abilities.values():
            ability.update(dt)

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        if not self.sprite or not self.sprite.sprite_sheet:
            return
            
        current_frame = self.sprite.get_current_frame()
        scaled_size = (
            int(current_frame.get_width() * self.scale_factor),
            int(current_frame.get_height() * self.scale_factor)
        )
        scaled_frame = pygame.transform.scale(current_frame, scaled_size)
        
        screen_pos = camera.world_to_screen(self.position)
        draw_pos = (screen_pos[0] - scaled_size[0] // 2, screen_pos[1] - scaled_size[1] // 2)
        surface.blit(scaled_frame, draw_pos)

    def use_ability(self, ability_name: str) -> bool:
        """Use a named ability if it's available"""
        if ability_name not in self.abilities:
            return False

        ability = self.abilities[ability_name]
        if ability.is_ready():
            # todo: Change the current asset to the ability's animation...
            ability.trigger()
            return True
            
        return False
