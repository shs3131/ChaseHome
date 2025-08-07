"""
Room management for ChaseHome multiplayer sessions
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime

from models import Room, PlayerState, User, GameEvent
from database import db

logger = logging.getLogger(__name__)

class RoomManager:
    def __init__(self):
        self.active_rooms: Dict[str, Room] = {}
        self.player_connections: Dict[str, Set[str]] = {}  # room_id -> set of user_ids
        
    async def create_room(self, room_name: str, creator_uid: str, creator_username: str) -> Optional[str]:
        """Create a new room"""
        try:
            # Create room instance
            room = Room(name=room_name)
            
            # Add creator as first player
            creator = PlayerState(
                uid=creator_uid,
                username=creator_username,
                position={"x": 100, "y": 100},
                is_connected=True
            )
            
            room.add_player(creator)
            
            # Save to database
            success = await db.create_room(room)
            if success:
                self.active_rooms[room.room_id] = room
                if room.room_id not in self.player_connections:
                    self.player_connections[room.room_id] = set()
                self.player_connections[room.room_id].add(creator_uid)
                
                logger.info(f"Room {room.room_id} created by {creator_username}")
                return room.room_id
            
            return None
        except Exception as e:
            logger.error(f"Failed to create room: {e}")
            return None
    
    async def join_room(self, room_id: str, user_uid: str, username: str) -> bool:
        """Join an existing room"""
        try:
            # Get room from memory or database
            room = self.active_rooms.get(room_id)
            if not room:
                room = await db.get_room(room_id)
                if room:
                    self.active_rooms[room_id] = room
            
            if not room or not room.is_active:
                return False
            
            # Check if room is full
            if len(room.players) >= room.max_players:
                return False
            
            # Create player state
            player = PlayerState(
                uid=user_uid,
                username=username,
                position={"x": 100, "y": 100},
                is_connected=True
            )
            
            # Add player to room
            success = room.add_player(player)
            if success:
                # Update database
                await db.update_room(room)
                
                # Update connections
                if room_id not in self.player_connections:
                    self.player_connections[room_id] = set()
                self.player_connections[room_id].add(user_uid)
                
                logger.info(f"Player {username} joined room {room_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to join room: {e}")
            return False
    
    async def leave_room(self, room_id: str, user_uid: str) -> bool:
        """Leave a room"""
        try:
            room = self.active_rooms.get(room_id)
            if not room:
                return False
            
            # Remove player from room
            success = room.remove_player(user_uid)
            if success:
                # Update connections
                if room_id in self.player_connections:
                    self.player_connections[room_id].discard(user_uid)
                
                # If room is empty, deactivate it
                if len(room.players) == 0:
                    room.is_active = False
                    if room_id in self.active_rooms:
                        del self.active_rooms[room_id]
                    if room_id in self.player_connections:
                        del self.player_connections[room_id]
                
                # Update database
                await db.update_room(room)
                
                logger.info(f"Player {user_uid} left room {room_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to leave room: {e}")
            return False
    
    async def update_player_position(self, room_id: str, user_uid: str, x: float, y: float) -> bool:
        """Update player position in room"""
        try:
            room = self.active_rooms.get(room_id)
            if not room:
                return False
            
            # Find and update player
            for player in room.players:
                if player.uid == user_uid:
                    player.position = {"x": x, "y": y}
                    # Don't update database for every position change - too frequent
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to update player position: {e}")
            return False
    
    async def complete_task(self, room_id: str, user_uid: str, task_id: str) -> bool:
        """Mark a task as completed"""
        try:
            room = self.active_rooms.get(room_id)
            if not room:
                return False
            
            # Add to completed tasks if not already there
            if task_id not in room.completed_tasks:
                room.completed_tasks.append(task_id)
                
                # Remove from active tasks if present
                if task_id in room.active_tasks:
                    room.active_tasks.remove(task_id)
                
                # Update database
                await db.update_room(room)
                
                logger.info(f"Task {task_id} completed in room {room_id} by {user_uid}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to complete task: {e}")
            return False
    
    async def start_new_floor(self, room_id: str) -> bool:
        """Progress room to next floor"""
        try:
            room = self.active_rooms.get(room_id)
            if not room:
                return False
            
            # Get house info to check max floors
            house = await db.get_house(room.current_house)
            if not house:
                return False
            
            # Check if can progress
            if room.current_floor >= house.floors:
                return False  # Already at max floor
            
            # Progress to next floor
            room.current_floor += 1
            room.completed_tasks = []  # Reset completed tasks for new floor
            
            # Load tasks for new floor
            tasks = await db.get_tasks_for_house_floor(room.current_house, room.current_floor)
            room.active_tasks = [task.id for task in tasks]
            
            # Update database
            await db.update_room(room)
            
            logger.info(f"Room {room_id} progressed to floor {room.current_floor}")
            return True
        except Exception as e:
            logger.error(f"Failed to start new floor: {e}")
            return False
    
    async def change_house(self, room_id: str, house_id: int) -> bool:
        """Change the current house for the room"""
        try:
            room = self.active_rooms.get(room_id)
            if not room:
                return False
            
            # Validate house exists
            house = await db.get_house(house_id)
            if not house:
                return False
            
            # Update room
            room.current_house = house_id
            room.current_floor = 1
            room.completed_tasks = []
            
            # Load tasks for first floor
            tasks = await db.get_tasks_for_house_floor(house_id, 1)
            room.active_tasks = [task.id for task in tasks]
            
            # Update database
            await db.update_room(room)
            
            logger.info(f"Room {room_id} changed to house {house_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to change house: {e}")
            return False
    
    def get_room(self, room_id: str) -> Optional[Room]:
        """Get room by ID"""
        return self.active_rooms.get(room_id)
    
    def get_room_players(self, room_id: str) -> List[PlayerState]:
        """Get all players in a room"""
        room = self.active_rooms.get(room_id)
        return room.players if room else []
    
    def get_connected_players(self, room_id: str) -> Set[str]:
        """Get set of connected player UIDs in room"""
        return self.player_connections.get(room_id, set())
    
    async def check_floor_completion(self, room_id: str) -> bool:
        """Check if all tasks on current floor are completed"""
        try:
            room = self.active_rooms.get(room_id)
            if not room:
                return False
            
            # Get required tasks for current floor
            tasks = await db.get_tasks_for_house_floor(room.current_house, room.current_floor)
            required_task_ids = [task.id for task in tasks]
            
            # Check if all required tasks are completed
            return all(task_id in room.completed_tasks for task_id in required_task_ids)
        except Exception as e:
            logger.error(f"Failed to check floor completion: {e}")
            return False
    
    async def get_room_state(self, room_id: str) -> Optional[Dict]:
        """Get complete room state for clients"""
        try:
            room = self.active_rooms.get(room_id)
            if not room:
                return None
            
            # Get house info
            house = await db.get_house(room.current_house)
            
            # Get current floor tasks
            tasks = await db.get_tasks_for_house_floor(room.current_house, room.current_floor)
            
            return {
                "room_id": room.room_id,
                "room_name": room.name,
                "players": [player.dict() for player in room.players],
                "current_house": room.current_house,
                "current_floor": room.current_floor,
                "house_name": house.name if house else "Unknown",
                "max_floors": house.floors if house else 1,
                "active_tasks": [task.dict() for task in tasks],
                "completed_tasks": room.completed_tasks,
                "tasks_remaining": len(tasks) - len(room.completed_tasks),
                "is_floor_complete": await self.check_floor_completion(room_id)
            }
        except Exception as e:
            logger.error(f"Failed to get room state: {e}")
            return None

# Global room manager instance
room_manager = RoomManager()