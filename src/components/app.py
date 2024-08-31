import os
from pydantic import BaseModel, Field
import pygame

# todo: create some macro that allow some custom 'import *' from any python module
# todo:   - this to import particular keys from pygame
# from pygame import K_\*

from constants import GameInfo
from components.game_state import GameState
from utils.resource_loader import AssetManager
from components.engine import Engine

class App(BaseModel):
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
        self.engine = Engine(game_state=GameState())

        # * Set the display mode based on the settings
        self.display_surface = self.set_display_mode()
        self.engine.initialize_display(self.display_surface)

        print(f"\033[94mApp Running\033[0m")

    def set_display_mode(self) -> pygame.Surface:
        match self.engine.game_state.settings.fullscreen:
            case True: return pygame.display.set_mode((0, 0), pygame.NOFRAME)
                # from pygame._sdl2.video import Window
                # win = Window.from_display_module()
                # print(f"\033[94mwin: {win.position}\033[0m")
            case False: return pygame.display.set_mode(self.engine.game_state.settings.get_screen_size(), pygame.RESIZABLE)

    def _toggle_fullscreen(self):
        self.engine.game_state.settings.fullscreen ^= True  # xor the fullscreen setting
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

        # todo: Impl the Settings.weight and Settings.height constraints
        # *  width = 640..=3840 (1080 default)
        # * height = 480..=2160 (720 default)
        # self.engine.game_state.settings.width
        # self.engine.game_state.settings.height


    def run(self) -> None:
        try:
            while self.running:
                dt: float = self.clock.tick(self.engine.game_state.settings.fps) / 1000.0
                self.handle_events()  # Handle events before updating the engine
                self.engine.run(dt)   # Update the engine with the delta time
                
                match pygame.get_init():  # Check if pygame is initialized
                    case True: pygame.display.flip()  # Update the display if it is
                    case False: self.running = False  # Stop the loop if pygame is not
        finally:  # Ensure cleanup is done even if an exception occurs
            if pygame.get_init(): pygame.quit()
