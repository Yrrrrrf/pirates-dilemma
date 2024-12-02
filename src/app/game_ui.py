import pygame
from pygame import Surface, Rect, Color
from typing import Tuple, List
from project.settings import Settings
from project.settings.lang import LanguageManager
from utils import AssetManager


class InventoryItem:
    def __init__(self, name: str, quantity: int, icon: Surface):
        self.name = name
        self.quantity = quantity
        self.icon = icon

class GameUI:
    def __init__(self, screen_size: Tuple[int, int], settings: Settings):
        self.screen_size = screen_size
        self.font = pygame.font.Font(AssetManager.get_font("CascadiaCode.ttf"), 18)
        self.small_font = pygame.font.Font(AssetManager.get_font("CascadiaCodeItalic.ttf"), 14)

        self.lang_manager = LanguageManager(language=settings.language)
        self.lang_manager.load_translations()
        print(f"Current language: {self.lang_manager.language}")

        # Game state
        self.money = 1000
        self.date = "15-05-12"
        self.reputation = 75

        # Colors
        self.bg_color = Color(20, 20, 20, 200)
        self.text_color = Color(240, 240, 240)
        self.accent_color = Color(255, 215, 0)  # Gold color for pirate theme
        
        # UI elements
        self.info_section_width = 300
        self.info_section_height = 100
        self.info_section = Rect(10, 10, self.info_section_width, self.info_section_height)
        self.inventory_btn = Rect(self.screen_size[0] - 150, self.screen_size[1] - 50, 130, 40)

        # Inventory
        self.inventory_open = False
        self.inventory_rect = Rect(self.screen_size[0] // 4, self.screen_size[1] // 4,
                                   self.screen_size[0] // 2, self.screen_size[1] // 2)
        self.close_btn = Rect(self.inventory_rect.right - 30, self.inventory_rect.top + 10, 20, 20)
        self.inventory_items = self.create_sample_items()

    def create_sample_items(self) -> List[InventoryItem]:
        items = [
            InventoryItem("sword", 1, self.create_icon("⚔️")),
            InventoryItem("gold_coins", 50, self.create_icon("🪙")),
            InventoryItem("rum", 5, self.create_icon("🍾")),
            InventoryItem("map", 2, self.create_icon("🗺️")),
            InventoryItem("compass", 1, self.create_icon("🧭")),
        ]
        return items

    def create_icon(self, emoji: str) -> Surface:
        icon = self.font.render(emoji, True, self.text_color)
        return icon

    def draw(self, surface: Surface):
        # Info section
        pygame.draw.rect(surface, self.bg_color, self.info_section, border_radius=10)
        pygame.draw.rect(surface, self.accent_color, self.info_section, border_radius=10, width=2)
        
        # Date
        date_text = self.font.render(f"{self.lang_manager.get_text('date')}: {self.date}", True, self.text_color)
        date_rect = date_text.get_rect(topleft=(self.info_section.x + 10, self.info_section.y + 10))
        surface.blit(date_text, date_rect)
        
        # Money
        money_text = self.font.render(f"{self.lang_manager.get_text('money')}: ${self.money}", True, self.accent_color)
        money_rect = money_text.get_rect(topleft=(self.info_section.x + 10, self.info_section.y + 40))
        surface.blit(money_text, money_rect)
        
        # Reputation bar
        rep_bar_width = self.info_section_width - 20
        rep_bar_height = 20
        rep_bar_x = self.info_section.x + 10
        rep_bar_y = self.info_section.y + 70
        pygame.draw.rect(surface, Color(100, 100, 100), (rep_bar_x, rep_bar_y, rep_bar_width, rep_bar_height), border_radius=5)
        pygame.draw.rect(surface, self.accent_color, (rep_bar_x, rep_bar_y, rep_bar_width * (self.reputation / 100), rep_bar_height), border_radius=5)
        rep_text = self.small_font.render(f"{self.lang_manager.get_text('reputation')}: {self.reputation}%", True, self.text_color)
        surface.blit(rep_text, (rep_bar_x + 5, rep_bar_y + 2))
        
        # Inventory button
        pygame.draw.rect(surface, self.accent_color, self.inventory_btn, border_radius=5)
        inv_text = self.font.render(self.lang_manager.get_text('inventory'), True, Color(20, 20, 20))
        inv_text_rect = inv_text.get_rect(center=self.inventory_btn.center)
        surface.blit(inv_text, inv_text_rect)

        # Draw inventory if open
        if self.inventory_open:
            self.draw_inventory(surface)

    def draw_inventory(self, surface: Surface):
        # Draw inventory background
        pygame.draw.rect(surface, self.bg_color, self.inventory_rect, border_radius=10)
        pygame.draw.rect(surface, self.accent_color, self.inventory_rect, border_radius=10, width=2)

        # Draw close button
        pygame.draw.rect(surface, self.accent_color, self.close_btn, border_radius=5)
        close_text = self.font.render(self.lang_manager.get_text('close'), True, self.bg_color)
        close_text_rect = close_text.get_rect(center=self.close_btn.center)
        surface.blit(close_text, close_text_rect)

        # Draw inventory title
        title_text = self.font.render(self.lang_manager.get_text('inventory'), True, self.accent_color)
        title_rect = title_text.get_rect(midtop=(self.inventory_rect.centerx, self.inventory_rect.top + 15))
        surface.blit(title_text, title_rect)

        # Draw inventory items
        item_x, item_y = self.inventory_rect.left + 20, self.inventory_rect.top + 50
        for item in self.inventory_items:
            pygame.draw.rect(surface, self.text_color, (item_x, item_y, 200, 40), border_radius=5, width=1)
            surface.blit(item.icon, (item_x + 5, item_y + 5))
            item_text = self.small_font.render(f"{self.lang_manager.get_text(item.name)} x{item.quantity}", True, self.text_color)
            surface.blit(item_text, (item_x + 40, item_y + 10))
            item_y += 50

    def update(self, events: list):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.inventory_btn.collidepoint(event.pos) and not self.inventory_open:
                    self.inventory_open = True
                elif self.inventory_open:
                    if self.close_btn.collidepoint(event.pos) or not self.inventory_rect.collidepoint(event.pos):
                        self.inventory_open = False

    def toggle_inventory(self):
        self.inventory_open = not self.inventory_open
