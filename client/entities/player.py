"""
Player entity for ChaseHome game
"""
import pygame
import sys
import os
from typing import Dict, Any
# Fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client.config import PLAYER_SPEED, PLAYER_SIZE

class Player:
    def __init__(self, x: float, y: float, uid: str, username: str, is_local: bool = False):
        self.x = x
        self.y = y
        self.uid = uid
        self.username = username
        self.is_local = is_local
        
        # Visual properties
        self.width, self.height = PLAYER_SIZE
        self.color = (0, 255, 0) if is_local else (0, 0, 255)
        
        # Movement
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Game state
        self.current_task = None
        self.is_interacting = False
        
        # Create player surface
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(self.color)
        
        # Add a simple face
        if is_local:
            # Local player - green with yellow face
            pygame.draw.circle(self.surface, (255, 255, 0), (self.width//2, self.height//3), 8)
            pygame.draw.circle(self.surface, (0, 0, 0), (self.width//2 - 3, self.height//3 - 2), 2)
            pygame.draw.circle(self.surface, (0, 0, 0), (self.width//2 + 3, self.height//3 - 2), 2)
        else:
            # Other players - blue with white face
            pygame.draw.circle(self.surface, (255, 255, 255), (self.width//2, self.height//3), 8)
            pygame.draw.circle(self.surface, (0, 0, 0), (self.width//2 - 3, self.height//3 - 2), 2)
            pygame.draw.circle(self.surface, (0, 0, 0), (self.width//2 + 3, self.height//3 - 2), 2)
    
    def update(self, dt: float, keys_pressed: Dict[int, bool] = None):
        """Update player state"""
        if self.is_local and keys_pressed:
            # Handle local player movement
            self.velocity_x = 0
            self.velocity_y = 0
            
            if keys_pressed.get(pygame.K_a) or keys_pressed.get(pygame.K_LEFT):
                self.velocity_x = -PLAYER_SPEED
            if keys_pressed.get(pygame.K_d) or keys_pressed.get(pygame.K_RIGHT):
                self.velocity_x = PLAYER_SPEED
            if keys_pressed.get(pygame.K_w) or keys_pressed.get(pygame.K_UP):
                self.velocity_y = -PLAYER_SPEED
            if keys_pressed.get(pygame.K_s) or keys_pressed.get(pygame.K_DOWN):
                self.velocity_y = PLAYER_SPEED
            
            # Update position
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
            
            # Keep player on screen (basic boundary check)
            self.x = max(0, min(self.x, 1024 - self.width))
            self.y = max(0, min(self.y, 768 - self.height))
    
    def set_position(self, x: float, y: float):
        """Set player position (for network updates)"""
        self.x = x
        self.y = y
    
    def get_rect(self) -> pygame.Rect:
        """Get player rectangle for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        """Draw the player"""
        # Calculate screen position
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Draw player
        screen.blit(self.surface, (screen_x, screen_y))
        
        # Draw username
        font = pygame.font.Font(None, 20)
        text_color = (255, 255, 255) if self.is_local else (200, 200, 200)
        text = font.render(self.username, True, text_color)
        text_rect = text.get_rect(center=(screen_x + self.width//2, screen_y - 10))
        screen.blit(text, text_rect)
        
        # Draw interaction indicator
        if self.is_interacting:
            pygame.draw.circle(screen, (255, 255, 0), 
                             (int(screen_x + self.width//2), int(screen_y + self.height//2)), 
                             30, 3)
    
    def can_interact_with_task(self, task_x: float, task_y: float, interaction_distance: float = 50) -> bool:
        """Check if player can interact with a task"""
        dx = self.x + self.width//2 - task_x
        dy = self.y + self.height//2 - task_y
        distance = (dx*dx + dy*dy) ** 0.5
        return distance <= interaction_distance
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary for network transmission"""
        return {
            "uid": self.uid,
            "username": self.username,
            "x": self.x,
            "y": self.y,
            "current_task": self.current_task,
            "is_interacting": self.is_interacting
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], is_local: bool = False):
        """Create player from dictionary"""
        player = cls(
            x=data.get("x", 0),
            y=data.get("y", 0),
            uid=data.get("uid", ""),
            username=data.get("username", "Player"),
            is_local=is_local
        )
        player.current_task = data.get("current_task")
        player.is_interacting = data.get("is_interacting", False)
        return player