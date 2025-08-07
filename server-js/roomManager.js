/**
 * Room Manager for ChaseHome
 * Converted from Python room_manager.py
 */

import { Room, User, GameEvent, Task } from './models.js';
import { config } from './config.js';

export class RoomManager {
  constructor() {
    this.activeRooms = new Map(); // roomId -> Room data cache
    this.connectedPlayers = new Map(); // roomId -> Set of userIds
  }

  async createRoom(roomName, hostUserId, hostUsername) {
    try {
      // Check if user already has an active room
      const existingRoom = await Room.findOne({
        hostUserId,
        isActive: true
      });

      if (existingRoom) {
        return existingRoom.roomId;
      }

      // Create new room
      const room = new Room({
        name: roomName,
        hostUserId,
        players: [{
          userId: hostUserId,
          username: hostUsername,
          x: 100,
          y: 100,
          isActive: true,
          lastSeen: new Date()
        }],
        isActive: true,
        lastActivity: new Date()
      });

      await room.save();

      // Update cache
      this.activeRooms.set(room.roomId, room);
      this.connectedPlayers.set(room.roomId, new Set([hostUserId]));

      // Log event
      await this.logGameEvent(room.roomId, hostUserId, 'game_start', {
        roomName,
        hostUsername
      });

      console.log(`Room created: ${room.roomId} by ${hostUsername}`);
      return room.roomId;
    } catch (error) {
      console.error('Error creating room:', error);
      return null;
    }
  }

  async joinRoom(roomId, userId, username) {
    try {
      const room = await Room.findOne({ roomId, isActive: true });
      
      if (!room) {
        console.log(`Room not found: ${roomId}`);
        return false;
      }

      // Check if room is full
      if (room.players.length >= config.MAX_PLAYERS_PER_ROOM) {
        console.log(`Room ${roomId} is full`);
        return false;
      }

      // Check if user is already in room
      const existingPlayer = room.players.find(p => p.userId === userId);
      if (existingPlayer) {
        existingPlayer.isActive = true;
        existingPlayer.lastSeen = new Date();
      } else {
        // Add new player
        room.players.push({
          userId,
          username,
          x: 100,
          y: 100,
          isActive: true,
          lastSeen: new Date()
        });
      }

      room.lastActivity = new Date();
      await room.save();

      // Update cache
      this.activeRooms.set(roomId, room);
      if (!this.connectedPlayers.has(roomId)) {
        this.connectedPlayers.set(roomId, new Set());
      }
      this.connectedPlayers.get(roomId).add(userId);

      // Log event
      await this.logGameEvent(roomId, userId, 'player_join', { username });

      console.log(`User ${username} joined room ${roomId}`);
      return true;
    } catch (error) {
      console.error('Error joining room:', error);
      return false;
    }
  }

  async leaveRoom(roomId, userId) {
    try {
      const room = await Room.findOne({ roomId, isActive: true });
      
      if (!room) {
        return false;
      }

      // Remove player from room
      room.players = room.players.filter(p => p.userId !== userId);
      
      // If room is empty or host left, mark as inactive
      if (room.players.length === 0 || room.hostUserId === userId) {
        room.isActive = false;
      }

      room.lastActivity = new Date();
      await room.save();

      // Update cache
      if (this.connectedPlayers.has(roomId)) {
        this.connectedPlayers.get(roomId).delete(userId);
        
        if (this.connectedPlayers.get(roomId).size === 0) {
          this.connectedPlayers.delete(roomId);
          this.activeRooms.delete(roomId);
        }
      }

      // Log event
      await this.logGameEvent(roomId, userId, 'player_leave', {});

      console.log(`User ${userId} left room ${roomId}`);
      return true;
    } catch (error) {
      console.error('Error leaving room:', error);
      return false;
    }
  }

  async updatePlayerPosition(roomId, userId, x, y) {
    try {
      const room = await Room.findOne({ roomId, isActive: true });
      
      if (!room) {
        return false;
      }

      // Find and update player position
      const player = room.players.find(p => p.userId === userId);
      if (player) {
        player.x = x;
        player.y = y;
        player.lastSeen = new Date();
        
        room.lastActivity = new Date();
        await room.save();

        // Update cache
        this.activeRooms.set(roomId, room);
        return true;
      }

      return false;
    } catch (error) {
      console.error('Error updating player position:', error);
      return false;
    }
  }

