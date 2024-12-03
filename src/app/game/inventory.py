from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    QUEST = "quest"

class Item(BaseModel):
    id: str
    name: str
    type: ItemType
    description: str
    value: int
    stackable: bool = False
    quantity: int = 1
    image_path: Optional[str] = None

class Inventory(BaseModel):
    items: List[Item] = Field(default_factory=list)
    capacity: int = Field(default=20)

    def add_item(self, item: Item) -> bool:
        """Add an item to inventory. Returns True if successful."""
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
        """Remove an item from inventory. Returns True if successful."""
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
        """Get an item from inventory without removing it."""
        return next((item for item in self.items if item.id == item_id), None)
