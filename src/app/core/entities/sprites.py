import pygame
from enum import Enum
from typing import Tuple, List, Dict, Optional
from pydantic import BaseModel, Field

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
