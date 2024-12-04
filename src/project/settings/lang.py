from enum import IntEnum
import json
from typing import Dict, List

from pydantic import BaseModel, Field

class Language(IntEnum):
    """Enumeration of available languages for the game."""
    ENGLISH = 0     # * Seize the day
    SPANISH = 1     # * Aprovecha el día
    FRENCH = 2      # * Cueille le jour
    GERMAN = 3      # * Nutze den Tag
    ITALIAN = 4     # * Cogli l'attimo
    PORTUGUESE = 5  # * Aproveite o dia

    # RUSSIAN = 6     # * Лови момент        -> read_as("Lovi moment")
    # JAPANESE = 7    # * 今を生きろ          -> read_as("Ima o ikiro")
    # CHINESE = 8     # * 把握今天            -> read_as("Bǎwò jīntiān")
    # KOREAN = 9      # * 오늘을 즐겨라       -> read_as("Oneul-eul jeulgyeola")
    # ARABIC = 10     # * استغل اليوم        -> read_as("Istghl alyawm")
    # HINDI = 11      # * आज का दिन जीतो     -> read_as("Aaj ka din jeeto")
    # LATIN = 12      # *^Carpe diem
    # POLISH = 13     # *^Wykorzystaj dzień

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

    def set_language(self, language: Language) -> None:
        self.language = language
