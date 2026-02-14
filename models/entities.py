# models/entities.py
# Domain models: representasi data dari tabel database

from pydantic import BaseModel
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date

from models.enums import StatusAbsensi, MetodeAbsensi, StatusPenempatan

if TYPE_CHECKING:
    from models.statistics import StatistikSiswa, StatistikKelas


# ── Siswa (Student) ────────────────────────────────────

class SiswaBase(BaseModel):
    """Field dasar siswa"""
    nama: str
    nis: Optional[str] = None
    nisn: Optional[str] = None
    jenis_kelamin: Optional[str] = None
    tempat_lahir: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    alamat: Optional[str] = None
    no_telepon: Optional[str] = None
    email: Optional[str] = None


class SiswaCreate(SiswaBase):
    """Data untuk membuat siswa baru"""
    kelas_id: Optional[int] = None


class SiswaRead(SiswaBase):
    """Data siswa dari database (read-only)"""
    id: int
    status: Optional[str] = None
    nama_orang_tua: Optional[str] = None
    whatsapp_orang_tua: Optional[str] = None
    kelas: Optional[str] = None  # nama kelas dari JOIN
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SiswaDetail(SiswaRead):
    """Data lengkap siswa + relasi"""
    riwayat_absensi: Optional[List["AbsensiRead"]] = []
    statistik: Optional["StatistikSiswa"] = None


# ── Kelas (Class) ──────────────────────────────────────

class KelasBase(BaseModel):
    """Field dasar kelas"""
    nama: str
    tingkat: Optional[int] = None
    jurusan: Optional[str] = None
    wali_kelas: Optional[str] = None


class KelasCreate(KelasBase):
    """Data untuk membuat kelas baru"""
    tahun_ajaran_id: Optional[int] = None


class KelasRead(KelasBase):
    """Data kelas dari database"""
    id: int
    jumlah_siswa: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class KelasDetail(KelasRead):
    """Data lengkap kelas + relasi"""
    daftar_siswa: Optional[List[SiswaRead]] = []
    statistik_absensi: Optional["StatistikKelas"] = None


# ── Absensi (Attendance) ──────────────────────────────

class AbsensiBase(BaseModel):
    """Field dasar absensi"""
    siswa_id: int
    tanggal: date
    status: str  # StatusAbsensi values: Hadir, Izin, Sakit, Alfa
    metode: Optional[str] = None
    keterangan: Optional[str] = None


class AbsensiCreate(AbsensiBase):
    """Data untuk membuat record absensi baru"""
    kelas_id: Optional[int] = None
    waktu_absen: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    jarak_meter: Optional[float] = None


class AbsensiRead(AbsensiBase):
    """Data absensi dari database"""
    id: int
    kelas_id: Optional[int] = None
    nama_siswa: Optional[str] = None
    nama_kelas: Optional[str] = None
    waktu_absen: Optional[str] = None  # string dari TIME column
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    jarak_meter: Optional[float] = None
    catatan: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Penempatan Kelas ───────────────────────────────────

class PenempatanKelasRead(BaseModel):
    """Data penempatan siswa di kelas"""
    id: int
    siswa_id: int
    kelas_id: int
    status: StatusPenempatan = StatusPenempatan.AKTIF

    class Config:
        from_attributes = True


# ── Tahun Ajaran ───────────────────────────────────────

class TahunAjaranRead(BaseModel):
    """Data tahun ajaran"""
    id: int
    nama: str
    tanggal_mulai: Optional[date] = None
    tanggal_selesai: Optional[date] = None
    is_active: bool = True


# ── Sekolah (School Info) ──────────────────────────────

class SekolahInfo(BaseModel):
    """Informasi sekolah untuk kop surat & laporan"""
    nama_sekolah: Optional[str] = None
    school_name: Optional[str] = None  # alias compat
    npsn: Optional[str] = None
    alamat: Optional[str] = None
    school_address: Optional[str] = None  # alias compat
    kota: Optional[str] = None
    provinsi: Optional[str] = None
    kepala_sekolah: Optional[str] = None
    principal_name: Optional[str] = None  # alias compat
    nip_kepala_sekolah: Optional[str] = None
    kode_sekolah: Optional[str] = None
    telepon: Optional[str] = None
    school_phone: Optional[str] = None  # alias compat
    email: Optional[str] = None
    school_email: Optional[str] = None  # alias compat
    logo_path: Optional[str] = None
