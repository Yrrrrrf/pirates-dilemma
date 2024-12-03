# stdlib
from dataclasses import Field
from typing import Any, Dict, Optional
# third party
from pydantic import BaseModel
import pygame
# local
from layout.ui import *
from utils import AssetManager


class DebugUI(BaseModel):
    sections: Dict[str, Section] = Field(default_factory=dict)
    theme: UITheme = Field(default_factory=UITheme)
    fonts: Dict[str, pygame.font.Font] = Field(default_factory=dict)
    visible: bool = Field(default=True)
    
    class Config:
        arbitrary_types_allowed = True

    def initialize(self, debug_data: Dict[str, Dict[str, Any]]) -> None:
        """Initialize the UI with fonts and sections"""
        self.fonts = {
            'header': pygame.font.Font(AssetManager.get_font("CascadiaCode.ttf"), 18),
            'detail': pygame.font.Font(AssetManager.get_font("CascadiaCodeItalic.ttf"), 14)
        }
        
        for section_name, section_data in debug_data.items():
            height = self._calculate_section_height(section_data)
            section = Section(
                title=section_name.title(),
                theme=self.theme,
                size=(self.theme.section_width, height)
            )
            section.initialize(self.fonts['header'], self.fonts['detail'], section_data)
            self.sections[section_name] = section
        
        self._update_layout()
        self.update(debug_data)

    def update(self, debug_data: Dict[str, Dict[str, Any]]) -> None:
        for name, data in debug_data.items():
            if name in self.sections:
                self.sections[name].update_content(data)
    
    def _calculate_section_height(self, data: Dict[str, Any]) -> int:
        num_items = len(data) + 1  # +1 for title
        return (
            self.theme.padding * 2 +  # some padding
            (num_items - 1) * self.theme.spacing +  # Spacing between items
            32 +  # Title height
            20 * len(data)  # Content items height
        )
    
    def _update_layout(self) -> None:
        current_y = 40
        for section in self.sections.values():
            section.position = (10, current_y)
            current_y += section.size[1] + self.theme.spacing
    
    def draw(self, surface: Surface) -> None:
        if not self.visible:
            return
        for section in self.sections.values():
            section.draw(surface)

def create_debug_ui(debug_data: Dict[str, Dict[str, Any]], theme: Optional[UITheme] = None) -> DebugUI:
    """Create and initialize a debug UI instance"""
    debug_ui = DebugUI(theme=theme or UITheme())
    debug_ui.initialize(debug_data)
    return debug_ui
