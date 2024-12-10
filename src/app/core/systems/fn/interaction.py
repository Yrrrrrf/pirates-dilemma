from enum import Enum
from typing import List, Dict, Optional, Tuple, Callable
import pygame
from pydantic import BaseModel, Field

from tools import AssetManager

class InteractionType(Enum):
    TALK = "Talk"
    BUY = "Buy"
    SELL = "Sell"
    STEAL = "Steal"

    @property
    def color(self) -> Tuple[int, int, int]:
        return {
            InteractionType.TALK: (64, 196, 255),  # Light blue
            InteractionType.BUY: (96, 255, 96),    # Light green
            InteractionType.SELL: (255, 196, 64),  # Gold
            InteractionType.STEAL: (255, 64, 64),  # Red
        }[self]

class DialogueMenuOption(BaseModel):
    """Represents a selectable menu option in the dialogue box"""
    text: str
    interaction_type: InteractionType
    callback: Optional[Callable] = None
    rect: Optional[pygame.Rect] = None
    is_hovered: bool = Field(default=False)
    
    class Config:
        arbitrary_types_allowed = True

    def trigger(self) -> None:
        """Trigger the option's callback if it exists"""
        if self.callback:
            self.callback()

class DialogueMenu(BaseModel):
    """Handles the interaction menu within the dialogue box"""
    options: List[DialogueMenuOption] = Field(default_factory=list)
    font: Optional[pygame.font.Font] = None
    padding: int = Field(default=20)
    spacing: int = Field(default=60)
    option_height: int = Field(default=40)
    
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.font = pygame.font.Font(AssetManager.get_font("CascadiaCode.ttf"), 20)

    def update_hover(self, mouse_pos: Tuple[int, int]) -> None:
        """Update hover states based on mouse position"""
        for option in self.options:
            if option.rect:
                option.is_hovered = option.rect.collidepoint(mouse_pos)

    def handle_click(self, mouse_pos: Tuple[int, int]) -> None:
        """Handle mouse clicks on menu options"""
        for option in self.options:
            if option.rect and option.rect.collidepoint(mouse_pos):
                option.trigger()
                break

    def draw(self, surface: pygame.Surface, box_rect: pygame.Rect, alpha: int = 255) -> None:
        """Draw menu options integrated in the dialogue box"""
        if not self.options:
            return

        # Create a content area within the dialogue box
        content_width = box_rect.width - (self.padding * 2)
        content_height = len(self.options) * self.option_height + (self.padding * 2)
        
        # Position options in the center of the dialogue box
        start_x = box_rect.x + self.padding
        start_y = box_rect.centery - (content_height / 2)

        # Draw semi-transparent background for menu area
        menu_bg = pygame.Surface((content_width, content_height), pygame.SRCALPHA)
        pygame.draw.rect(
            menu_bg,
            (0, 0, 0, int(alpha * 0.3)),  # Semi-transparent black
            menu_bg.get_rect(),
            border_radius=10
        )
        surface.blit(menu_bg, (start_x, start_y))

        # Draw options
        for i, option in enumerate(self.options):
            # Calculate option position
            option_rect = pygame.Rect(
                start_x,
                start_y + (i * self.option_height) + self.padding,
                content_width,
                self.option_height - 10  # Slight gap between options
            )
            option.rect = option_rect

            # Draw option background when hovered
            if option.is_hovered:
                pygame.draw.rect(
                    surface,
                    (*option.interaction_type.color, int(alpha * 0.2)),
                    option_rect,
                    border_radius=5
                )
                pygame.draw.rect(
                    surface,
                    option.interaction_type.color,
                    option_rect,
                    width=2,
                    border_radius=5
                )

            # Draw option text
            text_surface = self.font.render(
                option.interaction_type.value,
                True,
                option.interaction_type.color
            )
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(center=option_rect.center)
            surface.blit(text_surface, text_rect)

    def handle_click(self, pos: Tuple[int, int]) -> None:
        """Handle mouse clicks on menu options"""
        for option in self.options:
            if option.rect and option.rect.collidepoint(pos):
                if option.callback:
                    option.callback()
                    return True  # Indicate click was handled
        return False
