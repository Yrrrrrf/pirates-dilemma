from pathlib import Path
from enum import Enum
from typing import Callable, Union
from pydantic import BaseModel


class PathSolver(Enum):
    """Manages paths for various types of game assets."""
    root = Path(__file__).parent.parent.parent / "assets"
    audio = root / "audio"
    fonts = root / "fonts"
    images = root / "images"
    maps = root / "maps"

    @classmethod
    def _get_asset(cls, asset_type: 'PathSolver', filename: str) -> Path:
        return asset_type.value / filename

    @classmethod
    def _get_absolute(cls, path: Path) -> str:
        return str(path.resolve())

    @classmethod
    def get_image(cls, filename: str) -> Path:
        return cls._get_asset(cls.images, filename)

    @classmethod
    def get_audio(cls, filename: str) -> Path:
        return cls._get_asset(cls.audio, filename)

    @classmethod
    def get_font(cls, filename: str) -> Path:
        return cls._get_asset(cls.fonts, filename)

    @classmethod
    def get_map(cls, filename: str) -> Path:
        return cls._get_asset(cls.maps, filename)

# Wrapper functions for getting absolute paths
get_image_absolute = lambda filename: PathSolver._get_absolute(PathSolver.get_image(filename))
get_audio_absolute = lambda filename: PathSolver._get_absolute(PathSolver.get_audio(filename))
get_font_absolute = lambda filename: PathSolver._get_absolute(PathSolver.get_font(filename))
get_map_absolute = lambda filename: PathSolver._get_absolute(PathSolver.get_map(filename))

# Generic asset getter factory
def asset_getter_factory(get_func: Callable[[str], Path], absolute: bool = False) -> Callable[[str], Union[Path, str]]:
    if absolute:
        return lambda filename: PathSolver._get_absolute(get_func(filename))
    return get_func

# Create getter functions
get_image = asset_getter_factory(PathSolver.get_image)
get_audio = asset_getter_factory(PathSolver.get_audio)
get_font = asset_getter_factory(PathSolver.get_font)
get_map = asset_getter_factory(PathSolver.get_map)

# Create absolute getter functions
get_image_abs = asset_getter_factory(PathSolver.get_image, absolute=True)
get_audio_abs = asset_getter_factory(PathSolver.get_audio, absolute=True)
get_font_abs = asset_getter_factory(PathSolver.get_font, absolute=True)
get_map_abs = asset_getter_factory(PathSolver.get_map, absolute=True)

from pathlib import Path
from enum import Enum
from typing import Callable, Union
from pydantic import BaseModel

class AssetManager(BaseModel):
    @staticmethod
    def get_image(filename: str) -> Path: return get_image(filename)
    @staticmethod
    def get_audio(filename: str) -> Path: return get_audio(filename)
    @staticmethod
    def get_font(filename: str) -> Path: return get_font(filename)
    @staticmethod
    def get_map(filename: str) -> Path: return get_map(filename)

    @staticmethod
    def get_image_abs(filename: str) -> str: return get_image_abs(filename)
    @staticmethod
    def get_audio_abs(filename: str) -> str: return get_audio_abs(filename)
    @staticmethod
    def get_font_abs(filename: str) -> str: return get_font_abs(filename)
    @staticmethod
    def get_map_abs(filename: str) -> str: return get_map_abs(filename)
