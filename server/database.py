"""
Database connection and operations for ChaseHome
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from config import MONGODB_URL, DATABASE_NAME
from models import User, Room, Task, House

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(MONGODB_URL)
            self.db = self.client[DATABASE_NAME]
            # Test connection
            await self.db.command("ping")
            logger.info("Connected to MongoDB")
            
            # Create indexes
            await self.create_indexes()
            
            # Initialize default data
            await self.initialize_default_data()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def create_indexes(self):
        """Create necessary database indexes"""
        try:
            # Users collection indexes
            await self.db.users.create_index("uid", unique=True)
            await self.db.users.create_index("username")
            
            # Rooms collection indexes
            await self.db.rooms.create_index("room_id", unique=True)
            await self.db.rooms.create_index("is_active")
            
            # Tasks collection indexes
            await self.db.tasks.create_index("id", unique=True)
            await self.db.tasks.create_index([("house_id", 1), ("floor", 1)])
            
            # Houses collection indexes
            await self.db.houses.create_index("id", unique=True)
            
            logger.info("Database indexes created")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    # User operations
    async def create_user(self, user: User) -> bool:
        """Create a new user"""
        try:
            await self.db.users.insert_one(user.dict())
            return True
        except DuplicateKeyError:
            return False
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return False
    
    async def get_user(self, uid: str) -> Optional[User]:
        """Get user by UID"""
        try:
            user_data = await self.db.users.find_one({"uid": uid})
            if user_data:
                return User(**user_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    async def update_user_progress(self, uid: str, house: int, floor: int, completed_tasks: List[str]) -> bool:
        """Update user progress"""
        try:
            result = await self.db.users.update_one(
                {"uid": uid},
                {
                    "$set": {
                        "current_house": house,
                        "current_floor": floor,
                        "completed_tasks": completed_tasks,
                        "last_active": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update user progress: {e}")
            return False
    
    # Room operations
    async def create_room(self, room: Room) -> bool:
        """Create a new room"""
        try:
            await self.db.rooms.insert_one(room.dict())
            return True
        except DuplicateKeyError:
            return False
        except Exception as e:
            logger.error(f"Failed to create room: {e}")
            return False
    
    async def get_room(self, room_id: str) -> Optional[Room]:
        """Get room by ID"""
        try:
            room_data = await self.db.rooms.find_one({"room_id": room_id})
            if room_data:
                return Room(**room_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get room: {e}")
            return None
    
    async def update_room(self, room: Room) -> bool:
        """Update room data"""
        try:
            result = await self.db.rooms.replace_one(
                {"room_id": room.room_id},
                room.dict()
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update room: {e}")
            return False
    
    async def get_active_rooms(self) -> List[Room]:
        """Get all active rooms"""
        try:
            rooms_data = await self.db.rooms.find({"is_active": True}).to_list(None)
            return [Room(**room_data) for room_data in rooms_data]
        except Exception as e:
            logger.error(f"Failed to get active rooms: {e}")
            return []
    
    # Task operations
    async def get_tasks_for_house_floor(self, house_id: int, floor: int) -> List[Task]:
        """Get tasks for specific house and floor"""
        try:
            tasks_data = await self.db.tasks.find({
                "house_id": house_id,
                "floor": floor
            }).to_list(None)
            return [Task(**task_data) for task_data in tasks_data]
        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            return []
    
    # House operations
    async def get_house(self, house_id: int) -> Optional[House]:
        """Get house by ID"""
        try:
            house_data = await self.db.houses.find_one({"id": house_id})
            if house_data:
                return House(**house_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get house: {e}")
            return None
    
    async def get_all_houses(self) -> List[House]:
        """Get all houses"""
        try:
            houses_data = await self.db.houses.find().to_list(None)
            return [House(**house_data) for house_data in houses_data]
        except Exception as e:
            logger.error(f"Failed to get houses: {e}")
            return []
    
    async def initialize_default_data(self):
        """Initialize default game data if not exists"""
        try:
            # Check if houses exist
            house_count = await self.db.houses.count_documents({})
            if house_count == 0:
                await self._create_default_houses()
            
            # Check if tasks exist
            task_count = await self.db.tasks.count_documents({})
            if task_count == 0:
                await self._create_default_tasks()
                
            logger.info("Default data initialized")
        except Exception as e:
            logger.error(f"Failed to initialize default data: {e}")
    
    async def _create_default_houses(self):
        """Create default houses"""
        houses = [
            {"id": 1, "name": "Bakımsız Apartman", "theme": "abandoned", "floors": 3, "horror_type": "Gölgeler", "description": "Eski ve bakımsız bir apartman", "tasks_per_floor": 3},
            {"id": 2, "name": "Terkedilmiş Malikâne", "theme": "mansion", "floors": 4, "horror_type": "Aynada görünen yaratık", "description": "Büyük ve karanlık bir malikane", "tasks_per_floor": 3},
            {"id": 3, "name": "Yetimhane", "theme": "orphanage", "floors": 5, "horror_type": "Çocuk fısıltısı", "description": "Terk edilmiş yetimhane", "tasks_per_floor": 3},
            {"id": 4, "name": "Tren Garı", "theme": "station", "floors": 3, "horror_type": "Anonslu jumpscare", "description": "Eski tren garı", "tasks_per_floor": 3},
            {"id": 5, "name": "Fabrika", "theme": "factory", "floors": 4, "horror_type": "Metal sürtme sesleri", "description": "Terk edilmiş fabrika", "tasks_per_floor": 3},
            {"id": 6, "name": "Orman içi ev", "theme": "forest", "floors": 3, "horror_type": "Ağaçlarda yaratık", "description": "Ormanda kaybolmuş ev", "tasks_per_floor": 3},
            {"id": 7, "name": "Lüks villa", "theme": "villa", "floors": 5, "horror_type": "Sessizlik + ani ışık", "description": "Lüks ama lanetli villa", "tasks_per_floor": 3},
            {"id": 8, "name": "Terkedilmiş hastane", "theme": "hospital", "floors": 5, "horror_type": "Hasta yatakları", "description": "Eski hastane binası", "tasks_per_floor": 3},
            {"id": 9, "name": "Laboratuvar", "theme": "lab", "floors": 4, "horror_type": "Biyolojik varlıklar", "description": "Araştırma laboratuvarı", "tasks_per_floor": 3},
            {"id": 10, "name": "Kütüphane", "theme": "library", "floors": 3, "horror_type": "Kitaplar düşüyor, notlar yazıyor", "description": "Büyük eski kütüphane", "tasks_per_floor": 3},
        ]
        
        await self.db.houses.insert_many(houses)
    
    async def _create_default_tasks(self):
        """Create default tasks for all houses and floors"""
        task_templates = [
            {"id": "fix_power", "name": "Sigorta Kutusunu Onar", "description": "Işıklar gelsin", "task_type": "repair"},
            {"id": "fix_photo", "name": "Eski Fotoğrafı Yeniden Kur", "description": "Parçaları sırayla birleştir", "task_type": "puzzle"},
            {"id": "open_coded_door", "name": "Kodlu Kapıyı Aç", "description": "Sayıları evdeki nesnelerden bul", "task_type": "puzzle"},
            {"id": "fix_toy", "name": "Kurmalı Oyuncak Tamiri", "description": "Dişlileri sırayla tak", "task_type": "repair"},
            {"id": "reopen_door", "name": "Kapanan Kapıyı Yeniden Aç", "description": "Diğer katlardan güç ver", "task_type": "interact"},
            {"id": "adjust_radio", "name": "Radyo Frekansı Ayarla", "description": "Doğru frekansla gizli mesajı al", "task_type": "interact"},
            {"id": "find_key", "name": "Kayıp Anahtarı Bul", "description": "Random spawn – herkes arar", "task_type": "collect"},
            {"id": "fix_leak", "name": "Su Sızıntısını Kapat", "description": "Boru parçalarını birleştir", "task_type": "repair"},
            {"id": "sort_books", "name": "Kitapları Sıralama", "description": "Harf sırasına göre yerleştir", "task_type": "puzzle"},
            {"id": "collect_notebook", "name": "Not Defterini Topla", "description": "Sayfalar 4 farklı yerde", "task_type": "collect"},
        ]
        
        tasks = []
        for house_id in range(1, 11):
            house = await self.get_house(house_id)
            if house:
                for floor in range(1, house.floors + 1):
                    for i in range(house.tasks_per_floor):
                        template = task_templates[i % len(task_templates)]
                        task = {
                            "id": f"{template['id']}_{house_id}_{floor}_{i}",
                            "name": template["name"],
                            "description": template["description"],
                            "house_id": house_id,
                            "floor": floor,
                            "room": f"room_{i + 1}",
                            "steps": 1,
                            "position": {"x": 100 + i * 150, "y": 200},
                            "interact_time": 3.0,
                            "task_type": template["task_type"]
                        }
                        tasks.append(task)
        
        await self.db.tasks.insert_many(tasks)

# Global database instance
db = Database()