from enum import Enum
from dataclasses import dataclass, field
from typing import Tuple
from functools import lru_cache


class GameInfo:
    """
    Contains constant information about the game that doesn't change during runtime.

    Attributes:
        NAME (str): The name of the game.
        VERSION (str): The current version of the game.
    """
    name: str = "Pirate's Dilemma"
    version: str = "v0.0.1"

@dataclass
class GameSettings:
    """
    Represents the adjustable settings of the game.

    These settings can be changed during runtime or loaded from a configuration file.

    Attributes:
        width (int): The width of the game window in pixels.
        height (int): The height of the game window in pixels.
        tile_size (int): The size of a single tile in pixels.
        animation_speed (int): The speed of animations in the game.
        volume (float): The master volume of the game, range 0.0 to 1.0.
        fullscreen (bool): Whether the game is in fullscreen mode.
    """
    width: int = 1080
    height: int = 720
    tile_size: int = 32
    animation_speed: int = 8
    volume: float = 0.7
    fullscreen: bool = False
    fps: int = 72
    # fps: int = 60

    def update(self, **kwargs):
        """
        Update the game settings with new values.

        Args:
            **kwargs: Arbitrary keyword arguments corresponding to settings attributes.
        """
        # * One-liner to update settings attributes if they exist (do nothing otherwise)
        [setattr(self, key, value) for key, value in kwargs.items() if hasattr(self, key)]
        # * Same as above but a bit more verbose
        # for key, value in kwargs.items():
        #     match hasattr(self, key):
        #         case True: setattr(self, key, value)
        #         case _: raise AttributeError(f"GameSettings has no attribute '{key}'")

@dataclass
class Assets:
    """
    Enumeration of asset file paths for the Pirate's Dilemma game.

    This enum contains the base directory paths for various types of game assets.

    Attributes:
        IMAGES (str): Path to the images directory.
        FONTS (str): Path to the fonts directory.
        SOUNDS (str): Path to the sound effects directory.
        MUSIC (str): Path to the music directory.
        VIDEOS (str): Path to the videos directory.
        ANIMATIONS (str): Path to the animations directory.
    """
    images: str = "assets/images/"
    fonts: str = "assets/fonts/"
    sounds: str = "assets/sounds/"
    music: str = "assets/music/"
    animations: str = "assets/animations/"

@dataclass(frozen=True)
class Theme:
    """
    Represents a color theme for the Pirate's Dilemma game.

    This dataclass defines the colors and font used in a specific game theme.

    Attributes:
        name (str): The name of the theme.
        main_color (Tuple[int, int, int]): The RGB values for the main color.
        secondary_color (Tuple[int, int, int]): The RGB values for the secondary color.
        highlight_color (Tuple[int, int, int]): The RGB values for the highlight color.
        font (str): The filename or path of the font used in this theme.
    """
    name: str
    main_color: Tuple[int, int, int]
    secondary_color: Tuple[int, int, int]
    highlight_color: Tuple[int, int, int]
    font: str

class Themes(Enum):
    """
    Enumeration of predefined themes for the Pirate's Dilemma game.

    This enum contains various Theme instances representing different visual styles for the game.

    Attributes:
        LIGHT (Theme): A light-colored theme.
        DARK (Theme): A dark-colored theme.
        DARK_PLUS (Theme): An enhanced dark theme.
        DEBUG (Theme): A high-contrast theme useful for debugging.
    """
    LIGHT: Theme = Theme("Light Theme", (255, 255, 255), (191, 191, 191), (255, 0, 0), "assets/fonts/Roboto-Regular.ttf")
    DARK: Theme = Theme("Dark Theme", (0, 0, 0), (63, 63, 63), (255, 0, 0), "assets/fonts/Roboto-Regular.ttf")
    DARK_PLUS: Theme = Theme("Dark+ Theme", (0, 0, 0), (31, 31, 31), (255, 0, 0), "assets/fonts/Roboto-Regular.ttf")
    DEBUG: Theme = Theme("Debug Theme", (255, 0, 0), (0, 0, 0), (255, 0, 0), "Consolas")

    @classmethod  # Class method to retrieve a theme by name (case-insensitive)
    @lru_cache(maxsize=None)  # Cache the results of this method for performance
    def get_theme(cls, theme_name: str) -> Theme:
        """
        Retrieve a Theme instance by its name.

        This method allows getting a theme by its string name, case-insensitive.
        Results are cached for performance.

        Args:
            theme_name (str): The name of the theme to retrieve.

        Returns:
            Theme: The Theme instance corresponding to the given name.

        Raises:
            KeyError: If the theme name is not found in the enum.
        """
        return cls[theme_name.upper()].value

@dataclass
class GameState:
    """
    Represents the current state of the Pirate's Dilemma game.

    This class holds runtime state information for the game, including settings and current theme.

    Attributes:
        settings (GameSettings): The current game settings.
        current_theme (Theme): The currently active theme for the game.
        player_data (Dict[str, Any]): Dictionary to store player-specific data.
    """
    settings: GameSettings = field(default_factory=GameSettings)
    current_theme: Theme = Themes.DARK
    # player_data: Dict[str, Any] = field(default_factory=dict)

    def update_theme(self, new_theme: str) -> None:
        """
        Update the current theme of the game.

        Args:
            new_theme (str): The name of the new theme to apply.

        Raises:
            KeyError: If the provided theme name is not found.
        """
        self.current_theme = Themes.get_theme(new_theme)

    def update_settings(self, **kwargs) -> None:
        """
        Update the game settings.

        Args:
            **kwargs: Arbitrary keyword arguments corresponding to settings attributes.

        Raises:
            AttributeError: If an invalid setting name is provided.
        """
        self.settings.update(**kwargs)

# Global game state instance
game_state: GameState = GameState()


if __name__ == '___main__':
    print(f"Game Name: {GameInfo.name}")
    print(f"Current Resolution: {game_state.settings.width}x{game_state.settings.height}")
    game_state.update_settings(width=1920, height=1080)
    print(f"Updated Resolution: {game_state.settings.width}x{game_state.settings.height}")
    print(f"Current Theme: {game_state.current_theme.name}")
    game_state.update_theme("dark")
    print(f"Updated Theme: {game_state.current_theme.name}")
