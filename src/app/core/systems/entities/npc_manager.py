from typing import List, Optional, Tuple
import pygame
from pydantic import BaseModel, Field
from pygame import Surface, font
from pygame.math import Vector2

from app.core.engine.camera import Camera
from app.core.systems.entities.interaction import InteractionMenu
from app.core.systems.entities.npc import NPC, NPCType
from app.core.systems.interactions.dialogue_system import DialogueSystem
from app.game.base.player import Player
from tools import AssetManager


class InteractionHint(BaseModel):
    font: Optional[pygame.font.Font] = None
    text: str = "Press E to talk"
    color: Tuple[int, int, int] = (255, 255, 255)
    background_color: Tuple[int, int, int] = (0, 0, 0)
    padding: int = 5
    border_radius: int = 8
    offset_y: int = -50  # Offset above the NPC
    fade_speed: float = 2.0  # Speed of fade animation
    alpha: float = 0.0  # Current opacity

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.font = font.Font(AssetManager.get_font("CascadiaCode.ttf"), 16)
        self._surface = None
        self._create_surface()

    def _create_surface(self) -> None:
        # Render text
        text_surface = self.font.render(self.text, True, self.color)
        text_rect = text_surface.get_rect()

        # Create background surface with padding
        width = text_rect.width + (self.padding * 2)
        height = text_rect.height + (self.padding * 2)
        self._surface = Surface((width, height), pygame.SRCALPHA)

        # Draw background with border radius
        pygame.draw.rect(
            self._surface,
            (*self.background_color, 180),  # Semi-transparent background
            self._surface.get_rect(),
            border_radius=self.border_radius
        )

        # Draw text centered on background
        self._surface.blit(
            text_surface,
            (self.padding, self.padding)
        )

    def update(self, dt: float, should_show: bool) -> None:
        # Update alpha based on whether hint should be shown
        target_alpha = 255.0 if should_show else 0.0
        self.alpha += (target_alpha - self.alpha) * self.fade_speed * dt
        self.alpha = max(0.0, min(255.0, self.alpha))

    def draw(self, surface: Surface, position: Tuple[int, int]) -> None:
        if self.alpha > 0:
            # Create a copy of the surface with current alpha
            display_surface = self._surface.copy()
            display_surface.set_alpha(int(self.alpha))
            
            # Calculate position (centered above NPC)
            x = position[0] - display_surface.get_width() // 2
            y = position[1] + self.offset_y
            
            surface.blit(display_surface, (x, y))

class NPCManager(BaseModel):
    npcs: List[NPC] = Field(default_factory=list)
    interaction_range: float = Field(default=100.0)
    hint: InteractionHint = Field(default_factory=InteractionHint)
    closest_npc: Optional[NPC] = None
    dialogue_system: DialogueSystem = Field(default_factory=DialogueSystem)
    interaction_menu: InteractionMenu = Field(default_factory=InteractionMenu)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self._add_test_npcs()

    def update(self, dt: float, player_pos: Vector2) -> None:
        """Update all NPCs and interaction systems"""
        # Update individual NPCs
        for npc in self.npcs:
            npc.update(dt)

        # Find closest NPC and update interaction hint
        self.closest_npc = self._get_closest_npc(player_pos)
        show_hint = bool(
            self.closest_npc and 
            self._get_distance(player_pos, self.closest_npc.position) <= self.interaction_range
        )
        self.hint.update(dt, show_hint)
        
        # Update dialogue system
        self.dialogue_system.update(dt)

        # Update interaction menu if visible
        if self.interaction_menu.visible:
            self.interaction_menu.update(dt, pygame.mouse.get_pos())

    def handle_interaction(self, player: Player) -> None:
        """Handle player interaction with closest NPC"""
        if not self.closest_npc:
            return

        if self.dialogue_system.active:
            dialog = self.dialogue_system.dialogue_box
            if dialog.is_complete():
                self.dialogue_system.advance_dialogue()
                if self.dialogue_system.current_message_index >= len(self.dialogue_system.messages):
                    self.interaction_menu.show_for_npc(self.closest_npc, player)
            else:
                dialog.complete_text()
        else:
            print(f"Starting dialogue with {self.closest_npc.npc_type}")
            self.dialogue_system.start_dialogue(self.closest_npc)
            player.reputation.modify(2)

    def draw(self, surface: Surface, camera: Camera) -> None:
        """Draw all NPCs and interaction systems"""
        # Draw NPCs
        for npc in self.npcs:
            npc.draw(surface, camera)
            
            # Draw interaction hint for closest NPC
            if npc == self.closest_npc:
                screen_pos = camera.world_to_screen(npc.position)
                self.hint.draw(surface, (int(screen_pos.x), int(screen_pos.y)))

        # Draw dialogue system
        if self.dialogue_system.active:
            self.dialogue_system.draw(surface)

        # Draw interaction menu
        if self.interaction_menu.visible:
            self.interaction_menu.draw(surface)

    def _get_closest_npc(self, player_pos: Vector2) -> Optional[NPC]:
        """Find the closest NPC within interaction range"""
        if not self.npcs:
            return None

        closest = min(self.npcs,
            key=lambda npc: self._get_distance(player_pos, npc.position)
        )

        return closest if self._get_distance(player_pos, closest.position) <= self.interaction_range else None

    def _get_distance(self, pos1: Vector2, pos2: Vector2) -> float: return pos1.distance_to(pos2)

    def _add_test_npcs(self) -> None:
        """Add test NPCs with their dialogue keys"""
        test_npcs = [
            NPC(position=Vector2(400, 300),
                npc_type=NPCType.MERCHANT,
                dialogue_keys=[f"merchant-{i:02d}" for i in range(1, 6)]),
            NPC(position=Vector2(150, 240),
                npc_type=NPCType.HARBOR_MASTER,
                dialogue_keys=[f"harbor-{i:02d}" for i in range(1, 6)]),
            NPC(position=Vector2(600, 400),
                npc_type=NPCType.TAVERN_KEEPER,
                dialogue_keys=[f"tavern-{i:02d}" for i in range(1, 6)]),
            NPC(position=Vector2(200, 500),
                npc_type=NPCType.WANDERING_MERCHANT,
                dialogue_keys=[f"wanderer-{i:02d}" for i in range(1, 6)])
        ]
        self.npcs.extend(test_npcs)
