# 🚀 Quick Start - Build Miluv.app Production

## ✅ Sudah Disiapkan untuk Anda:

1. ✅ **app.json** - Dikonfigurasi dengan:
   - App name: Miluv
   - Package: com.miluv.app
   - Permissions lengkap (Camera, Location, Microphone)
   - Icon & Splash screen settings

2. ✅ **eas.json** - Build profiles:
   - Development (debug)
   - Preview (APK testing)
   - Production (store release)

3. ✅ **build.sh** - Interactive build helper script

---

## 🎯 CARA TERCEPAT BUILD APK (5 Langkah)

### 1️⃣ Install EAS CLI
```bash
npm install -g eas-cli
```

### 2️⃣ Login ke Expo
```bash
cd /app/frontend
eas login
```

**Belum punya account?** Daftar gratis: https://expo.dev/signup

### 3️⃣ Build APK
```bash
eas build --platform android --profile preview
```

### 4️⃣ Tunggu Build Selesai
- Proses: 15-25 menit
- Notifikasi via email
- Monitor di: https://expo.dev

### 5️⃣ Download & Install APK
- Download dari URL yang diberikan
- Transfer ke HP Android
- Install (enable Unknown Sources jika diminta)

**SELESAI!** 🎉

---

## 📱 Build Options

### 🟢 Testing (APK)
```bash
eas build --platform android --profile preview
```
- Output: APK file
- Untuk: Internal testing
- Time: ~15-20 menit

### 🔵 Production Android (AAB untuk Play Store)
```bash
eas build --platform android --profile production
```
- Output: AAB file
- Untuk: Google Play Store
- Time: ~20-30 menit

### 🟣 Production iOS (IPA untuk App Store)
```bash
eas build --platform ios --profile production
```
- ⚠️ Butuh: Apple Developer Account ($99/tahun)
- Output: IPA file
- Untuk: App Store / TestFlight
- Time: ~25-35 menit

### 🔴 Build Keduanya
```bash
eas build --platform all --profile production
```
- Build Android + iOS sekaligus
- Time: ~30-45 menit

---

## 🛠️ Menggunakan Build Script (Recommended)

```bash
cd /app/frontend
./build.sh
```

Script ini akan menampilkan menu interaktif:
```
1) Build Android APK (testing)
2) Build Android AAB (Play Store)
3) Build iOS IPA (App Store)
4) Build Both (Android + iOS)
5) Development Build (debug)
6) View Build Status
7) Configure Credentials
8) View Build History
```

Pilih nomor dan tekan Enter!

---

## 📋 Pre-Build Checklist

Sebelum build production:

- [ ] **Backend URL** sudah production (bukan localhost)
  ```bash
  # Edit /app/frontend/.env
  EXPO_PUBLIC_BACKEND_URL=https://your-backend.com
  ```

- [ ] **Icon & Splash Screen** siap (sudah ada template di assets/)

- [ ] **Test di Expo Go** dulu untuk pastikan no bugs

- [ ] **Expo Account** sudah dibuat dan login

- [ ] **Apple Developer** (hanya untuk iOS)

---

## 💰 Biaya

| Item | Biaya |
|------|-------|
| Expo Account | **GRATIS** |
| EAS Build (30 builds/bulan) | **GRATIS** |
| Google Play Console | $25 (sekali) |
| Apple Developer Program | $99/tahun |

**Total untuk Android**: $25 (sekali)
**Total untuk iOS**: $99/tahun

---

## 🆘 Troubleshooting

### Build gagal?
```bash
# Clear cache dan rebuild
eas build --clear-cache --platform android
```

### Credentials error?
```bash
# Reset credentials
eas credentials
```

### Check build status
```bash
eas build:list
```

### View build logs
```bash
eas build:view [BUILD_ID]
```

---

## 📚 Resources

- **Panduan Lengkap**: Baca `PRODUCTION_BUILD_GUIDE.md`
- **EAS Docs**: https://docs.expo.dev/build/introduction/
- **Build Dashboard**: https://expo.dev
- **Forum Support**: https://forums.expo.dev

---

## 🎬 Next Steps

Setelah APK/AAB ready:

### Untuk Android:
1. Test APK di device
2. Jika OK, build AAB production
3. Daftar Google Play Console ($25)
4. Upload AAB
5. Fill store listing
6. Submit for review

### Untuk iOS:
1. Join Apple Developer ($99/year)
2. Build IPA
3. Submit ke TestFlight (beta)
4. Submit to App Store
5. Wait for review (2-7 hari)

---

## 💡 Tips

- **First build?** Mulai dengan `preview` profile untuk testing
- **Testing?** Gunakan Expo Go app (instant, no build needed)
- **Production?** Pastikan semua test pass dulu
- **iOS build?** Tidak perlu Mac, EAS build di cloud

---

## ⚡ Super Quick Command

Untuk yang sudah familiar:

```bash
cd /app/frontend && eas login && eas build --platform android --profile preview
```

Done! ✅

---

**Happy Building!** 🚀

Questions? Check `PRODUCTION_BUILD_GUIDE.md` untuk detail lengkap.
