from pydantic import BaseModel, Field
import pygame
from app.core.menu.pause import PauseMenu
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
    pause_menu: PauseMenu = Field(default=None)

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
        self.menu = MenuManager(self.display_surface, self.init_new_game)  # Pass the method directly
        self._init_pause_menu()

        print(f"\033[94mApp Running\033[0m")

    def _init_pause_menu(self):
        """Initialize the pause menu with necessary callbacks"""
        self.pause_menu = PauseMenu(
            self.display_surface,
            resume_callback=lambda: setattr(self, 'game_state', GameState.PLAYING),
            exit_callback=self.return_to_menu  # Use new method for returning to menu
        )

    def init_engine(self):
        """Initialize or reinitialize the game engine"""
        if self.engine:
            del self.engine
            self.engine = None
        
        self.engine = Engine()
        self.engine.initialize_display(self.display_surface)
        print(f"\033[92mEngine Initialized\033[0m")

    def init_new_game(self):
        """Start a new game, ensuring clean state"""
        print("Initializing new game...")
        self.init_engine()  # Reinitialize engine
        self.game_state = GameState.PLAYING
        print(f"Game state changed to: {self.game_state}")

    def return_to_menu(self):
        """Safely return to the main menu"""
        print("Returning to menu...")
        if self.engine:
            del self.engine
            self.engine = None
        self.game_state = GameState.MENU
        print(f"Game state changed to: {self.game_state}")

    def set_display_mode(self) -> pygame.Surface:
        if self.app_data.settings.fullscreen:
            return pygame.display.set_mode((0, 0), pygame.NOFRAME)
        return pygame.display.set_mode(self.app_data.settings.get_screen_size(), pygame.RESIZABLE)

    def _toggle_fullscreen(self):
        self.app_data.settings.fullscreen ^= True
        self.display_surface = self.set_display_mode()
        
        # Reinitialize components with new display surface
        if self.engine:
            self.engine.initialize_display(self.display_surface)
        if self.menu:
            self.menu = MenuManager(self.display_surface, self.init_new_game)
        if self.pause_menu:
            self._init_pause_menu()

    def _toggle_pause(self):
        match self.game_state:
            case GameState.PAUSED:
                self.game_state = GameState.PLAYING
            case GameState.PLAYING:
                # Capture the game screen before entering pause state
                if hasattr(self.pause_menu, 'capture_game_screen'):
                    self.pause_menu.capture_game_screen()
                self.game_state = GameState.PAUSED

    def handle_events(self) -> None:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                
                case pygame.KEYDOWN:
                    # Global keydown events
                    match event.key:
                        case pygame.K_ESCAPE: self._toggle_pause()
                        case pygame.K_F11: self._toggle_fullscreen()

                    # State-specific keydown events
                    match self.game_state:
                        case GameState.MENU: self.menu.handle_keydown(event)
                        case GameState.PLAYING: self.engine.handle_keydown(event)
                        case GameState.PAUSED: self.pause_menu.handle_keydown(event)
                
                case pygame.MOUSEBUTTONDOWN:
                    match self.game_state:
                        case GameState.MENU: self.menu.handle_click(event.pos)
                        case GameState.PLAYING: self.engine.handle_click(event)
                        case GameState.PAUSED: self.pause_menu.handle_click(event.pos)
                
                case pygame.MOUSEMOTION:
                    match self.game_state:
                        case GameState.PAUSED: self.pause_menu.update_hover_states(event.pos)
                        # case GameState.MENU: self.menu.update_hover_states(event.pos)
                
                case pygame.VIDEORESIZE:
                    self.display_surface = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                    if self.engine:
                        self.engine.initialize_display(self.display_surface)
                    if self.menu:
                        self.menu = MenuManager(self.display_surface, self.init_new_game)
                    if self.pause_menu:
                        self._init_pause_menu()

    def run(self) -> None:
        while self.running:
            dt: float = self.clock.tick(self.app_data.settings.fps) / 1000.0
            self.handle_events()

            match self.game_state:
                case GameState.MENU:
                    self.menu.draw(self.display_surface)
                case GameState.PLAYING:
                    if self.engine:
                        self.engine.run(dt)
                case GameState.PAUSED:
                    self.pause_menu.draw()

            pygame.display.flip()

        pygame.quit()