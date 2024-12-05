# app/core/systems/menu/base.py
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Protocol, Tuple, TypeVar, Callable
from pygame import Surface, Rect
import pygame

from project import menu_lang_manager
from project.theme.ui import UITheme

class Renderable(Protocol):
    """Protocol for any UI element that can be rendered"""
    def render(self, surface: Surface) -> None: ...

class Interactable(Protocol):
    """Protocol for any UI element that can be interacted with"""
    def handle_click(self, pos: Tuple[int, int]) -> bool: ...
    def handle_hover(self, pos: Tuple[int, int]) -> None: ...
    def handle_key(self, event: pygame.event.Event) -> bool: ...


class UIElement(ABC):
    """Base class for all UI elements"""
    def __init__(self, theme: UITheme):
        self.theme = theme
        self.is_visible = True
        self.is_enabled = True
        self.rect: Optional[Rect] = None

    @abstractmethod
    def render(self, surface: Surface) -> None: pass

    @abstractmethod
    def handle_click(self, pos: Tuple[int, int]) -> bool: pass

    @abstractmethod
    def handle_hover(self, pos: Tuple[int, int]) -> None: pass

    @abstractmethod
    def handle_key(self, event: pygame.event.Event) -> bool: pass

class MenuItem(UIElement):
    """Base class for menu items"""
    def __init__(self, 
                 text_key: str,
                 theme: UITheme,
                 callback: Callable[[], None],
                 position: Tuple[int, int] = (0, 0)):
        super().__init__(theme)
        self.text_key = text_key
        self.callback = callback
        self.position = position
        self.is_hovered = False
        self.is_selected = False

    @property
    def text(self) -> str:
        return menu_lang_manager.get_text(self.text_key)

    def render(self, surface: Surface) -> None:
        if not self.is_visible:
            return
        # Implementation for rendering menu item...

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        if not self.is_enabled or not self.is_visible:
            return False
        if self.rect and self.rect.collidepoint(pos):
            self.callback()
            return True
        return False

    def handle_hover(self, pos: Tuple[int, int]) -> None:
        if not self.is_enabled or not self.is_visible:
            return
        self.is_hovered = bool(self.rect and self.rect.collidepoint(pos))

    def handle_key(self, event: pygame.event.Event) -> bool:
        if not self.is_enabled or not self.is_visible:
            return False
        return False

T = TypeVar('T', bound=MenuItem)

class MenuContainer(Generic[T]):
    """Base class for menu containers (like cards or panels)"""
    def __init__(self, theme: UITheme):
        self.theme = theme
        self.items: List[T] = []
        self.selected_index = -1
        self.background: Optional[Surface] = None

    def add_item(self, item: T) -> None:
        self.items.append(item)
        if self.selected_index < 0:
            self.selected_index = 0

    def navigate(self, direction: int) -> None:
        """Navigate through menu items"""
        if not self.items:
            return
        self.selected_index = (self.selected_index + direction) % len(self.items)
        for item in self.items:
            item.is_selected = False
        self.items[self.selected_index].is_selected = True

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Handle click events for all items"""
        return any(item.handle_click(pos) for item in self.items if item.is_visible)

    def handle_hover(self, pos: Tuple[int, int]) -> None:
        """Handle hover events for all items"""
        for item in self.items:
            if item.is_visible:
                item.handle_hover(pos)

    def handle_key(self, event: pygame.event.Event) -> bool:
        """Handle key events"""
        if event.key == pygame.K_UP:
            self.navigate(-1)
            return True
        elif event.key == pygame.K_DOWN:
            self.navigate(1)
            return True
        elif event.key == pygame.K_RETURN and 0 <= self.selected_index < len(self.items):
            self.items[self.selected_index].callback()
            return True
        return False
