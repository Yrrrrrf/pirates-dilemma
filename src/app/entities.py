import os
import pygame
from app.camera import Camera
from utils import AssetManager
from pydantic import BaseModel, Field
from typing import Tuple, List, Dict, Optional
from enum import Enum


class AnimationState(Enum):
    IDLE = 0
    MOVE = 1
    ATTACK = 2
    DEATH = 3

class Direction(Enum):
    RIGHT = 1
    LEFT = -1

class AnimatedSprite(BaseModel):
    sprite_sheet: Optional[pygame.Surface] = None
    frame_size: Tuple[int, int] = (48, 48)
    animations: Dict[AnimationState, List[Tuple[int, int]]] = Field(default_factory=dict)
    current_state: AnimationState = AnimationState.IDLE
    current_frame: int = 0
    animation_speed: float = 0.1
    animation_timer: float = 0
    direction: Direction = Direction.RIGHT

    class Config:
        arbitrary_types_allowed = True

    def update(self, dt: float):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            if self.current_state in self.animations:
                self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_state])

    def get_current_frame(self) -> pygame.Surface:
        if self.sprite_sheet is None:
            return self.create_default_frame()

        if self.current_state not in self.animations:
            return self.create_default_frame()

        frame_coords = self.animations[self.current_state][self.current_frame]
        sheet_width, sheet_height = self.sprite_sheet.get_size()
        frame_width, frame_height = self.frame_size

        x = frame_coords[0] * frame_width
        y = frame_coords[1] * frame_height

        if x + frame_width > sheet_width or y + frame_height > sheet_height:
            print(f"Warning: Attempted to create out-of-bounds subsurface.")
            print(f"Sprite sheet size: {sheet_width}x{sheet_height}")
            print(f"Frame size: {frame_width}x{frame_height}")
            print(f"Attempted coordinates: ({x}, {y})")
            return self.create_default_frame()

        try:
            frame = self.sprite_sheet.subsurface((x, y, frame_width, frame_height))
        except ValueError as e:
            print(f"Error creating subsurface: {e}")
            return self.create_default_frame()

        if self.direction == Direction.LEFT:
            return pygame.transform.flip(frame, True, False)
        return frame

    def create_default_frame(self) -> pygame.Surface:
        surface = pygame.Surface(self.frame_size, pygame.SRCALPHA)
        surface.fill((255, 0, 0, 128))  # Semi-transparent red
        pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), 1)  # White border
        return surface


class Entity(BaseModel):
    position: pygame.math.Vector2 = Field(default_factory=lambda: pygame.math.Vector2(0, 0))
    
    class Config:
        arbitrary_types_allowed = True

class Actor(Entity):
    speed: float = Field(default=200.0)
    size: pygame.math.Vector2 = Field(default_factory=lambda: pygame.math.Vector2(48, 48))
    sprite: Optional[AnimatedSprite] = None

    def move(self, dx: float, dy: float, dt: float):
        self.position.x += dx * self.speed * dt
        self.position.y += dy * self.speed * dt

    def draw(self, surface: pygame.Surface, camera: Camera):
        if self.sprite:
            screen_pos = camera.world_to_screen(self.position)
            surface.blit(self.sprite.get_current_frame(), screen_pos)

class NPC(Actor):
    dialogue: str = Field(default="Hello, I'm an NPC!")


