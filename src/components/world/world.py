from pydantic import BaseModel, Field
import pygame
from typing import List, Tuple

# * Represents of a water tile (used for the background)
class Water(BaseModel):
    sprite_sheet: pygame.Surface = Field(...)
    tile_size: int = Field(...)
    animation_speed: float = Field(...)
    animation_time: float = Field(default=0)
    current_frame: int = Field(default=0)
    frames: List[List[pygame.Surface]] = Field(default_factory=list)
    selected_row: int = Field(default=0)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.frames = self.split_sprite_sheet()

    def split_sprite_sheet(self) -> List[List[pygame.Surface]]:
        frames = []
        sheet_width = self.sprite_sheet.get_width()
        sheet_height = self.sprite_sheet.get_height()
        for y in range(0, sheet_height, self.tile_size):
            row = []
            for x in range(0, sheet_width, self.tile_size):
                frame = self.sprite_sheet.subsurface((x, y, self.tile_size, self.tile_size))
                row.append(frame)
            frames.append(row)
        return frames

    def update(self, dt: float) -> None:
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(self.frames[0])
            self.animation_time = 0

    def get_tile(self) -> pygame.Surface:
        return self.frames[self.selected_row][self.current_frame]

    def draw(self, surface: pygame.Surface, position: Tuple[int, int]) -> None:
        surface.blit(self.get_tile(), position)

    def set_row(self, row: int) -> None:
        if 0 <= row < len(self.frames):
            self.selected_row = row

# * Represents of the game World<map + entities>
# Field(...) means that the field is required, and the value cannot be None
from components.rendering.camera import Camera

class World(BaseModel):
    size: Tuple[int, int] = Field(...)
    tile_size: int = Field(...)
    water: Water = Field(...)

    class Config:
        arbitrary_types_allowed = True

    def update(self, dt: float):
        self.water.update(dt)

    def draw(self, surface: pygame.Surface, camera: Camera):
        visible_area = pygame.Rect(camera.position, surface.get_size())
        start_x = max(0, int(camera.position.x // self.tile_size))
        start_y = max(0, int(camera.position.y // self.tile_size))
        end_x = min(self.size[0], start_x + surface.get_width() // self.tile_size + 2)
        end_y = min(self.size[1], start_y + surface.get_height() // self.tile_size + 2)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                if visible_area.colliderect(tile_rect):
                    screen_pos = camera.apply(tile_rect)
                    self.water.draw(surface, screen_pos.topleft)
