/**
 * Database initialization script
 * Loads houses, tasks, and jumpscares data from JSON files
 */

import mongoose from 'mongoose';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

import { connectDatabase } from './database.js';
import { House, Task } from './models.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function initializeDatabase() {
  try {
    console.log('🔄 Veritabanı bağlantısı kuruluyor...');
    await connectDatabase();

    // Load data files
    const dataDir = path.join(__dirname, '..', 'data');
    
    const housesData = JSON.parse(fs.readFileSync(path.join(dataDir, 'houses.json'), 'utf8'));
    const tasksData = JSON.parse(fs.readFileSync(path.join(dataDir, 'tasks.json'), 'utf8'));
    const jumpscaresData = JSON.parse(fs.readFileSync(path.join(dataDir, 'jumpscares.json'), 'utf8'));

    console.log('📊 Evler yükleniyor...');
    
    // Clear existing data
    await House.deleteMany({});
    await Task.deleteMany({});

    // Insert houses
    for (const houseData of housesData) {
      const house = new House({
        id: houseData.id,
        name: houseData.name,
        theme: houseData.theme,
        floors: houseData.floors,
        horrorType: houseData.horror_type,
        description: houseData.description,
        tasksPerFloor: houseData.tasks_per_floor || 3,
        jumpscareTrigs: houseData.jumpscare_triggers || []
      });
      
      await house.save();
      console.log(`✅ Ev yüklendi: ${house.name}`);
    }

    console.log('📋 Görevler yükleniyor...');

    // Insert tasks
    for (const taskData of tasksData) {
      const task = new Task({
        taskId: taskData.id,
        name: taskData.name,
        taskType: taskData.type,
        description: taskData.description,
        houseId: taskData.house_id,
        floor: taskData.floor,
        x: taskData.x,
        y: taskData.y,
        duration: taskData.duration || 5,
        isCompleted: false
      });
      
      await task.save();
    }

    console.log(`✅ ${tasksData.length} görev yüklendi`);

    console.log('🎮 Veritabanı başarıyla başlatıldı!');
    
    // Display statistics
    const housesCount = await House.countDocuments();
    const tasksCount = await Task.countDocuments();
    
    console.log('\n📊 Veritabanı İstatistikleri:');
    console.log(`   🏠 Toplam Ev: ${housesCount}`);
    console.log(`   📋 Toplam Görev: ${tasksCount}`);
    console.log(`   👻 Jumpscare Türleri: ${jumpscaresData.length}`);

  } catch (error) {
    console.error('❌ Veritabanı başlatılırken hata:', error);
    process.exit(1);
  } finally {
    await mongoose.disconnect();
    console.log('\n🔌 Veritabanı bağlantısı kapatıldı');
    process.exit(0);
  }
}

// Run initialization if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  initializeDatabase();
}

export { initializeDatabase };