class Player(Actor):
    health: int = Field(default=100)
    max_health: int = Field(default=100)
    sprite_sheet_path: str = Field(default="static/player.png")
    # scale_factor: float = Field(default=2.0)  # New field for scaling
    scale_factor: float = Field(default=4.0)  # New field for coscaling

    def __init__(self, **data):
        super().__init__(**data)
        self.sprite = AnimatedSprite()
        self.load_sprite_sheet()

    def load_sprite_sheet(self):
        try:
            img_path = AssetManager.get_image("static\\player.png")
            if not os.path.exists(img_path): raise FileNotFoundError(f"Image file not found: {img_path}")
            print(f"Image file exists: {img_path}")

            # Load image
            sprite_sheet = pygame.image.load(img_path)
            print(f"Image loaded successfully. Type: {type(sprite_sheet)}")

            # Check if the surface is valid
            if not isinstance(sprite_sheet, pygame.Surface):
                raise TypeError(f"Loaded object is not a pygame.Surface. Got {type(sprite_sheet)}")

            # Get and print surface information
            print(f"Image size: {sprite_sheet.get_size()}")
            print(f"Image color key: {sprite_sheet.get_colorkey()}")
            print(f"Image alpha: {sprite_sheet.get_alpha()}")
            print(f"Image bit size: {sprite_sheet.get_bitsize()}")

            # Try to optimize the surface for display
            try:
                sprite_sheet = sprite_sheet.convert()
                print("Surface converted successfully")
            except pygame.error:
                print("Failed to convert surface, using original")

            # Set color key for transparency if needed
            if sprite_sheet.get_alpha() is None:
                sprite_sheet.set_colorkey((0, 0, 0))  # Assuming black is the transparent color
                print("Set color key for transparency")

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
            self.create_fallback_sprite_sheet()
        except Exception as e:
            print(f"Unexpected error loading player sprite sheet: {e}")
            self.create_fallback_sprite_sheet()

    def create_fallback_sprite_sheet(self):
        print("Creating fallback sprite sheet")
        self.sprite.sprite_sheet = pygame.Surface((48, 48))
        self.sprite.sprite_sheet.fill((255, 0, 0))  # Red placeholder
        self.sprite.frame_size = (48, 48)
        self.sprite.animations = {state: [(0, 0)] for state in AnimationState}

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper):
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        
        if dx != 0 or dy != 0:
            self.sprite.current_state = AnimationState.MOVE
            self.sprite.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
        else:
            self.sprite.current_state = AnimationState.IDLE

        self.move(dx, dy, dt)
        self.sprite.update(dt)

    def draw(self, surface: pygame.Surface, camera: Camera):
        if self.sprite and self.sprite.sprite_sheet:
            current_frame = self.sprite.get_current_frame()
            
            # Scale the frame
            scaled_size = (int(current_frame.get_width() * self.scale_factor),
                           int(current_frame.get_height() * self.scale_factor))
            scaled_frame = pygame.transform.scale(current_frame, scaled_size)
            
            # Calculate the position, considering the new size
            screen_pos = camera.world_to_screen(self.position)
            draw_pos = (screen_pos[0] - scaled_size[0] // 2,
                        screen_pos[1] - scaled_size[1] // 2)
            
            surface.blit(scaled_frame, draw_pos)

            # Draw health bar (adjusted for new size)
            health_bar_width = scaled_size[0] * (self.health / self.max_health)
            health_bar_height = 5 * self.scale_factor  # Scale the health bar height
            pygame.draw.rect(surface, (255, 0, 0), (draw_pos[0], draw_pos[1] - health_bar_height - 2, scaled_size[0], health_bar_height))
            pygame.draw.rect(surface, (0, 255, 0), (draw_pos[0], draw_pos[1] - health_bar_height - 2, health_bar_width, health_bar_height))


        # # * TO HANDLE THE COLLISION
        # self.collision_rect = pygame.Rect(
        #     self.position.x - (self.sprite.frame_size[0] * self.scale_factor) // 2,
        #     self.position.y - (self.sprite.frame_size[1] * self.scale_factor) // 2,
        #     self.sprite.frame_size[0] * self.scale_factor,
        #     self.sprite.frame_size[1] * self.scale_factor
        # )

    def attack(self):
        self.sprite.current_state = AnimationState.ATTACK

    def take_damage(self, amount: int):
        self.health = max(0, self.health - amount)
        if self.health == 0:
            self.sprite.current_state = AnimationState.DEATH
