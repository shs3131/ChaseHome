/**
 * Database connection and configuration
 */

import mongoose from 'mongoose';
import { config } from './config.js';

export async function connectDatabase() {
  try {
    const connectionUrl = `${config.MONGODB_URL}/${config.DATABASE_NAME}`;
    
    await mongoose.connect(connectionUrl);

    console.log(`Connected to MongoDB: ${config.DATABASE_NAME}`);
    
    // Handle connection events
    mongoose.connection.on('error', (error) => {
      console.error('Database connection error:', error);
    });

    mongoose.connection.on('disconnected', () => {
      console.log('Database disconnected');
    });

    return mongoose.connection;
  } catch (error) {
    console.error('Failed to connect to database:', error);
    console.log('💡 Note: MongoDB is required for full functionality');
    console.log('💡 Install MongoDB locally or use MongoDB Atlas');
    throw error;
  }
}

export async function disconnectDatabase() {
  try {
    await mongoose.disconnect();
    console.log('Database disconnected');
  } catch (error) {
    console.error('Error disconnecting from database:', error);
    throw error;
  }
}

// Graceful shutdown
process.on('SIGINT', async () => {
  try {
    await mongoose.connection.close();
    console.log('Database connection closed due to app termination');
    process.exit(0);
  } catch (error) {
    console.error('Error during database shutdown:', error);
    process.exit(1);
  }
});