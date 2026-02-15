

Baik, saya akan jelaskan kegunaan masing-masing query secara detail. Script ini pada dasarnya adalah **sistem laporan lengkap untuk manajemen sekolah** yang mencakup kehadiran, keuangan SPP, data siswa, dan dashboard eksekutif.

---

## Variabel Parameter

```sql
SET @tanggal_awal  = '2026-01-01';
SET @tanggal_akhir = '2026-02-28';
SET @bulan         = 2;
SET @tahun         = 2026;
```

Ini bukan query laporan, melainkan **deklarasi variabel** yang berfungsi sebagai "remote control" untuk seluruh script. Dengan mengubah nilai di sini saja, semua query di bawahnya otomatis menyesuaikan periode laporannya. Jadi tidak perlu edit satu per satu di setiap query.

---

## Modul 1 — Kehadiran / Absensi

### 1.1 Rekap Kehadiran Per Siswa Per Bulan

**Kegunaan:** Menampilkan laporan absensi **setiap siswa secara individual** untuk bulan dan tahun tertentu (sesuai `@bulan` dan `@tahun`).

**Data yang dihasilkan:**

- NIS, nama siswa, dan kelasnya
- Nama bulan dan tahun
- Jumlah hari hadir, sakit, izin, dan alpa
- Total hari tercatat
- **Persentase kehadiran** (hadir ÷ total hari × 100)

**Siapa yang butuh:** Wali kelas dan guru BK untuk memantau kehadiran masing-masing siswa. Berguna juga untuk cetak rapor atau laporan ke orang tua.

---

### 1.2 Rekap Kehadiran Per Kelas (Dashboard Wali Kelas)

**Kegunaan:** Menampilkan **ringkasan kehadiran di level kelas**, bukan per individu. Jadi satu baris = satu kelas.

**Data yang dihasilkan:**

- Nama kelas, jurusan, dan wali kelas
- Jumlah siswa unik yang tercatat absensinya
- **Rata-rata kehadiran** seluruh kelas (dalam persen)
- Total alpa dan sakit seluruh siswa di kelas tersebut

**Siapa yang butuh:** Kepala sekolah atau wakil kurikulum untuk membandingkan performa kehadiran antar kelas. Kelas diurutkan dari kehadiran tertinggi ke terendah.

---

### 1.3 Daftar Siswa Rawan (Kehadiran < 75%)

**Kegunaan:** Mendeteksi **siswa yang kehadirannya di bawah ambang batas 75%** sepanjang tahun berjalan. Ini adalah query "early warning system".

**Data yang dihasilkan:**

- NIS, nama, kelas, dan **nomor WhatsApp orang tua**
- Total hari, total hadir, dan persentase kehadiran
- Hanya menampilkan siswa dengan `persen_hadir < 75`

**Siapa yang butuh:** Guru BK dan wali kelas untuk **tindak lanjut langsung** — misalnya menghubungi orang tua via WhatsApp. Kolom `whatsapp_orang_tua` sengaja ditampilkan agar bisa langsung kontak.

---

## Modul 2 — Keuangan SPP

### 2.1 Rekap Tagihan & Pembayaran SPP Per Siswa

**Kegunaan:** Menampilkan **status pembayaran SPP setiap siswa per bulan** — apakah lunas, belum lunas, atau menunggak.

**Data yang dihasilkan:**

- NIS, nama, kelas
- Bulan dan tahun tagihan
- Nominal tagihan, sisa tagihan, dan total yang sudah dibayar
- Status tagihan dari database
- **Keterangan otomatis**: `LUNAS`, `BELUM LUNAS`, atau `MENUNGGAK` (jika sudah lewat jatuh tempo)

**Siapa yang butuh:** Bagian keuangan/TU untuk melihat detail pembayaran per siswa. Juga berguna untuk cetak bukti tagihan atau slip pembayaran.

---

### 2.2 Laporan Tunggakan SPP (Piutang)

**Kegunaan:** Menampilkan **daftar siswa yang masih punya tunggakan SPP** (sisa tagihan > 0 dan sudah lewat jatuh tempo). Ini adalah laporan piutang sekolah.

**Data yang dihasilkan:**

- NIS, nama, nama orang tua, WhatsApp orang tua
- Kelas
- **Jumlah bulan yang menunggak**
- **Total nominal tunggakan**
- Periode tunggakan (dari bulan/tahun berapa sampai bulan/tahun berapa)

**Siapa yang butuh:** Bendahara sekolah dan kepala sekolah. Diurutkan dari tunggakan terbesar, sehingga prioritas penagihan jelas. Kolom WhatsApp disertakan untuk kemudahan komunikasi.

---

### 2.3 Laporan Pendapatan SPP Harian/Bulanan

**Kegunaan:** Menampilkan **rekapitulasi pemasukan SPP** dalam rentang tanggal tertentu, dikelompokkan per hari dan per metode pembayaran.

**Data yang dihasilkan:**

- Tanggal transaksi
- Metode pembayaran (cash, transfer, dll.)
- Jumlah transaksi pada hari itu
- Total nominal pendapatan
- **Nama kasir** yang memproses pembayaran

