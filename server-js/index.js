/**
 * ChaseHome Node.js/Express Server
 * Converted from Python FastAPI backend
 */

import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import mongoose from 'mongoose';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import rateLimit from 'express-rate-limit';
import dotenv from 'dotenv';

import { config } from './config.js';
import { connectDatabase } from './database.js';
import { User, Room, GameEvent } from './models.js';
import { RoomManager } from './roomManager.js';
import { adminRoutes } from './routes/admin.js';
import { apiRoutes } from './routes/api.js';

dotenv.config();

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Initialize room manager
const roomManager = new RoomManager();

// Security middleware
app.use(helmet());
app.use(cors());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use('/api/', limiter);

// Logging
app.use(morgan('combined'));

// Body parsing
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Static files for admin panel
app.use('/admin', express.static('admin-panel'));

// Connection manager for WebSocket connections
class ConnectionManager {
  constructor() {
    this.activeConnections = new Map(); // userId -> socket
    this.userRooms = new Map(); // userId -> roomId
  }

  connect(socket, userId) {
    this.activeConnections.set(userId, socket);
    console.log(`User ${userId} connected`);
  }

  disconnect(userId) {
    this.activeConnections.delete(userId);
    this.userRooms.delete(userId);
    console.log(`User ${userId} disconnected`);
  }

  sendPersonalMessage(message, userId) {
    const socket = this.activeConnections.get(userId);
    if (socket) {
      socket.emit('message', message);
    }
  }

  broadcastToRoom(message, roomId, excludeUser = null) {
    const connectedPlayers = roomManager.getConnectedPlayers(roomId);
    connectedPlayers.forEach(userId => {
      if (excludeUser && userId === excludeUser) return;
      this.sendPersonalMessage(message, userId);
    });
  }
}

const connectionManager = new ConnectionManager();

// Routes
app.use('/api', apiRoutes);
app.use('/admin', adminRoutes);

