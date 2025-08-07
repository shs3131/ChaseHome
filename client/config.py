"""
Client configuration for ChaseHome game
"""
import os

# Window settings
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
WINDOW_TITLE = "ChaseHome"
FPS = 60

# Game settings
PLAYER_SPEED = 200  # pixels per second
PLAYER_SIZE = (32, 48)

# Network settings
SERVER_URL = os.getenv("SERVER_URL", "ws://localhost:8000")
RECONNECT_DELAY = 5

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)

# UI Colors
UI_BACKGROUND = (32, 32, 32)
UI_PANEL = (48, 48, 48)
UI_BUTTON = (64, 64, 64)
UI_BUTTON_HOVER = (80, 80, 80)
UI_BUTTON_ACTIVE = (96, 96, 96)
UI_TEXT = WHITE
UI_TEXT_DISABLED = GRAY

# Task Colors
TASK_INCOMPLETE = YELLOW
TASK_COMPLETE = GREEN
TASK_INTERACTION = BLUE

# Jumpscare settings
JUMPSCARE_DURATION = 2.0  # seconds
SCREEN_SHAKE_INTENSITY = 10  # pixels

# Audio settings
MASTER_VOLUME = 0.7
SFX_VOLUME = 0.8
MUSIC_VOLUME = 0.5

# Input settings
INTERACT_KEY = "e"
MENU_KEY = "escape"