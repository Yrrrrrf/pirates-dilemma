import os
from pydantic import BaseModel, Field
import pygame

# todo: Create some macro that allow some custom 'import *' from any python module
# todo:   - this to import particular keys from pygame
# from pygame import K_\*

from constants import GameInfo
from components.game_state import AppData, app_data
from utils.resource_loader import AssetManager
from components.engine import Engine

class App(BaseModel):
    app_data: AppData = Field(default=app_data)
    display_surface: pygame.Surface = Field(default=None)
    running: bool = Field(default=True)
    engine: Engine = Field(default=None)
    clock: pygame.time.Clock = Field(default_factory=pygame.time.Clock)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        pygame.init()

        # * Set the window title and icon
        pygame.display.set_caption(f"{GameInfo.NAME} {GameInfo.VERSION}")
        pygame.display.set_icon(pygame.image.load(AssetManager.get_image("pirate-hat.png")))

        # * Init game engine
        self.engine = Engine()

        # * Set the display mode based on the settings
        self.display_surface = self.set_display_mode()
        self.engine.initialize_display(self.display_surface)

        print(f"\033[94mApp Running\033[0m")

    def set_display_mode(self) -> pygame.Surface:
        match self.app_data.settings.fullscreen:
            case True: return pygame.display.set_mode((0, 0), pygame.NOFRAME)
                # from pygame._sdl2.video import Window
                # win = Window.from_display_module()
                # print(f"\033[94mwin: {win.position}\033[0m")
            case False: return pygame.display.set_mode(self.app_data.settings.get_screen_size(), pygame.RESIZABLE)

    def _toggle_fullscreen(self):
        self.app_data.settings.fullscreen ^= True  # xor the fullscreen setting
        self.display_surface = self.set_display_mode()  # update the display mode
        self.engine.initialize_display(self.display_surface)  # Reinitialize the display for the engine


    def handle_events(self) -> None:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT: self.running = False
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE: self.running = False
                        case pygame.K_F1: print("Impl: F1 to toggle editor mode")
                        case pygame.K_F11: self._toggle_fullscreen()
                        case _: pass

    def run(self) -> None:
        try:
            while self.running:
                dt: float = self.clock.tick(self.app_data.settings.fps) / 1000.0
                self.handle_events()  # Handle events before updating the engine
                self.engine.run(dt)   # Update the engine with the delta time
                
                match pygame.get_init():  # Check if pygame is initialized
                    case True: pygame.display.flip()  # Update the display if it is
                    case False: self.running = False  # Stop the loop if pygame is not
        finally:  # Ensure cleanup is done even if an exception occurs
            if pygame.get_init(): pygame.quit()
