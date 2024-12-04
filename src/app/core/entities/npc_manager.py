from typing import List, Optional, Tuple
import pygame
from pydantic import BaseModel, Field
from pygame import Surface, font
from pygame.math import Vector2

from app.core.entities.npc import NPC, NPCType
from app.core.camera import Camera
from app.game.player import Player
from app.rules.dialogue_system import DialogueSystem
from utils import AssetManager


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
    interaction_range: float = Field(default=100.0)  # Range for interaction in pixels
    hint: InteractionHint = Field(default_factory=InteractionHint)
    closest_npc: Optional[NPC] = None
    dialogue_system: DialogueSystem = Field(default_factory=DialogueSystem)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        # Add some test NPCs
        self._add_test_npcs()

    def _add_test_npcs(self) -> None:
        """Add test NPCs with their dialogue keys"""
        test_npcs = [
            # Merchant at the market
            NPC(
                position=Vector2(400, 300),
                npc_type=NPCType.MERCHANT,
                dialogue_keys=[f"merchant-{i:02d}" for i in range(1, 6)]
            ),
            # # Harbor Master
            # NPC(
            #     position=Vector2(150, 240),
            #     npc_type=NPCType.HARBOR_MASTER,
            #     dialogue_keys=[f"harbor-{i:02d}" for i in range(1, 6)]
            # ),
            # # Tavern Keeper
            # NPC(
            #     position=Vector2(600, 400),
            #     npc_type=NPCType.TAVERN_KEEPER,
            #     dialogue_keys=[f"tavern-{i:02d}" for i in range(1, 6)]
            # ),
            # # Wandering Merchant
            # NPC(
            #     position=Vector2(200, 500),
            #     npc_type=NPCType.WANDERING_MERCHANT,
            #     dialogue_keys=[f"wanderer-{i:02d}" for i in range(1, 6)]
            # )
        ]
        self.npcs.extend(test_npcs)

    def update(self, dt: float, player_pos: Vector2) -> None:
        for npc in self.npcs: npc.update(dt)

        # Find closest NPC and update interaction hint
        self.closest_npc = self._get_closest_npc(player_pos)
        show_hint = bool(
            self.closest_npc and 
            self._get_distance(player_pos, self.closest_npc.position) <= self.interaction_range
        )
        self.hint.update(dt, show_hint)
        self.dialogue_system.update(dt)

    def handle_interaction(self, 
        player: Player
    ) -> None:
        if not self.closest_npc: return  # * No NPC in range (early exit)
        self.dialogue_system.start_dialogue(self.closest_npc)
        player.reputation.modify(2)

    def draw(self, surface: Surface, camera: Camera) -> None:
        # Draw all NPCs
        for npc in self.npcs:
            # Convert world position to screen position
            screen_pos = camera.world_to_screen(npc.position)
            
            # Draw NPC (temporary representation)
            pygame.draw.circle(surface, (0, 255, 0), (int(screen_pos.x), int(screen_pos.y)), 20)
            
            # If this is the closest NPC and in range, draw the interaction hint
            if npc == self.closest_npc:
                self.hint.draw(surface, (int(screen_pos.x), int(screen_pos.y)))

        # Draw dialogue box
        if self.dialogue_system.active:
            self.dialogue_system.draw(surface)


    def _get_closest_npc(self, player_pos: Vector2) -> Optional[NPC]:
        if not self.npcs:
            return None

        closest = min(
            self.npcs,
            key=lambda npc: self._get_distance(player_pos, npc.position)
        )
        return closest if self._get_distance(player_pos, closest.position) <= self.interaction_range else None

    def _get_distance(self, pos1: Vector2, pos2: Vector2) -> float:
        return pos1.distance_to(pos2)
