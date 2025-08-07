"""
UI system for ChaseHome game
"""
import pygame
from typing import List, Dict, Any, Optional, Callable
import sys
import os

# Fix imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from client.config import *

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 callback: Optional[Callable] = None, font_size: int = 24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, font_size)
        self.is_hovered = False
        self.is_pressed = False
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events. Returns True if button was clicked."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return False
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                if self.callback:
                    self.callback()
                return True
            self.is_pressed = False
        
        return False
    
    def draw(self, screen: pygame.Surface):
        """Draw the button"""
        # Choose color based on state
        if self.is_pressed:
            color = UI_BUTTON_ACTIVE
        elif self.is_hovered:
            color = UI_BUTTON_HOVER
        else:
            color = UI_BUTTON
        
        # Draw button background
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, UI_TEXT, self.rect, 2)
        
        # Draw text
        text_surface = self.font.render(self.text, True, UI_TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class TextInput:
    def __init__(self, x: int, y: int, width: int, height: int, placeholder: str = "", 
                 max_length: int = 50, font_size: int = 24):
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.max_length = max_length
        self.font = pygame.font.Font(None, font_size)
        self.text = ""
        self.is_focused = False
        self.cursor_time = 0
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events. Returns True if enter was pressed."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.is_focused = self.rect.collidepoint(event.pos)
        
        elif event.type == pygame.KEYDOWN and self.is_focused:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_length and event.unicode.isprintable():
                self.text += event.unicode
        
        return False
    
    def update(self, dt: float):
        """Update cursor animation"""
        self.cursor_time += dt
    
    def draw(self, screen: pygame.Surface):
        """Draw the text input"""
        # Draw background
        color = UI_BUTTON_HOVER if self.is_focused else UI_BUTTON
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, UI_TEXT, self.rect, 2)
        
        # Draw text or placeholder
        display_text = self.text if self.text else self.placeholder
        text_color = UI_TEXT if self.text else UI_TEXT_DISABLED
        
        text_surface = self.font.render(display_text, True, text_color)
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        screen.blit(text_surface, text_rect)
        
        # Draw cursor
        if self.is_focused and self.cursor_time % 1 < 0.5:
            cursor_x = text_rect.right + 2 if self.text else self.rect.x + 10
            pygame.draw.line(screen, UI_TEXT, 
                           (cursor_x, self.rect.y + 5), 
                           (cursor_x, self.rect.bottom - 5), 2)

class Panel:
    def __init__(self, x: int, y: int, width: int, height: int, title: str = ""):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.font = pygame.font.Font(None, 32)
        self.content_font = pygame.font.Font(None, 24)
        
    def draw(self, screen: pygame.Surface):
        """Draw the panel background"""
        # Draw panel background
        pygame.draw.rect(screen, UI_PANEL, self.rect)
        pygame.draw.rect(screen, UI_TEXT, self.rect, 2)
        
        # Draw title
        if self.title:
            title_surface = self.font.render(self.title, True, UI_TEXT)
            title_rect = title_surface.get_rect(midtop=(self.rect.centerx, self.rect.y + 10))
            screen.blit(title_surface, title_rect)

