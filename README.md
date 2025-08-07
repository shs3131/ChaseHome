# ChaseHome - 2D Co-op Horror Game

ChaseHome is a 2D side-scrolling co-op horror game where 1-5 players work together to complete tasks and escape from haunted houses.

## 🎮 Game Features

### 👥 Multiplayer Co-op
- **1-5 players** online co-op via WebSocket
- **Real-time synchronization** of all players
- **Room system** with easy join/create functionality
- **Progress saving** - resume from where you left off

### 🏚️ Horror Experience  
- **10 unique houses** with different themes and horror types
- **3-5 floors per house** with progressive difficulty
- **Dynamic jumpscare system** with location and time-based triggers
- **Atmospheric horror** elements tailored to each house theme

### 📋 Task-Based Gameplay
- **20 different task types** - repair, puzzle, collect, interact
- **Among Us-style** task completion mechanics
- **Team coordination** required for certain tasks
- **Floor progression** when all tasks are completed

### 🎨 Houses & Themes
1. **Bakımsız Apartman** - Abandoned apartment with shadows
2. **Terkedilmiş Malikâne** - Mansion with mirror creatures  
3. **Yetimhane** - Orphanage with child whispers
4. **Tren Garı** - Train station with announcement scares
5. **Fabrika** - Factory with machinery sounds
6. **Orman içi ev** - Forest house with creature sightings
7. **Lüks villa** - Luxury villa with light flashes
8. **Terkedilmiş hastane** - Abandoned hospital with medical equipment
9. **Laboratuvar** - Laboratory with biological specimens
10. **Kütüphane** - Library with falling books and writing

## 🛠️ Technology Stack

- **Client**: Python + Pygame
- **Server**: FastAPI + WebSocket  
- **Database**: MongoDB
- **Communication**: WebSocket for real-time multiplayer
- **Deployment**: Render.com ready

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB connection (local or Atlas)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/shs3131/ChaseHome.git
cd ChaseHome
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
export MONGODB_URL="mongodb://localhost:27017"  # or your Atlas URL
export DATABASE_NAME="chasehome"
```

4. **Start the server:**
```bash
cd server
python main.py
```

5. **Start the client (in a new terminal):**
```bash
cd client
python main.py
```

## 🎯 Game Controls

- **Movement**: WASD or Arrow Keys
- **Interact**: E key (hold to complete tasks)
- **Menu**: ESC key

## 🏗️ Project Structure

```
ChaseHome/
├── server/              # FastAPI WebSocket server
│   ├── main.py         # Server entry point
│   ├── database.py     # MongoDB integration
│   ├── models.py       # Data models
│   ├── room_manager.py # Room and player management
│   └── config.py       # Server configuration
├── client/              # Pygame game client
│   ├── main.py         # Client entry point
│   ├── game.py         # Main game logic
│   ├── ui.py           # User interface system
│   ├── network.py      # WebSocket client
│   ├── entities/       # Game entities (Player, Task)
│   └── config.py       # Client configuration
├── data/               # Game configuration
│   ├── houses.json     # House definitions
│   ├── tasks.json      # Task definitions
│   └── jumpscares.json # Jumpscare configurations
├── requirements.txt    # Python dependencies
├── test_mvp.py        # Test script
├── DEPLOYMENT.md      # Deployment guide
├── ROADMAP.md         # Development roadmap
└── README.md          # This file
```

## 🌐 API Overview

### WebSocket Events
- `create_room` - Create a new multiplayer room
- `join_room` - Join an existing room
- `leave_room` - Leave current room
- `player_move` - Update player position
- `task_complete` - Mark task as completed
- `change_house` - Switch to different house

### HTTP Endpoints
- `GET /` - Health check
- `POST /api/users` - Create user
- `GET /api/houses` - List all houses
- `GET /api/rooms` - List active rooms

## 🗄️ Database Schema

### Users Collection
```javascript
{
  uid: String,
  username: String,
  current_house: Number,
  current_floor: Number,
  completed_tasks: [String],
  total_score: Number,
  created_at: Date,
  last_active: Date
}
```

### Rooms Collection  
```javascript
{
  room_id: String,
  name: String,
  players: [PlayerState],
  current_house: Number,
  current_floor: Number,
  active_tasks: [String],
  completed_tasks: [String],
  is_active: Boolean
}
```

## 🚀 Deployment

### Local Development
See the installation steps above.

### Production Deployment
1. **MongoDB Atlas**: Set up cloud database
2. **Render.com**: Deploy server with environment variables
3. **Client**: Update server URL in client config

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 🧪 Testing

Run the test suite to validate installation:
```bash
python test_mvp.py
```

This tests:
- ✅ Server module imports
- ✅ Database model creation  
- ✅ Client module imports
- ✅ Entity creation and basic functionality

## 🔮 Future Plans

See [ROADMAP.md](ROADMAP.md) for detailed development plans including:

### Phase 2 - Polish & Enhancement
- Enhanced graphics and audio
- Improved task variety  
- Player progression system
- Better UI/UX

### Phase 3 - Advanced Features
- New game modes (competitive, story mode)
- AI-controlled horror entities
- Content creation tools
- Performance optimization

### Phase 4 - Platform Expansion
- Mobile platforms (iOS, Android)
- Console versions
- Community features
- Modding support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly (`python test_mvp.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 Game Design Document

For detailed game mechanics and design decisions, see [oyun.md](oyun.md) (original Turkish specification).

## 🐛 Troubleshooting

### Common Issues

**Server won't start:**
- Check MongoDB connection
- Verify environment variables
- Ensure port 8000 is available

**Client can't connect:**
- Verify server is running
- Check server URL in client config
- Test WebSocket connection

**Database errors:**
- Verify MongoDB credentials
- Check network connectivity
- Review MongoDB Atlas IP whitelist

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Built with Python, Pygame, FastAPI, and MongoDB
- Inspired by Among Us task mechanics and horror game aesthetics
- Special thanks to the open source community

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/shs3131/ChaseHome/issues)
- **Documentation**: See docs in this repository
- **Community**: Join our discussions in GitHub Discussions

---

**🎮 Ready to play? Follow the Quick Start guide above and start your horror adventure!**