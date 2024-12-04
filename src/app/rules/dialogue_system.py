import random
from typing import List, Optional, Tuple
import pygame
from pydantic import BaseModel, Field
from pygame import Surface, font

from app.core.entities.npc import NPC
from utils import AssetManager

class DialogueMessage(BaseModel):
    text: str
    speaker: str
    portrait_path: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True

class DialogueBox(BaseModel):
    width: int = Field(default=800)
    height: int = Field(default=200)
    padding: int = Field(default=20)
    border_radius: int = Field(default=15)
    background_color: Tuple[int, int, int, int] = Field(default=(0, 0, 0, 220))
    text_color: Tuple[int, int, int] = Field(default=(255, 255, 255))
    name_color: Tuple[int, int, int] = Field(default=(255, 223, 0))  # Gold color for names
    font_size: int = Field(default=24)
    name_font_size: int = Field(default=28)
    animation_speed: float = Field(default=50.0)  # Characters per second
    
    # Runtime fields
    _font: Optional[font.Font] = None
    _name_font: Optional[font.Font] = None
    _current_text: str = ""
    _text_progress: float = 0
    _is_complete: bool = False
    
    class Config:
        arbitrary_types_allowed = True
        
    def __init__(self, **data):
        super().__init__(**data)
        self._font = font.Font(AssetManager.get_font("CascadiaCode.ttf"), self.font_size)
        self._name_font = font.Font(AssetManager.get_font("CascadiaCodeItalic.ttf"), self.name_font_size)
        # self._font = font.Font(AssetManager.get_font("Roboto-Regular.ttf"), self.font_size)
        # self._name_font = font.Font(AssetManager.get_font("Roboto-Bold.ttf"), self.name_font_size)
        
    def update(self, dt: float, full_text: str) -> None:
        if self._current_text != full_text:
            self._current_text = full_text
            self._text_progress = 0
            self._is_complete = False
            
        if not self._is_complete:
            self._text_progress += self.animation_speed * dt
            if self._text_progress >= len(full_text):
                self._text_progress = len(full_text)
                self._is_complete = True
                
    def draw(self, surface: Surface, message: DialogueMessage) -> None:
        screen_width, screen_height = surface.get_size()
        
        # Create dialogue box surface
        box_surface = Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(
            box_surface, 
            self.background_color,
            (0, 0, self.width, self.height),
            border_radius=self.border_radius
        )
        
        # Draw speaker name
        name_surface = self._name_font.render(message.speaker, True, self.name_color)
        box_surface.blit(name_surface, (self.padding, self.padding))
        
        # Draw portrait if available
        portrait_size = 120
        text_start_x = self.padding
        
        # todo: Improve this section to now:
        # 0. Select just the npc section, not all the spread sheet (as it is now)
        # for now it shows the complete asset image, so it is not the best way to show the portrait
        # 1. Load the portrait image from the path
        # 2. Scale the portrait to the correct size
        # 3. Draw the portrait on the box surface...
        # 4. Update the text start position based on the portrait size
        if message.portrait_path:
            try:
                portrait = pygame.image.load(AssetManager.get_image(message.portrait_path))
                portrait = pygame.transform.scale(portrait, (portrait_size, portrait_size))
                box_surface.blit(portrait, (self.padding, self.padding + 40))
                text_start_x = portrait_size + self.padding * 2
            except:
                pass  # If portrait loading fails, continue without it
        
        # Draw animated text
        visible_text = message.text[:int(self._text_progress)]
        text_y = self.padding * 2 + name_surface.get_height()
        
        # Word wrap the text
        words = visible_text.split(' ')
        line = []
        y_offset = 0
        x_offset = text_start_x
        max_width = self.width - text_start_x - self.padding
        
        for word in words:
            line.append(word)
            text_surface = self._font.render(' '.join(line), True, self.text_color)
            
            if text_surface.get_width() > max_width:
                line.pop()
                if line:
                    text_surface = self._font.render(' '.join(line), True, self.text_color)
                    box_surface.blit(text_surface, (x_offset, text_y + y_offset))
                line = [word]
                y_offset += self._font.get_height()
        
        if line:
            text_surface = self._font.render(' '.join(line), True, self.text_color)
            box_surface.blit(text_surface, (x_offset, text_y + y_offset))
        
        # Draw continue indicator if text is complete
        if self._is_complete:
            indicator_text = self._font.render('▼', True, self.text_color)
            box_surface.blit(
                indicator_text,
                (self.width - self.padding - indicator_text.get_width(),
                 self.height - self.padding - indicator_text.get_height())
            )
        
        # Position the dialogue box at the bottom center of the screen
        box_x = (screen_width - self.width) // 2
        box_y = screen_height - self.height - 20
        surface.blit(box_surface, (box_x, box_y))

    def is_complete(self) -> bool:
        return self._is_complete

    def complete_text(self) -> None:
        self._text_progress = len(self._current_text)
        self._is_complete = True



class DialogueSystem(BaseModel):
    active: bool = Field(default=False)
    messages: List[DialogueMessage] = Field(default_factory=list)
    current_message_index: int = Field(default=0)
    dialogue_box: DialogueBox = Field(default_factory=DialogueBox)
    
    class Config:
        arbitrary_types_allowed = True
    
    def start_dialogue(self, npc: NPC) -> None:

        print(f"Starting dialogue with {npc.name} ({npc.npc_type.value})")

        m: List[DialogueMessage] = []
        for message in npc.dialogues:
            m.append(DialogueMessage(text=message, speaker=npc.name, portrait_path=npc.sprite_sheet_path))

        self.messages = m
        self.current_message_index = 0
        self.active = True

    def update(self, dt: float) -> None:
        if not self.active or self.current_message_index >= len(self.messages):
            return
            
        current_message = self.messages[self.current_message_index]
        self.dialogue_box.update(dt, current_message.text)

    def advance_dialogue(self) -> None:
        self.current_message_index += 1
        if self.current_message_index >= len(self.messages):
            self.active = False

    def draw(self, surface: Surface) -> None:
        if not self.active or self.current_message_index >= len(self.messages):
            return

        current_message = self.messages[self.current_message_index]
        self.dialogue_box.draw(surface, current_message)
