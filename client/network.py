"""
Network client for ChaseHome game WebSocket communication
"""
import asyncio
import json
import logging
import websocket
import threading
from typing import Optional, Callable, Dict, Any
import time
import sys
import os

# Fix imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)

class NetworkClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.ws: Optional[websocket.WebSocket] = None
        self.is_connected = False
        self.user_id: Optional[str] = None
        self.message_handlers: Dict[str, Callable] = {}
        self.connection_thread: Optional[threading.Thread] = None
        self.should_reconnect = True
        
    def add_message_handler(self, event: str, handler: Callable):
        """Add a handler for specific message types"""
        self.message_handlers[event] = handler
    
    def connect(self, user_id: str) -> bool:
        """Connect to the WebSocket server"""
        try:
            self.user_id = user_id
            ws_url = f"{self.server_url}/ws/{user_id}"
            
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Start connection in a separate thread
            self.connection_thread = threading.Thread(
                target=self.ws.run_forever,
                daemon=True
            )
            self.connection_thread.start()
            
            # Wait a bit for connection
            time.sleep(1)
            return self.is_connected
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        self.should_reconnect = False
        if self.ws:
            self.ws.close()
        self.is_connected = False
    
    def send_message(self, event: str, data: Dict[str, Any] = None) -> bool:
        """Send a message to the server"""
        if not self.is_connected or not self.ws:
            logger.warning("Not connected to server")
            return False
        
        try:
            message = {
                "event": event,
                "data": data or {}
            }
            self.ws.send(json.dumps(message))
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def _on_open(self, ws):
        """Handle WebSocket connection opened"""
        self.is_connected = True
        logger.info("Connected to server")
    
    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            event = data.get("event")
            payload = data.get("data", {})
            
            # Call appropriate handler
            if event in self.message_handlers:
                self.message_handlers[event](payload)
            else:
                logger.warning(f"No handler for event: {event}")
                
        except Exception as e:
            logger.error(f"Failed to handle message: {e}")
    
    def _on_error(self, ws, error):
        """Handle WebSocket errors"""
        logger.error(f"WebSocket error: {error}")
        self.is_connected = False
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection closed"""
        self.is_connected = False
        logger.info("Disconnected from server")
        
        # Attempt to reconnect if needed
        if self.should_reconnect and self.user_id:
            logger.info("Attempting to reconnect...")
            time.sleep(5)  # Wait before reconnecting
            if self.should_reconnect:  # Check again in case disconnect was called
                self.connect(self.user_id)
    
    # Game-specific message methods
    def create_room(self, room_name: str, username: str) -> bool:
        """Create a new room"""
        return self.send_message("create_room", {
            "room_name": room_name,
            "username": username
        })
    
    def join_room(self, room_id: str, username: str) -> bool:
        """Join an existing room"""
        return self.send_message("join_room", {
            "room_id": room_id,
            "username": username
        })
    
    def leave_room(self) -> bool:
        """Leave current room"""
        return self.send_message("leave_room")
    
    def send_player_move(self, x: float, y: float) -> bool:
        """Send player position update"""
        return self.send_message("player_move", {
            "x": x,
            "y": y
        })
    
    def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed"""
        return self.send_message("task_complete", {
            "task_id": task_id
        })
    
    def change_house(self, house_id: int) -> bool:
        """Change to a different house"""
        return self.send_message("change_house", {
            "house_id": house_id
        })
    
    def get_room_state(self) -> bool:
        """Request current room state"""
        return self.send_message("get_room_state")