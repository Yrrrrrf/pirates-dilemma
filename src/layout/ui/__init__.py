from typing import Dict, List, Tuple, Optional, Any
import pygame
from pydantic import BaseModel, Field
from pygame import Surface, Rect
from utils import AssetManager

class UIColor(BaseModel):
    r: int = Field(default=0, ge=0, le=255)
    g: int = Field(default=0, ge=0, le=255)
    b: int = Field(default=0, ge=0, le=255)
    a: int = Field(default=255, ge=0, le=255)

    def as_tuple(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)
    
    def as_rgba(self) -> Tuple[int, int, int, int]:
        return (self.r, self.g, self.b, self.a)

class UITheme(BaseModel):
    background_color: UIColor = Field(default_factory=lambda: UIColor(r=20, g=20, b=20, a=128))
    border_color: UIColor = Field(default_factory=lambda: UIColor(r=64, g=128, b=96))
    text_color: UIColor = Field(default_factory=lambda: UIColor(r=255, g=255, b=255))
    title_color: UIColor = Field(default_factory=lambda: UIColor(r=64, g=128, b=96))
    spacing: int = Field(default=5)
    padding: int = Field(default=8)
    section_width: int = Field(default=300)

class UIComponent(BaseModel):
    position: Tuple[int, int] = Field(default=(0, 0))
    size: Tuple[int, int] = Field(default=(100, 25))
    visible: bool = Field(default=True)
    
    class Config:
        arbitrary_types_allowed = True

    def draw(self, surface: Surface) -> None:
        pass

class TextComponent(UIComponent):
    text: str = Field(default="")
    font: Optional[pygame.font.Font] = None
    color: UIColor = Field(default_factory=lambda: UIColor(r=255, g=255, b=255))
    
    def draw(self, surface: Surface) -> None:
        if not self.visible or not self.font:
            return
        text_surface = self.font.render(self.text, True, self.color.as_tuple())
        text_rect = text_surface.get_rect(topleft=self.position)
        surface.blit(text_surface, text_rect)

class Section(UIComponent):
    title: str = Field(default="")
    components: List[TextComponent] = Field(default_factory=list)
    theme: UITheme = Field(default_factory=UITheme)
    
    def initialize(self, title_font: pygame.font.Font, detail_font: pygame.font.Font, data: Dict[str, Any]) -> None:
        self.components = [
            TextComponent(
                text=self.title,
                font=title_font,
                color=self.theme.title_color,
                size=(self.size[0], 25)
            )
        ]
        
        for key in data:
            self.components.append(
                TextComponent(
                    text="",
                    font=detail_font,
                    color=self.theme.text_color,
                    size=(self.size[0], 20)
                )
            )
        self._update_layout()
    
    def update_content(self, data: Dict[str, Any]) -> None:
        for i, (key, value) in enumerate(data.items(), 1):
            if i < len(self.components):
                self.components[i].text = f"{key}: {value}"
        self._update_layout()
    
    def _update_layout(self) -> None:
        current_y = self.position[1] + self.theme.padding
        for component in self.components:
            component.position = (
                self.position[0] + self.theme.padding,
                current_y
            )
            current_y += component.size[1] + self.theme.spacing

    def draw(self, surface: Surface) -> None:
        if not self.visible:
            return
        
        bg_surface = pygame.Surface(self.size, pygame.SRCALPHA)
        bg_surface.fill(self.theme.background_color.as_rgba())
        surface.blit(bg_surface, self.position)
        
        if self.theme.border_color:
            pygame.draw.rect(surface, self.theme.border_color.as_tuple(), 
                           Rect(self.position, self.size), 1)
        
        for component in self.components:
            component.draw(surface)
