from pydantic import BaseModel, Field
import pygame

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

        pygame.display.set_caption(f"{GameInfo.NAME} {GameInfo.VERSION}")
        pygame.display.set_icon(pygame.image.load(AssetManager.get_image("pirate-hat.png")))

        # Initialize game state and engine
        game_state = GameState()
        self.display_surface = pygame.display.set_mode(
            game_state.settings.get_screen_size(), pygame.RESIZABLE
        )
        
        # Create and initialize the engine
        self.engine = Engine(game_state=game_state)
        self.engine.initialize_display(self.display_surface)

        print(f"\033[94mApp Running\033[0m")

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F1:
                    print("Impl: F1 to toggle editor mode")

    def run(self) -> None:
        while self.running:
            dt: float = self.clock.tick(self.engine.game_state.settings.fps) / 1000.0
            self.handle_events()
            self.engine.run(dt)
            pygame.display.update()

        pygame.quit()
