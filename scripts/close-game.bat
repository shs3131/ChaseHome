@echo off
title ChaseHome - Oyunu Bitir
color 0C

echo.
echo  ==================================================
echo   🎮 ChaseHome - Oyun Kapatma Araci
echo  ==================================================
echo.

echo  📊 Aktif ChaseHome islemlerini araniyor...
echo.

REM Python sunucusu ve client'ini bul ve kapat
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo  🐍 Python sunucusu bulundu, kapatiliyor...
    taskkill /F /IM python.exe /T >NUL 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo  ✅ Python islemleri basariyla kapatildi
    ) else (
        echo  ❌ Python islemlerini kapatirken hata olustu
    )
) else (
    echo  ℹ️  Python sunucusu bulunamadi
)

REM Node.js sunucusunu bul ve kapat
tasklist /FI "IMAGENAME eq node.exe" 2>NUL | find /I /N "node.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo  📦 Node.js sunucusu bulundu, kapatiliyor...
    taskkill /F /IM node.exe /T >NUL 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo  ✅ Node.js islemleri basariyla kapatildi
    ) else (
        echo  ❌ Node.js islemlerini kapatirken hata olustu
    )
) else (
    echo  ℹ️  Node.js sunucusu bulunamadi
)

REM pygame pencerelerini kapat
tasklist /FI "WINDOWTITLE eq ChaseHome*" 2>NUL | find /I /N "ChaseHome">NUL
if "%ERRORLEVEL%"=="0" (
    echo  🎮 ChaseHome oyun penceresi bulundu, kapatiliyor...
    taskkill /F /FI "WINDOWTITLE eq ChaseHome*" >NUL 2>&1
)

REM Tüm pygame/python game process'lerini temizle
FOR /F "tokens=2" %%i IN ('tasklist /FI "IMAGENAME eq python.exe" /FO TABLE /NH 2^>NUL') DO (
    IF NOT "%%i"=="INFO:" (
        echo  🧹 Python oyun islemi kapatiliyor: PID %%i
        taskkill /F /PID %%i >NUL 2>&1
    )
)

echo.
echo  🧹 Port temizligi yapiliyor...

REM 8000 portunu kullanan işlemleri bul ve kapat
for /f "tokens=5" %%a in ('netstat -aon ^| find "8000" ^| find "LISTENING"') do (
    echo  🔌 Port 8000'i kullanan islem kapatiliyor: PID %%a
    taskkill /F /PID %%a >NUL 2>&1
)

REM 3000 portunu kullanan işlemleri bul ve kapat  
for /f "tokens=5" %%a in ('netstat -aon ^| find "3000" ^| find "LISTENING"') do (
    echo  🔌 Port 3000'i kullanan islem kapatiliyor: PID %%a
    taskkill /F /PID %%a >NUL 2>&1
)

echo.
echo  🗂️  Gecici dosyalar temizleniyor...

REM Temp dosyalarını temizle
if exist "%TEMP%\chasehome*" (
    del /Q "%TEMP%\chasehome*" >NUL 2>&1
    echo  ✅ Gecici dosyalar temizlendi
)

REM Log dosyalarını temizle (opsiyonel)
if exist "*.log" (
    del /Q "*.log" >NUL 2>&1
    echo  ✅ Log dosyalari temizlendi
)

REM __pycache__ klasörlerini temizle
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" >NUL 2>&1

echo.
echo  🔍 Son kontrol yapiliyor...

REM Final check
timeout /t 2 >NUL

tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo  ⚠️  Bazi Python islemleri hala aktif olabilir
) else (
    echo  ✅ Tum Python islemleri kapatildi
)

tasklist /FI "IMAGENAME eq node.exe" 2>NUL | find /I /N "node.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo  ⚠️  Bazi Node.js islemleri hala aktif olabilir  
) else (
    echo  ✅ Tum Node.js islemleri kapatildi
)

echo.
echo  ==================================================
echo   ✅ ChaseHome oyunu basariyla kapatildi!
echo  ==================================================
echo.
echo  💡 Oyunu yeniden baslatmak icin:
echo     - start-server.js dosyasini calistirin
echo     - client/main.py dosyasini calistirin
echo.

REM Başarı sesi çal (Windows)
echo 
powershell -c "(New-Object Media.SoundPlayer 'C:\Windows\Media\Windows Ding.wav').PlaySync()" 2>NUL

echo  Pencere 5 saniye sonra kapanacak...
timeout /t 5

exit /b 0