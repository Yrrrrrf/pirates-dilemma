import sys
import random
from typing import Callable, Dict, Optional, Tuple

import pygame
from pygame import Surface

from app.core.systems.ui.volume_control import VolumeControl
from tools import AssetManager
from project import set_app_lang
from project.theme.ui import UITheme
from project.settings.lang import Language

from typing import Optional, Callable
from pygame import Surface

from app.core.systems.menu.base import UITheme, MenuItem, MenuContainer
from app.core.systems.menu.renderer import MenuRenderer
from project import menu_lang_manager
from tools.audio import AudioType, audio_manager


class StartMenuItem(MenuItem):
    """Extended MenuItem with background and positioning support"""
    def __init__(self, text_key: str, theme: UITheme, callback: Callable[[], None], renderer: MenuRenderer):
        super().__init__(text_key, theme, callback)
        self.renderer = renderer
        self.cached_text = None
        self.cached_rect = None

    def render(self, surface: Surface) -> None:
        if not self.is_visible: return

        # Determine text color based on state
        color = (
            self.theme.highlight_color if self.is_selected else
            self.theme.hover_color if self.is_hovered else
            self.theme.text_color
        )

        # Use appropriate font based on state
        font_type = 'highlight' if (self.is_selected or self.is_hovered) else 'option'

        # Calculate scale factor
        scale = 1.1 if self.is_hovered else 1.0

        # Get screen center for x position
        screen_width = surface.get_width()
        x = screen_width // 2

        # Render text with shadow
        self.rect = self.renderer.render_text(
            text=self.text,
            font_type=font_type,
            color=color,
            pos=(x, self.position[1]),
            surface=surface,
            centered=True,
            shadow=True
        )

class StartMenuContainer(MenuContainer[StartMenuItem]):
    """Extended MenuContainer with background support and dynamic spacing"""
    def __init__(self, theme: UITheme, screen: Surface, title_key: str):
        super().__init__(theme)
        self.screen = screen
        self.title_key = title_key
        self.renderer = MenuRenderer(theme)
        self.background: Optional[Surface] = None
        
        # Dynamic spacing configuration
        self.title_y = 100         # Y position for title
        self.start_y = 250         # Starting Y position for menu items
        self.min_spacing = 60      # Minimum spacing between items
        self.default_spacing = 100 # Default spacing for standard menus
        self.max_items_default = 4 # Number of items that use default spacing

        audio_manager.play_sound("bgm\\8-bit-arcade.mp3", AudioType.UI)

    def set_background(self, surface: Surface) -> None:
        self.background = surface

    def _calculate_spacing(self, screen_height: int) -> int:
        """Calculate optimal spacing based on number of items and screen height"""
        # Available space from start_y to bottom of screen (with padding)
        available_space = screen_height - self.start_y - 50  # 50px bottom padding
        
        # If we have more items than our default threshold, calculate dynamic spacing
        if len(self.items) > self.max_items_default:
            # Calculate spacing that would evenly distribute items in available space
            spacing = available_space / (len(self.items) - 1)  # -1 because we don't need space after last item
            # Clamp spacing between min and default
            return max(self.min_spacing, min(spacing, self.default_spacing))
        
        return self.default_spacing

    def render(self, surface: Surface) -> None:
        # First clear the surface
        surface.fill((0, 0, 0))
        
        # Draw background if available
        if self.background:
            surface.blit(self.background, (0, 0))

        # Get screen dimensions
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        screen_center = screen_width // 2

        # Render title
        title_text = menu_lang_manager.get_text(self.title_key)
        self.renderer.render_text(
            text=title_text,
            font_type='title',
            color=self.theme.highlight_color,
            pos=(screen_center, self.title_y),
            surface=surface,
            centered=True,
            shadow=True
        )

        # Calculate optimal spacing for current number of items
        spacing = self._calculate_spacing(screen_height)
        
        # For many items, we might want to start higher on the screen
        if len(self.items) > self.max_items_default:
            self.start_y = self.title_y + 100  # Reduce gap between title and first item

        # Calculate starting Y position and render items
        current_y = self.start_y
        visible_items = []  # Keep track of visible items for scroll indication

        for i, item in enumerate(self.items):
            # Check if item would be visible on screen
            if current_y < screen_height - 30:  # Leave space for scroll indicator
                # Update item position
                item.position = (screen_center, current_y)
                
                # Update selection state
                item.is_selected = (i == self.selected_index)
                
                # Render the item
                item.render(surface)
                visible_items.append(item)
            
            # Move to next position
            current_y += spacing

        # If not all items are visible, add a scroll indicator
        if len(visible_items) < len(self.items):
            self._render_scroll_indicator(surface, screen_center, screen_height - 25)

    def _render_scroll_indicator(self, surface: Surface, x: int, y: int) -> None:
        """Render a scroll indicator to show there are more items below"""
        color = self.theme.text_color
        size = 10
        points = [
            (x - size, y - size),
            (x + size, y - size),
            (x, y + size)
        ]
        pygame.draw.polygon(surface, color, points)