// Health check endpoint
app.get('/', (req, res) => {
  res.json({ 
    message: 'ChaseHome Node.js Server is running', 
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// WebSocket connection handling
io.on('connection', (socket) => {
  console.log('New socket connection:', socket.id);

  socket.on('authenticate', async (data) => {
    const { userId, username } = data;
    
    if (!userId) {
      socket.emit('error', { message: 'User ID required' });
      return;
    }

    // Connect user
    connectionManager.connect(socket, userId);
    socket.userId = userId;
    socket.username = username;

    socket.emit('authenticated', { userId, username });
  });

  socket.on('create_room', async (data) => {
    if (!socket.userId) {
      socket.emit('error', { message: 'Not authenticated' });
      return;
    }

    try {
      const { roomName, username } = data;
      const roomId = await roomManager.createRoom(roomName, socket.userId, username);
      
      if (roomId) {
        connectionManager.userRooms.set(socket.userId, roomId);
        socket.join(roomId);
        
        socket.emit('room_created', { roomId, roomName });
        
        // Send initial room state
        const roomState = await roomManager.getRoomState(roomId);
        if (roomState) {
          socket.emit('room_state', roomState);
        }
      } else {
        socket.emit('error', { message: 'Failed to create room' });
      }
    } catch (error) {
      console.error('Error creating room:', error);
      socket.emit('error', { message: 'Failed to create room' });
    }
  });

  socket.on('join_room', async (data) => {
    if (!socket.userId) {
      socket.emit('error', { message: 'Not authenticated' });
      return;
    }

    try {
      const { roomId, username } = data;
      
      if (!roomId) {
        socket.emit('error', { message: 'Room ID required' });
        return;
      }

      const success = await roomManager.joinRoom(roomId, socket.userId, username);
      
      if (success) {
        connectionManager.userRooms.set(socket.userId, roomId);
        socket.join(roomId);
        
        // Notify all players in room
        socket.to(roomId).emit('player_joined', {
          userId: socket.userId,
          username: username
        });
        
        // Send room state to new player
        const roomState = await roomManager.getRoomState(roomId);
        if (roomState) {
          socket.emit('room_state', roomState);
        }
      } else {
        socket.emit('error', { message: 'Failed to join room' });
      }
    } catch (error) {
      console.error('Error joining room:', error);
      socket.emit('error', { message: 'Failed to join room' });
    }
  });

  socket.on('leave_room', async () => {
    const roomId = connectionManager.userRooms.get(socket.userId);
    
    if (roomId) {
      try {
        const success = await roomManager.leaveRoom(roomId, socket.userId);
        
        if (success) {
          socket.to(roomId).emit('player_left', { userId: socket.userId });
          socket.leave(roomId);
          connectionManager.userRooms.delete(socket.userId);
          socket.emit('room_left', { roomId });
        }
      } catch (error) {
        console.error('Error leaving room:', error);
      }
    }
  });

  socket.on('player_move', async (data) => {
    const roomId = connectionManager.userRooms.get(socket.userId);
    
    if (roomId) {
      try {
        const { x, y } = data;
        const success = await roomManager.updatePlayerPosition(roomId, socket.userId, x, y);
        
        if (success) {
          socket.to(roomId).emit('player_moved', {
            userId: socket.userId,
            x,
            y
          });
        }
      } catch (error) {
        console.error('Error updating player position:', error);
      }
    }
  });

  socket.on('task_complete', async (data) => {
    const roomId = connectionManager.userRooms.get(socket.userId);
    const { taskId } = data;
    
    if (roomId && taskId) {
      try {
        const success = await roomManager.completeTask(roomId, socket.userId, taskId);
        
        if (success) {
          io.to(roomId).emit('task_completed', {
            taskId,
            completedBy: socket.userId
          });
          
          // Check if floor is complete
          const floorComplete = await roomManager.checkFloorCompletion(roomId);
          if (floorComplete) {
            io.to(roomId).emit('floor_complete', {
              message: 'All tasks completed! Ready to progress.'
            });
          }
        }
      } catch (error) {
        console.error('Error completing task:', error);
      }
    }
  });

  socket.on('change_house', async (data) => {
    const roomId = connectionManager.userRooms.get(socket.userId);
    const { houseId } = data;
    
    if (roomId && houseId) {
      try {
        const success = await roomManager.changeHouse(roomId, houseId);
        
        if (success) {
          const roomState = await roomManager.getRoomState(roomId);
          if (roomState) {
            io.to(roomId).emit('room_state', roomState);
          }
        }
      } catch (error) {
        console.error('Error changing house:', error);
      }
    }
  });

  socket.on('get_room_state', async () => {
    const roomId = connectionManager.userRooms.get(socket.userId);
    
    if (roomId) {
      try {
        const roomState = await roomManager.getRoomState(roomId);
        if (roomState) {
          socket.emit('room_state', roomState);
        }
      } catch (error) {
        console.error('Error getting room state:', error);
      }
    }
  });

  socket.on('disconnect', async () => {
    if (socket.userId) {
      const roomId = connectionManager.userRooms.get(socket.userId);
      
      if (roomId) {
        try {
          await roomManager.leaveRoom(roomId, socket.userId);
          socket.to(roomId).emit('player_left', { userId: socket.userId });
        } catch (error) {
          console.error('Error handling disconnect:', error);
        }
      }
      
      connectionManager.disconnect(socket.userId);
    }
  });
});

// Start server
async function startServer() {
  try {
    // Connect to database
    await connectDatabase();
    console.log('Database connected successfully');

    // Start HTTP server
    server.listen(config.PORT, config.HOST, () => {
      console.log(`ChaseHome server running on http://${config.HOST}:${config.PORT}`);
      console.log(`Admin panel available at http://${config.HOST}:${config.PORT}/admin`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    mongoose.connection.close();
    process.exit(0);
  });
});

process.on('SIGINT', async () => {
  console.log('SIGINT received, shutting down gracefully');
  server.close(() => {
    mongoose.connection.close();
    process.exit(0);
  });
});

// Start the server
startServer();