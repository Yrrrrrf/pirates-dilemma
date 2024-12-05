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
    RIGHT = 0
    LEFT = 1
    UP = 2
    DOWN = 3

class AnimatedSprite(BaseModel):
    sprite_sheet: Optional[pygame.Surface] = None
    frame_size: Tuple[int, int] = (32, 48)  # Updated to correct sprite size
    animations: Dict[AnimationState, List[Tuple[int, int]]] = Field(default_factory=dict)
    current_state: AnimationState = AnimationState.IDLE
    current_frame: int = 0
    animation_speed: float = 0.1
    animation_timer: float = 0
    direction: Direction = Direction.RIGHT
    flip_horizontal: bool = False

    class Config:
        arbitrary_types_allowed = True

    def update(self, dt: float):
        """Update animation frame based on timer"""
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            if self.current_state in self.animations:
                self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_state])

    def get_frame_coords(self, frame_index: int, row: int) -> Tuple[int, int]:
        """Calculate frame coordinates in sprite sheet"""
        frame_width, frame_height = self.frame_size
        x = frame_index * frame_width
        y = row * frame_height
        return x, y

    def get_current_frame(self) -> pygame.Surface:
        """Get the current animation frame as a surface"""
        if self.sprite_sheet is None or self.current_state not in self.animations:
            return self.create_default_frame()

        try:
            # Get current animation frame coordinates
            frame_coords = self.animations[self.current_state][self.current_frame]
            x, y = self.get_frame_coords(*frame_coords)
            
            # Get sprite sheet dimensions
            sheet_width, sheet_height = self.sprite_sheet.get_size()
            frame_width, frame_height = self.frame_size

            # Validate coordinates are within bounds
            if x + frame_width > sheet_width or y + frame_height > sheet_height:
                print(f"Warning: Frame coordinates out of bounds: ({x}, {y})")
                print(f"Sheet size: {sheet_width}x{sheet_height}")
                print(f"Frame size: {frame_width}x{frame_height}")
                return self.create_default_frame()

            # Extract frame from sprite sheet
            frame = self.sprite_sheet.subsurface((x, y, frame_width, frame_height))

            # Handle horizontal flipping if needed
            if self.flip_horizontal:
                frame = pygame.transform.flip(frame, True, False)

            return frame

        except (ValueError, AttributeError) as e:
            print(f"Error getting animation frame: {e}")
            return self.create_default_frame()

    def create_default_frame(self) -> pygame.Surface:
        """Create a fallback frame if sprite sheet is missing or invalid"""
        surface = pygame.Surface(self.frame_size, pygame.SRCALPHA)
        surface.fill((255, 0, 0, 128))  # Semi-transparent red
        pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), 1)  # White border
        return surface

    def set_direction(self, direction: Direction) -> None:
        """Set sprite direction and update flip state"""
        self.direction = direction
        self.flip_horizontal = direction == Direction.LEFT

    def setup_directional_animations(self) -> None:
        """Set up animations for all directions"""
        # Frame indices for each animation state
        idle_frames = range(4)  # First 4 frames
        walk_frames = range(4, 8)  # Next 4 frames

        # Calculate row offsets for each direction
        direction_rows = {
            Direction.RIGHT: 0,  # First row
            Direction.LEFT: 0,   # Same as right, but flipped
            Direction.UP: 1,     # Second row
            Direction.DOWN: 2    # Third row
        }

        # Set up animations for each state and direction
        self.animations = {
            AnimationState.IDLE: [(i, direction_rows[self.direction]) for i in idle_frames],
            AnimationState.MOVE: [(i, direction_rows[self.direction]) for i in walk_frames]
        }