class StartMenuManager:
    """Manages the main menu system using the new component architecture"""
    def __init__(self, surface: Surface, run_fn: Callable[[], None]) -> None:
        print("Initializing MenuManager...")
        self.surface = surface
        self.run = run_fn
        self.theme = UITheme()
        self.background = self._load_background()
        self.containers: Dict[str, StartMenuContainer] = {}
        self.current_container: Optional[str] = None
        
        self._initialize_containers()
        self.show_container('main')
        print("MenuManager initialized successfully")

    def _load_background(self) -> Surface:
        """Load and scale the background image"""
        try:
            # img_name = f"some-pirate-{random.randint(0, 2):02d}.png"
            img_name = f"bg.jpg"
            bg_image = pygame.image.load(AssetManager.get_image(img_name))
            bg_scaled = pygame.transform.scale(bg_image, self.surface.get_size())
            print(f"Background loaded: {img_name}")
            return bg_scaled
        except pygame.error as e:
            print(f"Error loading background: {e}")
            bg = Surface(self.surface.get_size())
            bg.fill((0, 0, 0))
            return bg

    def _initialize_containers(self) -> None:
        """Initialize all menu containers"""
        print("Initializing menu containers...")
    
        # Start menu
        main_container = StartMenuContainer(self.theme, self.surface, "menu_title")
        main_container.set_background(self.background)
        main_container.add_item(StartMenuItem("start", self.theme, self.run, main_container.renderer))
        main_container.add_item(StartMenuItem("options", self.theme, lambda: self.show_container('options'), main_container.renderer))
        main_container.add_item(StartMenuItem("exit", self.theme, sys.exit, main_container.renderer))
        self.containers['main'] = main_container

        # * Options menu
        options_container = StartMenuContainer(self.theme, self.surface, "settings")
        options_container.set_background(self.background)
        options_container.add_item(StartMenuItem("language", self.theme, lambda: self.show_container('language'), options_container.renderer))
        options_container.add_item(StartMenuItem("audio", self.theme, lambda: self.show_container('audio'), options_container.renderer))
        options_container.add_item(StartMenuItem("back", self.theme, lambda: self.show_container('main'), options_container.renderer))
        self.containers['options'] = options_container

        # * Language menu
        lang_container = StartMenuContainer(self.theme, self.surface, "language")
        lang_container.set_background(self.background)
        for lang in Language:
            lang_container.add_item(StartMenuItem(
                lang.name.lower(),
                self.theme,
                lambda l=lang: self._change_language(l),
                lang_container.renderer
            ))
        lang_container.add_item(StartMenuItem("back", self.theme, lambda: self.show_container('options'), lang_container.renderer))
        self.containers['language'] = lang_container

        # * Audio settings menu
        audio_container = StartMenuContainer(self.theme, self.surface, "audio")
        audio_container.set_background(self.background)

        # Add volume controls
        audio_container.add_item(VolumeControl("master_volume", self.theme, audio_container.renderer, AudioType.MUSIC))
        audio_container.add_item(VolumeControl("music_volume", self.theme, audio_container.renderer, AudioType.MUSIC))
        audio_container.add_item(VolumeControl("sfx_volume", self.theme, audio_container.renderer, AudioType.EFFECT))
        # audio_container.add_item(VolumeControl("ui_volume", self.theme, audio_container.renderer, AudioType.UI))
        audio_container.add_item(VolumeControl("env_volume", self.theme, audio_container.renderer, AudioType.AMBIENT))
        audio_container.add_item(StartMenuItem("back", self.theme, lambda: self.show_container('options'), audio_container.renderer))
        
        self.containers['audio'] = audio_container

        print("Menu containers initialized")

    def _change_language(self, lang: Language) -> None:
        """Handle language change"""
        set_app_lang(lang)
        self.show_container('options')

    def show_container(self, name: str) -> None:
        """Show a specific container"""
        if name in self.containers:
            self.current_container = name
            print(f"Current container set to: {name}")
        else:
            print(f"Container not found: {name}")

    def handle_keydown(self, event: pygame.event.Event) -> None:
        """Handle keyboard events"""
        if not self.current_container:
            return

        current = self.containers[self.current_container]
        if event.key == pygame.K_ESCAPE:
            if self.current_container != 'main':
                self.show_container('main')
            else:
                sys.exit()
        else:
            current.handle_key(event)

    def handle_click(self, pos: Tuple[int, int]) -> None:
        """Handle mouse click events"""
        if self.current_container:
            self.containers[self.current_container].handle_click(pos)

    def update_hover_states(self, pos: Tuple[int, int]) -> None:
        """Update hover states for current container"""
        if self.current_container:
            self.containers[self.current_container].handle_hover(pos)

    def draw(self, surface: Surface) -> None:
        """Draw the current menu state"""
        if self.current_container:
            # Clear surface
            surface.fill((0, 0, 0))
            
            # Render current container
            self.containers[self.current_container].render(surface)
        else:
            print("Warning: No container to display")

    def resize(self, size: Tuple[int, int]) -> None:
        """Handle window resizing"""
        print(f"Resizing menu to: {size}")
        self.background = pygame.transform.scale(self.background, size)
        for container in self.containers.values():
            container.set_background(self.background)

    def handle_mousemotion(self, pos: Tuple[int, int]) -> None:
        """Handle mouse motion events"""
        if self.current_container:
            # Update hover states
            self.containers[self.current_container].handle_hover(pos)
            # Handle volume control dragging
            for item in self.containers[self.current_container].items:
                if isinstance(item, VolumeControl):
                    item.handle_drag(pos)

    def handle_mouseup(self, pos: Tuple[int, int]) -> None:
        """Handle mouse button release"""
        if self.current_container:
            for item in self.containers[self.current_container].items:
                if isinstance(item, VolumeControl):
                    item.handle_release()
