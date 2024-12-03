from typing import Tuple, Dict
import pygame
from pydantic import BaseModel, Field

class Reputation(BaseModel):
    """Manages the player's reputation and standing in the game world"""
    value: float = Field(default=0, ge=0, le=100)
    
    # Color schemes based on reputation ranges
    _COLORS: Dict[str, Dict[str, Tuple]] = {
        'lawful': {
            'primary': (64, 196, 255),    # Light blue
            'secondary': (32, 128, 192),   # Dark blue
            'glow': (128, 224, 255, 50)    # Light blue with alpha
        },
        'neutral': {
            'primary': (255, 196, 64),    # Gold
            'secondary': (192, 128, 32),   # Dark gold
            'glow': (255, 224, 128, 50)    # Light gold with alpha
        },
        'chaotic': {
            'primary': (255, 64, 64),     # Bright red
            'secondary': (192, 32, 32),    # Dark red
            'glow': (255, 128, 128, 50)    # Light red with alpha
        }
    }

    class Config:
        arbitrary_types_allowed = True

    def get_reputation_type(self) -> str:
        """Determine reputation type based on value"""
        if self.value >= 75:
            return 'lawful'
        elif self.value <= 25:
            return 'chaotic'
        return 'neutral'

    def get_status(self) -> str:
        """Get a descriptive status of the current reputation"""
        match self.get_reputation_type():
            case 'lawful': return "Respected"
            case 'chaotic': return "Notorious"
            case _: return "Neutral"

    def modify(self, amount: int) -> None:
        """Modify reputation value ensuring it stays within bounds"""
        self.value = max(0, min(100, self.value + amount))

    def get_multiplier(self) -> float:
        """Get reputation-based multiplier for various game mechanics"""
        return 1.0 + (self.value - 50) / 100  # Range: 0.5 to 1.5

    def draw(self, surface: pygame.Surface, position: Tuple[int, int], size: Tuple[int, int] = (200, 30)) -> None:
        """Draw a stylized reputation bar with glow effect and status indicator"""
        x, y = position
        width, height = size
        
        # Get color scheme based on reputation value
        colors = self._COLORS[self.get_reputation_type()]
        
        # Create surfaces for glow effect
        glow_surface = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
        bar_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw glow
        pygame.draw.rect(glow_surface, colors['glow'], 
                        (10, 10, width, height), 
                        border_radius=height//2)
        
        # Draw background (darker portion)
        pygame.draw.rect(bar_surface, colors['secondary'], 
                        (0, 0, width, height), 
                        border_radius=height//2)
        
        # Draw filled portion
        fill_width = int(width * (self.value / 100))
        if fill_width > 0:
            pygame.draw.rect(bar_surface, colors['primary'],
                           (0, 0, fill_width, height),
                           border_radius=height//2)
            
            # Add shine effect to the filled portion
            shine_height = height // 3
            shine_rect = pygame.Surface((fill_width, shine_height), pygame.SRCALPHA)
            shine_color = (*colors['primary'], 100)
            pygame.draw.rect(shine_rect, shine_color, 
                           (0, 0, fill_width, shine_height),
                           border_radius=height//4)
            bar_surface.blit(shine_rect, (0, 2))
        
        # Draw border with gradient
        border_width = 2
        for i in range(border_width):
            alpha = 255 - (i * 50)
            pygame.draw.rect(bar_surface, (*colors['secondary'], alpha),
                           (i, i, width - i*2, height - i*2),
                           border_radius=height//2, width=1)
        
        # Add status text
        font = pygame.font.Font(None, height - 4)
        status = self.get_status()
        status_text = font.render(status, True, (255, 255, 255))
        text_rect = status_text.get_rect(center=(width//2, height//2))
        
        # Apply surfaces to main surface
        surface.blit(glow_surface, (x - 10, y - 10))
        surface.blit(bar_surface, (x, y))
        surface.blit(status_text, (x + text_rect.x, y + text_rect.y))
        
        # Draw numerical value
        value_text = font.render(f"{self.value}%", True, (255, 255, 255))
        surface.blit(value_text, (x + width + 10, y + height//2 - value_text.get_height()//2))