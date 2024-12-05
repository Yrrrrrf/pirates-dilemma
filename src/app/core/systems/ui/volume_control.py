#  app/game/ui/volume_control.py
from typing import Tuple, Callable
import pygame
from pygame import Surface, Rect

from app.core.systems.menu.base import MenuItem, UITheme
from app.core.systems.menu.renderer import MenuRenderer
from tools.audio import AudioManager, AudioType

class VolumeControl(MenuItem):
    def __init__(self, 
                 text_key: str,
                 theme: UITheme,
                 renderer: MenuRenderer,
                 audio_type: AudioType):
        super().__init__(text_key, theme, lambda: None)
        self.renderer = renderer
        self.audio_type = audio_type
        self.audio_manager = AudioManager()
        self.slider_width = 200
        self.slider_height = 10
        self.handle_radius = 8
        self.is_dragging = False

    def render(self, surface: Surface) -> None:
        if not self.is_visible:
            return

        screen_width = surface.get_width()
        screen_center = screen_width // 2

        # Render label
        label_color = (
            self.theme.highlight_color if self.is_selected else
            self.theme.text_color
        )
        label_rect = self.renderer.render_text(
            self.text,
            'option',
            label_color,
            (screen_center - self.slider_width//2 - 100, self.position[1]),
            surface,
            centered=False
        )

        # Calculate slider position
        slider_x = screen_center - self.slider_width//2 + 100
        slider_y = self.position[1] + label_rect.height//2

        # Draw slider background
        slider_rect = Rect(slider_x, slider_y - self.slider_height//2,
                         self.slider_width, self.slider_height)
        pygame.draw.rect(surface, self.theme.text_color, slider_rect)

        # Get current volume
        volume = self._get_current_volume()
        
        # Draw filled portion
        filled_width = int(self.slider_width * volume)
        filled_rect = Rect(slider_x, slider_y - self.slider_height//2,
                          filled_width, self.slider_height)
        pygame.draw.rect(surface, self.theme.highlight_color, filled_rect)

        # Draw handle
        handle_x = slider_x + filled_width
        handle_y = slider_y
        pygame.draw.circle(surface, self.theme.highlight_color,
                         (handle_x, handle_y), self.handle_radius)

        # Store the slider's rect for interaction
        self.rect = Rect(slider_x - self.handle_radius,
                        slider_y - self.handle_radius,
                        self.slider_width + self.handle_radius * 2,
                        self.handle_radius * 2)

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        if not self.rect or not self.is_enabled or not self.is_visible:
            return False

        if self.rect.collidepoint(pos):
            self.is_dragging = True
            self._update_volume(pos[0])
            return True
        return False

    def handle_drag(self, pos: Tuple[int, int]) -> None:
        """Handle mouse drag for volume adjustment"""
        if self.is_dragging:
            self._update_volume(pos[0])

    def handle_release(self) -> None:
        """Handle mouse release"""
        self.is_dragging = False

    def _update_volume(self, x_pos: int) -> None:
        """Update volume based on slider position"""
        slider_start = self.rect.left + self.handle_radius
        slider_end = self.rect.right - self.handle_radius
        volume = (x_pos - slider_start) / (slider_end - slider_start)
        volume = max(0.0, min(1.0, volume))
        
        # Update volume in audio manager
        self.audio_manager.set_type_volume(self.audio_type, volume)
        
        # Play test sound for UI volume changes
        if self.audio_type == AudioType.UI:
            self.audio_manager.play_sound("click.mp3", AudioType.UI)

    def _get_current_volume(self) -> float:
        """Get current volume for this control's audio type"""
        if self.audio_type == AudioType.MUSIC:
            return self.audio_manager.config.music_volume
        elif self.audio_type == AudioType.UI:
            return self.audio_manager.config.ui_volume
        elif self.audio_type == AudioType.EFFECT:
            return self.audio_manager.config.effects_volume
        elif self.audio_type == AudioType.AMBIENT:
            return self.audio_manager.config.ambient_volume
        return 1.0

