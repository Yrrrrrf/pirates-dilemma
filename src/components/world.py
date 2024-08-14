import pygame
import random
from typing import List, Tuple, Dict


class IsometricTile(pygame.sprite.Sprite):
    """
    Represents an isometric tile in the game world.

    This class is a subclass of pygame.sprite.Sprite and is used to create
    and manage individual tiles in the isometric world.
    """

    def __init__(self, x: int, y: int, image: pygame.Surface):
        """
        Initialize an IsometricTile object.

        Args:
            x (int): The x-coordinate of the tile's top-left corner.
            y (int): The y-coordinate of the tile's top-left corner.
            image (pygame.Surface): The image to use for this tile.
        """
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

class WaterAnimation:
    def __init__(self, screen_size: Tuple[int, int]):
        self.screen_size = screen_size
        self.tile_size = 32
        self.water_tiles: List[pygame.Surface] = []
        self.load_water_tiles()
        self.animation_speed = 10
        self.current_frame = 0

    def load_water_tiles(self):
        water_sheet = pygame.image.load("assets/images/static/water-demo.png").convert_alpha()
        for i in range(6):
            water_tile = water_sheet.subsurface((i * 32, 64, 32, 32))
            self.water_tiles.append(water_tile)

    def update(self):
        self.current_frame = (self.current_frame + 1) % (len(self.water_tiles) * self.animation_speed)

    def draw(self, surface: pygame.Surface):
        frame = self.current_frame // self.animation_speed
        water_tile = self.water_tiles[frame]

        # Draw water tiles
        for y in range(0, self.screen_size[1], self.tile_size):
            for x in range(0, self.screen_size[0], self.tile_size):
                surface.blit(water_tile, (x, y))

        # Draw shore lines
        shore_colors = [
            (226, 194, 117),  # Sand color
            (76, 108, 100),   # Dark green color
            (48, 104, 80)     # Darker green color
        ]
        shore_heights = [32, 16, 16]  # Heights for each shore line

        y_offset = 0
        for color, height in zip(shore_colors, shore_heights):
            shore = pygame.Surface((self.screen_size[0], height))
            shore.fill(color)
            surface.blit(shore, (0, y_offset))
            y_offset += height

class Tree(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.original_image = pygame.image.load(f"assets/images/static/tree-{random.randint(1,5):02d}.png")
        self.image = pygame.transform.scale(self.original_image, (128, 128))
        self.rect = self.image.get_rect(topleft=(x, y))

class Camera:
    def __init__(self, width: int, height: int):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity: pygame.sprite.Sprite) -> pygame.Rect:
        return entity.rect.move(-self.camera.x, -self.camera.y)

    def update(self, target: pygame.sprite.Sprite) -> None:
        x = -target.rect.centerx + int(self.width / 2)
        y = -target.rect.centery + int(self.height / 2)

        # Limit scrolling to game boundaries
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.camera.width - self.width), x)  # right
        y = max(-(self.camera.height - self.height), y)  # bottom

        self.camera = pygame.Rect(x, y, self.camera.width, self.camera.height)

class World:
    def __init__(self):
        self.screen: pygame.Surface = pygame.display.get_surface()
        self.tile_size: int = 96
        self.tiles: pygame.sprite.Group = pygame.sprite.Group()
        self.tile_images: Dict[str, pygame.Surface] = self.load_tile_images()
        
        self.world_width = 2560  # Adjust these values as needed
        self.world_height = 1440
        self.water_animation = WaterAnimation((self.world_width, self.world_height))

        self.trees = pygame.sprite.Group()
        for _ in range(24):
            tree = Tree(
                random.randint(0, self.world_width - 128),
                random.randint(0, self.world_height - 128)
            )
            self.trees.add(tree)

        self.player: Player = Player(self.screen.get_width() // 2, self.screen.get_height() // 2)
        self.camera = Camera(self.screen.get_width(), self.screen.get_height())

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.trees)
        self.all_sprites.add(self.tiles)

    def get_all_sprites(self) -> List[pygame.sprite.Sprite]:
        return self.all_sprites.sprites()

    def load_tile_images(self) -> Dict[str, pygame.Surface]:
        """
        Load and scale tile images for use in the world.

        Returns:
            Dict[str, pygame.Surface]: A dictionary of tile images keyed by their names.
        """
        tile_types = [
            ('dirt', 4),
            ('grass', 10),
            ('stone', 4),
        ]

        images = {}
        for tile_type, num_variations in tile_types:
            for i in range(1, num_variations + 1):
                key = f"{tile_type}{i}"
                try:
                    img = pygame.image.load(f"assets/images/static/isometric-nature-pack/{key}.png").convert_alpha()
                    images[key] = pygame.transform.scale(img, (self.tile_size, self.tile_size))
                except pygame.error:
                    continue  # Skip if the image doesn't exist
        return images

    def generate_world(self) -> None:
        """Generate the isometric world by placing tiles randomly."""
        w, h = self.screen.get_size()
        rows, cols = h // (self.tile_size // 2), w // self.tile_size
        
        for row in range(rows):
            for col in range(cols):
                x = col * self.tile_size + (row % 2) * (self.tile_size // 2)
                y = row * (self.tile_size // 2)
                
                # Generate only 85% of the tiles for a more natural look
                if random.random() < 0.85:
                    tile_key = random.choice(list(self.tile_images.keys()))
                    tile = IsometricTile(x, y, self.tile_images[tile_key])
                    self.tiles.add(tile)

    def update(self, dt: float) -> None:
        """
        Update the world state.

        Args:
            dt (float): Time elapsed since the last update.
        """
        self.water_animation.update()
        [tree.update() for tree in self.trees]
        self.player.update(dt)
        print(f"Player position: {self.player.rect.topleft}")

    def draw_background(self, ) -> None:
        """Draw the background elements."""
        self.screen.fill((135, 206, 235))  # Sky blue background
        self.water_animation.draw(self.screen)  # Draw water animation
        
    def draw(self) -> None:
        """Draw all elements of the world to the screen."""
        self.draw_background(self.screen)
        self.tiles.draw(self.screen)
        self.all_sprites.draw(self.screen)

    def handle_resize(self, new_size: Tuple[int, int]) -> None:
        """
        Handle screen resize events.

        Args:
            new_size (Tuple[int, int]): The new dimensions of the screen.
        """
        self.screen = pygame.display.get_surface()
        self.tiles.empty()
        self.water_animation = WaterAnimation(new_size)
        self.generate_world()

    def get_all_sprites(self) -> List[pygame.sprite.Sprite]:
        return self.all_sprites.sprites()

class Player(pygame.sprite.Sprite):
    """
    Represents the player character in the game.

    This class handles player movement and rendering.
    """

    def __init__(self, x: int, y: int):
        """
        Initialize a Player object.

        Args:
            x (int): The initial x-coordinate of the player's center.
            y (int): The initial y-coordinate of the player's center.
        """
        super().__init__()
        self.image = pygame.Surface((64, 64))
        self.image.fill('red')  # Temporary placeholder for the player
        self.rect = self.image.get_rect(center=(x, y))
        self.speed: int = 200  # Movement speed in pixels per second

    def update(self, dt: float) -> None:
        """
        Update the player's position based on input.

        Args:
            dt (float): Time elapsed since the last update.
        """
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT] + keys[pygame.K_d] - keys[pygame.K_a]) * self.speed * dt
        dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP] + keys[pygame.K_s] - keys[pygame.K_w]) * self.speed * dt
        self.rect.x += dx
        self.rect.y += dy
        # self.rect.clamp_ip(pygame.display.get_surface().get_rect())
