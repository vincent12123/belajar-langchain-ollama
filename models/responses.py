# models/responses.py
# Pydantic models untuk response API yang konsisten

from pydantic import BaseModel
from typing import Optional, Any, List, Dict
from datetime import datetime

from models.base import BaseResponse
from models.entities import KelasRead, AbsensiRead
from models.statistics import (
    AttendanceTrendResult,
    GeolocationResult,
    ClassComparisonResult,
    AnomalyReport,
    MetodeAnalisisResult,
    TopSiswaResult,
    TimeStatResult,
)


# ── Chat Response ─────────────────────────────────────

class QueryResponse(BaseModel):
    """Response untuk endpoint /chat (legacy)"""
    answer: str


class ChatSDKResponse(BaseModel):
    """Response untuk AI SDK format"""
    id: str
    choices: List[Dict[str, Any]]
    model: Optional[str] = None
    usage: Optional[Dict[str, int]] = None


# ── Analytics Responses ───────────────────────────────

class AttendanceTrendsResponse(BaseResponse):
    """Response analisis tren kehadiran"""
    data: Optional[AttendanceTrendResult] = None


class GeolocationAnalysisResponse(BaseResponse):
    """Response analisis geolokasi"""
    data: Optional[GeolocationResult] = None


class ClassComparisonResponse(BaseResponse):
    """Response perbandingan kelas"""
    data: Optional[ClassComparisonResult] = None


class AnomaliAbsensiResponse(BaseResponse):
    """Response deteksi anomali"""
    data: Optional[AnomalyReport] = None


class AnalisisMetodeResponse(BaseResponse):
    """Response analisis metode absensi"""
    data: Optional[MetodeAnalisisResult] = None


class TopSiswaResponse(BaseResponse):
    """Response ranking siswa"""
    data: Optional[TopSiswaResult] = None


class StatistikWaktuResponse(BaseResponse):
    """Response statistik waktu"""
    data: Optional[TimeStatResult] = None


# ── Report Responses ──────────────────────────────────

class LaporanResponse(BaseResponse):
    """Response generik untuk laporan yang digenerate"""
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_url: Optional[str] = None
    data_ringkasan: Optional[Dict[str, Any]] = None


# ── Kelas List Response ───────────────────────────────

class KelasListResponse(BaseResponse):
    """Response daftar kelas"""
    data: List[KelasRead] = []
    total: int = 0


# ── File Management ──────────────────────────────────

class FileItem(BaseModel):
    """Satu file yang tersedia untuk download"""
    filename: str
    filepath: Optional[str] = None
    size_bytes: Optional[int] = None
    created_at: Optional[datetime] = None
    tipe: Optional[str] = None  # "laporan_kepsek", "surat_peringatan", etc.


class FileListResponse(BaseResponse):
    """Response daftar file"""
    data: List[FileItem] = []
    total: int = 0
