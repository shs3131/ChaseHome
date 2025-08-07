"""
Data models for ChaseHome game
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class User(BaseModel):
    """User model for player data"""
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    current_house: int = 1
    current_floor: int = 1
    completed_tasks: List[str] = []
    total_score: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)

class PlayerState(BaseModel):
    """Player state in a room"""
    uid: str
    username: str
    position: Dict[str, float] = {"x": 100, "y": 100}
    is_connected: bool = True
    current_task: Optional[str] = None

class Room(BaseModel):
    """Room model for multiplayer sessions"""
    room_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    name: str
    players: List[PlayerState] = []
    max_players: int = 5
    current_house: int = 1
    current_floor: int = 1
    active_tasks: List[str] = []
    completed_tasks: List[str] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    
    def add_player(self, player: PlayerState) -> bool:
        """Add a player to the room"""
        if len(self.players) >= self.max_players:
            return False
        
        # Remove existing player with same uid
        self.players = [p for p in self.players if p.uid != player.uid]
        self.players.append(player)
        return True
    
    def remove_player(self, uid: str) -> bool:
        """Remove a player from the room"""
        initial_count = len(self.players)
        self.players = [p for p in self.players if p.uid != uid]
        return len(self.players) < initial_count

class Task(BaseModel):
    """Task model for game objectives"""
    id: str
    name: str
    description: str
    house_id: int
    floor: int
    room: str
    steps: int = 1
    position: Dict[str, float] = {"x": 0, "y": 0}
    interact_time: float = 3.0
    requires_all_players: bool = False
    task_type: str = "interact"  # interact, puzzle, collect, repair

class House(BaseModel):
    """House model for game levels"""
    id: int
    name: str
    theme: str
    floors: int
    horror_type: str
    description: str
    tasks_per_floor: int = 3
    jumpscare_triggers: List[Dict[str, Any]] = []

class GameEvent(BaseModel):
    """WebSocket event model"""
    event: str
    data: Dict[str, Any] = {}
    room_id: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)