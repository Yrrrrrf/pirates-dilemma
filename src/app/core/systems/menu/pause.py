from typing import Callable, Dict, Optional, Tuple
import pygame
from project.settings.lang import Language, LanguageManager
from tools import AssetManager
from project import menu_lang_manager

class PauseMenuItem:
    def __init__(self, text_key: str, callback: Callable[[], None]):
        self.text_key = text_key
        self.callback = callback
        self.rect: Optional[pygame.Rect] = None
        self.is_hovered = False

    def update_rect(self, rect: pygame.Rect) -> None:
        self.rect = rect

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        return bool(self.rect and self.rect.collidepoint(pos))

    def update_hover(self, pos: Tuple[int, int]) -> None:
        self.is_hovered = bool(self.rect and self.rect.collidepoint(pos))


class PauseMenu:
    def __init__(self, surface: pygame.Surface,
            resume_callback: Callable[[], None],
            exit_callback: Callable[[], None]
        ):
        self.surface = surface
        self.lang_manager = menu_lang_manager
        self.selected_index = 0
        self.items: list[PauseMenuItem] = []
        
        # Menu style configuration
        self.panel_width = 300
        self.panel_height = 300  # Reduced height
        self.item_height = 50
        self.item_padding = 20
        
        # Colors with more transparency
        self.bg_color = (20, 20, 20, 160)  # More transparent background
        self.text_color = (255, 255, 255)
        self.hover_color = (255, 223, 0)
        self.border_color = (200, 200, 200)

        # Initialize menu items
        self._init_menu_items(resume_callback, exit_callback)
        
        # Load fonts
        self.title_font = pygame.font.Font(AssetManager.get_font("CascadiaCode.ttf"), 32)
        self.item_font = pygame.font.Font(AssetManager.get_font("CascadiaCode.ttf"), 24)

    def _init_menu_items(self, resume_callback: Callable[[], None], 
                        exit_callback: Callable[[], None]) -> None:
        self.items = [
            PauseMenuItem("continue", resume_callback),
            PauseMenuItem("language", self.toggle_language),  # Now properly connected
            PauseMenuItem("exit", exit_callback)
        ]

    def toggle_language(self) -> None:
        # Toggle between available languages
        current_lang = self.lang_manager.language
        available_langs = list(Language)
        current_index = available_langs.index(current_lang)
        next_index = (current_index + 1) % len(available_langs)
        self.lang_manager.set_language(available_langs[next_index])

    def draw(self) -> None:

        # Calculate panel position (centered)
        screen_width, screen_height = self.surface.get_size()
        panel_x = (screen_width - self.panel_width) // 2
        panel_y = (screen_height - self.panel_height) // 2

        # Create single semi-transparent overlay
        overlay = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))  # Consistent transparency
        self.surface.blit(overlay, (0, 0))

        # Draw panel background
        panel = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, self.bg_color, panel.get_rect(), border_radius=10)
        pygame.draw.rect(panel, self.border_color, panel.get_rect(), width=2, border_radius=10)

        # Draw title
        title_text = self.title_font.render(self.lang_manager.get_text("pause")
                                            , True, self.text_color)
        title_rect = title_text.get_rect(midtop=(self.panel_width // 2, 20))
        panel.blit(title_text, title_rect)

        # Draw menu items
        start_y = 80  # Reduced spacing from title
        for i, item in enumerate(self.items):
            # Create a button background when hovered
            button_rect = pygame.Rect(
                10,
                start_y + i * (self.item_height + self.item_padding) - 5,
                self.panel_width - 20,
                self.item_height
            )
            
            if item.is_hovered:
                pygame.draw.rect(panel, (255, 255, 255, 30), button_rect, border_radius=5)
                pygame.draw.rect(panel, self.hover_color, button_rect, width=2, border_radius=5)
            
            # Get the text, adding current language for the language option
            text_content = self.lang_manager.get_text(item.text_key)
            if item.text_key == "language":
                text_content = f" ({self.lang_manager.language.name})"
                
            text = self.item_font.render(text_content, True, 
                self.hover_color if item.is_hovered else self.text_color
            )
            text_rect = text.get_rect(center=(self.panel_width // 2, 
                start_y + i * (self.item_height + self.item_padding) + self.item_height // 2)
            )
            panel.blit(text, text_rect)
            
            # Update item rect for hover/click detection with the full button area
            item.update_rect(pygame.Rect(
                panel_x + button_rect.x,
                panel_y + button_rect.y,
                button_rect.width,
                button_rect.height
            ))

        # Draw the panel
        self.surface.blit(panel, (panel_x, panel_y))

    def handle_click(self, pos: Tuple[int, int]) -> None:
        for item in self.items:
            if item.handle_click(pos):
                item.callback()
                break

    def handle_keydown(self, event: pygame.event.Event) -> None:
        match event.key:
            case pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.items)
            case pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.items)
            case pygame.K_RETURN:
                self.items[self.selected_index].callback()

    def update_hover_states(self, mouse_pos: Tuple[int, int]) -> None:
        for item in self.items:
            item.update_hover(mouse_pos)
