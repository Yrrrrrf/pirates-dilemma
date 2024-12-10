import random
from typing import List, Optional, Tuple
import pygame
from pydantic import BaseModel, Field
from pygame import Surface, Vector2, font

from app.core.systems.entities.npc import NPC, NPCType
from app.core.systems.fn.interaction import DialogueMenu, DialogueMenuOption, InteractionType
from project import npc_lang_manager
from tools import AssetManager

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
    name_color: Tuple[int, int, int] = Field(default=(255, 223, 0))
    font_size: int = Field(default=24)
    name_font_size: int = Field(default=28)
    animation_speed: float = Field(default=50.0)
    fade_speed: float = Field(default=3.0)  # New fade speed for smooth transitions
    
    # Runtime fields
    _font: Optional[font.Font] = None
    _name_font: Optional[font.Font] = None
    _current_text: str = ""
    _text_progress: float = 0
    _is_complete: bool = False
    _alpha: float = 0.0  # New alpha for fading
    
    class Config:
        arbitrary_types_allowed = True
        
    def __init__(self, **data):
        super().__init__(**data)
        self._font = font.Font(AssetManager.get_font("CascadiaCode.ttf"), self.font_size)
        self._name_font = font.Font(AssetManager.get_font("CascadiaCodeItalic.ttf"), self.name_font_size)
    
    def update(self, dt: float, full_text: str, should_show: bool = True) -> None:
        # Update fade
        target_alpha = 255.0 if should_show else 0.0
        self._alpha += (target_alpha - self._alpha) * self.fade_speed * dt
        self._alpha = max(0.0, min(255.0, self._alpha))

        # Update text animation only if visible
        if should_show:
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
        if self._alpha <= 0:
            return
            
        screen_width, screen_height = surface.get_size()
        
        # Create dialogue box surface
        box_surface = Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw background with current alpha
        pygame.draw.rect(
            box_surface, 
            (*self.background_color[:3], int(self._alpha * self.background_color[3] / 255)),
            (0, 0, self.width, self.height),
            border_radius=self.border_radius
        )
        
        # Draw content with current alpha
        name_surface = self._name_font.render(message.speaker, True, self.name_color)
        name_surface.set_alpha(int(self._alpha))
        box_surface.blit(name_surface, (self.padding, self.padding))
        
        # Handle portrait and text layout
        text_start_x = self.padding
        if message.portrait_path:
            portrait_size = 120
            try:
                portrait = self._get_npc_portrait(message.portrait_path, portrait_size)
                if portrait:
                    portrait.set_alpha(int(self._alpha))
                    
                    # Create a circular mask for the portrait
                    mask = pygame.Surface((portrait_size, portrait_size), pygame.SRCALPHA)
                    pygame.draw.circle(
                        mask,
                        (255, 255, 255, int(self._alpha)),
                        (portrait_size // 2, portrait_size // 2),
                        portrait_size // 2
                    )
                    
                    # Create a surface for the masked portrait
                    portrait_surface = pygame.Surface((portrait_size, portrait_size), pygame.SRCALPHA)
                    portrait_surface.blit(portrait, (0, 0))
                    portrait_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                    
                    # Add a decorative border
                    pygame.draw.circle(
                        portrait_surface,
                        self.name_color,  # Use the same gold color as the name
                        (portrait_size // 2, portrait_size // 2),
                        portrait_size // 2,
                        3  # Border width
                    )
                    
                    # Draw the portrait
                    box_surface.blit(portrait_surface, (self.padding, self.padding + 30))
                    text_start_x = portrait_size + self.padding * 2
            except Exception as e:
                print(f"Error drawing portrait: {e}")

        # Draw animated text
        visible_text = message.text[:int(self._text_progress)]
        text_y = self.padding * 2 + name_surface.get_height()
        
        self._draw_wrapped_text(
            box_surface, 
            visible_text, 
            (text_start_x, text_y), 
            self.width - text_start_x - self.padding
        )

        # Draw continue indicator
        if self._is_complete:
            indicator_text = self._font.render('▼', True, self.text_color)
            indicator_text.set_alpha(int(self._alpha))
            box_surface.blit(
                indicator_text,
                (self.width - self.padding - indicator_text.get_width(),
                 self.height - self.padding - indicator_text.get_height())
            )
        
        # Position and draw the dialogue box
        box_x = (screen_width - self.width) // 2
        box_y = screen_height - self.height - 20
        surface.blit(box_surface, (box_x, box_y))

    def _get_npc_portrait(self, sprite_sheet_path: str, portrait_size: int) -> Optional[Surface]:
        """Extract and process NPC portrait from sprite sheet"""
        try:
            # Load sprite sheet
            sprite_sheet = pygame.image.load(AssetManager.get_image(sprite_sheet_path))
            
            # Get the first frame (idle facing front) which is 24x24
            frame_rect = pygame.Rect(0, 0, 24, 24)
            portrait = sprite_sheet.subsurface(frame_rect)
            
            # Scale up the portrait
            scaled_portrait = pygame.transform.scale_by(portrait, portrait_size / 24)
            
            return scaled_portrait
        except Exception as e:
            print(f"Error processing portrait: {e}")
            return None

    def _draw_wrapped_text(self, surface: Surface, text: str, pos: Tuple[int, int], max_width: int) -> None:
        words = text.split(' ')
        line = []
        x, y = pos
        y_offset = 0
        
        for word in words:
            line.append(word)
            text_surface = self._font.render(' '.join(line), True, self.text_color)
            text_surface.set_alpha(int(self._alpha))
            
            if text_surface.get_width() > max_width:
                line.pop()
                if line:
                    final_surface = self._font.render(' '.join(line), True, self.text_color)
                    final_surface.set_alpha(int(self._alpha))
                    surface.blit(final_surface, (x, y + y_offset))
                line = [word]
                y_offset += self._font.get_height()
        
        if line:
            final_surface = self._font.render(' '.join(line), True, self.text_color)
            final_surface.set_alpha(int(self._alpha))
            surface.blit(final_surface, (x, y + y_offset))

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
    interaction_range: float = Field(default=100.0)  # Distance to maintain dialogue
    
    class Config:
        arbitrary_types_allowed = True
    
    def start_dialogue(self, npc: NPC) -> None:
        print(f"Starting dialogue with {npc.name} ({npc.npc_type.value})")
        
        m: List[DialogueMessage] = []
        for key in npc.dialogue_keys:
            message = npc_lang_manager.get_text(key)
            m.append(DialogueMessage(
                text=message, 
                speaker=npc.name, 
                portrait_path=npc.sprite_sheet_path
            ))

        self.messages = m
        self.current_message_index = 0
        self.active = True

    def update(self, dt: float, player_pos: Vector2, npc_pos: Vector2) -> None:
        if not self.active or self.current_message_index >= len(self.messages):
            return
        
        # Check if player is still in range
        distance = player_pos.distance_to(npc_pos)
        should_show = distance <= self.interaction_range
        
        # Update current message
        current_message = self.messages[self.current_message_index]
        self.dialogue_box.update(dt, current_message.text, should_show)
        
        # Auto-close dialogue if player moves too far
        if not should_show:
            self.active = False

    def advance_dialogue(self) -> None:
        self.current_message_index += 1
        if self.current_message_index >= len(self.messages):
            self.active = False

    def draw(self, surface: Surface) -> None:
        if not self.active or self.current_message_index >= len(self.messages):
            return

        current_message = self.messages[self.current_message_index]
        self.dialogue_box.draw(surface, current_message)



class EnhancedDialogueSystem(DialogueSystem):
    """Extended dialogue system with interaction menu support"""
    menu: DialogueMenu = Field(default_factory=DialogueMenu)
    menu_active: bool = Field(default=False)
    current_npc: Optional[NPC] = None

    def _get_npc_interactions(self, npc_type: NPCType) -> List[InteractionType]:
        """Get available interactions for NPC type"""
        type_interactions = {
            NPCType.MERCHANT: [InteractionType.BUY, InteractionType.SELL, InteractionType.STEAL],
            NPCType.HARBOR_MASTER: [InteractionType.BUY, InteractionType.STEAL],
            NPCType.TAVERN_KEEPER: [InteractionType.BUY, InteractionType.SELL],
            NPCType.WANDERING_MERCHANT: [InteractionType.BUY, InteractionType.SELL, InteractionType.STEAL],
            NPCType.CIVILIAN: [InteractionType.STEAL],
        }
        return type_interactions.get(npc_type, [])

    def start_dialogue(self, npc: NPC) -> None:
        """Start dialogue with an NPC"""
        super().start_dialogue(npc)
        self.current_npc = npc
        self.menu_active = False

    def advance_dialogue(self) -> None:
        """Advance dialogue or show menu when complete"""
        if self.menu_active:
            return

        self.current_message_index += 1
        if self.current_message_index >= len(self.messages):
            self.show_interaction_menu()

    def show_interaction_menu(self) -> None:
        """Show interaction menu after dialogue"""
        if not self.current_npc:
            return

        self.menu_active = True
        self.menu.options.clear()

        # Create menu options with proper callbacks
        for interaction in self._get_npc_interactions(self.current_npc.npc_type):
            # Create a callback that captures both self and interaction
            def create_callback(interaction_type):
                return lambda: self._handle_interaction(interaction_type)
                
            self.menu.options.append(DialogueMenuOption(
                text=interaction.value,
                interaction_type=interaction,
                callback=create_callback(interaction)
            ))

    def _handle_interaction(self, interaction: InteractionType) -> None:
        """Handle interaction selection"""
        if not self.current_npc:
            return

        # Handle the interaction
        match interaction:
            case InteractionType.BUY:
                print(f"Opening shop with {self.current_npc.name}")
            case InteractionType.SELL:
                print(f"Selling items to {self.current_npc.name}")
            case InteractionType.STEAL:
                success = random.random() < 0.5
                if success:
                    print(f"Successfully stole from {self.current_npc.name}")
                else:
                    print(f"Failed to steal from {self.current_npc.name}")

        # Close the dialogue and menu
        self.active = False
        self.menu_active = False
        self.current_npc = None

    def show_interaction_menu(self) -> None:
        """Show interaction menu after dialogue"""
        if not self.current_npc:
            return

        self.menu_active = True
        self.menu.options.clear()

        # Create menu options with proper callbacks
        for interaction in self._get_npc_interactions(self.current_npc.npc_type):
            callback = lambda i=interaction: self._handle_interaction(i)
            self.menu.options.append(DialogueMenuOption(
                text=interaction.value,
                interaction_type=interaction,
                callback=callback
            ))

    def update(self, dt: float, player_pos: Vector2, npc_pos: Vector2) -> None:
        """Update dialogue and menu state"""
        super().update(dt, player_pos, npc_pos)
        
        if self.menu_active:
            self.menu.update_hover(pygame.mouse.get_pos())

    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle input for dialogue and menu"""
        pass

    def draw(self, surface: Surface) -> None:
        """Draw dialogue box and integrated menu    """
        if not self.active:
            return

        # Draw the dialogue box background
        super().draw(surface)
        
        # Draw menu if active
        if self.menu_active:
            screen_width, screen_height = surface.get_size()
            box_rect = pygame.Rect(
                (screen_width - self.dialogue_box.width) // 2,
                screen_height - self.dialogue_box.height - 20,
                self.dialogue_box.width,
                self.dialogue_box.height
            )
            self.menu.draw(surface, box_rect, int(self.dialogue_box._alpha))
