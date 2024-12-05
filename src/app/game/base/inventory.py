from enum import Enum
import os
from typing import List, Optional, Tuple
import pygame
from pydantic import BaseModel, Field

class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    QUEST = "quest"

    @property
    def color(self) -> Tuple[int, int, int]:
        """Get color associated with item type"""
        return {
            ItemType.WEAPON: (255, 64, 64),      # Red
            ItemType.ARMOR: (64, 128, 255),      # Blue
            ItemType.CONSUMABLE: (64, 255, 128),  # Green
            ItemType.QUEST: (255, 255, 64)        # Yellow
        }[self]

class Item(BaseModel):
    id: str
    name: str
    type: ItemType
    description: str
    value: int
    stackable: bool = False
    quantity: int = 1
    image_path: Optional[str] = None
    _surface: Optional[pygame.Surface] = None

    class Config:
        arbitrary_types_allowed = True

    def get_surface(self, size: Tuple[int, int] = (48, 48)) -> pygame.Surface:
        """Get or create item's surface representation"""
        if self._surface is None:
            if self.image_path and os.path.exists(self.image_path):
                self._surface = pygame.image.load(self.image_path).convert_alpha()
                self._surface = pygame.transform.scale(self._surface, size)
            else:
                self._surface = self._create_default_surface(size)
        return self._surface

    def _create_default_surface(self, size: Tuple[int, int]) -> pygame.Surface:
        """Create a default visual representation for items without images"""
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        # Draw background with type color
        color = (*self.type.color, 180)
        pygame.draw.rect(surface, color, surface.get_rect(), border_radius=8)
        
        # Draw border
        pygame.draw.rect(surface, (255, 255, 255, 128), surface.get_rect(), width=2, border_radius=8)
        
        # Add first letter of item type
        font = pygame.font.Font(None, size[0] // 2)
        text = font.render(self.type.value[0].upper(), True, (255, 255, 255))
        text_rect = text.get_rect(center=(size[0]//2, size[1]//2))
        surface.blit(text, text_rect)
        
        return surface

class Inventory(BaseModel):
    items: List[Item] = Field(default_factory=list)
    capacity: int = Field(default=20)
    visible: bool = Field(default=False)
    selected_index: int = Field(default=-1)
    grid_size: Tuple[int, int] = Field(default=(5, 4))
    cell_size: Tuple[int, int] = Field(default=(64, 64))
    padding: int = Field(default=10)
    
    # Visual settings
    background_color: Tuple[int, int, int, int] = (20, 20, 20, 230)
    border_color: Tuple[int, int, int] = (64, 64, 64)
    highlight_color: Tuple[int, int, int] = (255, 255, 255)
    
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        # todo: Add some default items for testing
        self.items = [
            Item(id="sword", name="Sword", type=ItemType.WEAPON, description="A sharp sword", value=10, stackable=False),
            Item(id="sword", name="Sword", type=ItemType.WEAPON, description="A sharp sword", value=10, stackable=False),
            Item(id="shield", name="Shield", type=ItemType.ARMOR, description="A sturdy shield", value=15, stackable=False),
            Item(id="potion", name="Potion", type=ItemType.CONSUMABLE, description="A healing potion", value=5, stackable=True, quantity=3),
            Item(id="key", name="Key", type=ItemType.QUEST, description="A mysterious key", value=0, stackable=False)
        ]

    def toggle_visibility(self) -> None:
        """Toggle inventory visibility"""
        self.visible = not self.visible
        self.selected_index = -1  # Reset selection when toggling

    def add_item(self, item: Item) -> bool:
        if len(self.items) >= self.capacity:
            return False
            
        if item.stackable:
            for existing_item in self.items:
                if existing_item.id == item.id:
                    existing_item.quantity += item.quantity
                    return True
                    
        self.items.append(item)
        return True

    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        for item in self.items:
            if item.id == item_id:
                if item.stackable:
                    if item.quantity <= quantity:
                        self.items.remove(item)
                    else:
                        item.quantity -= quantity
                else:
                    self.items.remove(item)
                return True
        return False

    def get_item(self, item_id: str) -> Optional[Item]:
        return next((item for item in self.items if item.id == item_id), None)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the inventory interface if visible"""
        if not self.visible: return

        screen_width, screen_height = surface.get_size()
        grid_width, grid_height = self.grid_size
        cell_width, cell_height = self.cell_size
        
        # Calculate inventory panel dimensions and position
        inv_width = (cell_width + self.padding) * grid_width + self.padding
        inv_height = (cell_height + self.padding) * grid_height + self.padding
        inv_x = (screen_width - inv_width) // 2
        inv_y = (screen_height - inv_height) // 2
        
        # Draw semi-transparent background
        background = pygame.Surface((inv_width, inv_height), pygame.SRCALPHA)
        pygame.draw.rect(background, self.background_color, 
                        background.get_rect(), border_radius=10)
        surface.blit(background, (inv_x, inv_y))
        
        # Draw grid cells
        for y in range(grid_height):
            for x in range(grid_width):
                cell_index = y * grid_width + x
                cell_x = inv_x + x * (cell_width + self.padding) + self.padding
                cell_y = inv_y + y * (cell_height + self.padding) + self.padding
                
                # Draw cell background
                cell_rect = pygame.Rect(cell_x, cell_y, cell_width, cell_height)
                pygame.draw.rect(surface, self.border_color, cell_rect, 
                               border_radius=8)
                
                # Draw item if exists
                if cell_index < len(self.items):
                    item = self.items[cell_index]
                    item_surface = item.get_surface((cell_width-12, cell_height-12))
                    surface.blit(item_surface, 
                               (cell_x + 6, cell_y + 6))
                    
                    # Draw quantity for stackable items
                    if item.stackable and item.quantity > 1:
                        font = pygame.font.Font(None, 20)
                        qty_text = font.render(str(item.quantity), True, (255, 255, 255))
                        surface.blit(qty_text, (cell_x + cell_width - 20, cell_y + cell_height - 20))
                
                # Highlight selected cell
                if cell_index == self.selected_index:
                    pygame.draw.rect(surface, self.highlight_color, cell_rect, 
                                   width=2, border_radius=8)
        
        # Draw tooltip for selected item
        if 0 <= self.selected_index < len(self.items):
            self._draw_tooltip(surface, self.items[self.selected_index], 
                             pygame.mouse.get_pos())

    def _draw_tooltip(self, surface: pygame.Surface, item: Item, pos: Tuple[int, int]) -> None:
        """Draw item tooltip with details"""
        font = pygame.font.Font(None, 24)
        tooltip_padding = 10
        line_height = 25
        
        # Prepare tooltip text
        lines = [
            f"{item.name} ({item.type.value})",
            f"Value: {item.value}",
            f"{item.description}"
        ]
        
        # Calculate tooltip dimensions
        max_width = max(font.size(line)[0] for line in lines)
        tooltip_width = max_width + tooltip_padding * 2
        tooltip_height = len(lines) * line_height + tooltip_padding * 2
        
        # Adjust position to keep tooltip on screen
        x, y = pos
        screen_width, screen_height = surface.get_size()
        if x + tooltip_width > screen_width: x = screen_width - tooltip_width
        if y + tooltip_height > screen_height: y = screen_height - tooltip_height

        # Draw tooltip background
        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
        pygame.draw.rect(tooltip_surface, (20, 20, 20, 230), tooltip_surface.get_rect(), border_radius=5)
        pygame.draw.rect(tooltip_surface, item.type.color + (255,), tooltip_surface.get_rect(), width=1, border_radius=5)
        
        # Draw tooltip text
        for i, line in enumerate(lines):
            text = font.render(line, True, (255, 255, 255))
            tooltip_surface.blit(text, (tooltip_padding, tooltip_padding + i * line_height))
        
        surface.blit(tooltip_surface, (x, y))

    def handle_click(self, pos: Tuple[int, int]) -> None:
        """Handle mouse click in inventory grid"""
        if not self.visible:
            return

        screen_width, screen_height = pygame.display.get_surface().get_size()
        grid_width, grid_height = self.grid_size
        cell_width, cell_height = self.cell_size
        
        inv_width = (cell_width + self.padding) * grid_width + self.padding
        inv_height = (cell_height + self.padding) * grid_height + self.padding
        inv_x = (screen_width - inv_width) // 2
        inv_y = (screen_height - inv_height) // 2
        
        # Convert click position to grid coordinates
        rel_x = pos[0] - inv_x - self.padding
        rel_y = pos[1] - inv_y - self.padding
        
        if rel_x < 0 or rel_y < 0:
            self.selected_index = -1
            return
            
        grid_x = rel_x // (cell_width + self.padding)
        grid_y = rel_y // (cell_height + self.padding)
        
        if 0 <= grid_x < grid_width and 0 <= grid_y < grid_height:
            self.selected_index = grid_y * grid_width + grid_x
            if self.selected_index >= len(self.items):
                self.selected_index = -1
        else:
            self.selected_index = -1
