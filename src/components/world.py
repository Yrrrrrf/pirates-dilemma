import pygame
import random

class Tree(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(f"assets/images/static/tree-{random.randint(1, 5):02d}.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, dt):
        # Trees don't need to update, but we include this method for consistency
        pass

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((64, 64))
        self.image.fill('red')  # Temporary placeholder for the player
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 200  # pixels per second

    def update(self, dt):
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT] + keys[pygame.K_d] - keys[pygame.K_a]) * self.speed * dt
        dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP] + keys[pygame.K_s] - keys[pygame.K_w]) * self.speed * dt
        # print(f"Player update: dx={dx}, dy={dy}")  # Add this line
        self.rect.x += dx
        self.rect.y += dy
        # ... rest of the method
        # Keep the player within the screen boundaries
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())

class World:
    def __init__(self):
        self.trees = pygame.sprite.Group()
        self.generate_trees()

        self.player = Player(64, 64)  # Start the player in the middle of the screen
        self.player.image = pygame.transform.scale(self.player.image, (64, 64))

    def generate_trees(self):
        w, h = pygame.display.get_surface().get_size()
        self.trees.add([Tree(random.randint(0, w), random.randint(0, h)) for _ in range(20)])

    def update(self, dt):
        self.trees.update(dt)
        self.player.update(dt)
        print(f"Player position: {self.player.rect.topleft}")  # Add this line

    def draw(self, screen: pygame.Surface):
        self.trees.draw(screen)
        screen.blit(self.player.image, self.player.rect)
        