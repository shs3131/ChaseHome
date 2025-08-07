/**
 * Mongoose models for ChaseHome
 * Converted from Python models
 */

import mongoose from 'mongoose';

// User Schema
const userSchema = new mongoose.Schema({
  uid: {
    type: String,
    required: true,
    unique: true,
    default: () => `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  },
  username: {
    type: String,
    required: true,
    maxlength: 50
  },
  currentHouse: {
    type: Number,
    default: 1
  },
  currentFloor: {
    type: Number,
    default: 1
  },
  completedTasks: [{
    type: String
  }],
  totalScore: {
    type: Number,
    default: 0
  },
  isAdmin: {
    type: Boolean,
    default: false
  },
  passwordHash: {
    type: String,
    default: null
  }
}, {
  timestamps: true
});

// Player State Schema
const playerStateSchema = new mongoose.Schema({
  userId: {
    type: String,
    required: true
  },
  username: {
    type: String,
    required: true
  },
  x: {
    type: Number,
    default: 100
  },
  y: {
    type: Number,
    default: 100
  },
  isActive: {
    type: Boolean,
    default: true
  },
  lastSeen: {
    type: Date,
    default: Date.now
  }
});

// Room Schema
const roomSchema = new mongoose.Schema({
  roomId: {
    type: String,
    required: true,
    unique: true,
    default: () => `room_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`
  },
  name: {
    type: String,
    required: true,
    maxlength: 100
  },
  hostUserId: {
    type: String,
    required: true
  },
  players: [playerStateSchema],
  maxPlayers: {
    type: Number,
    default: 5
  },
  currentHouse: {
    type: Number,
    default: 1
  },
  currentFloor: {
    type: Number,
    default: 1
  },
  activeTasks: [{
    type: String
  }],
  completedTasks: [{
    type: String
  }],
  isActive: {
    type: Boolean,
    default: true
  },
  gameStarted: {
    type: Boolean,
    default: false
  },
  lastActivity: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Game Event Schema
const gameEventSchema = new mongoose.Schema({
  eventId: {
    type: String,
    required: true,
    unique: true,
    default: () => `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  },
  roomId: {
    type: String,
    required: true
  },
  userId: {
    type: String,
    required: true
  },
  eventType: {
    type: String,
    required: true,
    enum: ['player_join', 'player_leave', 'task_complete', 'house_change', 'floor_complete', 'game_start', 'game_end']
  },
  eventData: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  }
}, {
  timestamps: true
});

// House Schema
const houseSchema = new mongoose.Schema({
  id: {
    type: Number,
    required: true,
    unique: true
  },
  name: {
    type: String,
    required: true
  },
  theme: {
    type: String,
    required: true
  },
  floors: {
    type: Number,
    required: true
  },
  horrorType: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  tasksPerFloor: {
    type: Number,
    default: 3
  },
  jumpscareTrigs: {
    type: mongoose.Schema.Types.Mixed,
    default: []
  }
});

// Task Schema
const taskSchema = new mongoose.Schema({
  taskId: {
    type: String,
    required: true,
    unique: true
  },
  name: {
    type: String,
    required: true
  },
  taskType: {
    type: String,
    required: true,
    enum: ['repair', 'collect', 'interact', 'puzzle', 'clean', 'fix']
  },
  description: {
    type: String,
    required: true
  },
  houseId: {
    type: Number,
    required: true
  },
  floor: {
    type: Number,
    required: true
  },
  x: {
    type: Number,
    required: true
  },
  y: {
    type: Number,
    required: true
  },
  duration: {
    type: Number,
    default: 5 // seconds
  },
  isCompleted: {
    type: Boolean,
    default: false
  }
});

// Admin Log Schema
const adminLogSchema = new mongoose.Schema({
  adminUserId: {
    type: String,
    required: true
  },
  action: {
    type: String,
    required: true
  },
  target: {
    type: String,
    default: null
  },
  details: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  },
  ipAddress: {
    type: String,
    default: null
  }
}, {
  timestamps: true
});

// Create and export models
export const User = mongoose.model('User', userSchema);
export const Room = mongoose.model('Room', roomSchema);
export const GameEvent = mongoose.model('GameEvent', gameEventSchema);
export const House = mongoose.model('House', houseSchema);
export const Task = mongoose.model('Task', taskSchema);
export const AdminLog = mongoose.model('AdminLog', adminLogSchema);

// Export schemas for use in other modules
export {
  userSchema,
  roomSchema,
  gameEventSchema,
  houseSchema,
  taskSchema,
  adminLogSchema,
  playerStateSchema
};