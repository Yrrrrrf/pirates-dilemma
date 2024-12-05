from typing import Dict, Tuple
import random
import sys
import pygame

from layout.card import Card
from layout.menu import MenuTheme
from project import set_app_lang
from project.settings.lang import Language
from tools import AssetManager

class MenuManager:
    def __init__(self, surface: pygame.Surface, run_fn: callable) -> None:
        print("Initializing MenuManager...")
        self.run: callable = run_fn
        self.surface = surface
        self.theme = MenuTheme()
        self.background = self._load_background()
        self.current_card = None
        self.cards = self._initialize_cards()
        self.show_card('main')
        print("MenuManager initialized successfully")

    def _load_background(self) -> pygame.Surface:
        try:
            img_name = f"some-pirate-{random.randint(0, 2):02d}.png"
            bg_image = pygame.image.load(AssetManager.get_image(img_name))
            bg_scaled = pygame.transform.scale(bg_image, self.surface.get_size())
            print(f"Background loaded: {img_name}")
            return bg_scaled
        except pygame.error as e:
            print(f"Error loading background: {e}")
            bg = pygame.Surface(self.surface.get_size())
            bg.fill((0, 0, 0))
            return bg

    def _initialize_cards(self) -> Dict[str, Card]:
        print("Initializing menu cards...")
        cards: Dict[str, Card] = {}

        # Initialize main card
        main_card = Card(self.surface, self.theme, "menu_title")
        main_card.set_background(self.background)
        main_card.add_item("start", (0, 0), self.run)  # Using the run callback directly
        main_card.add_item("options", (0, 0), lambda: self.show_card('options'))
        main_card.add_item("exit", (0, 0), lambda: sys.exit())
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
            lang_card.add_item(lang.name.lower(), (0, 0), lambda l=lang: self._change_language(l))
        lang_card.add_item("back", (0, 0), lambda: self.show_card('options'))
        cards['language'] = lang_card

        print("Menu cards initialized")
        return cards

    def _change_language(self, lang: Language) -> None:
        """Handle language change and return to options menu"""
        set_app_lang(lang)
        self.show_card('options')

    def show_card(self, card_name: str) -> None:
        print(f"Showing card: {card_name}")
        if card_name in self.cards:
            self.current_card = self.cards[card_name]
            print(f"Current card set to: {card_name}")
        else:
            print(f"Card not found: {card_name}")

    def update_hover_states(self, pos: Tuple[int, int]) -> None:
        """Update hover states for the current card"""
        if self.current_card:
            self.current_card.update_hover_states(pos)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the current menu state"""
        if self.current_card:
            # Clear the surface first
            surface.fill((0, 0, 0))
            
            # Draw background
            if self.background:
                surface.blit(self.background, (0, 0))
            
            # Display the current card
            self.current_card.display()
        else:
            print("Warning: No card to display")

    def handle_keydown(self, event: pygame.event.Event) -> None:
        """Handle keyboard navigation"""
        if not self.current_card:
            return

        match event.key:
            case pygame.K_ESCAPE:
                if self.current_card != self.cards['main']:
                    self.show_card('main')
            case pygame.K_UP:
                self.current_card.navigate(-1)
            case pygame.K_DOWN:
                self.current_card.navigate(1)
            case pygame.K_RETURN:
                if 0 <= self.current_card.selected_index < len(self.current_card.items):
                    self.current_card.items[self.current_card.selected_index].callback()

    def handle_click(self, pos: Tuple[int, int]) -> None:
        """Handle mouse clicks"""
        if self.current_card:
            self.current_card.handle_click(pos)

    def resize(self, size: Tuple[int, int]) -> None:
        """Handle window resizing"""
        print(f"Resizing menu to: {size}")
        # Reload and rescale background
        self.background = pygame.transform.scale(self.background, size)
        # Update all cards with new background
        for card in self.cards.values():
            card.set_background(self.background)
