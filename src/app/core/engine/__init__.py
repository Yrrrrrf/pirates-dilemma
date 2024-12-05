# app/core/engine/core.py
from typing import Optional, Dict, Any
import pygame
from pydantic import BaseModel, Field

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

    class Config:
        arbitrary_types_allowed = True

    def initialize(self, surface: pygame.Surface) -> None:
        """Initialize the engine with a display surface"""
        self.display_surface = surface
        # Initialize any required systems here
        def init_systems():
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

        self.display_surface.fill((0, 0, 0))

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

    def handle_click(self, event: pygame.event.Event) -> None:
        """Handle mouse click events"""
        match event.button:
            case 1: print("Left click")
            case 2: print("Middle click")
            case 3: print("Right click")

    def run(self) -> None:
        """Main game loop"""
        if not self.display_surface:
            raise ValueError("Engine not initialized. Call initialize() first.")

        dt = self.clock.tick(self.state.fps) / 1000.0
        self.update(dt)
        self.render()

    def cleanup(self) -> None:
        """Clean up engine resources"""
        # Cleanup systems
        for system in self.systems.values():
            if hasattr(system, 'cleanup'):
                system.cleanup()

        # Reset engine state
        self.state = EngineState()
        self.systems.clear()