from pydantic import BaseModel, Field
import pygame
from typing import Optional

from components.world.world_manager import WorldManager
from components.rendering.camera import Camera

class Engine(BaseModel):
    display_surface: Optional[pygame.Surface] = Field(default=None)
    world_manager: WorldManager = Field(default_factory=WorldManager)
    clock: pygame.time.Clock = Field(default_factory=pygame.time.Clock)
    camera: Camera = Field(default_factory=Camera)

    class Config:
        arbitrary_types_allowed = True

    def initialize_display(self, surface: pygame.Surface):
        self.display_surface = surface

        # * Create the main world
        self.world_manager.create_world("main", 'some-map.tmx')
        # self.world_manager.create_world("main")
        # self.world_manager.set_water_row(1)  # * set a default row for the water

    def event_loop(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.KEYDOWN:
                    match event.key:
                        case _: pass  # do anything ...


    # todo: Move this fn to the camera class
    def handle_input(self):
        keys = pygame.key.get_pressed()  # Get the state of all keys
        
        # d: Callable = lambda k1, k2: keys[k1] - keys[k2]
        # self.camera.move(d(pygame.K_d, pygame.K_a), d(pygame.K_s, pygame.K_w))
        
        # * Same as above w/ a more readable format (commented out for reference)
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        self.camera.move(dx, dy)

    def run(self, dt: float) -> None:
        if self.display_surface is None or self.world_manager is None:
            raise ValueError("Display surface or WorldManager not initialized. Call initialize_display() first.")
        
        self.handle_input()
        self.world_manager.update(dt)

        self.display_surface.fill((0, 0, 0))  # Clear the screen
        
        # Draw the world
        current_world = self.world_manager.worlds.get(self.world_manager.current_world)
        if current_world:
            current_world.draw(self.display_surface, self.camera)
        
        # Draw camera position for debugging
        debug_font = pygame.font.Font(None, 24)
        camera_pos = debug_font.render(f"Camera: ({int(self.camera.position.x)}, {int(self.camera.position.y)})", True, (255, 255, 255))
        self.display_surface.blit(camera_pos, (10, 70))

        self.camera.draw_fps(self.display_surface, dt)

        pygame.display.flip()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        self.camera.move(dx, dy)

        # Add a key to reset camera position
        if keys[pygame.K_r]:
            self.camera.reset_position()