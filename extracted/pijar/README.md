# PIJAR
Platform Interaktif Jejaring Asesmen dan Refleksi — **Terangi Potensi, Ukir Prestasi.**

## Jalankan lokal
1. Python 3.11+ disarankan.
2. `python -m venv .venv`
3. Aktifkan virtual environment.
4. `pip install -r requirements.txt`
5. Salin `.env.example` menjadi `.env` dan ganti `SECRET_KEY`.
6. Untuk lokal, SQLite akan dipakai dari `DATABASE_URL` default. Untuk produksi, gunakan PostgreSQL.
7. Inisialisasi migrasi jika folder migration belum berisi revision: `flask --app run.py db init` lalu `flask --app run.py db migrate -m "initial schema"` dan `flask --app run.py db upgrade`.
8. Jalankan: `python run.py`.

## Bootstrap superadmin
Superadmin tidak dibuat dari registrasi publik. Setelah database aktif, buat melalui shell administratif satu kali:

```python
from app import create_app
from app.extensions import db
from app.models import User
app=create_app()
with app.app_context():
    u=User(full_name="Platform Admin",email="admin@example.com",role="SUPERADMIN")
    u.set_password("GANTI-DENGAN-SECRET-KUAT")
    db.session.add(u); db.session.commit()
```

Jangan memasukkan password produksi ke repository.

## Fitur utama
- Guru: akun, dashboard, ujian, bank soal, publikasi, kode ujian, hasil, penilaian esai.
- Siswa: kode ujian, identitas peserta, timer server, autosave backend, submit, hasil sesuai pengaturan.
- Superadmin: statistik aktual, daftar guru, aktivasi/deaktivasi, daftar ujian.
- Soal: pilihan ganda, benar/salah, jawaban singkat exact-match, esai manual.

## Pengujian
`pytest -q` setelah dependensi terpasang.

## Status verifikasi
Lihat `IMPLEMENTATION_STATUS.md`. Runtime test tidak dijalankan di lingkungan pembuatan ini karena dependensi Flask belum terpasang. Tidak ada hasil tes yang diklaim lulus tanpa eksekusi nyata.
