from functools import partial
from pydantic import BaseModel, Field
import pygame
from project import AppData
from project.settings.constants import GameInfo
from utils import AssetManager
from app.core.engine import Engine
from enum import Enum
from app.core.menu_manager import MenuManager  # Import your menu manager



class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"


class App(BaseModel):
    app_data: AppData = Field(...)
    display_surface: pygame.Surface = Field(default=None)
    running: bool = Field(default=True)
    engine: Engine = Field(default=None)
    clock: pygame.time.Clock = Field(default_factory=pygame.time.Clock)
    game_state: GameState = Field(default=GameState.MENU)
    menu: MenuManager = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self, __context) -> None:
        """Initialize pygame and setup the application after Pydantic validation"""
        pygame.init()
        pygame.display.set_caption(f"{GameInfo.NAME} {GameInfo.VERSION}")
        pygame.display.set_icon(pygame.image.load(AssetManager.get_image("pirate-hat.png")))
        
        # Initialize display first
        self.display_surface = self.set_display_mode()
        
        # Then initialize menu and engine
        self.menu = MenuManager(self.display_surface, lambda: setattr(self, 'game_state', GameState.PLAYING))
        self.engine = Engine()
        self.engine.initialize_display(self.display_surface)
        
        print(f"\033[94mApp Running\033[0m")

    def set_display_mode(self) -> pygame.Surface:
        if self.app_data.settings.fullscreen: return pygame.display.set_mode((0, 0), pygame.NOFRAME)
        return pygame.display.set_mode(self.app_data.settings.get_screen_size(), pygame.RESIZABLE)

    def _toggle_fullscreen(self):
        self.app_data.settings.fullscreen ^= True
        self.display_surface = self.set_display_mode()
        self.engine.initialize_display(self.display_surface)
        if self.menu:
            self.menu = MenuManager(self.display_surface, lambda: setattr(self, 'game_state', GameState.PLAYING))


    def _toggle_pause(self):
        match self.game_state:
            case GameState.PAUSED: self.game_state = GameState.PLAYING
            case GameState.PLAYING: self.game_state = GameState.PAUSED
            case _: print("Invalid game state!!!")

    def handle_events(self) -> None:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT: self.running = False
                case pygame.KEYDOWN:
                    # * General app keydown events!
                    match event.key:
                        case pygame.K_ESCAPE: self._toggle_pause()
                        case pygame.K_F11: self._toggle_fullscreen()
                    # * Specific keydown events for each game state
                    match self.game_state:
                        case GameState.MENU: self.menu.handle_keydown(event)
                        case GameState.PLAYING: self.engine.handle_keydown(event)
                        case GameState.PAUSED: pass  # todo: Add some pause menu keydown events here...
                        # todo: Add more game states here...
                case pygame.MOUSEBUTTONDOWN:
                    match self.game_state:
                        case GameState.MENU: self.menu.handle_click(event.pos)
                        case GameState.PLAYING: self.engine.handle_click(event)                        
                case pygame.MOUSEMOTION: pass
                    # if self.game_state == GameState.MENU: self.menu.update_hover_states(event.pos)

                case pygame.VIDEORESIZE:
                    self.display_surface = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                    self.engine.initialize_display(self.display_surface)
                    if self.menu: self.menu = MenuManager(self.display_surface, lambda: setattr(self, 'game_state', GameState.PLAYING))

    def _draw_pause_overlay(self):
        # todo: Check this cool effect! (Overlay with transparency)

        # todo: Add this effecto to the 'Wasted' screen... (Game Over)
        overlay = pygame.Surface(self.display_surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 10))
        font = pygame.font.Font(None, 64)
        text = font.render("PAUSED", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.display_surface.get_width() // 2,
                                        self.display_surface.get_height() // 2))
        overlay.blit(text, text_rect)
        self.display_surface.blit(overlay, (0, 0))

    def run(self) -> None:
        while self.running:
            dt: float = self.clock.tick(self.app_data.settings.fps) / 1000.0
            self.handle_events()

            match self.game_state:
                case GameState.MENU:
                    self.menu.draw(self.display_surface)  # Changed from display() to draw()
                case GameState.PLAYING:
                    self.engine.run(dt)
                case GameState.PAUSED:
                    self._draw_pause_overlay()

            pygame.display.flip()

        pygame.quit()