/**
 * Configuration settings for ChaseHome Node.js server
 */

export const config = {
  // Server settings
  HOST: process.env.HOST || '0.0.0.0',
  PORT: process.env.PORT || 8000,
  
  // Database settings
  MONGODB_URL: process.env.MONGODB_URL || 'mongodb://localhost:27017',
  DATABASE_NAME: process.env.DATABASE_NAME || 'chasehome',
  
  // Security settings
  JWT_SECRET: process.env.JWT_SECRET || 'your-super-secret-jwt-key-change-in-production',
  BCRYPT_ROUNDS: 10,
  
  // Rate limiting
  RATE_LIMIT_WINDOW: 15 * 60 * 1000, // 15 minutes
  RATE_LIMIT_MAX: 100,
  
  // Game settings
  MAX_PLAYERS_PER_ROOM: 5,
  MAX_ROOMS: 100,
  ROOM_TIMEOUT: 30 * 60 * 1000, // 30 minutes
  
  // Admin settings
  ADMIN_USERNAME: process.env.ADMIN_USERNAME || 'admin',
  ADMIN_PASSWORD: process.env.ADMIN_PASSWORD || 'chasehome123',
  
  // Debug settings
  DEBUG: process.env.NODE_ENV !== 'production',
  
  // CORS settings
  CORS_ORIGINS: process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : ['*']
};