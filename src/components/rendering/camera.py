from dataclasses import dataclass
import pygame
from typing import List

from components.world import World

class YSortCamera:
    """
    A camera that sorts sprites based on their Y-coordinate for depth effect.
    """
    def __init__(self, target: pygame.sprite.Sprite, screen_size: tuple[int, int]):
        self.target = target
        self.offset = pygame.math.Vector2(0, 0)
        self.screen_size = screen_size
        self.zoom = 1.0

    def update(self):
        """Update camera position to follow the target."""
        self.offset.x = self.target.rect.centerx - self.screen_size[0] // 2
        self.offset.y = self.target.rect.centery - self.screen_size[1] // 2

    def apply(self, sprite: pygame.sprite.Sprite) -> pygame.Rect:
        """Apply camera offset to a sprite's position."""
        return pygame.Rect(
            (sprite.rect.x - self.offset.x) * self.zoom,
            (sprite.rect.y - self.offset.y) * self.zoom,
            sprite.rect.width * self.zoom,
            sprite.rect.height * self.zoom
        )

    def draw_sprites(self, surface: pygame.Surface, sprites: List[pygame.sprite.Sprite]):
        """Draw sprites sorted by their Y-coordinate."""
        sorted_sprites = sorted(sprites, key=lambda sprite: sprite.rect.bottom)
        for sprite in sorted_sprites:
            adjusted_rect = self.apply(sprite)
            scaled_image = pygame.transform.scale(sprite.image, adjusted_rect.size)
            surface.blit(scaled_image, adjusted_rect)
