# ChaseHome - Deployment Guide

## Overview
ChaseHome is a 2D co-op horror game built with Python, featuring WebSocket multiplayer, task-based gameplay, and MongoDB persistence.

## Architecture
- **Server**: FastAPI + WebSocket + MongoDB
- **Client**: Pygame + WebSocket client
- **Data**: JSON configuration files
- **Deployment**: Render.com ready

## Prerequisites

### For Local Development
- Python 3.8+
- MongoDB (local or Atlas)
- Git

### For Production Deployment
- MongoDB Atlas account
- Render.com account (or similar hosting)

## Local Setup

### 1. Clone Repository
```bash
git clone https://github.com/shs3131/ChaseHome.git
cd ChaseHome
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create environment variables:
```bash
# For MongoDB connection
export MONGODB_URL="mongodb://localhost:27017"  # or Atlas URL
export DATABASE_NAME="chasehome"

# For server
export PORT=8000
export DEBUG=false
```

### 4. Run Server
```bash
cd server
python main.py
```
Server will start on http://localhost:8000

### 5. Run Client
```bash
cd client
python main.py
```

## Production Deployment

### MongoDB Atlas Setup
1. Create MongoDB Atlas account
2. Create a new cluster
3. Create database user
4. Get connection string
5. Whitelist IP addresses

### Render.com Deployment

#### Server Deployment
1. Create new Web Service on Render
2. Connect GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `cd server && python main.py`
5. Add environment variables:
   - `MONGODB_URL`: Your Atlas connection string
   - `PORT`: 8000 (or use Render's default)

#### Environment Variables for Production
```
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/chasehome
DATABASE_NAME=chasehome
DEBUG=false
PORT=8000
```

### Client Configuration for Production
Update `client/config.py`:
```python
SERVER_URL = "wss://your-app-name.onrender.com"  # Production server URL
```

## Game Features

### Multiplayer System
- 1-5 players per room
- Real-time synchronization via WebSocket
- Room creation and joining
- Player position and state sync

### Task System
- 20 different task types
- JSON-configurable tasks
- Progress tracking
- Completion rewards

### House System
- 10 unique houses with themes
- 3-5 floors per house
- Progressive difficulty
- Horror elements and jumpscares

### Jumpscare System
- Location-based triggers
- Time-based events
- Random occurrences
- Visual and audio effects

## API Endpoints

### HTTP Endpoints
- `GET /` - Health check
- `POST /api/users` - Create user
- `GET /api/users/{uid}` - Get user data
- `GET /api/houses` - List all houses
- `GET /api/rooms` - List active rooms

### WebSocket Events
- `create_room` - Create new room
- `join_room` - Join existing room
- `leave_room` - Leave current room
- `player_move` - Update player position
- `task_complete` - Mark task as completed
- `change_house` - Switch to different house

## Configuration Files

### Houses Configuration (`data/houses.json`)
```json
{
  "id": 1,
  "name": "House Name",
  "theme": "house_theme",
  "floors": 3,
  "horror_type": "Type of horror",
  "description": "House description",
  "tasks_per_floor": 3
}
```

### Tasks Configuration (`data/tasks.json`)
```json
{
  "id": "task_id",
  "name": "Task Name",
  "description": "Task description",
  "task_type": "interact|repair|puzzle|collect",
  "interact_time": 5.0,
  "requires_all_players": false
}
```

## Database Schema

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
  is_active: Boolean,
  created_at: Date
}
```

## Troubleshooting

### Common Issues

#### Server Won't Start
- Check MongoDB connection
- Verify environment variables
- Check port availability

#### Client Can't Connect
- Verify server URL in client config
- Check firewall settings
- Ensure server is running

#### Database Connection Issues
- Verify MongoDB Atlas credentials
- Check IP whitelist
- Test connection string

### Logs
Server logs are printed to console. For production, consider:
- Log aggregation service
- Error monitoring (Sentry)
- Performance monitoring

## Performance Considerations

### Server Optimization
- Use connection pooling for MongoDB
- Implement rate limiting
- Add caching for frequently accessed data
- Monitor WebSocket connections

### Client Optimization
- Optimize sprite rendering
- Limit network message frequency
- Use connection retries
- Implement graceful degradation

## Security

### Production Security
- Use HTTPS/WSS in production
- Validate all user inputs
- Implement rate limiting
- Monitor for suspicious activity
- Use environment variables for secrets

### Database Security
- Use MongoDB Atlas security features
- Regular backups
- Access control
- Audit logging

## Monitoring

### Key Metrics
- Active players
- Room creation rate
- Task completion rate
- Connection stability
- Response times

### Tools
- MongoDB Atlas monitoring
- Render.com metrics
- Custom application metrics
- Error tracking

## Scaling

### Horizontal Scaling
- Multiple server instances
- Load balancer
- Redis for session storage
- CDN for static assets

### Database Scaling
- MongoDB sharding
- Read replicas
- Indexing optimization
- Data archiving

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License
MIT License - see LICENSE file for details.

## Support
For issues and questions:
- GitHub Issues
- Documentation
- Community Discord (if available)

## Version History
- v1.0.0 - Initial MVP release
- Features: Basic multiplayer, 10 houses, 20 tasks, MongoDB persistence