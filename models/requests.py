# models/requests.py
# Pydantic models untuk validasi input di setiap API endpoint
# Field names HARUS sesuai dengan parameter di db_functions.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


# ── Chat / Query ───────────────────────────────────────

class QueryRequest(BaseModel):
    """Request untuk endpoint /chat (legacy)"""
    query: str
    model: Optional[str] = None  # Override model Ollama


class ChatSDKRequest(BaseModel):
    """Request dari Vercel AI SDK / useChat hook"""
    messages: List[dict]
    model: Optional[str] = None
    stream: Optional[bool] = False


# ── Attendance Trends ─────────────────────────────────

class AttendanceTrendsRequest(BaseModel):
    """Request untuk analisis tren kehadiran"""
    siswa_id: Optional[int] = None
    nama_siswa: Optional[str] = None
    kelas_id: Optional[int] = None
    nama_kelas: Optional[str] = None
    months: Optional[int] = 6


# ── Geolocation ───────────────────────────────────────

class GeolocationAnalysisRequest(BaseModel):
    """Request untuk analisis geolokasi absensi"""
    kelas_id: Optional[int] = None
    nama_kelas: Optional[str] = None
    tanggal: Optional[str] = None


# ── Class Comparison ──────────────────────────────────

class ClassComparisonRequest(BaseModel):
    """Request untuk perbandingan kehadiran antar kelas"""
    tingkat: Optional[int] = None
    jurusan: Optional[str] = None


# ── Anomaly Detection ─────────────────────────────────

class AnomaliAbsensiRequest(BaseModel):
    """Request untuk deteksi anomali absensi"""
    kelas_id: Optional[int] = None
    nama_kelas: Optional[str] = None
    tanggal_mulai: Optional[str] = None
    tanggal_akhir: Optional[str] = None


# ── Metode Analisis ───────────────────────────────────

class AnalisisMetodeAbsenRequest(BaseModel):
    """Request untuk analisis metode absensi"""
    kelas_id: Optional[int] = None
    nama_kelas: Optional[str] = None
    tanggal_mulai: Optional[str] = None
    tanggal_akhir: Optional[str] = None


# ── Top Siswa ─────────────────────────────────────────

class TopSiswaRequest(BaseModel):
    """Request untuk ranking siswa berdasarkan status absensi"""
    kelas_id: Optional[int] = None
    nama_kelas: Optional[str] = None
    tanggal_mulai: Optional[str] = None
    tanggal_akhir: Optional[str] = None
    status: Optional[str] = "Alfa"
    limit: Optional[int] = 10


# ── Statistik Waktu ───────────────────────────────────

class StatistikWaktuRequest(BaseModel):
    """Request untuk statistik waktu kehadiran"""
    kelas_id: Optional[int] = None
    nama_kelas: Optional[str] = None
    tanggal_mulai: Optional[str] = None
    tanggal_akhir: Optional[str] = None
    jam_telat: Optional[str] = "07:15:00"
    limit: Optional[int] = 10


# ── Laporan Kepsek (Range) ────────────────────────────

class LaporanKepsekRequest(BaseModel):
    """Request untuk laporan ringkasan kepala sekolah (lintas kelas)"""
    tanggal_mulai: str
    tanggal_akhir: str
    tingkat: Optional[int] = None
    jurusan: Optional[str] = None
    threshold_kehadiran: Optional[float] = 85.0


# ── Laporan Guru Harian ──────────────────────────────

class LaporanGuruHarianRequest(BaseModel):
    """Request untuk laporan harian detail per kelas"""
    kelas_id: Optional[int] = None
    nama_kelas: Optional[str] = None
    tanggal: Optional[str] = None


# ── Pagination ────────────────────────────────────────

class PaginationRequest(BaseModel):
    """Parameter pagination generik"""
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
