# ChaseHome Node.js Backend Conversion

Bu belge, ChaseHome oyununun Python FastAPI backend'inin Node.js/Express backend'ine dönüştürülmesi sürecini ve Türkçe gereksinimlere göre eklenen özellikleri açıklar.

## 🎯 Türkçe Gereksinimler

### Tamamlanan Özellikler:
- ✅ **Backend'i Node.js/Express'e dönüştürme**
- ✅ **Admin yönetim paneli ekleme**
- ✅ **Sunucuyu çalıştırmak için JavaScript dosyası**
- ✅ **Oyunu bitirmek için batch kodu**
- ✅ **Executable (EXE) oluşturma altyapısı**

## 📁 Yeni Dosya Yapısı

```
ChaseHome/
├── server-js/              # Node.js Express backend
│   ├── index.js            # Ana sunucu dosyası
│   ├── config.js           # Konfigürasyon
│   ├── database.js         # MongoDB bağlantısı
│   ├── models.js           # Mongoose modelleri
│   ├── roomManager.js      # Oda yöneticisi
│   ├── init-db.js          # Veritabanı başlatma
│   ├── routes/
│   │   ├── api.js          # API endpoints
│   │   └── admin.js        # Admin endpoints
│   └── package.json        # Node.js bağımlılıkları
├── admin-panel/            # Admin yönetim paneli
│   └── index.html          # Admin arayüzü
├── scripts/                # Yardımcı scriptler
│   ├── start-server.js     # Sunucu başlatma (JS)
│   ├── close-game.bat      # Oyun kapatma (BAT)
│   └── build-exe.js        # EXE oluşturma
└── (mevcut dosyalar...)
```

## 🚀 Kullanım

### 1. Node.js Backend Başlatma

```bash
# Sunucuyu JavaScript ile başlat
node scripts/start-server.js

# Veya direkt Node.js backend'i başlat
cd server-js
npm install
npm start
```

### 2. Oyunu Kapatma

Windows'ta batch dosyasını çalıştırın:
```cmd
scripts\close-game.bat
```

### 3. Admin Panel

Sunucu çalışırken admin paneline erişin:
- URL: `http://localhost:8000/admin`
- Varsayılan giriş: `admin` / `chasehome123`

### 4. EXE Dosyaları Oluşturma

```bash
node scripts/build-exe.js
```

Bu komut şunları oluşturur:
- `dist/ChaseHome-Client.exe` - Oyun istemcisi
- `dist/chasehome-server.exe` - Node.js sunucusu
- `dist/setup.bat` - Kurulum scripti
- `dist/run-game.bat` - Oyun başlatma scripti

## 🔧 Teknoloji Stack

### Node.js Backend:
- **Express.js** - Web framework
- **Socket.io** - WebSocket iletişimi
- **Mongoose** - MongoDB ODM
- **JWT** - Kimlik doğrulama
- **bcryptjs** - Şifre hash'leme
- **Helmet** - Güvenlik
- **CORS** - Cross-origin istekler

### Admin Panel:
- **Vanilla JavaScript** - Frontend
- **Responsive CSS** - Mobil uyumlu tasarım
- **WebSocket** - Gerçek zamanlı güncellemeler

## 📊 Admin Panel Özellikleri

### Dashboard:
- Toplam kullanıcı sayısı
- Aktif oyuncu sayısı  
- Aktif oda sayısı
- Sunucu çalışma süresi

### Kullanıcı Yönetimi:
- Kullanıcı listesi görüntüleme
- Kullanıcı silme
- Admin kullanıcı oluşturma

### Oda Yönetimi:
- Aktif odalar listesi
- Oda detayları görüntüleme
- Oda kapatma

### Oyun Olayları:
- Gerçek zamanlı oyun olayları
- Filtreleme ve sayfalama

### Admin Logları:
- Admin işlem geçmişi
- IP adresi takibi

## 🔐 Güvenlik Özellikleri

- JWT tabanlı kimlik doğrulama
- Admin panel koruması
- Rate limiting
- CORS koruması
- Helmet güvenlik başlıkları
- bcrypt şifre hash'leme

## 🎮 WebSocket Olayları

Node.js backend, Python backend ile aynı WebSocket olaylarını destekler:

- `create_room` - Oda oluşturma
- `join_room` - Odaya katılma
- `leave_room` - Odadan ayrılma
- `player_move` - Oyuncu hareketi
- `task_complete` - Görev tamamlama
- `change_house` - Ev değiştirme

## 📱 API Endpoints

### Genel API:
- `GET /` - Sağlık kontrolü
- `POST /api/users` - Kullanıcı oluşturma
- `GET /api/users/:uid` - Kullanıcı bilgisi
- `POST /api/login` - Kullanıcı girişi
- `GET /api/houses` - Ev listesi
- `GET /api/rooms` - Aktif odalar

### Admin API:
- `POST /admin/login` - Admin girişi
- `GET /admin/dashboard` - Dashboard verileri
- `GET /admin/users` - Kullanıcı yönetimi
- `GET /admin/rooms` - Oda yönetimi
- `GET /admin/events` - Oyun olayları
- `GET /admin/logs` - Admin logları

## 🔧 Konfigürasyon

Environment variables ile konfigürasyon:

```bash
# Server
HOST=0.0.0.0
PORT=8000

# Database  
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=chasehome

# Security
JWT_SECRET=your-secret-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-admin-password

# Production
NODE_ENV=production
```

## 🏗️ Geliştirme

### Node.js Backend Geliştirme:
```bash
cd server-js
npm install
npm run dev  # nodemon ile otomatik restart
```

### Database İnizialization:
```bash
cd server-js
node init-db.js  # Ev ve görev verilerini yükle
```

## 🐛 Sorun Giderme

### MongoDB Bağlantı Hatası:
1. MongoDB'nin çalıştığından emin olun
2. Connection string'i kontrol edin
3. Network bağlantısını kontrol edin

### Port Kullanım Hatası:
1. 8000 portunu kullanan işlemleri sonlandırın
2. Farklı port kullanmak için `PORT` environment variable'ı ayarlayın

### Admin Panel Erişim Sorunu:
1. Sunucunun çalıştığından emin olun
2. URL'in doğru olduğunu kontrol edin: `http://localhost:8000/admin`
3. Admin credentials'ları kontrol edin

## 📝 Notlar

- Python backend ile paralel çalışabilir
- Mevcut client kodunu değiştirmeden kullanılabilir
- MongoDB olmadan da çalışır (sınırlı özelliklerle)
- Production ortamında environment variables kullanın
- Admin panel responsive tasarımla mobil uyumlu

## 🎯 Gelecek Geliştirmeler

- [ ] SSL/HTTPS desteği
- [ ] Database clustering
- [ ] Redis cache entegrasyonu
- [ ] Grafana monitoring
- [ ] Docker container desteği
- [ ] Kubernetes deployment
- [ ] Load balancer desteği

## 📞 Destek

Herhangi bir sorun veya soru için:
- GitHub Issues kullanın
- Admin panel üzerinden sistem loglarını kontrol edin
- Development mode'da detaylı logları inceleyin