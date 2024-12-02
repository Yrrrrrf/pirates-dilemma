from pydantic import BaseModel, Field
from typing import Tuple

from project.theme.theme import Theme, Themes
from project.settings import Settings


class AppData(BaseModel):
    settings: Settings = Field(default_factory=Settings)
    current_theme: Theme = Field(default=Themes.DARK.value)

    class Config:
        arbitrary_types_allowed = True  # it allows the use of arbitrary types in the model
        # so, it can be used with pygame objects

    def get_screen_size(self) -> Tuple[int, int]:
        return (self.settings.width, self.settings.height)


app_data = AppData()
