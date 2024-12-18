# app/core/engine/core.py
from typing import Optional, Dict, Any
import pygame
from pydantic import BaseModel, Field

from app.core.engine.world import WorldManager
from tools.audio import AudioType, audio_manager

class EngineState(BaseModel):
    """Holds the current state of the game engine"""
    debug: bool = Field(default=False)
    fps: int = Field(default=60)
    delta_time: float = Field(default=0.0)

class Engine(BaseModel):
    """Core game engine handling basic game loop and state management"""
    state: EngineState = Field(default_factory=EngineState)
    display_surface: Optional[pygame.Surface] = Field(default=None)
    clock: pygame.time.Clock = Field(default_factory=pygame.time.Clock)
    # * Store modules/systems that can be added to the engine
    systems: Dict[str, Any] = Field(default_factory=dict)  # * Add systems dictionary
    world_manager: Optional[WorldManager] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def init(self, surface: pygame.Surface) -> None:
        """Initialize the engine with a display surface"""
        self.display_surface = surface

        self.world_manager = WorldManager()
        # self.world_manager.create_world("main", 'main-map.tmx')
        self.world_manager.create_world("main", 'main-copy.tmx')
        # Initialize any required systems here
        def init_systems():
            # * init audio system
            audio_manager.play_sound("env\\env-00.mp3", AudioType.UI)
            pass

        init_systems()
        print(f"\033[92mEngine Initialized\033[0m")

    def add_system(self, name: str, system: Any) -> None: self.systems[name] = system

    def get_system(self, name: str) -> Optional[Any]: return self.systems.get(name)

    def update(self, dt: float) -> None:
        if not self.display_surface: return
        self.state.delta_time = dt # Update delta time
        [system.update(dt) for system in self.systems.values() if hasattr(system, 'update')]

    def render(self) -> None:
        """Render the current frame"""
        if not self.display_surface: return

        # * Render all systems
        [system.render(self.display_surface) for system in self.systems.values() if hasattr(system, 'render')]
        pygame.display.flip()  # Flip display (update screen)

    def handle_keydown(self, event: pygame.event.Event) -> None:
        """Handle keyboard events"""
        match event.key:
            # todo: Add some debug overlay...
            case pygame.K_F3:
                print("Toggling debug mode")
                self.state.debug ^= True  # Toggle debug mode (XOR)

    def handle_keydown(self, event: pygame.event.Event):
        if self.world_manager.npc_manager:
            npc_manager = self.world_manager.npc_manager
            if npc_manager.dialogue_system.active:
                npc_manager.dialogue_system.handle_input(event)

        match event.key:
            case pygame.K_i: self.world_manager.player.inventory.toggle_visibility()
            case pygame.K_e: 
                if self.world_manager.npc_manager:
                    # self.world_manager.npc_manager.dialogue_system.handle_input(event)
                    self.world_manager.npc_manager.handle_interaction(self.world_manager.player)
            case pygame.K_SPACE:
                if self.world_manager.npc_manager and self.world_manager.npc_manager.dialogue_system.active:
                    dialogue_box = self.world_manager.npc_manager.dialogue_system.dialogue_box
                    if dialogue_box.is_complete():
                        self.world_manager.npc_manager.dialogue_system.advance_dialogue()
                    else:
                        dialogue_box.complete_text()

    def handle_click(self, event: pygame.event.Event):
        if self.world_manager.npc_manager:
            npc_manager = self.world_manager.npc_manager
            if npc_manager.dialogue_system.active and npc_manager.dialogue_system.menu_active:
                npc_manager.dialogue_system.handle_input(event)

        match event.button:
            case 1:  # Left click
                # First check if dialogue system is active
                if (self.world_manager.npc_manager and 
                    self.world_manager.npc_manager.dialogue_system.active):
                    if self.world_manager.npc_manager.dialogue_system.menu_active:
                        # Handle menu clicks
                        self.world_manager.npc_manager.dialogue_system.menu.handle_click(event.pos)
                        return
                
                # If no dialogue is active, handle inventory clicks
                self.world_manager.player.inventory.handle_click(event.pos)
            
            case 2: print("Middle mouse button click")
            case 3: print("Right mouse button click")


    def run(self) -> None:
        """Main game loop"""
        if not self.display_surface:
            raise ValueError("Engine not initialized. Call initialize() first.")

        dt = self.clock.tick(self.state.fps) / 1000.0
        self.update(dt)
        self.render()

        self.display_surface.fill((0, 0, 0))  # Clear the screen
        self.world_manager.update(dt)  # Update the world
        self.world_manager.draw(self.display_surface)

        pygame.display.flip()


    def cleanup(self) -> None:
        """Clean up engine resources"""
        # Cleanup systems
        for system in self.systems.values():
            if hasattr(system, 'cleanup'):
                system.cleanup()

        # Reset engine state
        self.state = EngineState()
        self.systems.clear()
