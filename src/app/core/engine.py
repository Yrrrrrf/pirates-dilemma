# stdlib
from typing import Optional
# third party
import pygame
from pydantic import BaseModel, Field
# local
from app.core.world import WorldManager


class Engine(BaseModel):
    display_surface: Optional[pygame.Surface] = Field(default=None)
    world_manager: WorldManager = Field(default_factory=WorldManager)
    clock: pygame.time.Clock = Field(default_factory=pygame.time.Clock)

    class Config:
        arbitrary_types_allowed = True

    def initialize_display(self, surface: pygame.Surface):
        self.display_surface = surface
        # todo: Change the map file to 'big-map.tmx' to test the big map
        self.world_manager.create_world("main", 'big-map.tmx')
        # self.world_manager.create_world("main", 'mapp.tmx')

    def run(self, dt: float):
        if self.display_surface is None or self.world_manager.current_world is None:
            raise ValueError("Display surface or World not initialized. Call initialize_display() first.")
    
        self.display_surface.fill((0, 0, 0))  # Clear the screen
        self.world_manager.update(dt)  # Update the world
        self.world_manager.draw(self.display_surface)

        pygame.display.flip()
        return True

    def handle_keydown(self, event: pygame.event.Event):
        # Handle interaction menu clicks
        if self.world_manager.npc_manager and self.world_manager.npc_manager.interaction_menu.visible:
            self.world_manager.npc_manager.interaction_menu.handle_click(event)

        match event.key:
            case pygame.K_i: self.world_manager.player.inventory.toggle_visibility()
            case pygame.K_e: self.world_manager.npc_manager.handle_interaction(self.world_manager.player)
            case pygame.K_SPACE:  # dialogue system...
                dialogue_box = self.world_manager.npc_manager.dialogue_system.dialogue_box
                match dialogue_box.is_complete():
                    case True: self.world_manager.npc_manager.dialogue_system.advance_dialogue()
                    case False: dialogue_box.complete_text()

    def handle_click(self, event: pygame.event.Event):
        match event.button:
            case 1: 
                self.world_manager.player.inventory.handle_click(event.pos)
            case 2: print("Impl: Middle mouse button click")
            case 3: print("Impl: Right mouse button click")
