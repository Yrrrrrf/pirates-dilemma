from pydantic import BaseModel, Field
import pygame
import psutil
from typing import Optional

from app.world import WorldManager
from app.game_ui import GameUI
from project.settings.lang import Language
from project.settings import Settings

class Engine(BaseModel):
    display_surface: Optional[pygame.Surface] = Field(default=None)
    world_manager: WorldManager = Field(default_factory=WorldManager)
    clock: pygame.time.Clock = Field(default_factory=pygame.time.Clock)
    ui: Optional[GameUI] = Field(default=None)  # Add GameUI field

    class Config:
        arbitrary_types_allowed = True

    def initialize_display(self, surface: pygame.Surface):
        # Initialize the display surface and the world manager
        self.display_surface = surface
        # todo: Change the map file to 'big-map.tmx' to test the big map
        self.world_manager.create_world("main", 'big-map.tmx')
        # self.world_manager.create_world("main", 'mapp.tmx')

        # * Initialize the UI
        # settings: Settings = Settings(language=Language.SPANISH)
        settings: Settings = Settings(language=Language.ENGLISH)
        self.ui = GameUI(surface.get_size(), settings=settings)

    def load_debug_font(self, font_name: str = None, font_size: int = 18):
            """Load the font for displaying debug information."""
            # Load a system font or a custom font if specified
            if font_name: return pygame.font.Font(font_name, font_size)
            else: return pygame.font.SysFont('Arial', font_size)  # Default to Arial if no font specified

    def draw_debug(self):
        """Draw compact system performance info at the top of the screen."""
        # Get performance data
        fps = int(self.clock.get_fps())
        cpu_load = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        memory_usage = memory_info.percent
        elapsed_time = pygame.time.get_ticks() // 1000

        compact_info = (
            f"FPS: {fps:3d} | "
            f"CPU: {cpu_load:04.1f}% | "
            f"Mem: {memory_usage:04.1f}% | "
            f"Time: {elapsed_time//3600:02d}:{(elapsed_time%3600)//60:02d}:{elapsed_time%60:02d}:{pygame.time.get_ticks()%1000:03d}"
        )

        # Define text position and colors
        text_x, text_y = 10, 10
        text_color = (255, 255, 255)
        shadow_color = (0, 0, 0)
        bg_color = (0, 0, 0, 128)

        # Render the compact info text
        compact_font = self.load_debug_font()
        compact_surface = compact_font.render(compact_info, True, text_color)
        shadow_surface = compact_font.render(compact_info, True, shadow_color)

        text_width, text_height = compact_surface.get_size()

        # Draw a semi-transparent background rectangle
        background_rect = pygame.Rect(text_x - 5, text_y - 5, text_width + 10, text_height + 10)
        pygame.draw.rect(self.display_surface, bg_color, background_rect)

        # Glow/Shadow Effect
        shadow_offsets = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        for offset in shadow_offsets:
            self.display_surface.blit(shadow_surface, (text_x + offset[0], text_y + offset[1]))

        # Draw the main text
        self.display_surface.blit(compact_surface, (text_x, text_y))

        # Update the clock
        self.clock.tick()

    def run(self, dt: float):
        if self.display_surface is None or self.world_manager.current_world is None:
            raise ValueError("Display surface or World not initialized. Call initialize_display() first.")
    
        self.world_manager.update(dt)

        self.display_surface.fill((0, 0, 0))  # Clear the screen
        self.world_manager.draw(self.display_surface)
        self.world_manager.draw_debug(self.display_surface, dt)
        
        self.ui.draw(self.display_surface)  # Draw the UI

        pygame.display.flip()
        return True
