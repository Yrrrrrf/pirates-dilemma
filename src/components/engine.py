from pydantic import BaseModel, Field, validator
import pygame

from components.game_state import GameState

class Engine(BaseModel):
    game_state: GameState = Field(default_factory=GameState)
    display_surface: pygame.Surface | None = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)

    def initialize_display(self, surface: pygame.Surface):
        self.display_surface = surface

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    print("Yeeeeeeeeeees, CScience!")

    def run(self, dt: float) -> None:
        if self.display_surface is None:
            raise ValueError("Display surface not initialized. Call initialize_display() first.")
        self.event_loop()
        self.display_surface.fill((0, 0, 0))  # Clear the screen
        self.draw_debug_info()

    def draw_debug_info(self) -> None:
        if self.display_surface is None:
            return
        font = pygame.font.Font(None, 30)
        # Add debug info drawing logic here
