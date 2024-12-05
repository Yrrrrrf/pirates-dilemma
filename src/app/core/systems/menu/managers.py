# app/core/systems/menu/managers.py
from typing import Dict, Optional, Callable
import pygame
from pygame import Surface

from app import State

from .base import UITheme, MenuItem, MenuContainer
from project import menu_lang_manager

class CardManager:
    """Manages menu cards for the main menu system"""
    def __init__(self, surface: Surface, theme: UITheme):
        self.surface = surface
        self.theme = theme
        self.cards: Dict[str, MenuContainer] = {}
        self.current_card: Optional[str] = None
        self._setup_cards()

    def _setup_cards(self) -> None:
        """Initialize default cards"""
        self.add_card('main')
        self.add_card('options')
        self.add_card('pause')

    def add_card(self, name: str) -> MenuContainer:
        """Add a new card to the manager"""
        card = MenuContainer(self.theme)
        self.cards[name] = card
        return card

    def show_card(self, name: str) -> None:
        """Show a specific card"""
        if name in self.cards:
            self.current_card = name

    def handle_input(self, event: pygame.event.Event) -> bool:
        """Handle all input for current card"""
        if not self.current_card:
            return False

        current = self.cards[self.current_card]
        if event.type == pygame.MOUSEBUTTONDOWN:
            return current.handle_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            current.handle_hover(event.pos)
            return True
        elif event.type == pygame.KEYDOWN:
            return current.handle_key(event)
        return False

    def render(self) -> None:
        """Render current card"""
        if self.current_card and self.current_card in self.cards:
            self.cards[self.current_card].render(self.surface)

class UIManager:
    """Manages all UI elements and menus during gameplay"""
    def __init__(self, surface: Surface, theme: UITheme):
        self.surface = surface
        self.theme = theme
        self.menus: Dict[str, MenuContainer] = {}
        self._setup_menus()

    def _setup_menus(self) -> None:
        """Initialize default UI menus"""
        self.add_menu('inventory')
        self.add_menu('character')
        self.add_menu('quest_log')
        # Add other default menus...

    def add_menu(self, name: str) -> MenuContainer:
        """Add a new menu to the manager"""
        menu = MenuContainer(self.theme)
        self.menus[name] = menu
        return menu

    def toggle_menu(self, name: str) -> None:
        """Toggle visibility of a specific menu"""
        if name in self.menus:
            menu = self.menus[name]
            menu.is_visible = not menu.is_visible

    def handle_input(self, event: pygame.event.Event) -> bool:
        """Handle input for all visible menus"""
        handled = False
        for menu in self.menus.values():
            if not menu.is_visible:
                continue
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                handled |= menu.handle_click(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                menu.handle_hover(event.pos)
                handled = True
            elif event.type == pygame.KEYDOWN:
                handled |= menu.handle_key(event)
                
        return handled

    def render(self) -> None:
        """Render all visible menus"""
        for menu in self.menus.values():
            if menu.is_visible:
                menu.render(self.surface)

# Example usage in your Game class:
class GameMenuSystem:
    """Coordinates all menu systems in the game"""
    def __init__(self, surface: Surface):
        self.theme = UITheme()  # Create default theme
        self.card_manager = CardManager(surface, self.theme)
        self.ui_manager = UIManager(surface, self.theme)
        
        self._setup_menu_system()

    def _setup_menu_system(self) -> None:
        """Setup the complete menu system"""
        # Setup main menu cards
        main_card = self.card_manager.cards['main']
        main_card.add_item(MenuItem('new_game', self.theme, self._start_new_game))
        main_card.add_item(MenuItem('options', self.theme, lambda: self.card_manager.show_card('options')))
        main_card.add_item(MenuItem('exit', self.theme, self._exit_game))

        # Setup options card
        options_card = self.card_manager.cards['options']
        options_card.add_item(MenuItem('video', self.theme, self._show_video_options))
        options_card.add_item(MenuItem('audio', self.theme, self._show_audio_options))
        options_card.add_item(MenuItem('back', self.theme, lambda: self.card_manager.show_card('main')))

        # Setup pause menu
        pause_card = self.card_manager.cards['pause']
        pause_card.add_item(MenuItem('resume', self.theme, self._resume_game))
        pause_card.add_item(MenuItem('options', self.theme, lambda: self.card_manager.show_card('options')))
        pause_card.add_item(MenuItem('quit', self.theme, self._quit_to_main))

        # Setup in-game UI
        inventory_menu = self.ui_manager.menus['inventory']
        inventory_menu.add_item(MenuItem('close', self.theme, lambda: self.ui_manager.toggle_menu('inventory')))
        # Add other inventory items...

    def handle_input(self, event: pygame.event.Event) -> bool:
        """Handle input for appropriate menu system based on game state"""
        if self.game_state == State.MENU:
            return self.card_manager.handle_input(event)
        else:
            return self.ui_manager.handle_input(event)

    def render(self) -> None:
        """Render appropriate menu system based on game state"""
        if self.game_state == State.MENU:
            self.card_manager.render()
        else:
            self.ui_manager.render()

    # Callback methods
    def _start_new_game(self) -> None: pass
    def _exit_game(self) -> None: pass
    def _show_video_options(self) -> None: pass
    def _show_audio_options(self) -> None: pass
    def _resume_game(self) -> None: pass
    def _quit_to_main(self) -> None: pass
