from enum import Enum
from typing import Dict, Optional, Tuple
import pygame
from pydantic import BaseModel, Field

from app.core.engine.camera import Camera
from app.core.systems.entities import Actor
# todo: Handle this as a same module (mecanics) or something like that...
from app.game.base.abilities import Ability
from app.game.base.inventory import Inventory
from app.game.base.reputation import Reputation

from tools import AssetManager
from tools.console import *


class PlayerState(Enum):
    IDLE = "idle"
    WALK = "walk"
    ATTACK = "attack"
    PICKUP = "pick up"

class PlayerDirection(Enum):
    DOWN = "down"
    UP = "up"
    SIDE = "side"

class PlayerSprite(BaseModel):
    """Enhanced sprite system for player character with multiple sprite sheets"""
    sprite_sheets: Dict[str, Optional[pygame.Surface]] = Field(default_factory=dict)
    frame_size: Tuple[int, int] = (64, 64)  # Sprite size is 64x64
    current_state: PlayerState = Field(default=PlayerState.IDLE)
    current_direction: PlayerDirection = Field(default=PlayerDirection.DOWN)
    current_frame: int = Field(default=0)
    animation_speed: float = Field(default=0.1)
    animation_timer: float = Field(default=0.0)
    flip_horizontal: bool = Field(default=False)
    
    # Frame counts for each animation type
    frame_counts: Dict[PlayerState, int] = {
        PlayerState.IDLE: 4,
        PlayerState.WALK: 4,
        PlayerState.ATTACK: 3,
        PlayerState.PICKUP: 4
    }

    class Config:
        arbitrary_types_allowed = True

    def load_sprite_sheets(self):
        """Load all required sprite sheets"""
        # First load regular directional animations
        for direction in PlayerDirection:
            for state in PlayerState:
                # Skip pickup since it's handled separately
                if state == PlayerState.PICKUP:
                    continue
                
                sheet_name = f"_{direction.value} {state.value}.png"
                try:
                    path = AssetManager.get_image(f"static/main-character/{sheet_name}")
                    sheet = pygame.image.load(path).convert_alpha()
                    self.sprite_sheets[f"{direction.value}_{state.value}"] = sheet
                except Exception as e:
                    self.sprite_sheets[f"{direction.value}_{state.value}"] = None

        # Load pickup animation separately
        try:
            pickup_path = AssetManager.get_image("static/main-character/_pick up.png")
            pickup_sheet = pygame.image.load(pickup_path).convert_alpha()
            self.sprite_sheets["pickup"] = pickup_sheet
        except Exception as e:
            print(f"Error loading pickup animation: {e}")
            self.sprite_sheets["pickup"] = None

    def update(self, dt: float):
        """Update animation frame"""
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            max_frames = self.frame_counts[self.current_state]
            self.current_frame = (self.current_frame + 1) % max_frames

    def get_current_frame(self) -> pygame.Surface:
        """Get the current animation frame"""
        # Special handling for pickup animation
        if self.current_state == PlayerState.PICKUP:
            sheet = self.sprite_sheets.get("pickup")
            if sheet is None:
                return self.create_default_frame()
            
            try:
                frame_x = self.current_frame * self.frame_size[0]
                frame = sheet.subsurface((frame_x, 0, *self.frame_size))
                if self.flip_horizontal:
                    frame = pygame.transform.flip(frame, True, False)
                return frame
            except ValueError as e:
                print(f"Error getting pickup frame: {e}")
                return self.create_default_frame()

        # Normal handling for other animations
        sheet_key = f"{self.current_direction.value}_{self.current_state.value}"
        sheet = self.sprite_sheets.get(sheet_key)
        
        if sheet is None:
            return self.create_default_frame()

        try:
            frame_x = self.current_frame * self.frame_size[0]
            frame = sheet.subsurface((frame_x, 0, *self.frame_size))
            
            if self.flip_horizontal:
                frame = pygame.transform.flip(frame, True, False)
            
            return frame
        except ValueError as e:
            print(f"Error getting frame from sheet {sheet_key}: {e}")
            return self.create_default_frame()

    def create_default_frame(self) -> pygame.Surface:
        """Create a default frame for error cases"""
        surface = pygame.Surface(self.frame_size, pygame.SRCALPHA)
        surface.fill((255, 0, 0, 128))  # Semi-transparent red
        pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), 1)
        return surface

    def set_state(self, state: PlayerState, direction: PlayerDirection = None):
        """Set the current animation state and optionally direction"""
        if state != self.current_state:
            self.current_state = state
            self.current_frame = 0
            self.animation_timer = 0
        
        if direction is not None:
            if direction != self.current_direction:
                self.current_direction = direction
                self.current_frame = 0
                self.animation_timer = 0

    def set_direction(self, dx: float, dy: float):
        """Set direction based on movement vector"""
        if dx == 0 and dy == 0:
            return



        if abs(dx) > abs(dy):
            self.current_direction = PlayerDirection.SIDE
            self.flip_horizontal = dx > 0  # Flip when moving left
        else:
            self.current_direction = PlayerDirection.UP if dy < 0 else PlayerDirection.DOWN
            self.flip_horizontal = False


class Player(Actor):
    sprite: Optional[PlayerSprite] = Field(default=None)
    scale_factor: float = Field(default=3.0)  # No scaling needed since sprites are 64x64
    
    reputation: Reputation = Field(default_factory=Reputation)
    inventory: Inventory = Field(default_factory=Inventory)
    abilities: Dict[str, Ability] = Field(default_factory=dict)
    pickup_cooldown: float = Field(default=0.0)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.sprite is None:
            self.sprite = PlayerSprite()
        self.load_sprites()

    def load_sprites(self):
        """Load all player sprite sheets"""
        try:
            self.sprite.load_sprite_sheets()
        except Exception as e:
            print(f"Error loading player sprites: {e}")

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        if not self.sprite: return
        # Movement
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            # Normalize by dividing by √2
            dx *= 0.7071  # ≈ 1/√2
            dy *= 0.7071  # ≈ 1/√2

        # Update sprite state and direction
        if dx != 0 or dy != 0:
            self.sprite.set_state(PlayerState.WALK)
            self.sprite.set_direction(dx, dy)
        else:
            self.sprite.set_state(PlayerState.IDLE)


        # Handle actions
        if keys[pygame.K_SPACE]:
            self.sprite.set_state(PlayerState.ATTACK)
        elif keys[pygame.K_e]:
            self.sprite.set_state(PlayerState.PICKUP)

        # Move character
        self.move(dx, dy, dt)
        
        # Update animation
        self.sprite.update(dt)
        
        # Update abilities
        for ability in self.abilities.values():
            ability.update(dt)

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        if not self.sprite:
            return
                
        current_frame = self.sprite.get_current_frame()
        
        # Scale the frame
        scaled_size = (
            int(self.sprite.frame_size[0] * self.scale_factor),
            int(self.sprite.frame_size[1] * self.scale_factor)
        )
        scaled_frame = pygame.transform.scale(current_frame, scaled_size)
        
        # Convert world position to screen position
        screen_pos = camera.world_to_screen(self.position)
        
        # Center the scaled sprite
        draw_pos = (
            screen_pos[0] - scaled_size[0] // 2,
            screen_pos[1] - scaled_size[1] // 2
        )
        
        surface.blit(scaled_frame, draw_pos)
