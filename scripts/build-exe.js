#!/usr/bin/env node

/**
 * ChaseHome Executable Builder
 * EXE dosyaları oluşturmak için araç
 */

const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('🔨 ChaseHome Executable Builder\n');

const projectRoot = path.join(__dirname, '..');
const clientDir = path.join(projectRoot, 'client');
const serverJsDir = path.join(projectRoot, 'server-js');
const distDir = path.join(projectRoot, 'dist');

// Create dist directory if it doesn't exist
if (!fs.existsSync(distDir)) {
    fs.mkdirSync(distDir, { recursive: true });
}

async function buildExecutables() {
    console.log('🏗️  Executable dosyaları oluşturuluyor...\n');

    try {
        // Build Python client executable
        await buildPythonClient();
        
        // Build Node.js server executable  
        await buildNodeServer();
        
        // Create setup scripts
        createSetupScripts();
        
        console.log('\n✅ Tüm executable dosyaları başarıyla oluşturuldu!');
        console.log(`📁 Dosyalar: ${distDir}`);
        
    } catch (error) {
        console.error('❌ Build işlemi başarısız:', error);
        process.exit(1);
    }
}

async function buildPythonClient() {
    console.log('🐍 Python client executable oluşturuluyor...');
    
    return new Promise((resolve, reject) => {
        // Check if PyInstaller is installed
        exec('pyinstaller --version', (error) => {
            if (error) {
                console.log('📦 PyInstaller yükleniyor...');
                exec('pip install pyinstaller', (installError) => {
                    if (installError) {
                        reject('PyInstaller yüklenemedi: ' + installError.message);
                        return;
                    }
                    createPythonExecutable();
                });
            } else {
                createPythonExecutable();
            }
        });
        
        function createPythonExecutable() {
            const pyinstallerArgs = [
                '--onefile',
                '--windowed',
                '--name=ChaseHome-Client',
                '--icon=icon.ico',
                '--add-data=entities;entities',
                '--add-data=../data;data',
                '--distpath=' + distDir,
                '--workpath=' + path.join(distDir, 'build'),
                '--specpath=' + path.join(distDir, 'specs'),
                path.join(clientDir, 'main.py')
            ];
            
            const pyinstaller = spawn('pyinstaller', pyinstallerArgs, {
                cwd: clientDir,
                stdio: 'inherit',
                shell: true
            });
            
            pyinstaller.on('close', (code) => {
                if (code === 0) {
                    console.log('✅ Python client executable oluşturuldu');
                    resolve();
                } else {
                    reject(`PyInstaller failed with code ${code}`);
                }
            });
        }
    });
}

async function buildNodeServer() {
    console.log('📦 Node.js server executable oluşturuluyor...');
    
    return new Promise((resolve, reject) => {
        // Check if pkg is installed
        exec('npx pkg --version', { cwd: serverJsDir }, (error) => {
            if (error) {
                console.log('📦 pkg yükleniyor...');
                exec('npm install -g pkg', (installError) => {
                    if (installError) {
                        reject('pkg yüklenemedi: ' + installError.message);
                        return;
                    }
                    createNodeExecutable();
                });
            } else {
                createNodeExecutable();
            }
        });
        
        function createNodeExecutable() {
            // Update package.json for pkg
            const packageJsonPath = path.join(serverJsDir, 'package.json');
            const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
            
            packageJson.bin = './index.js';
            packageJson.pkg = {
                scripts: [
                    'index.js',
                    'config.js',
                    'database.js',
                    'models.js',
                    'roomManager.js',
                    'routes/*.js'
                ],
                assets: [
                    'admin-panel/**/*',
                    '../data/*.json'
                ],
                targets: ['node18-win-x64', 'node18-linux-x64', 'node18-macos-x64']
            };
            
            fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
            
            const pkgArgs = [
                'pkg',
                '.',
                '--out-path',
                distDir,
                '--targets',
                'node18-win-x64'
            ];
            
            const pkg = spawn('npx', pkgArgs, {
                cwd: serverJsDir,
                stdio: 'inherit',
                shell: true
            });
            
            pkg.on('close', (code) => {
                if (code === 0) {
                    console.log('✅ Node.js server executable oluşturuldu');
                    resolve();
                } else {
                    reject(`pkg failed with code ${code}`);
                }
            });
        }
    });
}

