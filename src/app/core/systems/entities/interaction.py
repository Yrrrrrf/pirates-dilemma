from app.core.systems.entities.npc import NPC, NPCType
from app.game.base.player import Player
from tools import AssetManager

from enum import Enum
import random
from typing import List, Optional, Tuple, Callable
import pygame
from pydantic import BaseModel, Field
from pygame import Surface

class InteractionType(Enum):
    TALK = "Talk"
    BUY = "Buy"
    SELL = "Sell"
    STEAL = "Steal"

    @property
    def color(self) -> Tuple[int, int, int]:
        return {
            InteractionType.TALK: (64, 196, 255),  # Light blue
            InteractionType.BUY: (96, 255, 96),    # Light green
            InteractionType.SELL: (255, 196, 64),  # Gold
            InteractionType.STEAL: (255, 64, 64),  # Red
        }[self]

class InteractionMenuItem(BaseModel):
    interaction_type: InteractionType
    rect: Optional[pygame.Rect] = None
    callback: Optional[Callable] = None
    is_hovered: bool = Field(default=False)
    is_enabled: bool = Field(default=True)
    
    class Config:
        arbitrary_types_allowed = True

    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Return True if item was clicked and is enabled"""
        if not self.rect or not self.is_enabled:
            return False
        return self.rect.collidepoint(mouse_pos[0], mouse_pos[1])

    def update_hover(self, mouse_pos: Tuple[int, int]) -> None:
        """Update hover state based on mouse position"""
        if self.rect:
            self.is_hovered = self.rect.collidepoint(mouse_pos[0], mouse_pos[1])
        else:
            self.is_hovered = False

class InteractionMenu(BaseModel):
    visible: bool = Field(default=False)
    items: List[InteractionMenuItem] = Field(default_factory=list)
    current_npc: Optional[NPC] = None
    font: Optional[pygame.font.Font] = None
    selected_index: int = Field(default=-1)
    
    # Visual settings
    background_color: Tuple[int, int, int, int] = (20, 20, 20, 230)
    hover_color: Tuple[int, int, int] = (64, 64, 64)
    disabled_color: Tuple[int, int, int] = (128, 128, 128)
    text_color: Tuple[int, int, int] = (255, 255, 255)
    padding: int = Field(default=10)
    item_height: int = Field(default=40)
    menu_width: int = Field(default=200)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.font = pygame.font.Font(AssetManager.get_font("CascadiaCode.ttf"), 16)

    def show_for_npc(self, npc: NPC, player: Player) -> None:
        """Show interaction menu for specific NPC"""
        self.current_npc = npc
        self.visible = True
        self.selected_index = 0
        self.items.clear()

        # Get available interactions for NPC type
        available_interactions = self._get_available_interactions(npc.npc_type)
        
        # Create menu items
        for interaction in available_interactions:
            callback = self._create_callback(interaction, npc, player)
            self.items.append(InteractionMenuItem(
                interaction_type=interaction,
                callback=callback
            ))

    def _get_available_interactions(self, npc_type: NPCType) -> List[InteractionType]:
        """Get available interactions based on NPC type"""
        base_interactions = [InteractionType.TALK]
        
        type_interactions = {
            NPCType.MERCHANT: [InteractionType.BUY, InteractionType.SELL, InteractionType.STEAL],
            NPCType.HARBOR_MASTER: [InteractionType.BUY, InteractionType.STEAL],
            NPCType.TAVERN_KEEPER: [InteractionType.BUY, InteractionType.SELL],
            NPCType.WANDERING_MERCHANT: [InteractionType.BUY, InteractionType.SELL, InteractionType.STEAL],
            NPCType.CIVILIAN: [InteractionType.STEAL],
        }
        
        return base_interactions + type_interactions.get(npc_type, [])

    def _create_callback(self, interaction: InteractionType, npc: NPC, player: Player) -> Callable:
        """Create callback for interaction type"""
        def talk_callback():
            print(f"Talking to {npc.name}")
            npc.current_dialogue_index = 0
            self.hide()

        def buy_callback():
            print(f"Opening shop with {npc.name}")
            player.reputation.modify(1)
            self.hide()

        def sell_callback():
            print(f"Selling items to {npc.name}")
            player.reputation.modify(1)
            self.hide()

        def steal_callback():
            success_chance = min(0.5, player.reputation.value / 200)
            if random.random() < success_chance:
                print(f"Successfully stole from {npc.name}")
                player.reputation.modify(-10)
            else:
                print(f"Failed to steal from {npc.name}")
                player.reputation.modify(-20)
            self.hide()

        callbacks = {
            InteractionType.TALK: talk_callback,
            InteractionType.BUY: buy_callback,
            InteractionType.SELL: sell_callback,
            InteractionType.STEAL: steal_callback,
        }
        return callbacks.get(interaction)

    def update(self, dt: float, mouse_pos: Tuple[int, int]) -> None:
        """Update menu state"""
        if not self.visible:
            return
            
        # Update hover states
        for i, item in enumerate(self.items):
            item.update_hover(mouse_pos)
            if item.is_hovered:
                self.selected_index = i

    def hide(self) -> None:
        """Hide the menu"""
        self.visible = False
        self.current_npc = None
        self.selected_index = -1

    def handle_click(self, mouse_pos: Tuple[int, int]) -> None:
        """Handle mouse clicks"""
        if not self.visible:
            return

        for item in self.items:
            if item.handle_click(mouse_pos):
                if item.callback:
                    item.callback()
                break

    def draw(self, surface: Surface) -> None:
        """Draw the menu"""
        if not self.visible or not self.current_npc:
            return

        # Calculate menu dimensions
        menu_height = len(self.items) * self.item_height + self.padding * 2
        screen_width, screen_height = surface.get_size()
        menu_x = (screen_width - self.menu_width) // 2
        menu_y = (screen_height - menu_height) // 2

        # Draw menu background
        menu_rect = pygame.Rect(menu_x, menu_y, self.menu_width, menu_height)
        s = pygame.Surface((self.menu_width, menu_height), pygame.SRCALPHA)
        pygame.draw.rect(s, self.background_color, s.get_rect(), border_radius=10)
        surface.blit(s, menu_rect)

        # Draw menu items
        for i, item in enumerate(self.items):
            item_y = menu_y + self.padding + i * self.item_height
            item_rect = pygame.Rect(
                menu_x + self.padding,
                item_y,
                self.menu_width - self.padding * 2,
                self.item_height
            )
            item.rect = item_rect  # Store rectangle for hit testing

            # Draw hover/selection highlight
            if item.is_hovered or i == self.selected_index:
                s = pygame.Surface((item_rect.width, item_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(s, (*self.hover_color, 128), s.get_rect(), border_radius=5)
                surface.blit(s, item_rect)

            # Draw text
            color = item.interaction_type.color if item.is_enabled else self.disabled_color
            text = self.font.render(item.interaction_type.value, True, color)
            text_rect = text.get_rect(midleft=(item_rect.left + 10, item_rect.centery))
            surface.blit(text, text_rect)