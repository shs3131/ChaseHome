"""
Task entity for ChaseHome game
"""
import pygame
import math
import sys
import os
from typing import Dict, Any
# Fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client.config import TASK_INCOMPLETE, TASK_COMPLETE, TASK_INTERACTION

class Task:
    def __init__(self, task_id: str, name: str, description: str, x: float, y: float, 
                 task_type: str = "interact", steps: int = 1, interact_time: float = 3.0):
        self.id = task_id
        self.name = name
        self.description = description
        self.x = x
        self.y = y
        self.task_type = task_type
        self.steps = steps
        self.interact_time = interact_time
        
        # Visual properties
        self.width = 40
        self.height = 40
        self.is_completed = False
        self.is_being_interacted = False
        self.interaction_progress = 0.0
        
        # Animation
        self.animation_time = 0.0
        
        # Create task surface
        self.update_surface()
    
    def update_surface(self):
        """Update the task visual surface"""
        self.surface = pygame.Surface((self.width, self.height))
        
        # Choose color based on state
        if self.is_completed:
            color = TASK_COMPLETE
        elif self.is_being_interacted:
            color = TASK_INTERACTION
        else:
            color = TASK_INCOMPLETE
        
        self.surface.fill(color)
        
        # Add task type indicator
        center_x, center_y = self.width // 2, self.height // 2
        
        if self.task_type == "repair":
            # Wrench icon
            pygame.draw.rect(self.surface, (0, 0, 0), 
                           (center_x - 8, center_y - 12, 4, 24))
            pygame.draw.rect(self.surface, (0, 0, 0), 
                           (center_x - 12, center_y - 8, 12, 4))
        elif self.task_type == "puzzle":
            # Puzzle piece icon
            pygame.draw.circle(self.surface, (0, 0, 0), (center_x, center_y), 8)
            pygame.draw.rect(self.surface, color, 
                           (center_x - 4, center_y - 12, 8, 8))
        elif self.task_type == "collect":
            # Diamond icon
            points = [
                (center_x, center_y - 10),
                (center_x - 8, center_y),
                (center_x, center_y + 10),
                (center_x + 8, center_y)
            ]
            pygame.draw.polygon(self.surface, (0, 0, 0), points)
        else:  # interact
            # Circle icon
            pygame.draw.circle(self.surface, (0, 0, 0), (center_x, center_y), 8, 2)
    
    def update(self, dt: float):
        """Update task state"""
        self.animation_time += dt
        
        # Update surface if state changed
        if self.is_being_interacted or self.is_completed:
            self.update_surface()
    
    def start_interaction(self):
        """Start task interaction"""
        if not self.is_completed:
            self.is_being_interacted = True
            self.interaction_progress = 0.0
            self.update_surface()
    
    def update_interaction(self, dt: float) -> bool:
        """Update interaction progress. Returns True if completed."""
        if not self.is_being_interacted or self.is_completed:
            return False
        
        self.interaction_progress += dt / self.interact_time
        
        if self.interaction_progress >= 1.0:
            self.complete_task()
            return True
        
        return False
    
    def stop_interaction(self):
        """Stop task interaction"""
        self.is_being_interacted = False
        self.interaction_progress = 0.0
        self.update_surface()
    
    def complete_task(self):
        """Mark task as completed"""
        self.is_completed = True
        self.is_being_interacted = False
        self.interaction_progress = 1.0
        self.update_surface()
    
    def get_rect(self) -> pygame.Rect:
        """Get task rectangle for collision detection"""
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, 
                          self.width, self.height)
    
    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        """Draw the task"""
        # Calculate screen position
        screen_x = self.x - camera_x - self.width // 2
        screen_y = self.y - camera_y - self.height // 2
        
        # Add floating animation for incomplete tasks
        if not self.is_completed:
            float_offset = math.sin(self.animation_time * 2) * 3
            screen_y += float_offset
        
        # Draw task
        screen.blit(self.surface, (screen_x, screen_y))
        
        # Draw interaction progress
        if self.is_being_interacted and self.interaction_progress > 0:
            progress_width = 60
            progress_height = 8
            progress_x = screen_x + self.width//2 - progress_width//2
            progress_y = screen_y - 20
            
            # Background
            pygame.draw.rect(screen, (64, 64, 64), 
                           (progress_x, progress_y, progress_width, progress_height))
            
            # Progress bar
            filled_width = int(progress_width * self.interaction_progress)
            pygame.draw.rect(screen, TASK_INTERACTION, 
                           (progress_x, progress_y, filled_width, progress_height))
            
            # Border
            pygame.draw.rect(screen, (255, 255, 255), 
                           (progress_x, progress_y, progress_width, progress_height), 1)
        
        # Draw task name when near
        if not self.is_completed:
            font = pygame.font.Font(None, 16)
            text = font.render(self.name, True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen_x + self.width//2, screen_y - 30))
            
            # Draw text background
            bg_rect = text_rect.copy()
            bg_rect.inflate_ip(8, 4)
            pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
            
            screen.blit(text, text_rect)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "x": self.x,
            "y": self.y,
            "task_type": self.task_type,
            "steps": self.steps,
            "interact_time": self.interact_time,
            "is_completed": self.is_completed,
            "is_being_interacted": self.is_being_interacted,
            "interaction_progress": self.interaction_progress
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create task from dictionary"""
        task = cls(
            task_id=data.get("id", ""),
            name=data.get("name", "Task"),
            description=data.get("description", ""),
            x=data.get("x", 0),
            y=data.get("y", 0),
            task_type=data.get("task_type", "interact"),
            steps=data.get("steps", 1),
            interact_time=data.get("interact_time", 3.0)
        )
        
        task.is_completed = data.get("is_completed", False)
        task.is_being_interacted = data.get("is_being_interacted", False)
        task.interaction_progress = data.get("interaction_progress", 0.0)
        task.update_surface()
        
        return task