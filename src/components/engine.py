from pydantic import BaseModel, Field
import pygame
from typing import Optional, Tuple

from components.world.world import World
from components.world import Player
from components.world.world_manager import WorldManager

class Engine(BaseModel):
    display_surface: Optional[pygame.Surface] = Field(default=None)
    world_manager: WorldManager = Field(default_factory=WorldManager)
    clock: pygame.time.Clock = Field(default_factory=pygame.time.Clock)
    player: Player = Field(default_factory=Player)

    class Config:
        arbitrary_types_allowed = True

    def initialize_display(self, surface: pygame.Surface):
        self.display_surface = surface
        self.world_manager.create_world("main", 'some-map.tmx')
        current_world = self.world_manager.get_current_world()
        if current_world:
            map_size = current_world.get_map_size()
            self.player.position = pygame.math.Vector2(map_size[0] // 2, map_size[1] // 2)

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_positions()

    def reset_positions(self):
        current_world = self.world_manager.get_current_world()
        if current_world:
            map_size = current_world.get_map_size()
            self.player.position = pygame.math.Vector2(map_size[0] // 2, map_size[1] // 2)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        
        current_world = self.world_manager.get_current_world()
        if current_world:
            self.player.move(dx, dy, current_world.get_map_size())

    def run(self, dt: float) -> None:
        if self.display_surface is None or self.world_manager is None:
            raise ValueError("Display surface or WorldManager not initialized. Call initialize_display() first.")
    
        self.event_loop()
        self.handle_input()
        self.world_manager.update(dt)

        self.display_surface.fill((0, 0, 0))  # Clear the screen
        
        current_world: World = self.world_manager.get_current_world()
        if current_world:
            current_world.draw(self.display_surface)
            
            # Draw the player
            player_surface = pygame.Surface((32, 32))
            player_surface.fill((255, 0, 0))  # Red square for the player
            player_rect = player_surface.get_rect(center=self.player.position)
            self.display_surface.blit(player_surface, player_rect)
        else:
            pygame.draw.rect(self.display_surface, (255, 0, 0), pygame.Rect(0, 0, 128, 128))

        self.world_manager.draw_debug_info(self.display_surface, current_world, dt)

        pygame.display.flip()