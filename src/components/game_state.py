from pydantic import BaseModel, Field
from typing import Tuple

from settings import GameSettings
from constants import Themes, Theme


class GameState(BaseModel):
    settings: GameSettings = Field(default_factory=GameSettings)
    current_theme: Theme = Field(default=Themes.DARK.value)

    def get_screen_size(self) -> Tuple[int, int]:
        return (self.settings.width, self.settings.height)

    class Config:
        arbitrary_types_allowed = True  # it allows the use of arbitrary types in the model
        # so, it can be used with pygame objects


# game_state = GameState()
# print(game_state.model_dump_json())  # Easily serialize to JSON
