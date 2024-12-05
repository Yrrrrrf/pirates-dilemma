from pydantic import BaseModel, Field
import pygame
from app.core.systems.menu.start import StartMenuManager
from project import AppData
from project.settings.constants import GameInfo
from tools import AssetManager
from tools.console import *
from app.core.engine import Engine
from enum import Enum


class State(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"

class App(BaseModel):
    app_data: AppData = Field(...)
    display_surface: pygame.Surface = Field(default=None)
    running: bool = Field(default=True)
    engine: Engine = Field(default=None)
    clock: pygame.time.Clock = Field(default_factory=pygame.time.Clock)
    game_state: State = Field(default=State.MENU)
    menu: StartMenuManager = Field(default=None)

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
        self.menu = StartMenuManager(self.display_surface, self.new_game)  # Pass the method directly
        # self._init_pause_menu()

        print(f"\033[94mApp Running\033[0m")

    def init_engine(self):
        """Initialize or reinitialize the game engine"""
        if self.engine:
            del self.engine
            self.engine = None
        
        self.engine = Engine()
        self.engine.initialize(self.display_surface)
        print(f"\033[92mEngine Initialized\033[0m")

    def new_game(self):
        """Start a new game, ensuring clean state"""
        print("Initializing new game...")
        self.init_engine()  # Reinitialize engine
        self.game_state = State.PLAYING
        print(f"Game state changed to: {self.game_state}")

    def set_display_mode(self) -> pygame.Surface:
        if self.app_data.settings.fullscreen:
            return pygame.display.set_mode((0, 0), pygame.NOFRAME)
        return pygame.display.set_mode(self.app_data.settings.get_screen_size(), pygame.RESIZABLE)

    def _toggle_fullscreen(self):
        self.app_data.settings.fullscreen ^= True
        self.display_surface = self.set_display_mode()
        # todo: Def some more generic 'init_components' fn
        # # Reinitialize components with new display surface
        # if self.engine: self.engine.initialize_display(self.display_surface)
        # if self.menu: self.menu = MenuManager(self.display_surface, self.new_game)
        # if self.pause_menu: self._init_pause_menu()

    def _toggle_pause(self):
        match self.game_state:
            case State.PAUSED:
                print(f"{bold(green('\tGame resumed'))}")
                self.game_state = State.PLAYING
            case State.PLAYING: 
                print(f"{bold(blue('\tGame paused'))}")
                self.game_state = State.PAUSED

    def handle_keydown(self, event: pygame.event.Event) -> None:
        match event.key:
            case pygame.K_ESCAPE: self._toggle_pause()
            case pygame.K_F11: self._toggle_fullscreen()
        match self.game_state:
            case State.MENU: self.menu.handle_keydown(event)
            case State.PLAYING: self.engine.handle_keydown(event)

    def handle_click(self, event: pygame.event.Event) -> None:
        pos = event.pos
        match self.game_state:
            case State.MENU: 
                self.menu.handle_click(pos)
                self.menu.handle_mousemotion(pos)
                self.menu.handle_mouseup(pos)
            case State.PLAYING: self.engine.handle_click(pos)

    # def handle_hover(self, event: pygame.event.Event) -> None:
    #     pos = event.pos
    #     match self.game_state:
    #         case State.MENU: self.menu.update_hover_states(pos)

    # def handle_resize(self, event: pygame.event.Event) -> None:
    #     self.display_surface = pygame.display.set_mode(event.size, pygame.RESIZABLE)
    #     if self.engine: self.engine.initialize(self.display_surface)
    #     if self.menu: self.menu = MenuManager(self.display_surface, self.new_game)

    def handle_events(self, event: pygame.event.Event) -> None:
        match event.type:
            case pygame.QUIT: self.running = False
            case pygame.KEYDOWN: self.handle_keydown(event)
            # case pygame.MOUSEBUTTONDOWN: self.handle_click(event)
            # case pygame.MOUSEMOTION: self.handle_hover(event)
            # case pygame.VIDEORESIZE: self.handle_resize(event)

    def run(self) -> None:
        while self.running:
            dt: float = self.clock.tick(self.app_data.settings.fps) / 1000.0
            self.handle_events(pygame.event.poll())  # * Handle events in the queue
            match self.game_state:  # * Match the current game state
                case State.MENU:
                    self.menu.draw(self.display_surface)
                case State.PLAYING:
                    self.engine.update(dt)
                    self.engine.run()

            pygame.display.flip()

        pygame.quit()
