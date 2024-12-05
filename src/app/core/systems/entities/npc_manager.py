
from typing import List, Optional
from pydantic import BaseModel, Field
from pygame import Vector2
from app.core.engine.camera import Camera
from app.core.systems.entities.npc import NPC, NPCType
from app.core.systems.interactions.dialogue import DialogueSystem
from app.core.systems.ui.hint import *
from project import int_lang_manager
from app.game.base.player import Player


class NPCManager(BaseModel):
    npcs: List[NPC] = Field(default_factory=list)
    interaction_range: float = Field(default=100.0)
    hint_manager: HintManager = Field(default_factory=HintManager)
    dialogue_system: DialogueSystem = Field(default_factory=DialogueSystem)
    closest_npc: Optional[NPC] = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self._initialize_hints()
        self._add_test_npcs()

    def _initialize_hints(self) -> None:
        """Initialize interaction hints"""
        interaction_hint = Hint(
            text=int_lang_manager.get_text("interact with e"),
            position=HintPosition.ABOVE,
            style=HintStyle(
                font_size=16,
                bg_color=(20, 20, 20),
                bg_alpha=200,
                offset=40,
                fade_speed=3.0
            )
        )
        self.hint_manager.add_hint("interact", interaction_hint)

    def update(self, dt: float, player_pos: Vector2) -> None:
        """Update all NPCs, hints and dialogue"""
        # Update NPCs
        for npc in self.npcs:
            npc.update(dt)

        # Find closest NPC
        self.closest_npc = self._get_closest_npc(player_pos)
        
        # Update hint visibility
        show_hint = bool(
            self.closest_npc and 
            self._get_distance(player_pos, self.closest_npc.position) <= self.interaction_range and
            not self.dialogue_system.active  # Don't show hint during dialogue
        )
    
        match show_hint:
            case True: self.hint_manager.show_hint("interact")
            case False: self.hint_manager.hide_hint("interact")

        # Update hints
        self.hint_manager.update(dt)
        
        # Update dialogue system if active
        if self.dialogue_system.active and self.closest_npc:
            self.dialogue_system.update(dt, player_pos, self.closest_npc.position)

    def handle_interaction(self, player: Player) -> None:
        """Handle player interaction with closest NPC"""
        if not self.closest_npc:
            return

        if self.dialogue_system.active:
            if self.dialogue_system.dialogue_box.is_complete():
                self.dialogue_system.advance_dialogue()
            else:
                self.dialogue_system.dialogue_box.complete_text()
        else:
            self.dialogue_system.start_dialogue(self.closest_npc)
            player.reputation.modify(1)  # Small reputation boost for talking

    def draw(self, surface: Surface, camera: Camera) -> None:
        """Draw NPCs, hints and dialogue"""
        # Draw NPCs
        for npc in self.npcs:
            npc.draw(surface, camera)
        
        # Draw hint if there's a closest NPC
        if self.closest_npc and not self.dialogue_system.active:
            screen_pos = camera.world_to_screen(self.closest_npc.position)
            self.hint_manager.draw(surface, {
                "interact": (int(screen_pos.x), int(screen_pos.y))
            })
            
        # Draw dialogue system
        if self.dialogue_system.active:
            self.dialogue_system.draw(surface)

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
