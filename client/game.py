"""
Main game class for ChaseHome
"""
import pygame
import logging
import uuid
from typing import Dict, List, Optional, Any
import time
import sys
import os

# Fix imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from client.config import *
from client.network import NetworkClient
from client.ui import GameUI
from client.entities.player import Player
from client.entities.task import Task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Screen setup
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        
        # Game state
        self.running = True
        self.game_state = "menu"  # menu, lobby, game
        self.user_id = str(uuid.uuid4())
        
        # Network
        self.network = NetworkClient(SERVER_URL)
        self.setup_network_handlers()
        
        # UI
        self.ui = GameUI(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Game objects
        self.local_player: Optional[Player] = None
        self.other_players: Dict[str, Player] = {}
        self.tasks: Dict[str, Task] = {}
        self.room_state: Optional[Dict[str, Any]] = None
        
        # Game settings
        self.camera_x = 0
        self.camera_y = 0
        self.current_task_interaction: Optional[str] = None
        self.interaction_start_time = 0
        
        # Input state
        self.keys_pressed = {}
        
        # Jumpscare system
        self.jumpscare_active = False
        self.jumpscare_timer = 0
        self.screen_shake_x = 0
        self.screen_shake_y = 0
        
        logger.info(f"Game initialized with user ID: {self.user_id}")
    
    def setup_network_handlers(self):
        """Set up network message handlers"""
        self.network.add_message_handler("room_created", self.on_room_created)
        self.network.add_message_handler("room_state", self.on_room_state)
        self.network.add_message_handler("player_joined", self.on_player_joined)
        self.network.add_message_handler("player_left", self.on_player_left)
        self.network.add_message_handler("player_moved", self.on_player_moved)
        self.network.add_message_handler("task_completed", self.on_task_completed)
        self.network.add_message_handler("floor_complete", self.on_floor_complete)
        self.network.add_message_handler("error", self.on_error)
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.draw()
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed[event.key] = True
                
                # Handle specific game inputs
                if event.key == pygame.K_e and self.game_state == "game":
                    self.handle_interact()
                elif event.key == pygame.K_ESCAPE:
                    if self.game_state == "game":
                        self.ui.set_screen("menu")
                        self.game_state = "menu"
            
            elif event.type == pygame.KEYUP:
                if event.key in self.keys_pressed:
                    del self.keys_pressed[event.key]
                
                # Stop interaction on key release
                if event.key == pygame.K_e and self.current_task_interaction:
                    self.stop_task_interaction()
            
            # Handle UI events
            ui_action = self.ui.handle_event(event)
            if ui_action:
                self.handle_ui_action(ui_action)
    
    def handle_ui_action(self, action: str):
        """Handle UI actions"""
        if action == "create_room":
            self.create_room()
        elif action == "join_room":
            self.join_room()
        elif action == "leave_room":
            self.leave_room()
        elif action == "start_game":
            self.start_game()
        elif action == "show_menu":
            self.show_menu()
    
    def update(self, dt: float):
        """Update game state"""
        # Update UI
        self.ui.update(dt)
        
        # Update based on game state
        if self.game_state == "game":
            self.update_game(dt)
        
        # Update jumpscare
        if self.jumpscare_active:
            self.update_jumpscare(dt)
    
    def update_game(self, dt: float):
        """Update game-specific logic"""
        # Update local player
        if self.local_player:
            old_x, old_y = self.local_player.x, self.local_player.y
            self.local_player.update(dt, self.keys_pressed)
            
            # Send position update if player moved
            if (self.local_player.x != old_x or self.local_player.y != old_y):
                self.network.send_player_move(self.local_player.x, self.local_player.y)
            
            # Update camera to follow player
            self.camera_x = self.local_player.x - WINDOW_WIDTH // 2
            self.camera_y = self.local_player.y - WINDOW_HEIGHT // 2
        
        # Update other players
        for player in self.other_players.values():
            player.update(dt)
        
        # Update tasks
        for task in self.tasks.values():
            task.update(dt)
        
        # Update task interaction
        if self.current_task_interaction:
            task = self.tasks.get(self.current_task_interaction)
            if task and task.update_interaction(dt):
                # Task completed
                self.network.complete_task(task.id)
                self.stop_task_interaction()
    
    def update_jumpscare(self, dt: float):
        """Update jumpscare effects"""
        self.jumpscare_timer -= dt
        
        if self.jumpscare_timer <= 0:
            self.jumpscare_active = False
            self.screen_shake_x = 0
            self.screen_shake_y = 0
        else:
            # Screen shake effect
            import random
            self.screen_shake_x = random.randint(-SCREEN_SHAKE_INTENSITY, SCREEN_SHAKE_INTENSITY)
            self.screen_shake_y = random.randint(-SCREEN_SHAKE_INTENSITY, SCREEN_SHAKE_INTENSITY)
    
    def draw(self):
        """Draw everything"""
        # Clear screen
        self.screen.fill(BLACK)
        
        # Apply screen shake
        shake_offset_x = self.screen_shake_x if self.jumpscare_active else 0
        shake_offset_y = self.screen_shake_y if self.jumpscare_active else 0
        
        if self.game_state == "game":
            self.draw_game(shake_offset_x, shake_offset_y)
        
        # Draw UI
        self.ui.draw(self.screen)
        
        # Draw jumpscare overlay
        if self.jumpscare_active:
            self.draw_jumpscare_overlay()
        
        pygame.display.flip()
    
    def draw_game(self, shake_x: float = 0, shake_y: float = 0):
        """Draw game world"""
        # Draw background
        self.screen.fill((32, 32, 32))
        
        # Draw simple floor grid
        grid_size = 64
        start_x = int(-self.camera_x - shake_x) % grid_size
        start_y = int(-self.camera_y - shake_y) % grid_size
        
        for x in range(start_x, WINDOW_WIDTH + grid_size, grid_size):
            pygame.draw.line(self.screen, (48, 48, 48), (x, 0), (x, WINDOW_HEIGHT))
        
        for y in range(start_y, WINDOW_HEIGHT + grid_size, grid_size):
            pygame.draw.line(self.screen, (48, 48, 48), (0, y), (WINDOW_WIDTH, y))
        
        # Draw tasks
        for task in self.tasks.values():
            task.draw(self.screen, self.camera_x + shake_x, self.camera_y + shake_y)
        
        # Draw other players
        for player in self.other_players.values():
            player.draw(self.screen, self.camera_x + shake_x, self.camera_y + shake_y)
        
        # Draw local player
        if self.local_player:
            self.local_player.draw(self.screen, self.camera_x + shake_x, self.camera_y + shake_y)
    
    def draw_jumpscare_overlay(self):
        """Draw jumpscare visual effects"""
        # Flash red overlay
        flash_intensity = int(128 * (self.jumpscare_timer / JUMPSCARE_DURATION))
        if flash_intensity > 0:
            flash_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            flash_surface.fill((255, 0, 0))
            flash_surface.set_alpha(flash_intensity)
            self.screen.blit(flash_surface, (0, 0))
        
        # Draw "SCARE!" text
        if self.jumpscare_timer > JUMPSCARE_DURATION * 0.5:
            font = pygame.font.Font(None, 72)
            text = font.render("SCARE!", True, (255, 255, 255))
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(text, text_rect)
    
    def handle_interact(self):
        """Handle interaction key press"""
        if not self.local_player:
            return
        
        # Find nearest task
        nearest_task = None
        nearest_distance = float('inf')
        
        for task in self.tasks.values():
            if task.is_completed:
                continue
            
            if self.local_player.can_interact_with_task(task.x, task.y):
                dx = self.local_player.x - task.x
                dy = self.local_player.y - task.y
                distance = (dx*dx + dy*dy) ** 0.5
                
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_task = task
        
        # Start interaction with nearest task
        if nearest_task and not self.current_task_interaction:
            self.start_task_interaction(nearest_task.id)
    
    def start_task_interaction(self, task_id: str):
        """Start interacting with a task"""
        task = self.tasks.get(task_id)
        if task and not task.is_completed:
            self.current_task_interaction = task_id
            self.interaction_start_time = time.time()
            task.start_interaction()
            
            if self.local_player:
                self.local_player.is_interacting = True
    
    def stop_task_interaction(self):
        """Stop current task interaction"""
        if self.current_task_interaction:
            task = self.tasks.get(self.current_task_interaction)
            if task:
                task.stop_interaction()
            
            self.current_task_interaction = None
            
            if self.local_player:
                self.local_player.is_interacting = False
    
    def trigger_jumpscare(self):
        """Trigger a jumpscare effect"""
        self.jumpscare_active = True
        self.jumpscare_timer = JUMPSCARE_DURATION
        
        # Play sound effect if available
        try:
            # pygame.mixer.Sound("assets/jumpscare.wav").play()
            pass
        except:
            pass
    
    # Network handlers
    def create_room(self):
        """Create a new room"""
        if not self.network.is_connected:
            success = self.network.connect(self.user_id)
            if not success:
                logger.error("Failed to connect to server")
                return
        
        room_name = f"{self.ui.get_player_name()}'s Room"
        self.network.create_room(room_name, self.ui.get_player_name())
    
    def join_room(self):
        """Join an existing room"""
        room_id = self.ui.get_room_id()
        if not room_id:
            logger.warning("No room ID provided")
            return
        
        if not self.network.is_connected:
            success = self.network.connect(self.user_id)
            if not success:
                logger.error("Failed to connect to server")
                return
        
        self.network.join_room(room_id, self.ui.get_player_name())
    
    def leave_room(self):
        """Leave current room"""
        self.network.leave_room()
        self.ui.set_screen("menu")
        self.game_state = "menu"
        
        # Reset game state
        self.local_player = None
        self.other_players.clear()
        self.tasks.clear()
        self.room_state = None
    
    def start_game(self):
        """Start the game"""
        self.ui.set_screen("game")
        self.game_state = "game"
        
        # Create local player
        if self.room_state:
            # Find local player in room state
            for player_data in self.room_state.get('players', []):
                if player_data.get('uid') == self.user_id:
                    self.local_player = Player.from_dict(player_data, is_local=True)
                    break
            
            # Create other players
            self.other_players.clear()
            for player_data in self.room_state.get('players', []):
                if player_data.get('uid') != self.user_id:
                    self.other_players[player_data['uid']] = Player.from_dict(player_data)
            
            # Create tasks
            self.tasks.clear()
            for task_data in self.room_state.get('active_tasks', []):
                self.tasks[task_data['id']] = Task.from_dict(task_data)
    
    def show_menu(self):
        """Show main menu"""
        self.leave_room()
    
    # Network event handlers
    def on_room_created(self, data: Dict[str, Any]):
        """Handle room created event"""
        logger.info(f"Room created: {data}")
        self.ui.set_screen("lobby")
        self.game_state = "lobby"
    
    def on_room_state(self, data: Dict[str, Any]):
        """Handle room state update"""
        self.room_state = data
        self.ui.update_room_state(data)
        
        # Update tasks if in game
        if self.game_state == "game":
            # Update existing tasks or create new ones
            new_tasks = {}
            for task_data in data.get('active_tasks', []):
                task_id = task_data['id']
                if task_id in self.tasks:
                    # Update existing task
                    task = self.tasks[task_id]
                    if task_data['id'] in data.get('completed_tasks', []):
                        task.complete_task()
                else:
                    # Create new task
                    new_tasks[task_id] = Task.from_dict(task_data)
            
            self.tasks.update(new_tasks)
    
    def on_player_joined(self, data: Dict[str, Any]):
        """Handle player joined event"""
        logger.info(f"Player joined: {data}")
        self.network.get_room_state()  # Request updated room state
    
    def on_player_left(self, data: Dict[str, Any]):
        """Handle player left event"""
        user_id = data.get('user_id')
        if user_id in self.other_players:
            del self.other_players[user_id]
        logger.info(f"Player left: {data}")
    
    def on_player_moved(self, data: Dict[str, Any]):
        """Handle player movement"""
        user_id = data.get('user_id')
        x = data.get('x', 0)
        y = data.get('y', 0)
        
        if user_id in self.other_players:
            self.other_players[user_id].set_position(x, y)
    
    def on_task_completed(self, data: Dict[str, Any]):
        """Handle task completion"""
        task_id = data.get('task_id')
        completed_by = data.get('completed_by')
        
        if task_id in self.tasks:
            self.tasks[task_id].complete_task()
        
        # Random chance for jumpscare after task completion
        import random
        if random.random() < 0.1:  # 10% chance
            self.trigger_jumpscare()
        
        logger.info(f"Task {task_id} completed by {completed_by}")
    
    def on_floor_complete(self, data: Dict[str, Any]):
        """Handle floor completion"""
        logger.info("Floor completed!")
        # Could show celebration animation or progress to next floor
    
    def on_error(self, data: Dict[str, Any]):
        """Handle error messages"""
        message = data.get('message', 'Unknown error')
        logger.error(f"Server error: {message}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.network:
            self.network.disconnect()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    try:
        game.run()
    except KeyboardInterrupt:
        pass
    finally:
        game.cleanup()