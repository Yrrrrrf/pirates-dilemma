from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple

from tools import AssetManager

@dataclass
class UITheme:
    """Base theme configuration for UI elements"""
    background_color: Tuple[int, int, int] = (0, 0, 0)
    text_color: Tuple[int, int, int] = (255, 255, 255)
    highlight_color: Tuple[int, int, int] = (255, 223, 0)
    hover_color: Tuple[int, int, int] = (255, 165, 0)
    disabled_color: Tuple[int, int, int] = (128, 128, 128)
    font_name: str = 'comicsansms'
    font_sizes: Dict[str, int] = None

    def __post_init__(self):
        if self.font_sizes is None:
            self.font_sizes = {
                'title': 80,
                'option': 45,
                'highlight': 55
            }
