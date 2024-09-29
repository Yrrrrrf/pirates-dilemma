# File: game/utils/settings.py
from pydantic import BaseModel, Field
from typing import Dict, List, Tuple
from enum import IntEnum
import json

from utils import AssetManager


class Language(IntEnum):
    """Enumeration of available languages for the game."""
    ENGLISH = 0
    SPANISH = 1
    # todo: Add the equivalent dialogues for the following languages
    # FRENCH = 2
    # GERMAN = 3
    # ITALIAN = 4
    # PORTUGUESE = 5
    # RUSSIAN = 6
    # JAPANESE = 7
    # Add more languages as needed

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


class LanguageManager(BaseModel):
    language: Language = Field(...)
    _translations: Dict[str, List[str]] = {}  # ^[key][language]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def load_translations(cls, file_path: str = AssetManager.get_script("ui.json")):
        try:
            with open(file_path, 'r', encoding='utf-8') as file: 
                cls._translations = json.load(file)
            # [print(f"\t{key}: {values}") for key, values in cls._translations.items()]
        except FileNotFoundError: print(f"Translations file not found: {file_path}")
        except json.JSONDecodeError as e: print(f"Error parsing translations file: {e}")

    def set_language(self, language: Language): self.language = language

    def get_text(self, key: str) -> str:
        try: return self._translations[key][self.language.value]
        except (KeyError, IndexError):
            print(f"Translation key '{key}' not found or invalid index for {self.language.name}")
            return "penchs"

    @classmethod
    def get_all_translations(cls, language: Language) -> Dict[str, str]:
        return {key: values[language.value] for key, values in cls._translations.items()}
