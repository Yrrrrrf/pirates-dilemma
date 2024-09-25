from pathlib import Path
from enum import Enum
from typing import Union
from pydantic import BaseModel


class AssetType(Enum):
    AUDIO = "audio"
    FONTS = "fonts"
    IMAGES = "images"
    MAPS = "maps"

class PathSolver:
    ROOT = Path(__file__).parent.parent.parent / "assets"

    @classmethod
    def get_asset(cls, asset_type: AssetType, filename: str, absolute: bool = False) -> Union[Path, str]:
        path = cls.ROOT / asset_type.value / filename
        return str(path.resolve()) if absolute else path

class AssetManager(BaseModel):
    @staticmethod
    def get_asset(asset_type: AssetType, filename: str, absolute: bool = False) -> Union[Path, str]:
        return PathSolver.get_asset(asset_type, filename, absolute)

    @classmethod
    def generate_methods(cls):
        for asset_type in AssetType:
            method_name = f"get_{asset_type.value.lower()}".rstrip("s")
            setattr(cls, method_name, lambda filename, at=asset_type: cls.get_asset(at, filename))
            setattr(cls, f"{method_name}_abs", lambda filename, at=asset_type: cls.get_asset(at, filename, True))

AssetManager.generate_methods()

# Usage examples:
# AssetManager.get_image("example.png")  # get path (relative)
# AssetManager.get_audio_abs("sound.mp3")  # get absolute path
