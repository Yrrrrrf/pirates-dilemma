import pygame
from pydantic import BaseModel, Field
from typing import Tuple

class Camera(BaseModel):
    position: pygame.math.Vector2 = Field(default_factory=lambda: pygame.math.Vector2(0, 0))
    target: pygame.math.Vector2 = Field(default_factory=lambda: pygame.math.Vector2(0, 0))
    viewport_size: Tuple[int, int] = Field(default=(800, 600))
    map_size: Tuple[int, int] = Field(default=(2000, 2000))
    lerp_speed: float = Field(default=0.1)
    font: pygame.font.Font = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)

    def set_target(self, target: pygame.math.Vector2):
        self.target = pygame.math.Vector2(target)  # Create a new Vector2 to avoid reference issues

    def update(self):
        # Calculate the desired camera position (center on target)
        desired_x = self.target.x - self.viewport_size[0] // 2
        desired_y = self.target.y - self.viewport_size[1] // 2

        # Clamp the camera position to map boundaries
        max_x = max(0, self.map_size[0] - self.viewport_size[0])
        max_y = max(0, self.map_size[1] - self.viewport_size[1])
        desired_x = max(0, min(desired_x, max_x))
        desired_y = max(0, min(desired_y, max_y))

        # Lerp towards the desired position
        self.position.x += (desired_x - self.position.x) * self.lerp_speed
        self.position.y += (desired_y - self.position.y) * self.lerp_speed

        # Ensure the camera position is always an integer to avoid subpixel rendering issues
        self.position.x = round(self.position.x)
        self.position.y = round(self.position.y)

    def get_offset(self) -> Tuple[int, int]:
        return -int(self.position.x), -int(self.position.y)

    def apply(self, target_rect: pygame.Rect) -> pygame.Rect:
        return target_rect.move(self.get_offset())

    def set_viewport_size(self, size: Tuple[int, int]):
        self.viewport_size = size

    def set_map_size(self, size: Tuple[int, int]):
        self.map_size = size
