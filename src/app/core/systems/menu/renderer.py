from typing import Dict, Tuple
import pygame

from project.theme.ui import UITheme


class MenuRenderer:
    """Handles rendering of menu elements"""
    def __init__(self, theme: UITheme):
        self.theme = theme
        self.fonts = self._initialize_fonts()
        self.cached_surfaces: Dict[str, pygame.Surface] = {}

    def _initialize_fonts(self) -> Dict[str, pygame.font.Font]:
        """Initialize fonts based on theme"""
        fonts: Dict[str, pygame.font.Font] = {}
        base_font = pygame.font.match_font(self.theme.font_name)
        for name, size in self.theme.font_sizes.items():
            fonts[name] = pygame.font.Font(base_font, size)
        return fonts

    def render_text(self, 
        text: str,
        font_type: str,
        color: Tuple[int, int, int],
        pos: Tuple[int, int],
        surface: pygame.Surface,
        centered: bool = True,
        shadow: bool = True
    ) -> pygame.Rect:
        """Render text with optional shadow and centering"""
        cache_key = f"{text}_{font_type}_{color}_{centered}_{shadow}"
        
        if cache_key not in self.cached_surfaces:
            font = self.fonts[font_type]
            text_surface = font.render(text, True, color)
            
            if shadow:
                shadow_surface = font.render(text, True, (128, 128, 128))
                
                if centered:
                    shadow_rect = shadow_surface.get_rect(center=(pos[0] + 3, pos[1] + 3))
                    text_rect = text_surface.get_rect(center=pos)
                else:
                    shadow_rect = shadow_surface.get_rect(topleft=(pos[0] + 3, pos[1] + 3))
                    text_rect = text_surface.get_rect(topleft=pos)
                
                self.cached_surfaces[cache_key] = (text_surface, text_rect, shadow_surface, shadow_rect)
            else:
                if centered:
                    text_rect = text_surface.get_rect(center=pos)
                else:
                    text_rect = text_surface.get_rect(topleft=pos)
                self.cached_surfaces[cache_key] = (text_surface, text_rect, None, None)
        
        text_surface, text_rect, shadow_surface, shadow_rect = self.cached_surfaces[cache_key]
        
        if shadow and shadow_surface:
            surface.blit(shadow_surface, shadow_rect)
        surface.blit(text_surface, text_rect)
        
        return text_rect
