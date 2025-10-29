# Miluv.app - Mobile Dating Application

Aplikasi mobile dating berbasis React Native (Expo) dan FastAPI dengan fitur face verification, assessment psikologi, algoritma matching, dan konsultasi berbayar.

## 🚀 Fitur Utama

### 1. **Registrasi & Verifikasi Wajah**
- Registrasi dengan profil lengkap (nama, email, foto, lokasi GPS)
- Verifikasi wajah menggunakan selfie (mocked AWS Rekognition)
- Status "Terverifikasi" dengan badge

### 2. **5 Asesmen Wajib**
Setiap pengguna harus menyelesaikan 5 asesmen (masing-masing 10 soal):
- **MBTI** - 16 tipe kepribadian
- **Love Language** - 5 bahasa cinta
- **Readiness** - Kesiapan hubungan (0-100%)
- **Temperament** - 4 tipe temperamen
- **DISC** - Profil perilaku

### 3. **Matching Algorithm**
Algoritma kompatibilitas berdasarkan:
- MBTI: 25%
- Love Language: 20%
- Readiness: 30%
- Temperament: 15%
- DISC: 10%
- Filter jarak GPS (1-1000 km)

### 4. **Discovery (Tinder-style Swipe)**
- Tampilan kartu profil dengan foto
- Swipe right (like) atau left (pass)
- Mutual like = Match dengan notifikasi
- Skor kompatibilitas dan jarak ditampilkan

### 5. **Chat Real-time**
- Chat hanya antar match
- Support text, image, voice note
- Real-time messaging (Socket.io - mocked)

### 6. **Feeds/Timeline**
- Post text dan foto
- Nama disamarkan untuk non-match
- Like dan comment

### 7. **Konsultasi Berbayar**
- Hanya untuk user dengan readiness ≥ 80%
- Pilih konselor
- Booking sesi (chat/video)
- Pembayaran via Xendit (mocked)

### 8. **Profil Pengguna**
- Maksimal 5 foto
- Tampilkan hasil semua asesmen
- Badge verified
- Statistik kompatibilitas

## 🛠️ Tech Stack

### Frontend
- **React Native** (Expo)
- **Expo Router** (file-based routing)
- **Axios** (API calls)
- **AsyncStorage** (token storage)
- **Expo Location** (GPS)
- **Expo Image Picker** (foto & kamera)
- **React Navigation** (bottom tabs)

### Backend
- **FastAPI** (Python)
- **MongoDB** (database)
- **Motor** (async MongoDB driver)
- **JWT** (authentication)
- **Bcrypt** (password hashing)
- **Python-Jose** (JWT encoding)

### Integrasi (Mocked)
- **AWS Rekognition** - Face verification
- **Socket.io** - Real-time chat
- **Xendit** - Payment gateway

## 📱 API Endpoints

### Auth
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login user
- `POST /api/auth/verify-face` - Verify face with selfie

### Assessment
- `GET /api/assessment/questions/{test_type}` - Get questions
- `POST /api/assessment/submit` - Submit answers
- `GET /api/assessment/status` - Get completion status

### Discovery & Matching
- `GET /api/discover?radius=50&page=1` - Get candidates
- `POST /api/like` - Like user
- `GET /api/matches` - Get matches

### Chat
- `GET /api/chat/{match_id}/messages` - Get messages
- `POST /api/chat/{match_id}/messages` - Send message

### Feeds
- `GET /api/feeds` - Get timeline
- `POST /api/feeds` - Create post

### Profile
- `GET /api/profile` - Get own profile
- `GET /api/profile/{user_id}` - Get user profile

### Consultation
- `GET /api/consultations` - Get counselors (readiness ≥ 80%)
- `POST /api/consultations/book` - Book session

## 🎯 User Flow

1. **Registrasi** → Upload foto profil + data diri + aktifkan GPS
2. **Face Verification** → Ambil selfie untuk verifikasi
3. **Asesmen** → Selesaikan 5 tes (MBTI, Love Language, Readiness, Temperament, DISC)
4. **Discovery** → Swipe kandidat berdasarkan kompatibilitas
5. **Match** → Mutual like → buka chat
6. **Chat** → Komunikasi real-time
7. **Feeds** → Posting & lihat timeline
8. **Konsultasi** → Booking konselor (jika readiness ≥ 80%)

## 📝 Notes

- Semua integrasi eksternal (AWS Rekognition, Socket.io, Xendit) saat ini **MOCKED** untuk keperluan development
- API keys belum dibutuhkan karena menggunakan dummy data
- Production deployment memerlukan:
  - Real API keys untuk AWS, Xendit
  - SSL certificate
  - Cloud storage untuk images (S3)
  - FCM setup untuk push notifications

---

**Built with ❤️ using Emergent AI**
