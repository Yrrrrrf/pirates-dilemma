from pydantic import BaseModel, Field
from project.theme.ui import UITheme
from project.settings import *
from tools import AssetManager


class AppData(BaseModel):
    settings: Settings = Field(default_factory=Settings)
    # current_theme: UITheme = Field(default=Themes.DARK.value)

    class Config:
        arbitrary_types_allowed = True  # it allows the use of arbitrary types in the model

    def __init__(self, **data):
        super().__init__(**data)


app_data: AppData = AppData()

menu_lang_manager = LanguageManager(language=app_data.settings.language)
npc_lang_manager = LanguageManager(language=app_data.settings.language)
int_lang_manager = LanguageManager(language=app_data.settings.language)

menu_lang_manager.load_translations(file_path=AssetManager.get_script("menu.json"))
npc_lang_manager.load_translations(file_path=AssetManager.get_script("npc-dialogues.json"))
int_lang_manager.load_translations(file_path=AssetManager.get_script("interactions.json"))

def set_app_lang(lang: Language) -> None:
    app_data.settings.language = lang
    menu_lang_manager.set_language(app_data.settings.language)
    npc_lang_manager.set_language(app_data.settings.language)
    int_lang_manager.set_language(app_data.settings.language)

# todo: Somehow re-strucutre the code to `def app_data.set_lang(lang: Language)`
# todo: to handle it using the same instance of `app_data` 