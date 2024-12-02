from typing import Callable, List, Tuple
from pygame import Surface

from layout.menu import MenuItem, MenuRenderer, MenuTheme, menu_lang_manager


class Card:
    def __init__(self, screen: Surface, theme: MenuTheme, title_key: str):
        self.screen = screen
        self.theme = theme
        self.title_key = title_key  # Store the key instead of the title
        self.items: List[MenuItem] = []
        self.selected_index = 0
        self.renderer = MenuRenderer(screen, theme)
        self.background_surface = None

    @property
    def title(self) -> str: return menu_lang_manager.get_text(self.title_key)

    def set_background(self, surface: Surface) -> None: self.background_surface = surface

    def add_item(self, text_key: str, position: Tuple[int, int], callback: Callable[[], None]) -> None:
        self.items.append(MenuItem(text_key, position, callback))

    def display(self) -> None:
        if self.background_surface: self.screen.blit(self.background_surface, (0, 0))        
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
        for item in self.items: item.is_hovered = False

    def handle_click(self, pos: Tuple[int, int]) -> None:
        for item in self.items:
            if item.handle_click(pos):
                item.callback()
                break

    def update_hover_states(self, mouse_pos: Tuple[int, int]) -> None:
        for item in self.items: item.update_hover(mouse_pos)
