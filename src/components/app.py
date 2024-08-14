from dataclasses import dataclass, field
from typing import Optional
import pygame

# Own imports
from globals import GameInfo, Assets, game_state
from components.editor import Editor
from components.engine import Engine

@dataclass
class App:
    """
    This class contains the main logic for the application GUI and game loop.
    """
    display_surface: pygame.Surface = field(init=False)
    running: bool = True
    editor: Optional[Editor] = None

    def __init__(self):
        """Initialize the app"""
        pygame.init()
        self.display_surface = pygame.display.set_mode(
            (game_state.settings.width, game_state.settings.height),
            pygame.RESIZABLE
        )
        pygame.display.set_caption(f"{GameInfo.name} {GameInfo.version}")
        pygame.display.set_icon(pygame.image.load(f"{Assets.images}pirate-hat.png"))
        print(f"\033[94mApp Running\033[0m")

        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.editor: Editor = Editor()
        self.engine: Engine = Engine()

        # Uncomment and modify the following lines if you want to set the window always on top
        # if sys.platform == "win32":
        #     import win32gui, win32con
        #     hwnd = win32gui.GetForegroundWindow()
        #     win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
        #                           win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    def handle_events(self) -> None:
        """Handle pygame events"""
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT: self.running = False
                case pygame.VIDEORESIZE:
                    self.display_surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    game_state.update_settings(width=event.w, height=event.h)
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE: self.running = False
                        case pygame.K_F1:  # * F1 to toggle editor mode
                            print("Impl: F1 to toggle editor mode")
                            # match self.editor:
                            #     case None: self.editor = Editor()
                            #     case _: self.editor = None
            # todo: Add the editor event handling
            # todo: Also add the engine event handling
            # self.editor.handle_events(event)


    # def update(self, dt: float):
    #     """
    #     Update game state
    #     """
    #     if self.editor:
    #         self.editor.run(dt)
    #     # Add more update logic as needed

    def run(self) -> None:
        """Main game loop"""
        while self.running:
            dt: float = self.clock.tick(game_state.settings.fps) / 1000.0  # get seconds since last tick
            self.handle_events()  # handle events

            # self.editor.run(dt)  # update game state
            self.engine.run(dt)  # update game state

            pygame.display.update()  # * render game (draw everything)

        pygame.quit()  # quit pygame when the loop ends (when self.running is False)
