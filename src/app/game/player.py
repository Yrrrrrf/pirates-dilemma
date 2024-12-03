import os
import pygame
from pydantic import BaseModel, Field
from typing import List, Optional

from app.core.camera import Camera
from app.core.entities.entities import Actor
from app.core.entities.sprites import *
from app.game.inventory import Inventory, Item
from utils import AssetManager


class Player(Actor):
    health: int = Field(default=100)
    max_health: int = Field(default=100)
    sprite_sheet_path: str = Field(default="static\\player.png")
    scale_factor: float = Field(default=4.0)
    inventory: Inventory = Field(default_factory=Inventory)
    gold: int = Field(default=0)
    experience: int = Field(default=0)
    level: int = Field(default=1)
    sprite: Optional[AnimatedSprite] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.sprite is None:
            self.sprite = AnimatedSprite()
        self.load_sprite_sheet()

    def load_sprite_sheet(self):
        try:
            img_path = AssetManager.get_image("static\\player.png")
            if not os.path.exists(img_path): raise FileNotFoundError(f"Image file not found: {img_path}")
            print(f"Image file exists: {img_path}")

            sprite_sheet = pygame.image.load(img_path)

            if not isinstance(sprite_sheet, pygame.Surface):  # Check if the surface is valid
                raise TypeError(f"Loaded object is not a pygame.Surface. Got {type(sprite_sheet)}")

            # Get and print surface information
            print(f"\tImage size: {sprite_sheet.get_size()}")
            print(f"\tImage color key: {sprite_sheet.get_colorkey()}")
            print(f"\tImage alpha: {sprite_sheet.get_alpha()}")
            print(f"\tImage bit size: {sprite_sheet.get_bitsize()}")

            try:  # Try to optimize the surface for display
                sprite_sheet = sprite_sheet.convert()  # Convert to the same pixel format as the display
            except pygame.error:
                print("Failed to convert surface, using original")

            # # Set color key for transparency if needed
            # if sprite_sheet.get_alpha() is None:
            #     sprite_sheet.set_colorkey((0, 0, 0))  # Assuming black is the transparent color
            #     print("Set color key for transparency")

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
        self.sprite.sprite_sheet = pygame.Surface((48, 48))
        self.sprite.sprite_sheet.fill((255, 0, 0))
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

        if keys[pygame.K_SPACE]:
            self.attack()

        self.move(dx, dy, dt)
        self.sprite.update(dt)

    def draw(self, surface: pygame.Surface, camera: Camera):
        if self.sprite and self.sprite.sprite_sheet:
            current_frame = self.sprite.get_current_frame()
            
            scaled_size = (int(current_frame.get_width() * self.scale_factor),
                         int(current_frame.get_height() * self.scale_factor))
            scaled_frame = pygame.transform.scale(current_frame, scaled_size)
            
            screen_pos = camera.world_to_screen(self.position)
            draw_pos = (screen_pos[0] - scaled_size[0] // 2,
                       screen_pos[1] - scaled_size[1] // 2)
            
            surface.blit(scaled_frame, draw_pos)

            # Draw health bar
            health_bar_width = scaled_size[0] * (self.health / self.max_health)
            health_bar_height = 5 * self.scale_factor
            pygame.draw.rect(surface, (255, 0, 0), 
                           (draw_pos[0], draw_pos[1] - health_bar_height - 2, scaled_size[0], health_bar_height))
            pygame.draw.rect(surface, (0, 255, 0), 
                           (draw_pos[0], draw_pos[1] - health_bar_height - 2, health_bar_width, health_bar_height))

    def collect_item(self, item: Item) -> bool:
        return self.inventory.add_item(item)

    def attack(self):
        self.sprite.current_state = AnimationState.ATTACK

    def take_damage(self, amount: int):
        self.health = max(0, self.health - amount)
        if self.health == 0:
            self.sprite.current_state = AnimationState.DEATH

    def gain_experience(self, amount: int):
        self.experience += amount
        new_level = 1 + self.experience // 1000
        if new_level > self.level:
            self.level = new_level
            self.max_health += 10
            self.health = self.max_health