function createSetupScripts() {
    console.log('📜 Kurulum scriptleri oluşturuluyor...');
    
    // Create Windows installer script
    const setupScript = `
@echo off
title ChaseHome Setup
color 0A

echo.
echo  ==================================================
echo   🎮 ChaseHome Oyun Kurulumu
echo  ==================================================
echo.

echo  📁 Kurulum dizini: %CD%
echo.

if not exist "ChaseHome-Client.exe" (
    echo  ❌ ChaseHome-Client.exe bulunamadi!
    echo  🔍 Lutfen bu dosyayi ChaseHome-Client.exe ile ayni klasore koyun
    pause
    exit /b 1
)

if not exist "chasehome-server.exe" (
    echo  ❌ chasehome-server.exe bulunamadi!  
    echo  🔍 Lutfen bu dosyayi chasehome-server.exe ile ayni klasore koyun
    pause
    exit /b 1
)

echo  ✅ Tum dosyalar mevcut
echo.

echo  🔗 Masaustu kisayollari olusturuluyor...

REM Create desktop shortcuts
echo  📎 ChaseHome Client kisayolu olusturuluyor...
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\\Desktop\\ChaseHome Client.lnk');$s.TargetPath='%CD%\\ChaseHome-Client.exe';$s.WorkingDirectory='%CD%';$s.Save()" >NUL 2>&1

echo  📎 ChaseHome Server kisayolu olusturuluyor...  
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\\Desktop\\ChaseHome Server.lnk');$s.TargetPath='%CD%\\chasehome-server.exe';$s.WorkingDirectory='%CD%';$s.Save()" >NUL 2>&1

echo.
echo  🎯 Start Menu kısayolları oluşturuluyor...
mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\ChaseHome" >NUL 2>&1

powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\ChaseHome\\ChaseHome Client.lnk');$s.TargetPath='%CD%\\ChaseHome-Client.exe';$s.WorkingDirectory='%CD%';$s.Save()" >NUL 2>&1

powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\ChaseHome\\ChaseHome Server.lnk');$s.TargetPath='%CD%\\chasehome-server.exe';$s.WorkingDirectory='%CD%';$s.Save()" >NUL 2>&1

echo.
echo  ==================================================
echo   ✅ ChaseHome başarıyla kuruldu!
echo  ==================================================
echo.
echo  🎮 Oyunu başlatmak için:
echo     1. Once ChaseHome Server'i baslatın (sunucu)
echo     2. Sonra ChaseHome Client'i baslatın (oyun)
echo.
echo  🔗 Masaustunden veya Start Menu'den erisebilirsiniz
echo.

pause
`;

    fs.writeFileSync(path.join(distDir, 'setup.bat'), setupScript);
    
    // Create run script
    const runScript = `
@echo off
title ChaseHome Launcher
color 0B

echo.
echo  ==================================================
echo   🎮 ChaseHome Oyun Baslatici
echo  ==================================================
echo.

echo  🔍 Dosyalar kontrol ediliyor...

if not exist "ChaseHome-Client.exe" (
    echo  ❌ ChaseHome-Client.exe bulunamadi!
    pause
    exit /b 1
)

if not exist "chasehome-server.exe" (
    echo  ❌ chasehome-server.exe bulunamadi!
    pause  
    exit /b 1
)

echo  ✅ Tum dosyalar mevcut
echo.

echo  🚀 Sunucu baslatiliyor...
start "ChaseHome Server" chasehome-server.exe

echo  ⏳ Sunucunun baslamasi bekleniyor...
timeout /t 3 >NUL

echo  🎮 Oyun baslatiliyor...
start "ChaseHome Client" ChaseHome-Client.exe

echo.
echo  ✅ ChaseHome baslatildi!
echo  🔗 Admin Panel: http://localhost:8000/admin
echo.

pause
`;

    fs.writeFileSync(path.join(distDir, 'run-game.bat'), runScript);
    
    console.log('✅ Kurulum scriptleri oluşturuldu');
}

// Run build if called directly
if (require.main === module) {
    buildExecutables();
}

module.exports = { buildExecutables };