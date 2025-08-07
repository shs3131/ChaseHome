"""
Simple test script to validate server startup without MongoDB
"""
import sys
import os
import asyncio
import unittest.mock

# Add server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

async def test_server_imports():
    """Test that server modules can be imported"""
    try:
        print("Testing server imports...")
        
        # Test basic imports
        import config
        print("✓ Config imported")
        
        import models
        print("✓ Models imported")
        
        # Mock MongoDB for testing
        with unittest.mock.patch('motor.motor_asyncio.AsyncIOMotorClient'):
            import database
            print("✓ Database imported (with mocked MongoDB)")
        
        with unittest.mock.patch('database.db'):
            import room_manager
            print("✓ Room manager imported")
        
        print("✓ All server imports successful!")
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

async def test_models():
    """Test model creation"""
    try:
        print("\nTesting models...")
        from models import User, Room, Task, House, PlayerState
        
        # Test User model
        user = User(username="TestUser")
        print(f"✓ User created: {user.username}")
        
        # Test Room model
        room = Room(name="Test Room")
        print(f"✓ Room created: {room.name}")
        
        # Test PlayerState
        player = PlayerState(uid="test123", username="TestPlayer")
        room.add_player(player)
        print(f"✓ Player added to room: {len(room.players)} players")
        
        # Test Task model
        task = Task(
            id="test_task",
            name="Test Task",
            description="A test task",
            house_id=1,
            floor=1,
            room="test_room"
        )
        print(f"✓ Task created: {task.name}")
        
        # Test House model
        house = House(
            id=1,
            name="Test House",
            theme="test",
            floors=3,
            horror_type="Test Horror",
            description="A test house for testing"
        )
        print(f"✓ House created: {house.name}")
        
        print("✓ All model tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_client_imports():
    """Test client imports without pygame display"""
    try:
        print("\nTesting client imports...")
        
        # Set SDL to use dummy video driver
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        
        # Test network client
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'client'))
        import network
        print("✓ Network client imported")
        
        import config as client_config
        print("✓ Client config imported")
        
        # Test entities
        from entities.player import Player
        from entities.task import Task as ClientTask
        print("✓ Client entities imported")
        
        # Test creating a player
        player = Player(100, 100, "test123", "TestPlayer", is_local=True)
        print(f"✓ Player created at ({player.x}, {player.y})")
        
        # Test creating a task
        task = ClientTask("test_task", "Test Task", "Description", 200, 200)
        print(f"✓ Task created at ({task.x}, {task.y})")
        
        print("✓ All client import tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Client import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("ChaseHome MVP - Testing Implementation")
    print("=" * 50)
    
    # Test server
    server_ok = await test_server_imports()
    if server_ok:
        models_ok = await test_models()
    else:
        models_ok = False
    
    # Test client
    client_ok = test_client_imports()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Server imports: {'✓' if server_ok else '✗'}")
    print(f"Model creation: {'✓' if models_ok else '✗'}")
    print(f"Client imports: {'✓' if client_ok else '✗'}")
    
    if server_ok and models_ok and client_ok:
        print("\n🎉 All tests passed! ChaseHome MVP is ready.")
        print("\nTo run the game:")
        print("1. Start server: cd server && python main.py")
        print("2. Start client: cd client && python main.py")
    else:
        print("\n❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())