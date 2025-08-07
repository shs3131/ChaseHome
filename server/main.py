"""
Main FastAPI server for ChaseHome game
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import HOST, PORT, DEBUG
from database import db
from models import User, Room, GameEvent, PlayerState
from room_manager import room_manager

# Configure logging
logging.basicConfig(level=logging.INFO if not DEBUG else logging.DEBUG)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="ChaseHome Server", version="1.0.0")

# CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  # user_id -> websocket
        self.user_rooms: Dict[str, str] = {}  # user_id -> room_id
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected")
    
    def disconnect(self, user_id: str):
        """Disconnect user"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_rooms:
            del self.user_rooms[user_id]
        logger.info(f"User {user_id} disconnected")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {user_id}: {e}")
    
    async def broadcast_to_room(self, message: dict, room_id: str, exclude_user: Optional[str] = None):
        """Broadcast message to all users in a room"""
        connected_players = room_manager.get_connected_players(room_id)
        for user_id in connected_players:
            if exclude_user and user_id == exclude_user:
                continue
            await self.send_personal_message(message, user_id)

manager = ConnectionManager()

# HTTP API endpoints
class CreateUserRequest(BaseModel):
    username: str

class CreateRoomRequest(BaseModel):
    room_name: str
    username: str

class JoinRoomRequest(BaseModel):
    room_id: str
    username: str

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await db.connect()

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await db.disconnect()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "ChaseHome Server is running", "version": "1.0.0"}

@app.post("/api/users")
async def create_user(request: CreateUserRequest):
    """Create a new user"""
    user = User(username=request.username)
    success = await db.create_user(user)
    
    if success:
        return {"uid": user.uid, "username": user.username}
    else:
        raise HTTPException(status_code=400, detail="Failed to create user")

@app.get("/api/users/{uid}")
async def get_user(uid: str):
    """Get user by UID"""
    user = await db.get_user(uid)
    if user:
        return user.dict()
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/api/houses")
async def get_houses():
    """Get all available houses"""
    houses = await db.get_all_houses()
    return [house.dict() for house in houses]

@app.get("/api/rooms")
async def get_active_rooms():
    """Get all active rooms"""
    rooms = await db.get_active_rooms()
    return [{"room_id": room.room_id, "name": room.name, "players": len(room.players), "max_players": room.max_players} for room in rooms]

# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """Main WebSocket endpoint for game communication"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            await handle_websocket_message(message, user_id)
            
    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected")
        # Handle disconnection - remove from room
        room_id = manager.user_rooms.get(user_id)
        if room_id:
            await room_manager.leave_room(room_id, user_id)
            
            # Notify other players
            await manager.broadcast_to_room({
                "event": "player_left",
                "data": {"user_id": user_id}
            }, room_id, exclude_user=user_id)
        
        manager.disconnect(user_id)
    
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)

async def handle_websocket_message(message: dict, user_id: str):
    """Handle incoming WebSocket messages"""
    event = message.get("event")
    data = message.get("data", {})
    
    try:
        if event == "create_room":
            await handle_create_room(data, user_id)
        
        elif event == "join_room":
            await handle_join_room(data, user_id)
        
        elif event == "leave_room":
            await handle_leave_room(data, user_id)
        
        elif event == "player_move":
            await handle_player_move(data, user_id)
        
        elif event == "task_complete":
            await handle_task_complete(data, user_id)
        
        elif event == "change_house":
            await handle_change_house(data, user_id)
        
        elif event == "get_room_state":
            await handle_get_room_state(data, user_id)
        
        else:
            logger.warning(f"Unknown event: {event} from user {user_id}")
    
    except Exception as e:
        logger.error(f"Error handling event {event} from user {user_id}: {e}")
        await manager.send_personal_message({
            "event": "error",
            "data": {"message": f"Failed to handle {event}"}
        }, user_id)

