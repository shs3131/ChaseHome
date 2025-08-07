"""
Server configuration for ChaseHome game
"""
import os

# Server settings
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# MongoDB settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "chasehome"

# Game settings
MAX_PLAYERS_PER_ROOM = 5
ROOM_ID_LENGTH = 8
DEFAULT_HOUSE_COUNT = 10
DEFAULT_FLOORS_PER_HOUSE = 3

# WebSocket settings
PING_INTERVAL = 20
PING_TIMEOUT = 10

# Collections
USERS_COLLECTION = "users"
ROOMS_COLLECTION = "rooms"
HOUSES_COLLECTION = "houses"
TASKS_COLLECTION = "tasks"