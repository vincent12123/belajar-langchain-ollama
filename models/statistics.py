# models/statistics.py
# Model untuk statistik, analisis, trend, anomali, dan perbandingan

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date

from models.enums import MetodeAbsensi, SeverityLevel, TrenDirection


# ── Statistik Per Siswa ────────────────────────────────

class StatistikSiswa(BaseModel):
    """Statistik absensi satu siswa"""
    siswa_id: int
    nama_siswa: Optional[str] = None
    total_hari: int = 0
    total_hadir: int = 0
    total_izin: int = 0
    total_sakit: int = 0
    total_alfa: int = 0
    total_terlambat: int = 0
    persentase_kehadiran: float = 0.0
    rata_rata_waktu_masuk: Optional[str] = None
    tren: Optional[TrenDirection] = None


class StatistikKelas(BaseModel):
    """Statistik absensi satu kelas"""
    kelas_id: int
    nama_kelas: Optional[str] = None
    jumlah_siswa: int = 0
    rata_rata_kehadiran: float = 0.0
    siswa_teraktif: Optional[str] = None
    siswa_bermasalah: Optional[List[str]] = []
    distribusi_status: Optional[Dict[str, int]] = {}


# ── Trend Data ─────────────────────────────────────────

class TrendDataPoint(BaseModel):
    """Satu titik data dalam grafik tren"""
    tanggal: date
    nilai: float
    label: Optional[str] = None


class AttendanceTrendResult(BaseModel):
    """Hasil analisis tren kehadiran"""
    siswa_id: Optional[int] = None
    kelas_id: Optional[int] = None
    nama: Optional[str] = None
    periode: str
    data_points: List[TrendDataPoint] = []
    ringkasan: Optional[str] = None
    tren_keseluruhan: Optional[TrenDirection] = None


# ── Geolocation Analysis ──────────────────────────────

class GeoPoint(BaseModel):
    """Satu titik geolokasi"""
    latitude: float
    longitude: float
    timestamp: Optional[str] = None
    siswa_id: Optional[int] = None
    nama_siswa: Optional[str] = None


class GeolocationResult(BaseModel):
    """Hasil analisis geolokasi absensi"""
    total_records: int = 0
    valid_locations: int = 0
    suspicious_locations: int = 0
    anomali_ditemukan: List[Dict[str, Any]] = []
    radius_sekolah_meter: Optional[float] = None
    detail_anomali: Optional[List["AnomalyDetail"]] = []


# ── Anomaly Detection ─────────────────────────────────

class AnomalyDetail(BaseModel):
    """Detail satu anomali yang terdeteksi"""
    siswa_id: Optional[int] = None
    nama_siswa: Optional[str] = None
    tanggal: Optional[date] = None
    jenis_anomali: str  # "lokasi_jauh", "waktu_tidak_wajar", "pola_mencurigakan"
    deskripsi: str
    severity: str = "medium"
    data_pendukung: Optional[Dict[str, Any]] = None


class AnomalyReport(BaseModel):
    """Laporan keseluruhan anomali"""
    total_anomali: int = 0
    anomali_tinggi: int = 0
    anomali_sedang: int = 0
    anomali_rendah: int = 0
    daftar_anomali: List[AnomalyDetail] = []
    rekomendasi: Optional[List[str]] = []


# ── Class Comparison ───────────────────────────────────

class ClassComparisonItem(BaseModel):
    """Satu kelas dalam perbandingan"""
    kelas_id: int
    nama_kelas: str
    jumlah_siswa: int
    rata_rata_kehadiran: float
    total_alfa: int
    total_terlambat: int = 0
    peringkat: Optional[int] = None


class ClassComparisonResult(BaseModel):
    """Hasil perbandingan antar kelas"""
    periode: Optional[str] = None
    kelas_terbaik: Optional[str] = None
    kelas_perlu_perhatian: Optional[str] = None
    data_perbandingan: List[ClassComparisonItem] = []
    ringkasan: Optional[str] = None


# ── Top Students ───────────────────────────────────────

class TopSiswaItem(BaseModel):
    """Satu siswa dalam ranking"""
    peringkat: int
    siswa_id: int
    nama_siswa: str
    nama_kelas: Optional[str] = None
    persentase_kehadiran: Optional[float] = None
    total_hadir: Optional[int] = None
    total_hari: Optional[int] = None
    jumlah: Optional[int] = None  # jumlah alfa/sakit/izin tergantung query


class TopSiswaResult(BaseModel):
    """Hasil daftar top siswa"""
    kategori: str  # "terrajin", "paling_sering_alfa", etc.
    periode: Optional[str] = None
    data: List[TopSiswaItem] = []


# ── Metode Analysis ───────────────────────────────────

class MetodeAnalisisItem(BaseModel):
    """Satu metode absensi dalam analisis"""
    metode: str
    total_penggunaan: int
    persentase: float
    rata_rata_akurasi: Optional[float] = None


class MetodeAnalisisResult(BaseModel):
    """Hasil analisis metode absensi"""
    periode: Optional[str] = None
    metode_terpopuler: Optional[str] = None
    distribusi: List[MetodeAnalisisItem] = []
    rekomendasi: Optional[str] = None


# ── Time Statistics ────────────────────────────────────

class TimeStatItem(BaseModel):
    """Satu slot waktu dalam statistik"""
    jam: str  # "07:00-07:30"
    jumlah_siswa: int
    persentase: Optional[float] = None


class TimeStatResult(BaseModel):
    """Hasil statistik waktu kehadiran"""
    periode: Optional[str] = None
    rata_rata_masuk: Optional[str] = None
    puncak_kehadiran: Optional[str] = None
    distribusi_waktu: List[TimeStatItem] = []
