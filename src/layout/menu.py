
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple
from pygame import Rect, Surface
import pygame

from project.settings.lang import LanguageManager
from project import app_data
from utils import AssetManager

menu_lang_manager = LanguageManager(language=app_data.settings.language)
menu_lang_manager.load_translations(file_path=AssetManager.get_script("menu.json"))


@dataclass
class MenuTheme:
    """Theme configuration for menu rendering"""
    background_color: Tuple[int, int, int] = (0, 0, 0)
    text_color: Tuple[int, int, int] = (255, 255, 255)
    highlight_color: Tuple[int, int, int] = (255, 223, 0)
    shadow_color: Tuple[int, int, int] = (128, 128, 128)
    shadow_offset: Tuple[int, int] = (3, 3)
    font_name: str = 'comicsansms'
    title_size: int = 80
    option_size: int = 45
    highlight_size: int = 55
    spacing: int = 100
    start_y: int = 250
    hover_scale: float = 1.1
    hover_color: Tuple[int, int, int] = (255, 165, 0)

class MenuRenderer:
    def __init__(self, screen: Surface, theme: MenuTheme):
        self.screen = screen
        self.theme = theme
        self.fonts = self._initialize_fonts()
        self.cached_surfaces: Dict[str, Surface] = {}
        
    def _initialize_fonts(self) -> Dict[str, pygame.font.Font]:
        base_font = pygame.font.match_font(self.theme.font_name)
        return {
            'title': pygame.font.Font(base_font, self.theme.title_size),
            'option': pygame.font.Font(base_font, self.theme.option_size),
            'highlight': pygame.font.Font(base_font, self.theme.highlight_size)
        }

    def render_text_with_shadow(self, text: str, font: pygame.font.Font, 
                              color: Tuple[int, int, int], pos: Tuple[int, int],
                              scale: float = 1.0) -> Rect:
        cache_key = f"{text}_{str(color)}_{str(scale)}"
        
        if cache_key not in self.cached_surfaces:
            shadow = font.render(text, True, self.theme.shadow_color)
            text_surface = font.render(text, True, color)
            
            if scale != 1.0:
                new_size = (int(text_surface.get_width() * scale), 
                          int(text_surface.get_height() * scale))
                shadow = pygame.transform.smoothscale(shadow, new_size)
                text_surface = pygame.transform.smoothscale(text_surface, new_size)
            
            self.cached_surfaces[cache_key] = (text_surface, shadow)
        
        text_surface, shadow = self.cached_surfaces[cache_key]
        
        text_rect = text_surface.get_rect(center=pos)
        shadow_pos = (pos[0] + self.theme.shadow_offset[0], pos[1] + self.theme.shadow_offset[1])
        shadow_rect = shadow.get_rect(center=shadow_pos)
        
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(text_surface, text_rect)
        return text_rect

class MenuItem:
    def __init__(self, text_key: str, position: Tuple[int, int], callback: Callable[[], None]):
        self.text_key = text_key  # Store the key instead of the text
        self.position = position
        self.callback = callback
        self.rect: Optional[Rect] = None
        self.is_selected = False
        self.is_hovered = False
        self.original_scale = 1.0

    @property
    def text(self) -> str: return menu_lang_manager.get_text(self.text_key)

    def update_rect(self, rect: Rect) -> None: self.rect = rect

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        return bool(self.rect and self.rect.collidepoint(pos))
    
    def update_hover(self, pos: Tuple[int, int]) -> None:
        self.is_hovered = bool(self.rect and self.rect.collidepoint(pos))
