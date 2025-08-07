# ChaseHome - 2D Co-op Horror Game

ChaseHome is a 2D side-scrolling co-op horror game where 1-5 players work together to complete tasks and escape from haunted houses.

## Features

- **Multiplayer**: 1-5 players online co-op via WebSocket
- **10 Unique Houses**: Each with 3-5 floors and unique themes
- **20 Different Tasks**: Among Us-style task system
- **Jumpscare System**: Dynamic horror elements
- **Progress Saving**: Resume from where you left off
- **Real-time Sync**: All players synchronized via WebSocket

## Technology Stack

- **Client**: Python + Pygame
- **Server**: FastAPI + WebSocket
- **Database**: MongoDB
- **Hosting**: Render.com

## Quick Start

### Prerequisites
- Python 3.8+
- MongoDB connection (Atlas recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/shs3131/ChaseHome.git
cd ChaseHome
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure server settings in `server/config.py`

4. Start the server:
```bash
cd server
python main.py
```

5. Start the client:
```bash
cd client
python main.py
```

## Game Controls

- **Movement**: WASD or Arrow Keys
- **Interact**: E key
- **Menu**: ESC key

## Game Flow

1. Create or join a room
2. Select a house to explore
3. Complete tasks as a team
4. Progress through floors
5. Escape before the horror catches you!

## Development

This is the MVP (Minimum Viable Product) implementation. See the technical documentation in `oyun.md` for detailed specifications.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.