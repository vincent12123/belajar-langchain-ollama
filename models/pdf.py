# models/pdf.py
# Model data terstruktur untuk PDF generator

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

from models.entities import SiswaRead, KelasRead, SekolahInfo, AbsensiRead
from models.statistics import StatistikSiswa, StatistikKelas, TopSiswaItem, AnomalyDetail


# ── Surat Peringatan ──────────────────────────────────

class SuratPeringatanData(BaseModel):
    """Data untuk generate surat peringatan alfa"""
    siswa: Dict[str, Any]  # data siswa (nama, nis, kelas, nama_orang_tua)
    daftar_tanggal_alfa: List[Any]  # list tanggal alfa
    rekap: Dict[str, Any]  # total_hadir, total_sakit, total_izin, total_alfa, total_hari
    persentase_kehadiran: Any  # bisa str atau float dari DB
    tingkat_peringatan: int = 1  # 1, 2, atau 3
    tanggal_surat: date = Field(default_factory=date.today)
    nomor_surat: Optional[str] = None
    catatan_tambahan: Optional[str] = None


# ── Laporan Absensi Alfa ──────────────────────────────

class LaporanAlfaData(BaseModel):
    """Data untuk generate laporan siswa alfa harian"""
    tanggal: Any  # str atau date
    daftar_siswa: List[Dict[str, Any]]  # list {nama_siswa, nis, kelas}
    total: int
    tanggal_cetak: date = Field(default_factory=date.today)


# ── Laporan Kepala Sekolah ────────────────────────────

class LaporanKepsekData(BaseModel):
    """Data untuk generate laporan kepsek (ringkasan range)"""
    sekolah: Optional[Dict[str, str]] = None
    periode: Optional[str] = None
    tanggal_cetak: date = Field(default_factory=date.today)
    ringkasan_sekolah: Optional[Dict[str, Any]] = None
    data_per_kelas: Optional[List[Dict[str, Any]]] = []
    ranking: Optional[List[Dict[str, Any]]] = []
    alerts: Optional[List[Dict[str, Any]]] = []


# ── Laporan Guru Harian ──────────────────────────────

class LaporanGuruHarianData(BaseModel):
    """Data untuk generate laporan guru harian detail"""
    sekolah: Optional[Dict[str, str]] = None
    kelas: Optional[Dict[str, Any]] = None
    tanggal: Any  # str atau date
    guru_pengajar: Optional[str] = None
    daftar_absensi: List[Dict[str, Any]] = []
    ringkasan: Optional[Dict[str, int]] = None
    missing_records: Optional[List[Dict[str, Any]]] = []
    catatan: Optional[str] = None


# ── Generic PDF Output ────────────────────────────────

class PDFOutput(BaseModel):
    """Hasil generate PDF"""
    file_path: str
    file_name: str
    file_size_bytes: Optional[int] = None
    generated_at: datetime = Field(default_factory=datetime.now)
    tipe_laporan: str
