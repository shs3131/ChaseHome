/**
 * Admin Routes for ChaseHome Management Panel
 */

import express from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { User, Room, House, Task, GameEvent, AdminLog } from '../models.js';
import { config } from '../config.js';

const router = express.Router();

// Middleware to check admin authentication
const requireAdmin = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({ error: 'Admin authentication required' });
    }

    const decoded = jwt.verify(token, config.JWT_SECRET);
    const user = await User.findOne({ uid: decoded.uid });

    if (!user || !user.isAdmin) {
      return res.status(403).json({ error: 'Admin access required' });
    }

    req.admin = user;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid admin token' });
  }
};

// Admin login
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    // Check default admin credentials
    if (username === config.ADMIN_USERNAME && password === config.ADMIN_PASSWORD) {
      // Create or get admin user
      let adminUser = await User.findOne({ username: config.ADMIN_USERNAME });
      
      if (!adminUser) {
        const hashedPassword = await bcrypt.hash(config.ADMIN_PASSWORD, config.BCRYPT_ROUNDS);
        adminUser = new User({
          username: config.ADMIN_USERNAME,
          passwordHash: hashedPassword,
          isAdmin: true
        });
        await adminUser.save();
      }

      const token = jwt.sign(
        { uid: adminUser.uid, username: adminUser.username, isAdmin: true },
        config.JWT_SECRET,
        { expiresIn: '8h' }
      );

      // Log admin login
      await new AdminLog({
        adminUserId: adminUser.uid,
        action: 'login',
        ipAddress: req.ip
      }).save();

      res.json({
        token,
        admin: {
          uid: adminUser.uid,
          username: adminUser.username
        }
      });
      return;
    }

    // Check database admin users
    const user = await User.findOne({ username, isAdmin: true });
    if (!user || !user.passwordHash) {
      return res.status(401).json({ error: 'Invalid admin credentials' });
    }

    const isValidPassword = await bcrypt.compare(password, user.passwordHash);
    if (!isValidPassword) {
      return res.status(401).json({ error: 'Invalid admin credentials' });
    }

    const token = jwt.sign(
      { uid: user.uid, username: user.username, isAdmin: true },
      config.JWT_SECRET,
      { expiresIn: '8h' }
    );

    // Log admin login
    await new AdminLog({
      adminUserId: user.uid,
      action: 'login',
      ipAddress: req.ip
    }).save();

    res.json({
      token,
      admin: {
        uid: user.uid,
        username: user.username
      }
    });
  } catch (error) {
    console.error('Admin login error:', error);
    res.status(500).json({ error: 'Login failed' });
  }
});

// Admin dashboard stats
router.get('/dashboard', requireAdmin, async (req, res) => {
  try {
    const [
      totalUsers,
      activeRooms,
      totalRooms,
      totalGameEvents,
      recentEvents
    ] = await Promise.all([
      User.countDocuments(),
      Room.countDocuments({ isActive: true }),
      Room.countDocuments(),
      GameEvent.countDocuments(),
      GameEvent.find().sort({ createdAt: -1 }).limit(10)
    ]);

    // Get active players (users in active rooms)
    const activeRoomsData = await Room.find({ isActive: true });
    const activePlayers = activeRoomsData.reduce((total, room) => total + room.players.length, 0);

    res.json({
      stats: {
        totalUsers,
        activePlayers,
        activeRooms,
        totalRooms,
        totalGameEvents,
        serverUptime: process.uptime()
      },
      recentEvents: recentEvents.map(event => ({
        id: event.eventId,
        type: event.eventType,
        roomId: event.roomId,
        userId: event.userId,
        data: event.eventData,
        timestamp: event.createdAt
      }))
    });
  } catch (error) {
    console.error('Error getting dashboard data:', error);
    res.status(500).json({ error: 'Failed to get dashboard data' });
  }
});

// Get all users with pagination
router.get('/users', requireAdmin, async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const skip = (page - 1) * limit;

    const [users, totalUsers] = await Promise.all([
      User.find()
        .select('uid username currentHouse currentFloor totalScore isAdmin createdAt updatedAt')
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(limit),
      User.countDocuments()
    ]);

    res.json({
      users,
      pagination: {
        currentPage: page,
        totalPages: Math.ceil(totalUsers / limit),
        totalUsers,
        hasNextPage: page * limit < totalUsers,
        hasPrevPage: page > 1
      }
    });
  } catch (error) {
    console.error('Error getting users:', error);
    res.status(500).json({ error: 'Failed to get users' });
  }
});

