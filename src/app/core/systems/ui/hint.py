from enum import Enum
from typing import Optional, Tuple, Dict
import pygame
from pydantic import BaseModel, Field
from pygame import Surface, font
from tools import AssetManager

class HintPosition(Enum):
    """Define possible hint positions relative to target"""
    ABOVE = "above"
    BELOW = "below"
    LEFT = "left"
    RIGHT = "right"

class HintStyle(BaseModel):
    """Define the visual style of a hint"""
    font_size: int = Field(default=16)
    font_name: str = Field(default="CascadiaCode.ttf")
    text_color: Tuple[int, int, int] = Field(default=(255, 255, 255))
    bg_color: Tuple[int, int, int] = Field(default=(0, 0, 0))
    bg_alpha: int = Field(default=180)
    padding: int = Field(default=5)
    border_radius: int = Field(default=8)
    offset: int = Field(default=50)  # Distance from target
    fade_speed: float = Field(default=2.0)

class Hint(BaseModel):
    """Base class for creating floating hints"""
    text: str = Field(...)
    position: HintPosition = Field(default=HintPosition.ABOVE)
    style: HintStyle = Field(default_factory=HintStyle)
    font: Optional[pygame.font.Font] = None
    _surface: Optional[Surface] = None
    alpha: float = Field(default=0.0)
    visible: bool = Field(default=False)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.font = font.Font(AssetManager.get_font(self.style.font_name), self.style.font_size)
        self._create_surface()

    def _create_surface(self) -> None:
        # Create text surface
        text_surface = self.font.render(self.text, True, self.style.text_color)
        text_rect = text_surface.get_rect()

        # Calculate surface size with padding
        width = text_rect.width + (self.style.padding * 2)
        height = text_rect.height + (self.style.padding * 2)
        
        # Create surface
        self._surface = Surface((width, height), pygame.SRCALPHA)
        
        # Draw background
        pygame.draw.rect(
            self._surface,
            (*self.style.bg_color, self.style.bg_alpha),
            self._surface.get_rect(),
            border_radius=self.style.border_radius
        )

        # Draw text
        self._surface.blit(text_surface, (self.style.padding, self.style.padding))

    def update(self, dt: float) -> None:
        target_alpha = 255.0 if self.visible else 0.0
        self.alpha += (target_alpha - self.alpha) * self.style.fade_speed * dt
        self.alpha = max(0.0, min(255.0, self.alpha))

    def get_position(self, target_pos: Tuple[int, int]) -> Tuple[int, int]:
        if not self._surface:
            return target_pos

        x, y = target_pos
        width = self._surface.get_width()
        height = self._surface.get_height()

        match self.position:
            case HintPosition.ABOVE:
                return (x - width // 2, y - height - self.style.offset)
            case HintPosition.BELOW:
                return (x - width // 2, y + self.style.offset)
            case HintPosition.LEFT:
                return (x - width - self.style.offset, y - height // 2)
            case HintPosition.RIGHT:
                return (x + self.style.offset, y - height // 2)

    def draw(self, surface: Surface, position: Tuple[int, int]) -> None:
        if self.alpha <= 0 or not self._surface:
            return

        # Create alpha copy
        display_surface = self._surface.copy()
        display_surface.set_alpha(int(self.alpha))
        
        # Get draw position
        draw_pos = self.get_position(position)
        
        # Draw hint
        surface.blit(display_surface, draw_pos)

class HintManager(BaseModel):
    """Manages multiple hints"""
    hints: Dict[str, Hint] = Field(default_factory=dict)

    def add_hint(self, key: str, hint: Hint) -> None:
        self.hints[key] = hint

    def show_hint(self, key: str) -> None:
        if key in self.hints:
            self.hints[key].visible = True

    def hide_hint(self, key: str) -> None:
        if key in self.hints:
            self.hints[key].visible = False

    def update(self, dt: float) -> None:
        for hint in self.hints.values():
            hint.update(dt)

    def draw(self, surface: Surface, positions: Dict[str, Tuple[int, int]]) -> None:
        for key, hint in self.hints.items():
            if key in positions:
                hint.draw(surface, positions[key])
