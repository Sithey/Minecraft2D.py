import pygame
import sys
from game.world import World
from game.player import Player
from game.block import Block
from game.settings import *

class Game:
    """
    Main game class that manages the game loop, rendering, and event handling.
    Coordinates interaction between the player, world, and UI elements.
    """
    def __init__(self):
        """Initialize pygame, create the game window, and set up game objects."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Minecraft 2D")
        self.clock = pygame.time.Clock()
        
        # Initialize world and player
        self.world = World()
        spawn_x = WORLD_WIDTH // 2
        spawn_y = self.world.get_surface_height(spawn_x) - 3 
        self.player = Player(spawn_x * BLOCK_SIZE, spawn_y * BLOCK_SIZE)
        
        # Camera system for scrolling
        self.camera_x = 0
        self.camera_y = 0
        
        # Block selection system
        self.available_blocks = ['dirt', 'stone', 'wood']  
        self.current_block_index = 0  
        self.player.selected_block = self.available_blocks[self.current_block_index]
        
    def handle_events(self):
        """
        Process all game events including input handling.
        
        Returns:
            bool: False if the game should quit, True otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse wheel for block selection
                if event.button == 4:  # Wheel up
                    self.current_block_index = (self.current_block_index - 1) % len(self.available_blocks)
                    self.player.selected_block = self.available_blocks[self.current_block_index]
                elif event.button == 5:  # Wheel down
                    self.current_block_index = (self.current_block_index + 1) % len(self.available_blocks)
                    self.player.selected_block = self.available_blocks[self.current_block_index]
                # Handle block breaking and placement
                elif event.button in (1, 3):  # Left or right click
                    # Adjust mouse position for camera offset
                    mouse_pos = (pygame.mouse.get_pos()[0] + self.camera_x,
                               pygame.mouse.get_pos()[1] + self.camera_y)
                    player_pos = (self.player.rect.centerx, self.player.rect.centery)
                    if event.button == 1:  # Left click to break
                        self.world.break_block(mouse_pos, player_pos)
                    elif event.button == 3:  # Right click to place
                        block_pos = (mouse_pos[0], mouse_pos[1], self.player.rect)
                        self.world.place_block(block_pos, self.player.selected_block)
                        
            if event.type == pygame.KEYDOWN:
                # Handle number keys for block selection
                if event.key == pygame.K_1:
                    self.current_block_index = 0
                    self.player.selected_block = self.available_blocks[self.current_block_index]
                elif event.key == pygame.K_2:
                    self.current_block_index = 1
                    self.player.selected_block = self.available_blocks[self.current_block_index]
                elif event.key == pygame.K_3:
                    self.current_block_index = 2
                    self.player.selected_block = self.available_blocks[self.current_block_index]
        return True

    def update(self):
        """Update game state including player position and camera."""
        self.player.update(self.world)
        # Center camera on player
        self.camera_x = self.player.rect.centerx - SCREEN_WIDTH // 2
        self.camera_y = self.player.rect.centery - SCREEN_HEIGHT // 2
        
    def render(self):
        """Render the entire game scene including world, player, and UI."""
        self.screen.fill(SKY_COLOR)
        
        # Render world blocks with camera offset
        for block in self.world.blocks.values():
            block_rect = block.rect.copy()
            block_rect.x -= self.camera_x
            block_rect.y -= self.camera_y
            if -BLOCK_SIZE <= block_rect.x <= SCREEN_WIDTH and -BLOCK_SIZE <= block_rect.y <= SCREEN_HEIGHT:
                pygame.draw.rect(self.screen, block.color, block_rect)
                pygame.draw.rect(self.screen, (0, 0, 0), block_rect, 1)
        
        # Render player with camera offset
        self.player.rect.x -= self.camera_x
        self.player.rect.y -= self.camera_y
        self.player.draw(self.screen)
        self.player.rect.x += self.camera_x
        self.player.rect.y += self.camera_y
        
        # Render hotbar UI
        hotbar_width = BLOCK_SIZE * 5
        hotbar_height = BLOCK_SIZE
        hotbar_x = (SCREEN_WIDTH - hotbar_width) // 2
        hotbar_y = SCREEN_HEIGHT - hotbar_height - 10
        
        # Draw hotbar background
        pygame.draw.rect(self.screen, (128, 128, 128), 
                        (hotbar_x, hotbar_y, hotbar_width, hotbar_height))
        
        # Draw hotbar slots
        for i in range(5):
            slot_x = hotbar_x + (i * BLOCK_SIZE)
            pygame.draw.rect(self.screen, (64, 64, 64), 
                           (slot_x, hotbar_y, BLOCK_SIZE, BLOCK_SIZE), 2)
            
            # Draw block preview in slot
            block_type = None
            if i < len(self.available_blocks):
                block_type = self.available_blocks[i]
                
            if block_type:
                temp_block = Block(0, 0, block_type)
                inner_rect = pygame.Rect(slot_x + 4, hotbar_y + 4, 
                                       BLOCK_SIZE - 8, BLOCK_SIZE - 8)
                pygame.draw.rect(self.screen, temp_block.color, inner_rect)
                pygame.draw.rect(self.screen, (0, 0, 0), inner_rect, 1)
                
            # Draw slot number
            font = pygame.font.Font(None, 20)
            text = font.render(str(i + 1), True, (255, 255, 255))
            text_rect = text.get_rect(center=(slot_x + BLOCK_SIZE // 2, 
                                            hotbar_y - 15))
            self.screen.blit(text, text_rect)
            
            # Highlight selected slot
            if i == self.current_block_index:
                pygame.draw.rect(self.screen, (255, 255, 255), 
                               (slot_x, hotbar_y, BLOCK_SIZE, BLOCK_SIZE), 3)
        
        pygame.display.flip()
        
    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()