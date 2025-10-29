# 🚀 Panduan Production Build - Miluv.app

## 📱 Informasi Aplikasi
- **Nama**: Miluv
- **Package**: 
  - Android: `com.miluv.app`
  - iOS: `com.miluv.app`
- **Version**: 1.0.0
- **Build Tools**: Expo Application Services (EAS)

---

## 🛠️ Persiapan Sebelum Build

### 1. Install EAS CLI (Jika Belum)
```bash
npm install -g eas-cli
```

### 2. Login ke Expo Account
```bash
cd /app/frontend
eas login
```

Jika belum punya account:
- Daftar di: https://expo.dev/signup
- Gratis untuk 30 builds/bulan

### 3. Konfigurasi Project EAS
```bash
eas build:configure
```

Jawab pertanyaan:
- Generate a new Android Keystore? → **Yes**
- Generate iOS credentials? → **Yes** (jika build iOS)

---

## 📦 BUILD ANDROID (APK untuk Testing)

### Quick Build APK:
```bash
cd /app/frontend
eas build --platform android --profile preview
```

**Proses:**
1. Code di-upload ke server Expo (~5 menit)
2. Build di cloud (~15-25 menit)
3. Download APK dari URL yang diberikan

**Install di Android:**
```bash
# Download APK dari URL
# Transfer ke Android device
# Install langsung (izinkan install from unknown sources)
```

---

## 📦 BUILD ANDROID (AAB untuk Google Play Store)

### Build Production AAB:
```bash
cd /app/frontend
eas build --platform android --profile production
```

**File Output:**
- Android App Bundle (.aab)
- Siap upload ke Google Play Console
- Size: ~20-50MB

**Upload ke Play Store:**
1. Buka https://play.google.com/console
2. Create new app → Upload AAB
3. Setup store listing (icon, screenshots, description)
4. Submit for review

**Biaya:**
- Google Play Console: $25 (sekali seumur hidup)

---

## 📱 BUILD iOS (IPA untuk App Store / TestFlight)

### ⚠️ REQUIREMENTS WAJIB:
- ✅ **Apple Developer Account** ($99/tahun)
- ✅ Account sudah aktif dan paid

### Setup iOS Credentials:
```bash
cd /app/frontend

# Setup credentials
eas credentials

# Pilih:
# 1. iOS
# 2. Production
# 3. Setup Push Notifications (optional)
# 4. Setup Distribution Certificate
# 5. Setup Provisioning Profile
```

### Build Production IPA:
```bash
eas build --platform ios --profile production
```

**Submit ke TestFlight (Beta Testing):**
```bash
eas submit --platform ios
```

**Submit ke App Store:**
- Buka App Store Connect
- Upload IPA
- Fill app information
- Submit for review

---

## 🔥 BUILD KEDUANYA SEKALIGUS

```bash
cd /app/frontend
eas build --platform all --profile production
```

Akan build Android AAB + iOS IPA sekaligus (butuh Apple Developer untuk iOS)

---

## ⚡ Quick Testing Build (Development)

### Build Development APK (Untuk Internal Testing):
```bash
eas build --platform android --profile development
```

Ini akan create APK dengan:
- Debug mode enabled
- Faster build time
- Untuk testing only

---

## 📊 Monitoring Build Progress

### Check Build Status:
```bash
eas build:list
```

### View Build Details:
```bash
eas build:view [BUILD_ID]
```

### Open Build in Dashboard:
https://expo.dev/accounts/[YOUR-USERNAME]/projects/miluv-app/builds

---

## 🔐 Environment Variables untuk Production

Pastikan backend URL sudah benar di `.env`:

```env
EXPO_PUBLIC_BACKEND_URL=https://your-production-backend.com
```

**PENTING**: 
- Ganti dengan URL production backend Anda
- Jangan gunakan localhost!
- Backend harus accessible dari internet

---

## 📝 Pre-Build Checklist

Sebelum build production, pastikan:

- [ ] **app.json** configured with correct name & bundle ID
- [ ] **Backend URL** set to production (not localhost)
- [ ] **Icon & Splash Screen** ready (1024x1024 PNG)
- [ ] **Permissions** properly configured
- [ ] **Privacy Policy** prepared (required for stores)
- [ ] **Testing** completed on Expo Go
- [ ] **Expo Account** created and logged in
- [ ] **Apple Developer Account** active (for iOS)

---

## 💰 Biaya Production

| Item | Android | iOS |
|------|---------|-----|
| **EAS Build** (30 builds/bulan) | GRATIS | GRATIS |
| **Store Registration** | $25 (sekali) | $99/tahun |
| **Total First Year** | $25 | $99 |
| **Annual After** | $0 | $99 |

**EAS Build Unlimited**: $29/bulan (optional)

---

## 🎯 Recommended Build Flow

### For First Time:
```bash
# 1. Test Build (APK only)
eas build --platform android --profile preview

# 2. Download & test APK on device
# 3. If OK, build production
eas build --platform android --profile production

# 4. For iOS (if you have Apple Developer)
eas build --platform ios --profile production
```

---

## 🐛 Troubleshooting

### Build Failed?
```bash
# Check logs
eas build:list
eas build:view [BUILD_ID]

# Common fixes:
# - Clear cache and rebuild
eas build --clear-cache --platform android

# - Update dependencies
npm update
```

### Credentials Issues?
```bash
# Reset credentials
eas credentials

# Then rebuild
eas build --platform [android|ios]
```

---

## 📱 Testing APK

Setelah download APK:

1. **Transfer ke Android device** (via USB / Google Drive / Email)
2. **Enable "Install from Unknown Sources"** di Settings
3. **Install APK**
4. **Test semua fitur**:
   - ✅ Register & Login
   - ✅ Face Verification (Camera permission)
   - ✅ Assessment Tests
   - ✅ Discovery & Matching
   - ✅ Chat
   - ✅ Feeds
   - ✅ Profile

---

## 🚀 Next Steps After Build

1. **Test thoroughly** pada device fisik
2. **Fix bugs** yang ditemukan
3. **Increment version** di app.json
4. **Rebuild** dengan version baru
5. **Submit to stores**

---

## 📞 Support

**Expo Documentation:**
- https://docs.expo.dev/build/introduction/
- https://docs.expo.dev/submit/introduction/

**Build Dashboard:**
- https://expo.dev/accounts/[YOUR-USERNAME]/projects/miluv-app

**Issues?**
- Check build logs di dashboard
- Forum: https://forums.expo.dev

---

## ⏱️ Estimated Build Times

| Build Type | Time |
|------------|------|
| Android APK (preview) | 15-20 min |
| Android AAB (production) | 20-30 min |
| iOS IPA (production) | 25-35 min |

**Note**: First build bisa lebih lama (download dependencies)

---

**Selamat Building! 🎉**
