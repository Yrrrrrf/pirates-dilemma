from pydantic import BaseModel, Field
from typing import Tuple

from project.settings.lang import Language

from pydantic import BaseModel, Field
from typing import Tuple


class Settings(BaseModel):
    """Represents the adjustable settings of the game."""
    language: Language = Field(default=Language.ENGLISH)
    width: int = Field(default=1080, ge=640, le=3840)
    height: int = Field(default=720, ge=480, le=2160)
    tile_size: int = Field(default=32, ge=16, le=128)
    animation_speed: int = Field(default=8, ge=1, le=20)
    volume: float = Field(default=0.7, ge=0.0, le=1.0)
    fullscreen: bool = Field(default=False)
    fps: int = Field(default=72, ge=30, le=144)

    def update(self, **kwargs):
        """Update the game settings with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def get_screen_size(self) -> Tuple[int, int]:
        """Return the screen size as a tuple."""
        return self.width, self.height
