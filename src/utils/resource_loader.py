from enum import Enum


class AssetManager(Enum):
    """Manages paths for various types of game assets."""
    root: str = "assets/"
    audio: str = root + "audio/"
    fonts: str = root + "fonts/"
    images: str = root + "images/"

    def get_image(filename: str) -> str: return AssetManager.images.value + filename
    def get_audio(filename: str) -> str: return AssetManager.audio.value + filename
    def get_font(filename: str) -> str: return AssetManager.fonts.value + filename