**Siapa yang butuh:** Bendahara untuk rekonsiliasi keuangan harian. Juga berguna untuk audit karena mencatat siapa kasir yang menginput setiap transaksi.

---

### 2.4 Ringkasan Keuangan Per Kelas

**Kegunaan:** Menampilkan **performa pembayaran SPP di level kelas** — seberapa besar tagihan total, berapa yang sudah terbayar, dan berapa sisanya.

**Data yang dihasilkan:**

- Nama kelas, jurusan, tingkat
- Jumlah siswa
- Total tagihan, total terbayar, total sisa
- **Persentase terbayar** (diurutkan dari yang tertinggi)

**Siapa yang butuh:** Kepala sekolah dan manajemen untuk melihat kelas mana yang paling disiplin bayar SPP dan kelas mana yang perlu perhatian lebih.

---

## Modul 3 — Data Kesiswaan

### 3.1 Laporan Jumlah Siswa Per Kelas & Jurusan

**Kegunaan:** Menampilkan **distribusi siswa** di setiap kelas pada tahun ajaran aktif.

**Data yang dihasilkan:**

- Nama kelas, tingkat, jurusan, wali kelas
- Tahun ajaran
- Total siswa di kelas
- Berapa yang **aktif** dan berapa yang **tidak aktif** (keluar/pindah/lulus)

**Siapa yang butuh:** Bagian kurikulum dan tata usaha untuk perencanaan — misalnya menentukan apakah suatu kelas kelebihan/kekurangan murid, atau untuk laporan ke Dinas Pendidikan.

---

### 3.2 Profil Lengkap Siswa

**Kegunaan:** Menampilkan **data lengkap seluruh siswa aktif** beserta penempatan kelasnya.

**Data yang dihasilkan:**

- NIS, nama, email, tanggal lahir, alamat
- Nama orang tua, WhatsApp siswa, WhatsApp orang tua
- Status siswa, foto profil
- Kelas, jurusan, tingkat, wali kelas, tahun ajaran

**Siapa yang butuh:** Tata usaha untuk keperluan administrasi umum, cetak biodata, atau ekspor data siswa. Filter `deleted_at IS NULL` memastikan siswa yang sudah dihapus (soft delete) tidak ikut tampil.

---

## Modul 4 — Tagihan Lain-Lain

### 4.1 Rekap Tagihan Lain Per Siswa

**Kegunaan:** Menampilkan **tagihan non-SPP** untuk setiap siswa, misalnya biaya seragam, biaya praktikum, biaya ujian, dll.

**Data yang dihasilkan:**

- NIS dan nama siswa
- Jenis tagihan (berupa ID, bisa di-join lebih lanjut ke tabel jenis tagihan)
- Nominal tagihan, sisa tagihan, dan status
- Keterangan: `LUNAS` atau `BELUM LUNAS`

**Siapa yang butuh:** Bagian keuangan untuk memantau tagihan di luar SPP. Query ini lebih sederhana karena tidak ada filter tanggal — menampilkan semua tagihan lain yang ada.

---

## Modul 5 — Dashboard Eksekutif

### 5.1 Dashboard Eksekutif (4 Query Sekaligus)

Modul ini terdiri dari **4 query independen** yang masing-masing menghasilkan satu angka/metrik kunci:

| Query | Metrik | Kegunaan |
|-------|--------|----------|
| **Query 1** | `total_siswa_aktif` | Menghitung jumlah seluruh siswa berstatus aktif (dan belum di-soft-delete) |
| **Query 2** | `rata_kehadiran` | Menghitung rata-rata kehadiran **bulan berjalan** (bulan ini) |
| **Query 3** | `pendapatan_bulan_ini` | Menghitung total pemasukan SPP **bulan berjalan** |
| **Query 4** | `total_tunggakan` | Menghitung total seluruh sisa tagihan SPP yang belum terbayar (piutang keseluruhan) |

**Siapa yang butuh:** Kepala sekolah atau pimpinan yayasan. Keempat angka ini biasanya ditampilkan sebagai **kartu/widget di halaman dashboard utama** aplikasi, memberikan gambaran kondisi sekolah secara sekilas (*at a glance*).

---

## Ringkasan Keseluruhan

Script ini adalah **satu paket laporan manajemen sekolah** yang terbagi dalam 5 modul:

- **Modul 1 (Kehadiran):** Rekap individu, rekap kelas, dan deteksi siswa rawan
- **Modul 2 (Keuangan SPP):** Status bayar per siswa, daftar penunggak, pendapatan harian, dan ringkasan per kelas
- **Modul 3 (Kesiswaan):** Distribusi siswa per kelas dan profil lengkap
- **Modul 4 (Tagihan Lain):** Tagihan non-SPP
- **Modul 5 (Dashboard):** 4 metrik kunci untuk overview eksekutif

Semua query saling independen dan bisa dijalankan satu per satu atau sekaligus sebagai batch di Navicat.

Ada yang ingin dibahas lebih lanjut? Misalnya:
- Ingin saya buatkan **versi optimasi/index** untuk query yang berat?
- Ingin menambahkan **filter tambahan** di query tertentu?
- Ingin saya buatkan **diagram ERD** dari relasi tabel yang dipakai?