class GameUI:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_screen = "menu"  # menu, lobby, game
        
        # UI elements for different screens
        self.elements: Dict[str, List] = {
            "menu": [],
            "lobby": [],
            "game": []
        }
        
        self.create_menu_ui()
        self.create_lobby_ui()
        self.create_game_ui()
        
        # Game state for UI
        self.room_state: Optional[Dict[str, Any]] = None
        self.player_name = "Player"
        
    def create_menu_ui(self):
        """Create main menu UI elements"""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # Title panel
        title_panel = Panel(center_x - 200, 100, 400, 100, "ChaseHome")
        
        # Player name input
        name_input = TextInput(center_x - 150, center_y - 100, 300, 40, 
                              "Enter your name...", font_size=20)
        
        # Create room button
        create_button = Button(center_x - 200, center_y - 30, 180, 50, "Create Room")
        
        # Join room button
        join_button = Button(center_x + 20, center_y - 30, 180, 50, "Join Room")
        
        # Room ID input (hidden initially)
        room_input = TextInput(center_x - 150, center_y + 40, 300, 40, 
                              "Enter room ID...", font_size=20)
        
        self.elements["menu"] = [title_panel, name_input, create_button, join_button, room_input]
        
        # Store references for easy access
        self.name_input = name_input
        self.room_input = room_input
        self.create_button = create_button
        self.join_button = join_button
    
    def create_lobby_ui(self):
        """Create lobby UI elements"""
        # Room info panel
        room_panel = Panel(50, 50, 300, 150, "Room Info")
        
        # Players panel
        players_panel = Panel(50, 220, 300, 300, "Players")
        
        # House selection panel
        house_panel = Panel(400, 50, 350, 200, "Select House")
        
        # Start game button
        start_button = Button(400, 280, 200, 50, "Start Game")
        
        # Leave room button
        leave_button = Button(620, 280, 130, 50, "Leave Room")
        
        self.elements["lobby"] = [room_panel, players_panel, house_panel, start_button, leave_button]
        
        # Store references
        self.room_panel = room_panel
        self.players_panel = players_panel
        self.house_panel = house_panel
        self.start_button = start_button
        self.leave_button = leave_button
    
    def create_game_ui(self):
        """Create in-game UI elements"""
        # Task list panel
        task_panel = Panel(self.screen_width - 300, 50, 250, 400, "Tasks")
        
        # Player list panel
        player_panel = Panel(self.screen_width - 300, 470, 250, 200, "Players")
        
        # Floor info panel
        floor_panel = Panel(50, self.screen_height - 100, 400, 80)
        
        # Menu button
        menu_button = Button(self.screen_width - 100, 10, 80, 30, "Menu")
        
        self.elements["game"] = [task_panel, player_panel, floor_panel, menu_button]
        
        # Store references
        self.task_panel = task_panel
        self.player_panel = player_panel
        self.floor_panel = floor_panel
        self.menu_button = menu_button
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle UI events. Returns action if any."""
        current_elements = self.elements.get(self.current_screen, [])
        
        for element in current_elements:
            if hasattr(element, 'handle_event'):
                result = element.handle_event(event)
                
                # Handle specific UI actions
                if result and self.current_screen == "menu":
                    if element == self.create_button:
                        self.player_name = self.name_input.text or "Player"
                        return "create_room"
                    elif element == self.join_button:
                        self.player_name = self.name_input.text or "Player"
                        return "join_room"
                    elif element == self.name_input:
                        self.player_name = self.name_input.text or "Player"
                
                elif result and self.current_screen == "lobby":
                    if element == self.start_button:
                        return "start_game"
                    elif element == self.leave_button:
                        return "leave_room"
                
                elif result and self.current_screen == "game":
                    if element == self.menu_button:
                        return "show_menu"
        
        return None
    
    def update(self, dt: float):
        """Update UI elements"""
        current_elements = self.elements.get(self.current_screen, [])
        
        for element in current_elements:
            if hasattr(element, 'update'):
                element.update(dt)
    
    def draw(self, screen: pygame.Surface):
        """Draw current screen UI"""
        current_elements = self.elements.get(self.current_screen, [])
        
        for element in current_elements:
            element.draw(screen)
        
        # Draw additional content based on screen
        if self.current_screen == "lobby":
            self.draw_lobby_content(screen)
        elif self.current_screen == "game":
            self.draw_game_content(screen)
    
    def draw_lobby_content(self, screen: pygame.Surface):
        """Draw lobby-specific content"""
        if not self.room_state:
            return
        
        # Draw room info
        font = pygame.font.Font(None, 20)
        y_offset = self.room_panel.rect.y + 40
        
        room_id_text = font.render(f"Room ID: {self.room_state.get('room_id', 'N/A')}", True, UI_TEXT)
        screen.blit(room_id_text, (self.room_panel.rect.x + 10, y_offset))
        
        room_name_text = font.render(f"Name: {self.room_state.get('room_name', 'N/A')}", True, UI_TEXT)
        screen.blit(room_name_text, (self.room_panel.rect.x + 10, y_offset + 25))
        
        house_text = font.render(f"House: {self.room_state.get('house_name', 'None')}", True, UI_TEXT)
        screen.blit(house_text, (self.room_panel.rect.x + 10, y_offset + 50))
        
        # Draw players
        y_offset = self.players_panel.rect.y + 40
        players = self.room_state.get('players', [])
        
        for i, player in enumerate(players):
            player_text = font.render(f"• {player.get('username', 'Unknown')}", True, UI_TEXT)
            screen.blit(player_text, (self.players_panel.rect.x + 10, y_offset + i * 25))
    
    def draw_game_content(self, screen: pygame.Surface):
        """Draw game-specific content"""
        if not self.room_state:
            return
        
        font = pygame.font.Font(None, 18)
        
        # Draw tasks
        y_offset = self.task_panel.rect.y + 40
        tasks = self.room_state.get('active_tasks', [])
        completed_tasks = self.room_state.get('completed_tasks', [])
        
        for i, task in enumerate(tasks[:12]):  # Limit to 12 visible tasks
            task_id = task.get('id', '')
            task_name = task.get('name', 'Unknown Task')
            is_complete = task_id in completed_tasks
            
            color = TASK_COMPLETE if is_complete else TASK_INCOMPLETE
            status = "✓" if is_complete else "○"
            
            task_text = font.render(f"{status} {task_name}", True, color)
            screen.blit(task_text, (self.task_panel.rect.x + 10, y_offset + i * 20))
        
        # Draw players
        y_offset = self.player_panel.rect.y + 40
        players = self.room_state.get('players', [])
        
        for i, player in enumerate(players):
            username = player.get('username', 'Unknown')
            is_connected = player.get('is_connected', False)
            
            color = UI_TEXT if is_connected else UI_TEXT_DISABLED
            status = "●" if is_connected else "○"
            
            player_text = font.render(f"{status} {username}", True, color)
            screen.blit(player_text, (self.player_panel.rect.x + 10, y_offset + i * 20))
        
        # Draw floor info
        font = pygame.font.Font(None, 24)
        current_floor = self.room_state.get('current_floor', 1)
        max_floors = self.room_state.get('max_floors', 1)
        house_name = self.room_state.get('house_name', 'Unknown House')
        tasks_remaining = self.room_state.get('tasks_remaining', 0)
        
        floor_text = font.render(f"{house_name} - Floor {current_floor}/{max_floors}", True, UI_TEXT)
        screen.blit(floor_text, (self.floor_panel.rect.x + 10, self.floor_panel.rect.y + 10))
        
        tasks_text = font.render(f"Tasks remaining: {tasks_remaining}", True, UI_TEXT)
        screen.blit(tasks_text, (self.floor_panel.rect.x + 10, self.floor_panel.rect.y + 35))
    
    def set_screen(self, screen: str):
        """Change current screen"""
        self.current_screen = screen
    
    def update_room_state(self, room_state: Dict[str, Any]):
        """Update room state for UI display"""
        self.room_state = room_state
    
    def get_player_name(self) -> str:
        """Get entered player name"""
        return self.player_name
    
    def get_room_id(self) -> str:
        """Get entered room ID"""
        return self.room_input.text