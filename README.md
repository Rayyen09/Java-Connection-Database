# PPIC-DSS System with Google Drive Auto-Sync

Production Planning and Inventory Control - Decision Support System dengan fitur backup otomatis ke Google Drive.

## ✨ Fitur Utama

- 📊 **Dashboard Overview** - Monitoring status produksi real-time
- 📋 **Input Pesanan Baru** - Form multi-product order entry
- 📦 **Daftar Order** - Management dan tracking semua order
- ⚙️ **Update Progress** - Update tracking produksi per workstation
- 🔍 **Tracking Produksi** - Monitoring detail per tahapan
- 💾 **Database Management** - Kelola data buyer dan produk
- 📈 **Analisis & Laporan** - Export dan visualisasi data
- 📊 **Gantt Chart** - Visualisasi timeline produksi
- ☁️ **Google Drive Auto-Sync** - Backup otomatis ke cloud (NEW!)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Application

```bash
streamlit run CODE.py
```

Aplikasi akan berjalan di: http://localhost:8501

## ☁️ Setup Google Drive Auto-Sync

Untuk mengaktifkan fitur backup otomatis ke Google Drive:

1. **Lihat panduan lengkap di**: [GDRIVE_SETUP.md](GDRIVE_SETUP.md)

2. **Setup singkat**:
   - Buat project di Google Cloud Console
   - Enable Google Drive API
   - Download `credentials.json`
   - Copy file ke folder aplikasi
   - Jalankan aplikasi (auto-sync akan aktif)

### Status Sync

- ✅ **Aktif**: Data otomatis ter-backup ke Google Drive
- ⚠️ **Tidak Aktif**: Data hanya tersimpan lokal

Status sync dapat dilihat di sidebar aplikasi.

## 📁 File Structure

```
Java-Connection-Database/
├── CODE.py                 # Main application
├── gdrive_sync.py         # Google Drive sync module
├── requirements.txt       # Python dependencies
├── GDRIVE_SETUP.md       # Setup guide untuk Google Drive
├── ppic_data.json        # Database produksi (auto-backup)
├── buyers.json           # Database buyer (auto-backup)
└── products.json         # Database produk (auto-backup)
```

## 🔄 Cara Kerja Auto-Sync

1. **Auto-Upload**: Setiap kali ada perubahan data → otomatis upload ke Google Drive
2. **Auto-Download**: Setiap kali aplikasi dibuka → otomatis download data terbaru
3. **Folder**: Data tersimpan di folder `PPIC_DSS_Data` di Google Drive Anda

## 🔒 Keamanan

- File `credentials.json` dan `token.pickle` sudah ada di `.gitignore`
- **JANGAN** commit file credentials ke Git/GitHub
- Service Account hanya punya akses ke folder yang Anda share

## 📦 Dependencies

- **streamlit** - Web framework
- **pandas** - Data processing
- **plotly** - Data visualization
- **PyDrive2** - Google Drive integration
- **google-auth** - Google authentication

## 🛠️ Development

### Local Database

Tanpa Google Drive sync, data tersimpan lokal di:
- `ppic_data.json` - Data produksi
- `buyers.json` - Data buyer
- `products.json` - Data produk

### With Google Drive Sync

Data tersimpan di:
1. Local files (untuk akses cepat)
2. Google Drive folder `PPIC_DSS_Data` (untuk backup)

## ❓ Troubleshooting

### Aplikasi tidak bisa running
```bash
# Check Python version
python3 --version  # Harus >= 3.8

# Reinstall dependencies
pip install -r requirements.txt
```

### Google Drive sync tidak aktif
- Pastikan `credentials.json` ada di folder aplikasi
- Check panduan lengkap di [GDRIVE_SETUP.md](GDRIVE_SETUP.md)

### Data tidak tersinkronisasi
- Check koneksi internet
- Pastikan service account sudah di-share ke folder Google Drive
- Check terminal untuk error messages

## 📞 Support

Untuk issue atau pertanyaan:
- Check dokumentasi: [GDRIVE_SETUP.md](GDRIVE_SETUP.md)
- Review error messages di terminal
- Check Google Cloud Console logs

## 📝 License

Internal use only - PT. [Company Name]

---

**Version**: 2.0 (with Google Drive Auto-Sync)
**Last Updated**: November 2025
