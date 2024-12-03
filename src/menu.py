# stdlib
import random
import sys
from typing import Dict
# 3rd party
import pygame
from pygame import Surface
# local
from main import main  # * App entry point (main game loop)
from utils import AssetManager
from layout.card import Card
from layout.menu import MenuTheme, menu_lang_manager
from project.settings.lang import Language


class GameMenu:
    def __init__(self, screen: Surface):
        self.screen = screen
        self.theme = MenuTheme()
        self.background = self._load_background()
        self.current_card = None
        self.cards = self._initialize_cards()
        self.show_card('main')

        # set icon
        icon = pygame.image.load(AssetManager.get_image("pirate-hat.png"))
        pygame.display.set_icon(icon)


    def _load_background(self) -> Surface:
        try:
            img_name = f"some-pirate-{random.randint(0, 2):02d}.png"
            bg_image = pygame.image.load(AssetManager.get_image(img_name))
            return pygame.transform.scale(bg_image, self.screen.get_size())
        except pygame.error:
            bg = Surface(self.screen.get_size())
            bg.fill((0, 0, 0))
            return bg

    def _initialize_cards(self) -> Dict[str, Card]:
        cards: Dict[str, Card] = {}

        # Initialize main card
        main_card = Card(self.screen, self.theme, "menu_title")
        main_card.set_background(self.background)
        main_card.add_item("start", (0, 0), lambda: main())
        main_card.add_item("options", (0, 0), lambda: self.show_card('options'))
        main_card.add_item("exit", (0, 0), lambda: sys.exit())
        cards['main'] = main_card

        # Initialize options card
        options_card = Card(self.screen, self.theme, "settings")
        options_card.set_background(self.background)
        options_card.add_item("spanish", (0, 0), lambda: self._change_lang(Language.SPANISH))
        options_card.add_item("english", (0, 0), lambda: self._change_lang(Language.ENGLISH))
        options_card.add_item("back", (0, 0), lambda: self.show_card('main'))
        cards['options'] = options_card

        return cards

    def _change_lang(self, lang: Language) -> None:
        menu_lang_manager.language = lang
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

        match event.type:
            case pygame.KEYDOWN: self._handle_keydown(event)
            case pygame.MOUSEBUTTONDOWN if event.button == 1: self.current_card.handle_click(event.pos)
            case pygame.MOUSEMOTION: self.current_card.update_hover_states(event.pos)

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        match event.key:
            case pygame.K_ESCAPE if self.current_card != self.cards['main']: self.show_card('main')
            case pygame.K_UP: self.current_card.navigate(-1)
            case pygame.K_DOWN: self.current_card.navigate(1)
            case pygame.K_RETURN:
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
                pygame.quit()  # * Quit the game
                sys.exit()  # * Exit the program
            menu.handle_event(event)

        menu.display()
        clock.tick(60)


if __name__ == "__main__":
    run_menu()
