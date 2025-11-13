# 🔧 Setup Google Drive Sync

## Cara Setup Google Drive Auto-Sync

### Metode 1: Menggunakan Service Account (Paling Mudah & Recommended)

1. **Buka Google Cloud Console**
   - Kunjungi: https://console.cloud.google.com/
   - Login dengan akun Google Anda

2. **Buat Project Baru**
   - Klik "Select Project" di header atas
   - Klik "New Project"
   - Nama project: `PPIC-DSS-Backup` (atau nama lain sesuai keinginan)
   - Klik "Create"

3. **Enable Google Drive API**
   - Di menu sebelah kiri, cari "APIs & Services" > "Library"
   - Cari "Google Drive API"
   - Klik dan tekan "Enable"

4. **Buat Service Account**
   - Di menu, pilih "APIs & Services" > "Credentials"
   - Klik "Create Credentials" > "Service Account"
   - Service account name: `ppic-backup`
   - Klik "Create and Continue"
   - Skip "Grant this service account access to project" (opsional)
   - Klik "Done"

5. **Download Credentials JSON**
   - Klik pada service account yang baru dibuat
   - Tab "Keys" > "Add Key" > "Create new key"
   - Pilih format "JSON"
   - File akan terdownload otomatis
   - **Rename file menjadi `credentials.json`**
   - **Copy file ke folder aplikasi ini**

6. **Buat Folder Google Drive untuk Backup**
   - Buka Google Drive: https://drive.google.com/
   - Buat folder baru bernama: `PPIC_DSS_Data`
   - Klik kanan folder > "Share"
   - Tambahkan email service account (format: `xxxx@xxxx.iam.gserviceaccount.com`)
   - Berikan akses "Editor"
   - Klik "Send"

### Metode 2: Menggunakan OAuth (Manual Auth)

Jika Anda ingin menggunakan akun Google pribadi:

1. **Setup Project (Langkah 1-3 sama dengan Metode 1)**

2. **Buat OAuth Credentials**
   - Di "APIs & Services" > "Credentials"
   - Klik "Create Credentials" > "OAuth client ID"
   - Application type: "Desktop app"
   - Name: `PPIC DSS Desktop`
   - Klik "Create"

3. **Download dan Setup Credentials**
   - Download file JSON
   - Rename menjadi `credentials.json`
   - Edit file `settings.yaml`:
     ```yaml
     client_config_backend: file
     client_config_file: credentials.json

     save_credentials: True
     save_credentials_backend: file
     save_credentials_file: token.pickle

     get_refresh_token: True

     oauth_scope:
       - https://www.googleapis.com/auth/drive.file
     ```

4. **First Run Authentication**
   - Jalankan aplikasi Streamlit
   - Browser akan terbuka otomatis untuk login
   - Login dengan akun Google Anda
   - Berikan permission untuk akses Drive
   - Token akan disimpan otomatis

## 📁 File Structure Setelah Setup

```
Java-Connection-Database/
├── CODE.py
├── gdrive_sync.py
├── settings.yaml
├── credentials.json       # ← File credentials dari Google Cloud
├── token.pickle           # ← Auto-generated setelah auth (OAuth)
├── ppic_data.json        # ← Local backup
├── buyers.json           # ← Local backup
└── products.json         # ← Local backup
```

## ✅ Verifikasi Setup

Setelah setup selesai:

1. Jalankan aplikasi: `streamlit run CODE.py`
2. Check bagian atas aplikasi, harusnya ada notifikasi:
   - ✅ **"Google Drive sync aktif"** (jika berhasil)
   - ⚠️ **"Google Drive sync tidak aktif"** (jika belum setup)

## 🔄 Cara Kerja Auto-Sync

- **Auto-Upload**: Setiap kali ada perubahan data (tambah order, update tracking, dll), data otomatis di-upload ke Google Drive
- **Auto-Download**: Setiap kali aplikasi dibuka, data terbaru otomatis di-download dari Google Drive
- **Backup**: Data tersimpan di folder `PPIC_DSS_Data` di Google Drive Anda

## 🔒 Keamanan

- File `credentials.json` dan `token.pickle` sudah ditambahkan ke `.gitignore`
- **JANGAN** commit file credentials ke Git/GitHub
- **JANGAN** share file credentials ke orang lain
- Service Account hanya punya akses ke folder yang Anda share

## ❓ Troubleshooting

### Error: "credentials.json not found"
- Pastikan file `credentials.json` sudah ada di folder aplikasi
- Pastikan nama file benar (huruf kecil semua)

### Error: "Permission denied"
- Pastikan service account email sudah di-share ke folder Google Drive
- Pastikan permission adalah "Editor", bukan "Viewer"

### Data tidak ter-sync
- Check koneksi internet
- Check apakah ada error di aplikasi Streamlit
- Buka folder `PPIC_DSS_Data` di Google Drive, pastikan file ter-upload

### Browser tidak terbuka untuk OAuth
- Jalankan di local machine, bukan di server remote
- Atau gunakan Metode 1 (Service Account) untuk server

## 📞 Support

Jika masih ada masalah, silakan check:
- Google Cloud Console logs
- Streamlit terminal output untuk error messages
