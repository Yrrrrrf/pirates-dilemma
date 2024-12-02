from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Callable
import pygame
from pygame import Surface, Rect
import sys
from settings import Language, LanguageManager
from utils import AssetManager
from app.game_state import app_data


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
        shadow_pos = (pos[0] + self.theme.shadow_offset[0], 
                     pos[1] + self.theme.shadow_offset[1])
        shadow_rect = shadow.get_rect(center=shadow_pos)
        
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(text_surface, text_rect)
        return text_rect

class MenuItem:
    def __init__(self, text_key: str, position: Tuple[int, int], callback: Callable[[], None], lang_manager: LanguageManager):
        self.text_key = text_key  # Store the key instead of the text
        self.lang_manager = lang_manager
        self.position = position
        self.callback = callback
        self.rect: Optional[Rect] = None
        self.is_selected = False
        self.is_hovered = False
        self.original_scale = 1.0

    @property
    def text(self) -> str:
        return self.lang_manager.get_text(self.text_key)

    def update_rect(self, rect: Rect) -> None:
        self.rect = rect

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        return bool(self.rect and self.rect.collidepoint(pos))
    
    def update_hover(self, pos: Tuple[int, int]) -> None:
        self.is_hovered = bool(self.rect and self.rect.collidepoint(pos))


class Card:
    def __init__(self, screen: Surface, theme: MenuTheme, title_key: str, lang_manager: LanguageManager):
        self.screen = screen
        self.theme = theme
        self.title_key = title_key  # Store the key instead of the title
        self.lang_manager = lang_manager
        self.items: List[MenuItem] = []
        self.selected_index = 0
        self.renderer = MenuRenderer(screen, theme)
        self.background_surface = None

    @property
    def title(self) -> str:
        return self.lang_manager.get_text(self.title_key)

    def set_background(self, surface: Surface) -> None:
        self.background_surface = surface

    def add_item(self, text_key: str, position: Tuple[int, int], callback: Callable[[], None]) -> None:
        self.items.append(MenuItem(text_key, position, callback, self.lang_manager))

    def display(self) -> None:
        if self.background_surface:
            self.screen.blit(self.background_surface, (0, 0))
        
        screen_center = self.screen.get_width() // 2
        
        # Render title
        self.renderer.render_text_with_shadow(
            self.title,
            self.renderer.fonts['title'],
            self.theme.highlight_color,
            (screen_center, 100),
            scale=1.2
        )

        # Render items
        for i, item in enumerate(self.items):
            font = self.renderer.fonts['highlight' if i == self.selected_index else 'option']
            color = self.theme.highlight_color if i == self.selected_index else \
                   self.theme.hover_color if item.is_hovered else \
                   self.theme.text_color
            
            scale = self.theme.hover_scale if item.is_hovered else 1.0
            pos = (screen_center, self.theme.start_y + i * self.theme.spacing)
            rect = self.renderer.render_text_with_shadow(item.text, font, color, pos, scale)
            item.update_rect(rect)

    def navigate(self, direction: int) -> None:
        self.selected_index = (self.selected_index + direction) % len(self.items)
        for item in self.items:
            item.is_hovered = False

    def handle_click(self, pos: Tuple[int, int]) -> None:
        for item in self.items:
            if item.handle_click(pos):
                item.callback()
                break

    def update_hover_states(self, mouse_pos: Tuple[int, int]) -> None:
        for item in self.items:
            item.update_hover(mouse_pos)


class GameMenu:
    def __init__(self, screen: Surface):
        self.screen = screen
        self.theme = MenuTheme()
        self.background = self._load_background()
        
        self.lang_manager = LanguageManager(language=app_data.settings.language)
        self.lang_manager.load_translations(file_path=AssetManager.get_script("menu.json"))

        self.current_card = None
        self.cards = self._initialize_cards()
        self.show_card('main')

    def _load_background(self) -> Surface:
        try:
            bg_image = pygame.image.load(AssetManager.get_image("pirate-hat.png"))
            return pygame.transform.scale(bg_image, self.screen.get_size())
        except pygame.error:
            bg = Surface(self.screen.get_size())
            bg.fill((0, 0, 0))
            return bg

    def _initialize_cards(self) -> Dict[str, Card]:
        from main import main
        cards = {}

        # Initialize main card
        main_card = Card(self.screen, self.theme, "menu_title", self.lang_manager)
        main_card.set_background(self.background)
        main_card.add_item("start", (0, 0), lambda: main())
        main_card.add_item("options", (0, 0), lambda: self.show_card('options'))
        main_card.add_item("exit", (0, 0), lambda: sys.exit())
        cards['main'] = main_card

        # Initialize options card
        options_card = Card(self.screen, self.theme, "settings", self.lang_manager)
        options_card.set_background(self.background)
        options_card.add_item("spanish", (0, 0), lambda: self._change_lang(Language.SPANISH))
        options_card.add_item("english", (0, 0), lambda: self._change_lang(Language.ENGLISH))
        options_card.add_item("back", (0, 0), lambda: self.show_card('main'))
        cards['options'] = options_card

        return cards

    def _change_lang(self, lang: Language) -> None:
        app_data.settings.language = lang  # Update the app_data settings
        self.lang_manager.language = lang  # Update the language manager
        print(f"Changed language to {lang.name}")
        self.show_card('main')  # No need to reinitialize cards - they will automatically use the new lang

    def show_card(self, card_name: str) -> None:
        if card_name in self.cards: self.current_card = self.cards[card_name]

    def display(self) -> None:
        if self.current_card:
            self.screen.fill((0, 0, 0))  # * Clear the screen before drawing
            self.current_card.display()  # Draw the current card
            pygame.display.flip()  # Update the display

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.current_card: return

        if event.type == pygame.KEYDOWN: self._handle_keydown(event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.current_card.handle_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self.current_card.update_hover_states(event.pos)

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE and self.current_card != self.cards['main']:
            self.show_card('main')
        elif event.key == pygame.K_UP:
            self.current_card.navigate(-1)
        elif event.key == pygame.K_DOWN:
            self.current_card.navigate(1)
        elif event.key == pygame.K_RETURN:
            selected_item = self.current_card.items[self.current_card.selected_index]
            selected_item.callback()


def run_menu() -> None:
    pygame.init()
    pygame.display.set_caption("Pirate Game Menu")

    menu = GameMenu(pygame.display.set_mode((940, 720)))
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            menu.handle_event(event)

        menu.display()
        clock.tick(60)


if __name__ == "__main__":
    run_menu()
