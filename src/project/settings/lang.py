from enum import IntEnum
import json
from typing import Dict, List

from pydantic import BaseModel, Field


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

class LanguageManager(BaseModel):
    language: Language = Field(...)
    _translations: Dict[str, List[str]] = {}  # ^[key][language]

    class Config:
        arbitrary_types_allowed = True

    def load_translations(cls, file_path: str) -> None:
        try:
            with open(file_path, 'r', encoding='utf-8') as file: 
                cls._translations = json.load(file)

            # Debug translations
            print(f"Loaded translations for {len(cls._translations)} keys:")
            # [print(f"\t{key}: {values}") for key, values in cls._translations.items()]
        except FileNotFoundError: print(f"Translations file not found: {file_path}")
        except json.JSONDecodeError as e: print(f"Error parsing translations file: {e}")

    def get_text(self, key: str) -> str:
        try: return self._translations[key][self.language.value]
        except (KeyError, IndexError):
            print(f"Translation key '{key}' not found or invalid index for {self.language.name}")
            return "penchs"

    @classmethod
    def get_all_translations(cls, language: Language) -> Dict[str, str]:
        return {key: values[language.value] for key, values in cls._translations.items()}
