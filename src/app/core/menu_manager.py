from typing import Dict, Tuple
import random
import sys

import pygame

from layout.card import Card
from layout.menu import MenuTheme
from project import set_app_lang
from project.settings.lang import Language
from utils import AssetManager

class MenuManager:
    def __init__(self, surface: pygame.Surface, run_fn: callable) -> None:
        self.run: callable = run_fn
        self.surface = surface
        self.theme = MenuTheme()
        self.background = self._load_background()
        self.current_card = None
        self.cards = self._initialize_cards()
        self.show_card('main')

    def _load_background(self) -> pygame.Surface:
        try:
            img_name = f"some-pirate-{random.randint(0, 2):02d}.png"
            bg_image = pygame.image.load(AssetManager.get_image(img_name))
            return pygame.transform.scale(bg_image, self.surface.get_size())
        except pygame.error:
            bg = pygame.Surface(self.surface.get_size())
            bg.fill((0, 0, 0))
            return bg

    def _initialize_cards(self) -> Dict[str, Card]:
        cards: Dict[str, Card] = {}

        # Initialize main card
        main_card = Card(self.surface, self.theme, "menu_title")
        main_card.set_background(self.background)
        main_card.add_item("start", (0, 0), lambda: self.run())
        main_card.add_item("options", (0, 0), lambda: self.show_card('options'))
        # main_card.add_item("options", (0, 0), lambda: print("Options not implemented yet!"))
        main_card.add_item("exit", (0, 0), sys.exit)
        cards['main'] = main_card

        # Initialize options card
        options_card = Card(self.surface, self.theme, "settings")
        options_card.set_background(self.background)
        options_card.add_item("language", (0, 0), lambda: self.show_card('language'))
        options_card.add_item("back", (0, 0), lambda: self.show_card('main'))
        cards['options'] = options_card

        # Initialize language card
        lang_card = Card(self.surface, self.theme, "language")
        lang_card.set_background(self.background)
        for lang in Language:
            lang_card.add_item(lang.name.lower(), (0, 0), lambda l=lang: set_app_lang(l))
        lang_card.add_item("back", (0, 0), lambda: self.show_card('options'))
        cards['language'] = lang_card

        return cards

    def show_card(self, card_name: str) -> None:
        if card_name in self.cards:
            self.current_card = self.cards[card_name]

    def resize(self, size: Tuple[int, int]) -> None:
        """Handle window resize"""
        self.background = pygame.transform.scale(self.background, size)
        for card in self.cards.values():
            card.set_background(self.background)

    def update(self, dt: float) -> None:
        """Update menu state"""
        if self.current_card:
            mouse_pos = pygame.mouse.get_pos()
            self.current_card.update_hover_states(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the current menu card"""
        if self.current_card:
            surface.fill((0, 0, 0))
            self.current_card.display()

    def handle_keydown(self, event: pygame.event.Event) -> None:
        """Handle keyboard input for menu navigation"""
        match self.current_card:
            case None: 
                return
                
            case card:
                match event.key:
                    case pygame.K_ESCAPE if card != self.cards['main']:
                        self.show_card('main')
                    case pygame.K_UP:
                        card.navigate(-1)
                    case pygame.K_DOWN:
                        card.navigate(1)
                    case pygame.K_RETURN if 0 <= card.selected_index < len(card.items):
                        card.items[card.selected_index].callback()

    def handle_click(self, pos: Tuple[int, int]) -> None:
        """Handle mouse clicks in the menu"""
        match self.current_card:
            case None: pass
            case card: card.handle_click(pos)
