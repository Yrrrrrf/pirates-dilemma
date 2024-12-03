from pydantic import BaseModel, Field
import pygame
from project import AppData
from project.settings.constants import GameInfo  # import global variables
from utils import AssetManager
from app.core.engine import Engine

class App(BaseModel):
    app_data: AppData = Field(...)
    display_surface: pygame.Surface = Field(default=None)
    running: bool = Field(default=True)
    engine: Engine = Field(default=None)
    clock: pygame.time.Clock = Field(default_factory=pygame.time.Clock)

    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self, __context) -> None:
        """Initialize pygame and setup the application after Pydantic validation"""
        pygame.init()

        pygame.display.set_caption(f"{GameInfo.NAME} {GameInfo.VERSION}")
        pygame.display.set_icon(pygame.image.load(AssetManager.get_image("pirate-hat.png")))

        self.engine = Engine()

        # Set the display mode based on the settings
        self.display_surface = self.set_display_mode()
        self.engine.initialize_display(self.display_surface)

        print(f"\033[94mApp Running\033[0m")

    def set_display_mode(self) -> pygame.Surface:
        if self.app_data.settings.fullscreen:
            return pygame.display.set_mode((0, 0), pygame.NOFRAME)
        return pygame.display.set_mode(
            self.app_data.settings.get_screen_size(), 
            pygame.RESIZABLE
        )

    def _toggle_fullscreen(self):
        self.app_data.settings.fullscreen ^= True  # xor the fullscreen setting
        self.display_surface = self.set_display_mode()  # update the display mode
        self.engine.initialize_display(self.display_surface)  # Reinitialize the display for the engine

    def handle_events(self) -> None:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT: 
                    self.running = False
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE: self.running = False
                        case pygame.K_F1: print("Impl: F1 to toggle editor mode")
                        case pygame.K_F11: self._toggle_fullscreen()
                        case pygame.K_i: self.engine.ui.toggle_inventory()
                        case _: pass

    def run(self) -> None:
        while self.running:
            dt: float = self.clock.tick(self.app_data.settings.fps) / 1000.0
            self.handle_events()  # Handle events before updating the engine
            self.engine.run(dt)   # Update the engine with the delta time

            match pygame.get_init():
                case True: pygame.display.flip()
                case False: self.running = False

        pygame.quit()
