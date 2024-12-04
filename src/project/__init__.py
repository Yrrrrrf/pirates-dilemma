from pydantic import BaseModel, Field
from typing import Tuple

from project.settings.lang import LanguageManager
from project.theme.theme import Theme, Themes
from project.settings import Settings
from utils import AssetManager


class AppData(BaseModel):
    settings: Settings = Field(default_factory=Settings)
    current_theme: Theme = Field(default=Themes.DARK.value)

    class Config:
        arbitrary_types_allowed = True  # it allows the use of arbitrary types in the model
        # so, it can be used with pygame objects

    def get_screen_size(self) -> Tuple[int, int]:
        return (self.settings.width, self.settings.height)


app_data = AppData()

# todo: Look for some way to load the translations from the settings file...

menu_lang_manager = LanguageManager(language=app_data.settings.language)
menu_lang_manager.load_translations(file_path=AssetManager.get_script("menu.json"))

npc_lang_manager = LanguageManager(language=app_data.settings.language)
npc_lang_manager.load_translations(file_path=AssetManager.get_script("npc-dialogues.json"))
