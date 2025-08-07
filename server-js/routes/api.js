/**
 * API Routes for ChaseHome
 */

import express from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { User, Room, House, Task } from '../models.js';
import { config } from '../config.js';

const router = express.Router();

// Create user endpoint
router.post('/users', async (req, res) => {
  try {
    const { username, password } = req.body;

    if (!username) {
      return res.status(400).json({ error: 'Username is required' });
    }

    // Check if username already exists
    const existingUser = await User.findOne({ username });
    if (existingUser) {
      return res.status(400).json({ error: 'Username already exists' });
    }

    const user = new User({ username });

    // Hash password if provided
    if (password) {
      user.passwordHash = await bcrypt.hash(password, config.BCRYPT_ROUNDS);
    }

    await user.save();

    res.status(201).json({
      uid: user.uid,
      username: user.username,
      currentHouse: user.currentHouse,
      currentFloor: user.currentFloor
    });
  } catch (error) {
    console.error('Error creating user:', error);
    res.status(500).json({ error: 'Failed to create user' });
  }
});

// Get user by UID
router.get('/users/:uid', async (req, res) => {
  try {
    const { uid } = req.params;
    const user = await User.findOne({ uid });

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({
      uid: user.uid,
      username: user.username,
      currentHouse: user.currentHouse,
      currentFloor: user.currentFloor,
      completedTasks: user.completedTasks,
      totalScore: user.totalScore,
      createdAt: user.createdAt
    });
  } catch (error) {
    console.error('Error getting user:', error);
    res.status(500).json({ error: 'Failed to get user' });
  }
});

// User login endpoint
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(400).json({ error: 'Username and password are required' });
    }

    const user = await User.findOne({ username });
    if (!user || !user.passwordHash) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const isValidPassword = await bcrypt.compare(password, user.passwordHash);
    if (!isValidPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Generate JWT token
    const token = jwt.sign(
      { uid: user.uid, username: user.username, isAdmin: user.isAdmin },
      config.JWT_SECRET,
      { expiresIn: '24h' }
    );

    res.json({
      token,
      user: {
        uid: user.uid,
        username: user.username,
        isAdmin: user.isAdmin
      }
    });
  } catch (error) {
    console.error('Error during login:', error);
    res.status(500).json({ error: 'Login failed' });
  }
});

// Get all houses
router.get('/houses', async (req, res) => {
  try {
    const houses = await House.find({}).sort({ id: 1 });
    res.json(houses);
  } catch (error) {
    console.error('Error getting houses:', error);
    res.status(500).json({ error: 'Failed to get houses' });
  }
});

// Get house by ID
router.get('/houses/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const house = await House.findOne({ id: parseInt(id) });

    if (!house) {
      return res.status(404).json({ error: 'House not found' });
    }

    res.json(house);
  } catch (error) {
    console.error('Error getting house:', error);
    res.status(500).json({ error: 'Failed to get house' });
  }
});

// Get tasks for a house and floor
router.get('/houses/:houseId/floors/:floor/tasks', async (req, res) => {
  try {
    const { houseId, floor } = req.params;
    const tasks = await Task.find({
      houseId: parseInt(houseId),
      floor: parseInt(floor)
    });

    res.json(tasks);
  } catch (error) {
    console.error('Error getting tasks:', error);
    res.status(500).json({ error: 'Failed to get tasks' });
  }
});

// Get active rooms
router.get('/rooms', async (req, res) => {
  try {
    const rooms = await Room.find({ isActive: true })
      .select('roomId name hostUserId players maxPlayers currentHouse gameStarted createdAt')
      .sort({ createdAt: -1 });

    const roomList = rooms.map(room => ({
      roomId: room.roomId,
      name: room.name,
      hostUserId: room.hostUserId,
      players: room.players.length,
      maxPlayers: room.maxPlayers,
      currentHouse: room.currentHouse,
      gameStarted: room.gameStarted,
      createdAt: room.createdAt
    }));

    res.json(roomList);
  } catch (error) {
    console.error('Error getting rooms:', error);
    res.status(500).json({ error: 'Failed to get rooms' });
  }
});

// Get room by ID
router.get('/rooms/:roomId', async (req, res) => {
  try {
    const { roomId } = req.params;
    const room = await Room.findOne({ roomId, isActive: true });

    if (!room) {
      return res.status(404).json({ error: 'Room not found' });
    }

    res.json({
      roomId: room.roomId,
      name: room.name,
      hostUserId: room.hostUserId,
      players: room.players,
      maxPlayers: room.maxPlayers,
      currentHouse: room.currentHouse,
      currentFloor: room.currentFloor,
      completedTasks: room.completedTasks,
      gameStarted: room.gameStarted,
      createdAt: room.createdAt
    });
  } catch (error) {
    console.error('Error getting room:', error);
    res.status(500).json({ error: 'Failed to get room' });
  }
});

// Server stats endpoint
router.get('/stats', async (req, res) => {
  try {
    const [totalUsers, activeRooms, totalHouses, totalTasks] = await Promise.all([
      User.countDocuments(),
      Room.countDocuments({ isActive: true }),
      House.countDocuments(),
      Task.countDocuments()
    ]);

    res.json({
      totalUsers,
      activeRooms,
      totalHouses,
      totalTasks,
      serverUptime: process.uptime(),
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error getting stats:', error);
    res.status(500).json({ error: 'Failed to get stats' });
  }
});

export { router as apiRoutes };