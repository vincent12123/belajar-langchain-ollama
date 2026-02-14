# models/enums.py
# Enum types untuk seluruh aplikasi

from enum import Enum


class StatusAbsensi(str, Enum):
    """Status kehadiran siswa"""
    HADIR = "Hadir"
    IZIN = "Izin"
    SAKIT = "Sakit"
    ALFA = "Alfa"
    TERLAMBAT = "Terlambat"


class MetodeAbsensi(str, Enum):
    """Metode yang digunakan untuk absensi"""
    GPS = "gps"
    MANUAL = "manual"
    QR_CODE = "qr_code"
    FACE_RECOGNITION = "face_recognition"


class StatusPenempatan(str, Enum):
    """Status penempatan siswa di kelas"""
    AKTIF = "aktif"
    NAIK_KELAS = "naik_kelas"
    PINDAH = "pindah"
    LULUS = "lulus"


class JenisLaporan(str, Enum):
    """Jenis laporan yang bisa digenerate"""
    HARIAN = "harian"
    MINGGUAN = "mingguan"
    BULANAN = "bulanan"
    SEMESTER = "semester"


class RoleUser(str, Enum):
    """Role pengguna sistem"""
    GURU = "guru"
    KEPSEK = "kepsek"
    ADMIN = "admin"
    WALI_KELAS = "wali_kelas"


class SeverityLevel(str, Enum):
    """Level severity untuk anomali"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TrenDirection(str, Enum):
    """Arah tren kehadiran"""
    NAIK = "naik"
    TURUN = "turun"
    STABIL = "stabil"
