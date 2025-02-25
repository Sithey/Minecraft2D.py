import pygame
import random
import math
from .settings import *
from .block import Block

class World:
    """
    World class that manages the game environment.
    Handles terrain generation, block placement/destruction, and collision detection.
    """
    def __init__(self):
        """Initialize an empty world and generate the terrain."""
        self.blocks = {}
        self.generate_terrain()
        self.add_bedrock_borders()
    
    def generate_terrain(self):
        """
        Generate a simple procedural terrain with hills.
        Uses a basic noise algorithm to create natural-looking elevation changes.
        """
        heights = []
        height = WORLD_HEIGHT // 2
        
        # Generate terrain heights using simple noise
        for x in range(WORLD_WIDTH):
            height += random.randint(-1, 1)
            height = max(WORLD_HEIGHT // 3, min(height, WORLD_HEIGHT - 10))
            heights.append(height)
        
        # Create blocks based on height map
        for x in range(WORLD_WIDTH):
            for y in range(WORLD_HEIGHT):
                if y > heights[x]:
                    if y < WORLD_HEIGHT - 5: 
                        self.blocks[(x, y)] = Block(x, y, 'stone')
                    else:
                        self.blocks[(x, y)] = Block(x, y, 'dirt')
                elif y == heights[x]:
                    self.blocks[(x, y)] = Block(x, y, 'grass')
    
    def add_bedrock_borders(self):
        """Add unbreakable bedrock borders to contain the player."""
        # Bottom border
        for x in range(WORLD_WIDTH):
            self.blocks[(x, WORLD_HEIGHT-1)] = Block(x, WORLD_HEIGHT-1, 'bedrock')
            
        # Side borders
        for y in range(WORLD_HEIGHT):
            self.blocks[(0, y)] = Block(0, y, 'bedrock')
            self.blocks[(WORLD_WIDTH-1, y)] = Block(WORLD_WIDTH-1, y, 'bedrock')
    
    def get_surface_height(self, x):
        """
        Find the first non-empty block position at given x coordinate.
        
        Args:
            x (int): X coordinate to check
            
        Returns:
            int: Y coordinate of the first block, or mid-height if none found
        """
        for y in range(WORLD_HEIGHT):
            if (x, y) in self.blocks:
                return y
        return WORLD_HEIGHT // 2
    
    def get_block(self, x, y):
        """
        Get the block at the specified coordinates.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            Block: The block at the position, or None if empty
        """
        return self.blocks.get((x, y))
    
    def check_line_of_sight(self, start_x, start_y, end_x, end_y):
        """
        Check if there are any blocks between two points.
        Uses Bresenham's line algorithm for accurate line-of-sight checking.
        
        Args:
            start_x, start_y: Starting point coordinates
            end_x, end_y: Ending point coordinates
            
        Returns:
            bool: True if line of sight is clear, False if blocked
        """
        # Convert to grid coordinates
        start_block_x = int(start_x // BLOCK_SIZE)
        start_block_y = int(start_y // BLOCK_SIZE)
        end_block_x = int(end_x // BLOCK_SIZE)
        end_block_y = int(end_y // BLOCK_SIZE)
        
        # Allow interaction with adjacent blocks
        if (abs(start_block_x - end_block_x) <= 1 and 
            abs(start_block_y - end_block_y) <= 1):
            return True
            
        # Modified Bresenham's algorithm
        dx = abs(end_block_x - start_block_x)
        dy = abs(end_block_y - start_block_y)
        x = start_block_x
        y = start_block_y
        
        step_x = 1 if start_block_x < end_block_x else -1
        step_y = 1 if start_block_y < end_block_y else -1
        
        if dx > dy:
            err = dx / 2
            while x != end_block_x:
                if (x, y) != (end_block_x, end_block_y) and self.get_block(x, y):
                    return False
                err -= dy
                if err < 0:
                    y += step_y
                    err += dx
                x += step_x
        else:
            err = dy / 2
            while y != end_block_y:
                if (x, y) != (end_block_x, end_block_y) and self.get_block(x, y):
                    return False
                err -= dx
                if err < 0:
                    x += step_x
                    err += dy
                y += step_y
                
        return True
    
    def break_block(self, pos, player_pos):
        """
        Try to break a block at the specified position.
        
        Args:
            pos (tuple): Target position (mouse coordinates)
            player_pos (tuple): Player's current position
        """
        block_x = pos[0] // BLOCK_SIZE
        block_y = pos[1] // BLOCK_SIZE
        
        # Basic checks
        if (block_x, block_y) not in self.blocks:
            return
        if not self.blocks[(block_x, block_y)].is_breakable():
            return
            
        player_block_x = player_pos[0] // BLOCK_SIZE
        player_block_y = player_pos[1] // BLOCK_SIZE
            
        # Range check
        distance = math.sqrt((block_x - player_block_x) ** 2 + (block_y - player_block_y) ** 2)
        if distance > 3:
            return
            
        # Line of sight check
        if not self.check_line_of_sight(
            player_pos[0], player_pos[1],
            block_x * BLOCK_SIZE + BLOCK_SIZE // 2,
            block_y * BLOCK_SIZE + BLOCK_SIZE // 2
        ):
            return
            
        # All checks passed, remove the block
        del self.blocks[(block_x, block_y)]
    
    def has_adjacent_block(self, x, y):
        """
        Check if there's at least one block adjacent to the given position.
        
        Args:
            x (int): X coordinate to check
            y (int): Y coordinate to check
            
        Returns:
            bool: True if there's an adjacent block, False otherwise
        """
        adjacent_positions = [
            (x + 1, y),    # Right
            (x - 1, y),    # Left
            (x, y + 1),    # Bottom
            (x, y - 1),    # Top
            (x + 1, y + 1),  # Bottom-right
            (x - 1, y + 1),  # Bottom-left
            (x + 1, y - 1),  # Top-right
            (x - 1, y - 1),  # Top-left
        ]
        
        return any((pos_x, pos_y) in self.blocks for pos_x, pos_y in adjacent_positions)
    
    def would_collide_with_player(self, block_x, block_y, player_rect):
        """
        Check if a block at the given position would collide with the player.
        
        Args:
            block_x (int): Block's X coordinate
            block_y (int): Block's Y coordinate
            player_rect: Player's collision rectangle
            
        Returns:
            bool: True if there would be a collision, False otherwise
        """
        block_rect = pygame.Rect(block_x * BLOCK_SIZE, block_y * BLOCK_SIZE, 
                               BLOCK_SIZE, BLOCK_SIZE)
        return block_rect.colliderect(player_rect)
    
    def place_block(self, pos, block_type):
        """
        Try to place a block at the specified position.
        
        Args:
            pos (tuple): Contains target position and player rectangle
            block_type (str): Type of block to place
        """
        block_x = pos[0] // BLOCK_SIZE
        block_y = pos[1] // BLOCK_SIZE
        
        # Basic checks
        if (block_x, block_y) in self.blocks:
            return
        if not self.has_adjacent_block(block_x, block_y):
            return
            
        # Get player collision rect and check for overlap
        player_rect = pos[2]
        if self.would_collide_with_player(block_x, block_y, player_rect):
            return
            
        # Range check
        player_block_x = player_rect.centerx // BLOCK_SIZE
        player_block_y = player_rect.centery // BLOCK_SIZE
        distance = math.sqrt((block_x - player_block_x) ** 2 + (block_y - player_block_y) ** 2)
        if distance > 3:
            return
            
        # Line of sight check
        if not self.check_line_of_sight(
            player_rect.centerx, player_rect.centery,
            block_x * BLOCK_SIZE + BLOCK_SIZE // 2,
            block_y * BLOCK_SIZE + BLOCK_SIZE // 2
        ):
            return
            
        # All checks passed, place the block
        self.blocks[(block_x, block_y)] = Block(block_x, block_y, block_type)
    
    def draw(self, screen):
        """
        Draw all blocks in the world.
        
        Args:
            screen: Pygame surface to draw on
        """
        for block in self.blocks.values():
            block.draw(screen)
    
    def check_collision(self, rect):
        """
        Check if a rectangle collides with any blocks in the world.
        
        Args:
            rect: Rectangle to check for collisions
            
        Returns:
            bool: True if there's a collision, False otherwise
        """
        # Convert rectangle coordinates to grid coordinates
        start_x = max(0, rect.left // BLOCK_SIZE)
        end_x = min(WORLD_WIDTH, (rect.right // BLOCK_SIZE) + 1)
        start_y = max(0, rect.top // BLOCK_SIZE)
        end_y = min(WORLD_HEIGHT, (rect.bottom // BLOCK_SIZE) + 1)
        
        # Check collisions with blocks in the area
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                if (x, y) in self.blocks:
                    block_rect = self.blocks[(x, y)].rect
                    if rect.colliderect(block_rect):
                        return True
        return False