  async completeTask(roomId, userId, taskId) {
    try {
      const room = await Room.findOne({ roomId, isActive: true });
      
      if (!room) {
        return false;
      }

      // Check if task is already completed
      if (room.completedTasks.includes(taskId)) {
        return false;
      }

      // Add to completed tasks
      room.completedTasks.push(taskId);
      
      // Remove from active tasks if present
      room.activeTasks = room.activeTasks.filter(id => id !== taskId);
      
      room.lastActivity = new Date();
      await room.save();

      // Update user's completed tasks
      await User.updateOne(
        { uid: userId },
        { $addToSet: { completedTasks: taskId } }
      );

      // Log event
      await this.logGameEvent(roomId, userId, 'task_complete', { taskId });

      // Update cache
      this.activeRooms.set(roomId, room);

      console.log(`Task ${taskId} completed by ${userId} in room ${roomId}`);
      return true;
    } catch (error) {
      console.error('Error completing task:', error);
      return false;
    }
  }

  async checkFloorCompletion(roomId) {
    try {
      const room = await Room.findOne({ roomId, isActive: true });
      
      if (!room) {
        return false;
      }

      // Get tasks for current house and floor
      const floorTasks = await Task.find({
        houseId: room.currentHouse,
        floor: room.currentFloor
      });

      const requiredTaskIds = floorTasks.map(task => task.taskId);
      const completedTaskIds = room.completedTasks;

      // Check if all floor tasks are completed
      const allCompleted = requiredTaskIds.every(taskId => 
        completedTaskIds.includes(taskId)
      );

      if (allCompleted) {
        // Log floor completion
        await this.logGameEvent(roomId, room.hostUserId, 'floor_complete', {
          house: room.currentHouse,
          floor: room.currentFloor
        });
      }

      return allCompleted;
    } catch (error) {
      console.error('Error checking floor completion:', error);
      return false;
    }
  }

  async changeHouse(roomId, houseId) {
    try {
      const room = await Room.findOne({ roomId, isActive: true });
      
      if (!room) {
        return false;
      }

      room.currentHouse = houseId;
      room.currentFloor = 1;
      room.completedTasks = [];
      room.activeTasks = [];
      room.lastActivity = new Date();

      await room.save();

      // Log event
      await this.logGameEvent(roomId, room.hostUserId, 'house_change', { 
        newHouseId: houseId 
      });

      // Update cache
      this.activeRooms.set(roomId, room);

      console.log(`Room ${roomId} changed to house ${houseId}`);
      return true;
    } catch (error) {
      console.error('Error changing house:', error);
      return false;
    }
  }

  async getRoomState(roomId) {
    try {
      const room = await Room.findOne({ roomId, isActive: true });
      
      if (!room) {
        return null;
      }

      // Get current floor tasks
      const floorTasks = await Task.find({
        houseId: room.currentHouse,
        floor: room.currentFloor
      });

      return {
        roomId: room.roomId,
        name: room.name,
        hostUserId: room.hostUserId,
        players: room.players,
        maxPlayers: room.maxPlayers,
        currentHouse: room.currentHouse,
        currentFloor: room.currentFloor,
        activeTasks: floorTasks.filter(task => 
          !room.completedTasks.includes(task.taskId)
        ),
        completedTasks: room.completedTasks,
        gameStarted: room.gameStarted,
        lastActivity: room.lastActivity
      };
    } catch (error) {
      console.error('Error getting room state:', error);
      return null;
    }
  }

  getConnectedPlayers(roomId) {
    return Array.from(this.connectedPlayers.get(roomId) || []);
  }

  async logGameEvent(roomId, userId, eventType, eventData = {}) {
    try {
      const gameEvent = new GameEvent({
        roomId,
        userId,
        eventType,
        eventData
      });

      await gameEvent.save();
    } catch (error) {
      console.error('Error logging game event:', error);
    }
  }

  // Cleanup inactive rooms
  async cleanupInactiveRooms() {
    try {
      const cutoffTime = new Date(Date.now() - config.ROOM_TIMEOUT);
      
      const inactiveRooms = await Room.find({
        $or: [
          { isActive: false },
          { lastActivity: { $lt: cutoffTime } }
        ]
      });

      for (const room of inactiveRooms) {
        room.isActive = false;
        await room.save();
        
        // Remove from cache
        this.activeRooms.delete(room.roomId);
        this.connectedPlayers.delete(room.roomId);
      }

      if (inactiveRooms.length > 0) {
        console.log(`Cleaned up ${inactiveRooms.length} inactive rooms`);
      }
    } catch (error) {
      console.error('Error cleaning up inactive rooms:', error);
    }
  }
}

export default RoomManager;