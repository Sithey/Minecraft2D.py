import pygame
from .settings import *

class Block:
    """
    Represents a single block in the game world.
    Each block has a position, type, and corresponding visual properties.
    """
    def __init__(self, x, y, block_type):
        """
        Initialize a new block.
        
        Args:
            x (int): Grid X coordinate
            y (int): Grid Y coordinate
            block_type (str): Type of block ('dirt', 'stone', 'grass', etc.)
        """
        self.rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        self.block_type = block_type
        self.color = self.get_color()
        
    def get_color(self):
        """
        Get the color for the block based on its type.
        
        Returns:
            tuple: RGB color value for the block
        """
        if self.block_type == 'dirt':
            return DIRT_COLOR
        elif self.block_type == 'grass':
            return GRASS_COLOR
        elif self.block_type == 'stone':
            return STONE_COLOR
        elif self.block_type == 'water':
            return WATER_COLOR
        elif self.block_type == 'bedrock':
            return BEDROCK_COLOR
        elif self.block_type == 'wood':
            return WOOD_COLOR
        return SKY_COLOR
    
    def is_breakable(self):
        """
        Check if the block can be broken by the player.
        Bedrock blocks are unbreakable.
        
        Returns:
            bool: True if the block can be broken, False otherwise
        """
        return self.block_type != 'bedrock'
        
    def draw(self, screen):
        """
        Draw the block on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 1)  