async def handle_create_room(data: dict, user_id: str):
    """Handle room creation"""
    room_name = data.get("room_name", "New Room")
    username = data.get("username", "Player")
    
    room_id = await room_manager.create_room(room_name, user_id, username)
    
    if room_id:
        manager.user_rooms[user_id] = room_id
        
        # Send success response
        await manager.send_personal_message({
            "event": "room_created",
            "data": {
                "room_id": room_id,
                "room_name": room_name
            }
        }, user_id)
        
        # Send initial room state
        room_state = await room_manager.get_room_state(room_id)
        if room_state:
            await manager.send_personal_message({
                "event": "room_state",
                "data": room_state
            }, user_id)
    else:
        await manager.send_personal_message({
            "event": "error",
            "data": {"message": "Failed to create room"}
        }, user_id)

async def handle_join_room(data: dict, user_id: str):
    """Handle joining a room"""
    room_id = data.get("room_id")
    username = data.get("username", "Player")
    
    if not room_id:
        await manager.send_personal_message({
            "event": "error",
            "data": {"message": "Room ID required"}
        }, user_id)
        return
    
    success = await room_manager.join_room(room_id, user_id, username)
    
    if success:
        manager.user_rooms[user_id] = room_id
        
        # Notify all players in room
        await manager.broadcast_to_room({
            "event": "player_joined",
            "data": {
                "user_id": user_id,
                "username": username
            }
        }, room_id)
        
        # Send room state to new player
        room_state = await room_manager.get_room_state(room_id)
        if room_state:
            await manager.send_personal_message({
                "event": "room_state",
                "data": room_state
            }, user_id)
    else:
        await manager.send_personal_message({
            "event": "error",
            "data": {"message": "Failed to join room"}
        }, user_id)

async def handle_leave_room(data: dict, user_id: str):
    """Handle leaving a room"""
    room_id = manager.user_rooms.get(user_id)
    
    if room_id:
        success = await room_manager.leave_room(room_id, user_id)
        
        if success:
            # Notify other players
            await manager.broadcast_to_room({
                "event": "player_left",
                "data": {"user_id": user_id}
            }, room_id, exclude_user=user_id)
            
            # Remove from user rooms
            del manager.user_rooms[user_id]
            
            await manager.send_personal_message({
                "event": "room_left",
                "data": {"room_id": room_id}
            }, user_id)

async def handle_player_move(data: dict, user_id: str):
    """Handle player movement"""
    room_id = manager.user_rooms.get(user_id)
    
    if room_id:
        x = data.get("x", 0)
        y = data.get("y", 0)
        
        success = await room_manager.update_player_position(room_id, user_id, x, y)
        
        if success:
            # Broadcast position to other players
            await manager.broadcast_to_room({
                "event": "player_moved",
                "data": {
                    "user_id": user_id,
                    "x": x,
                    "y": y
                }
            }, room_id, exclude_user=user_id)

async def handle_task_complete(data: dict, user_id: str):
    """Handle task completion"""
    room_id = manager.user_rooms.get(user_id)
    task_id = data.get("task_id")
    
    if room_id and task_id:
        success = await room_manager.complete_task(room_id, user_id, task_id)
        
        if success:
            # Broadcast task completion to all players
            await manager.broadcast_to_room({
                "event": "task_completed",
                "data": {
                    "task_id": task_id,
                    "completed_by": user_id
                }
            }, room_id)
            
            # Check if floor is complete
            floor_complete = await room_manager.check_floor_completion(room_id)
            if floor_complete:
                await manager.broadcast_to_room({
                    "event": "floor_complete",
                    "data": {"message": "All tasks completed! Ready to progress."}
                }, room_id)

async def handle_change_house(data: dict, user_id: str):
    """Handle house change"""
    room_id = manager.user_rooms.get(user_id)
    house_id = data.get("house_id")
    
    if room_id and house_id:
        success = await room_manager.change_house(room_id, house_id)
        
        if success:
            # Send updated room state to all players
            room_state = await room_manager.get_room_state(room_id)
            if room_state:
                await manager.broadcast_to_room({
                    "event": "room_state",
                    "data": room_state
                }, room_id)

async def handle_get_room_state(data: dict, user_id: str):
    """Handle room state request"""
    room_id = manager.user_rooms.get(user_id)
    
    if room_id:
        room_state = await room_manager.get_room_state(room_id)
        if room_state:
            await manager.send_personal_message({
                "event": "room_state",
                "data": room_state
            }, user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, debug=DEBUG)