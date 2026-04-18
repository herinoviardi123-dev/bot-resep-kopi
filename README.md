# ☕ Hey Kopi PWA — Deploy Guide

**URL Production:** https://iridescent-otter-0b20a1.netlify.app

---

## 📁 Struktur File

```
heykopi-pwa/
├── index.html          ← Aplikasi utama (semua fitur)
├── manifest.json       ← PWA manifest (nama, icon, warna)
├── sw.js               ← Service Worker (offline, cache)
├── netlify.toml        ← Konfigurasi Netlify (headers, redirect)
├── _redirects          ← SPA routing fallback
├── icons/
│   ├── icon-72.png
│   ├── icon-96.png
│   ├── icon-128.png
│   ├── icon-144.png
│   ├── icon-152.png
│   ├── icon-192.png    ← Android home screen icon
│   ├── icon-384.png
│   └── icon-512.png    ← Splash screen icon
└── screenshots/        ← (opsional) App store screenshots
```

---

## 🚀 Deploy ke Netlify

### Cara 1 — Netlify Drop (paling mudah)
1. Buka https://app.netlify.com/drop
2. Drag & drop **seluruh folder** `heykopi-pwa/`
3. Tunggu deploy selesai (~30 detik)
4. Salin URL yang diberikan → gunakan di Telegram Bot

### Cara 2 — Netlify CLI
```bash
npm install -g netlify-cli
cd heykopi-pwa
netlify deploy --prod --dir .
```

### Cara 3 — GitHub + Auto Deploy
1. Push folder ke GitHub repo
2. Di Netlify dashboard → "Import from Git"
3. Set publish directory: `.` (root)
4. Setiap push otomatis deploy

---

## 📱 Install sebagai Aplikasi

### Android (Chrome)
1. Buka URL di Chrome
2. Tap menu `⋮` → "Add to Home Screen" / "Install App"
3. Tap "Install" → ikon muncul di layar utama

### iOS (Safari)
1. Buka URL di Safari (HARUS Safari, bukan Chrome)
2. Tap tombol Share `⬆`
3. Scroll → "Add to Home Screen"
4. Ketik nama → "Add"

### Catatan iOS
- iOS 16.4+ mendukung push notification PWA
- Pastikan site menggunakan HTTPS (Netlify otomatis)

---

## ✈ Telegram Mini App Setup

### 1. Buat Bot
```
1. Chat @BotFather di Telegram
2. /newbot → ikuti instruksi
3. Simpan TOKEN yang diberikan
```

### 2. Daftarkan Web App
```
Di @BotFather:
/newapp → pilih bot kamu
→ Set URL: https://iridescent-otter-0b20a1.netlify.app
→ Set title: Hey Kopi
→ Set description: Resep & Kalkulator Kopi
```

### 3. Aktifkan Menu Button
```
/mybots → pilih bot → Bot Settings → Menu Button
→ Set URL: https://iridescent-otter-0b20a1.netlify.app
→ Set button text: ☕ Hey Kopi
```

### 4. Deep Links (untuk shortcut)
```
Botol:   https://t.me/NAMABOT/heykopi?startapp=botol
Brew:    https://t.me/NAMABOT/heykopi?startapp=brew
Report:  https://t.me/NAMABOT/heykopi?startapp=report
HPP:     https://t.me/NAMABOT/heykopi?startapp=hpp
```

---

## 🔔 OneSignal Push Notification

1. Buat akun di https://onesignal.com
2. Create App → Web Push
3. Set Site URL: `https://iridescent-otter-0b20a1.netlify.app`
4. Salin **App ID**
5. Di `index.html`, cari: `YOUR_ONESIGNAL_APP_ID`
6. Ganti dengan App ID kamu
7. Re-deploy

---

## ⚙ Kustomisasi

### Ganti URL Google Drive
Di `index.html` cari:
```js
function openGDrive(){window.open('https://drive.google.com/drive/folders/heykopi'...
```
Ganti dengan URL folder Google Drive kamu.

### Ganti URL Telegram Group
Di `index.html` cari:
```js
function openTelegramGroup(){window.open('https://t.me/heykopi'...
```
Ganti dengan link grup Telegram kamu.

---

## 🛠 Troubleshooting

**SW tidak terupdate?**
→ Di Chrome DevTools → Application → Service Workers → "Update on reload"

**Icon tidak muncul di iOS?**
→ Pastikan cache di-clear: Settings → Safari → Clear History and Website Data

**Telegram tidak fullscreen?**
→ Pastikan `tg.expand()` dipanggil (sudah otomatis di kode)

---

*Hey Kopi v8 PWA — Gayo Highland, Aceh ☕*
