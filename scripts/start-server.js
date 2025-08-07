#!/usr/bin/env node

/**
 * ChaseHome Server Launcher
 * Sunucuyu çalıştırmak için JavaScript dosyası
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('🎮 ChaseHome Sunucu Başlatılıyor...\n');

// Server paths
const serverJsPath = path.join(__dirname, '..', 'server-js');
const serverPyPath = path.join(__dirname, '..', 'server');

// Check which server to start
const useNodeServer = process.argv.includes('--node') || fs.existsSync(path.join(serverJsPath, 'package.json'));

if (useNodeServer) {
    console.log('📦 Node.js sunucusu başlatılıyor...');
    console.log(`📂 Dizin: ${serverJsPath}`);
    
    // Check if dependencies are installed
    if (!fs.existsSync(path.join(serverJsPath, 'node_modules'))) {
        console.log('📥 Bağımlılıklar yükleniyor...');
        const npmInstall = spawn('npm', ['install'], {
            cwd: serverJsPath,
            stdio: 'inherit',
            shell: true
        });
        
        npmInstall.on('close', (code) => {
            if (code === 0) {
                startNodeServer();
            } else {
                console.error('❌ Bağımlılık yüklemesi başarısız!');
                process.exit(1);
            }
        });
    } else {
        startNodeServer();
    }
} else {
    console.log('🐍 Python sunucusu başlatılıyor...');
    console.log(`📂 Dizin: ${serverPyPath}`);
    startPythonServer();
}

function startNodeServer() {
    console.log('\n🚀 Node.js sunucusu başlatılıyor...');
    console.log('🌐 Admin Panel: http://localhost:8000/admin');
    console.log('📊 API: http://localhost:8000/api');
    console.log('🔌 WebSocket: ws://localhost:8000\n');
    
    const server = spawn('node', ['index.js'], {
        cwd: serverJsPath,
        stdio: 'inherit',
        shell: true
    });
    
    server.on('close', (code) => {
        console.log(`\n🛑 Sunucu kapandı (kod: ${code})`);
    });
    
    // Handle Ctrl+C
    process.on('SIGINT', () => {
        console.log('\n🛑 Sunucu kapatılıyor...');
        server.kill('SIGINT');
        process.exit(0);
    });
}

function startPythonServer() {
    console.log('\n🚀 Python sunucusu başlatılıyor...');
    console.log('🌐 API: http://localhost:8000');
    console.log('🔌 WebSocket: ws://localhost:8000\n');
    
    const server = spawn('python', ['main.py'], {
        cwd: serverPyPath,
        stdio: 'inherit',
        shell: true
    });
    
    server.on('close', (code) => {
        console.log(`\n🛑 Sunucu kapandı (kod: ${code})`);
    });
    
    // Handle Ctrl+C
    process.on('SIGINT', () => {
        console.log('\n🛑 Sunucu kapatılıyor...');
        server.kill('SIGINT');
        process.exit(0);
    });
}

// Display help
if (process.argv.includes('--help') || process.argv.includes('-h')) {
    console.log(`
ChaseHome Server Launcher

Kullanım:
  node start-server.js [seçenekler]

Seçenekler:
  --node     Node.js sunucusunu zorla çalıştır
  --help     Bu yardım mesajını göster

Örnekler:
  node start-server.js          # Otomatik sunucu seçimi
  node start-server.js --node   # Node.js sunucusunu çalıştır
`);
    process.exit(0);
}