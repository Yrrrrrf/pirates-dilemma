from enum import Enum
from typing import Tuple
from pydantic import BaseModel

from utils import AssetManager


class GameInfo:
    """Contains constant information about the game that doesn't change during runtime."""
    NAME: str = "Pirate's Dilemma"
    VERSION: str = "v0.0.1"


class Theme(BaseModel):
    """Represents a color theme for the Pirate's Dilemma game."""
    name: str
    main_color: Tuple[int, int, int]
    secondary_color: Tuple[int, int, int]
    highlight_color: Tuple[int, int, int]
    font: str

    class Config: frozen = True  # it means that the object is immutable


class Themes(Enum):
    """Enumeration of predefined themes for the Pirate's Dilemma game."""
    LIGHT = Theme(
        name="Light Theme",
        main_color=(255, 255, 255),
        secondary_color=(191, 191, 191),
        highlight_color=(255, 0, 0),
        font=AssetManager.get_font_abs("Roboto-Regular.ttf")
    )
    DARK = Theme(
        name="Dark Theme",
        main_color=(0, 0, 0),
        secondary_color=(63, 63, 63),
        highlight_color=(255, 0, 0),
        font=AssetManager.get_font_abs("Roboto-Regular.ttf")
    )
    DARK_PLUS = Theme(
        name="Dark+ Theme",
        main_color=(0, 0, 0),
        secondary_color=(31, 31, 31),
        highlight_color=(255, 0, 0),
        font=AssetManager.get_font_abs("Roboto-Regular.ttf")
    )
    DEBUG = Theme(
        name="Debug Theme",
        main_color=(255, 0, 0),
        secondary_color=(0, 0, 0),
        highlight_color=(255, 0, 0),
        font="Consolas"
    )

    @classmethod
    def get_theme(cls, theme_name: str) -> Theme:
        """Retrieve a Theme instance by its name."""
        return cls[theme_name.upper()].value
