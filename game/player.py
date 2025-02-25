import pygame
import os
from .settings import *

class Player:
    """
    Player class representing Steve (the main character).
    Handles movement, physics, collision detection, and sprite rendering.
    """
    def __init__(self, x, y):
        """
        Initialize the player at the given spawn position.
        
        Args:
            x (int): Initial X coordinate
            y (int): Initial Y coordinate
        """
        self.spawn_x = x
        self.spawn_y = y
        total_height = int(BLOCK_SIZE * 2.6)  
        total_width = int(BLOCK_SIZE * 1.2)   
        self.rect = pygame.Rect(x, y, total_width, total_height)
        
        # Physics attributes
        self.velocity_y = 0
        self.velocity_x = 0
        self.on_ground = False
        
        # Game state
        self.selected_block = 'dirt'  
        self.facing_right = True      
        
        # Load and scale player sprite
        image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'steve.png')
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (total_width, total_height))
        self.image_flip = pygame.transform.flip(self.image, True, False)
        
    def respawn(self):
        """Reset player position and velocity to spawn point."""
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.velocity_y = 0
        self.velocity_x = 0
        
    def check_ground(self, world):
        """
        Check if the player is standing on a block.
        
        Args:
            world: World instance for collision detection
            
        Returns:
            bool: True if player is on ground, False if in air
        """
        test_rect = self.rect.copy()
        test_rect.y += 1
        return world.check_collision(test_rect)
        
    def update(self, world):
        """
        Update player physics and handle input.
        
        Args:
            world: World instance for collision detection
        """
        # Handle keyboard input
        keys = pygame.key.get_pressed()
        self.velocity_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = PLAYER_SPEED
            self.facing_right = True
            
        # Ground collision check
        self.on_ground = self.check_ground(world)
            
        # Jump handling
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
            self.velocity_y = JUMP_SPEED
            self.on_ground = False
                
        # Apply gravity
        if not self.on_ground:
            self.velocity_y = min(self.velocity_y + GRAVITY, MAX_FALL_SPEED)
        
        # Horizontal movement and collision
        self.rect.x += self.velocity_x
        if world.check_collision(self.rect):
            self.rect.x -= self.velocity_x
            
        # Vertical movement and collision with pixel-perfect precision
        if self.velocity_y != 0:
            step = 1 if self.velocity_y > 0 else -1
            for _ in range(abs(int(self.velocity_y))):
                self.rect.y += step
                if world.check_collision(self.rect):
                    self.rect.y -= step
                    self.velocity_y = 0
                    break
                    
        # Void check (fall detection)
        if self.rect.y > WORLD_HEIGHT * BLOCK_SIZE:
            self.respawn()
    
    def draw(self, screen):
        """
        Draw the player sprite on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        current_image = self.image if self.facing_right else self.image_flip
        screen.blit(current_image, (self.rect.x, self.rect.y))