// Get all rooms with details
router.get('/rooms', requireAdmin, async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const skip = (page - 1) * limit;

    const [rooms, totalRooms] = await Promise.all([
      Room.find()
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(limit),
      Room.countDocuments()
    ]);

    res.json({
      rooms: rooms.map(room => ({
        roomId: room.roomId,
        name: room.name,
        hostUserId: room.hostUserId,
        players: room.players,
        playersCount: room.players.length,
        maxPlayers: room.maxPlayers,
        currentHouse: room.currentHouse,
        currentFloor: room.currentFloor,
        completedTasksCount: room.completedTasks.length,
        isActive: room.isActive,
        gameStarted: room.gameStarted,
        createdAt: room.createdAt,
        lastActivity: room.lastActivity
      })),
      pagination: {
        currentPage: page,
        totalPages: Math.ceil(totalRooms / limit),
        totalRooms,
        hasNextPage: page * limit < totalRooms,
        hasPrevPage: page > 1
      }
    });
  } catch (error) {
    console.error('Error getting rooms:', error);
    res.status(500).json({ error: 'Failed to get rooms' });
  }
});

// Close/deactivate a room
router.post('/rooms/:roomId/close', requireAdmin, async (req, res) => {
  try {
    const { roomId } = req.params;
    const room = await Room.findOne({ roomId });

    if (!room) {
      return res.status(404).json({ error: 'Room not found' });
    }

    room.isActive = false;
    await room.save();

    // Log admin action
    await new AdminLog({
      adminUserId: req.admin.uid,
      action: 'close_room',
      target: roomId,
      details: { roomName: room.name },
      ipAddress: req.ip
    }).save();

    res.json({ message: 'Room closed successfully' });
  } catch (error) {
    console.error('Error closing room:', error);
    res.status(500).json({ error: 'Failed to close room' });
  }
});

// Delete a user (admin only)
router.delete('/users/:uid', requireAdmin, async (req, res) => {
  try {
    const { uid } = req.params;
    const user = await User.findOne({ uid });

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Don't allow deleting other admins
    if (user.isAdmin && user.uid !== req.admin.uid) {
      return res.status(403).json({ error: 'Cannot delete other admin users' });
    }

    await User.deleteOne({ uid });

    // Log admin action
    await new AdminLog({
      adminUserId: req.admin.uid,
      action: 'delete_user',
      target: uid,
      details: { username: user.username },
      ipAddress: req.ip
    }).save();

    res.json({ message: 'User deleted successfully' });
  } catch (error) {
    console.error('Error deleting user:', error);
    res.status(500).json({ error: 'Failed to delete user' });
  }
});

// Get game events with pagination
router.get('/events', requireAdmin, async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 50;
    const skip = (page - 1) * limit;
    const eventType = req.query.type;

    const filter = eventType ? { eventType } : {};

    const [events, totalEvents] = await Promise.all([
      GameEvent.find(filter)
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(limit),
      GameEvent.countDocuments(filter)
    ]);

    res.json({
      events: events.map(event => ({
        id: event.eventId,
        roomId: event.roomId,
        userId: event.userId,
        type: event.eventType,
        data: event.eventData,
        timestamp: event.createdAt
      })),
      pagination: {
        currentPage: page,
        totalPages: Math.ceil(totalEvents / limit),
        totalEvents,
        hasNextPage: page * limit < totalEvents,
        hasPrevPage: page > 1
      }
    });
  } catch (error) {
    console.error('Error getting events:', error);
    res.status(500).json({ error: 'Failed to get events' });
  }
});

// Get admin logs
router.get('/logs', requireAdmin, async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 50;
    const skip = (page - 1) * limit;

    const [logs, totalLogs] = await Promise.all([
      AdminLog.find()
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(limit),
      AdminLog.countDocuments()
    ]);

    res.json({
      logs,
      pagination: {
        currentPage: page,
        totalPages: Math.ceil(totalLogs / limit),
        totalLogs,
        hasNextPage: page * limit < totalLogs,
        hasPrevPage: page > 1
      }
    });
  } catch (error) {
    console.error('Error getting admin logs:', error);
    res.status(500).json({ error: 'Failed to get admin logs' });
  }
});

// Create admin user
router.post('/create-admin', requireAdmin, async (req, res) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(400).json({ error: 'Username and password are required' });
    }

    // Check if username already exists
    const existingUser = await User.findOne({ username });
    if (existingUser) {
      return res.status(400).json({ error: 'Username already exists' });
    }

    const hashedPassword = await bcrypt.hash(password, config.BCRYPT_ROUNDS);
    const adminUser = new User({
      username,
      passwordHash: hashedPassword,
      isAdmin: true
    });

    await adminUser.save();

    // Log admin action
    await new AdminLog({
      adminUserId: req.admin.uid,
      action: 'create_admin',
      target: adminUser.uid,
      details: { username },
      ipAddress: req.ip
    }).save();

    res.status(201).json({
      message: 'Admin user created successfully',
      uid: adminUser.uid,
      username: adminUser.username
    });
  } catch (error) {
    console.error('Error creating admin:', error);
    res.status(500).json({ error: 'Failed to create admin user' });
  }
});

export { router as adminRoutes };