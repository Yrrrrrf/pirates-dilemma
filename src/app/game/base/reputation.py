from typing import Tuple
import pygame
from pydantic import BaseModel, Field


class Reputation(BaseModel):
    """Manages the player's reputation and standing in the game world"""
    value: int = Field(default=10, ge=0, le=100)
    
    class Config:
        arbitrary_types_allowed = True

    def modify(self, amount: int) -> None:
        """Modify reputation value ensuring it stays within bounds"""
        self.value = max(0, min(100, self.value + amount))

    def get_multiplier(self) -> float:
        """Get reputation-based multiplier for various game mechanics"""
        return 1.0 + (self.value - 50) / 100  # Range: 0.5 to 1.5

    def get_status(self) -> str:
        """Get reputation status based on value"""
        if self.value <= 25: return "Chaotic"
        elif self.value >= 75: return "Lawful"
        return "Neutral"

    def draw(self, surface: pygame.Surface, position: Tuple[int, int], size: Tuple[int, int] = (200, 30)) -> None:
        """Draw a stylized reputation bar with gradient effect"""

        def get_gradient_color() -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
            """Get primary and secondary colors based on value gradient"""
            # Primary color transitions from red (low) to blue (high)
            r = int(255 * (1 - self.value / 100))  # Decreases from 255 to 0
            b = int(255 * (self.value / 100))      # Increases from 0 to 255
            g = int(128 * min(self.value, 100 - self.value) / 50)  # Peaks at 50

            return (r, g, b), (r//2, g//2, b//2)  # return primary & darkened secondary color

        primary_color, secondary_color = get_gradient_color()

        # * Unpack size tuple
        width, height = size

        # Create surfaces
        glow_surface = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
        bar_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw glow
        pygame.draw.rect(glow_surface, (*primary_color, 50), (10, 10, width, height), border_radius=height//2)        
        pygame.draw.rect(bar_surface, secondary_color, (0, 0, width, height), border_radius=height//2)
        
        # Draw filled portion
        fill_width = int(width * (self.value / 100))
        if fill_width > 0:
            pygame.draw.rect(bar_surface, primary_color, (0, 0, fill_width, height), border_radius=height//2)
        
        # Draw border with gradient
        border_width = 4
        for i in range(border_width):
            pygame.draw.rect(bar_surface, (*secondary_color, 255 - (i * 50)), (i, i, width - i*2, height - i*2), border_radius=height//2, width=1)
        
        font = pygame.font.Font(None, height - 4)

        # Add status text
        # todo: Add some more user-friendly status text (also add more types of status)
        status = self.get_status()
        status_text = font.render(status, True, (255, 255, 255))
        text_rect = status_text.get_rect(center=(width//2, height//2))

        # * Unpack position tuple
        x, y = position
        
        # Apply surfaces
        surface.blit(glow_surface, (x - 10, y - 10))
        surface.blit(bar_surface, (x, y))
        surface.blit(status_text, (x + text_rect.x, y + text_rect.y))
        
        # Draw value
        value_text = font.render(f"{self.value:.2f}%", True, (255, 255, 255))
        surface.blit(value_text, (x + width + 10, y + height//2 - value_text.get_height()//2))
