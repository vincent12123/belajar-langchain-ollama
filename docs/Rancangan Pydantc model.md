

Saya akan menarik detail dari source code Anda terlebih dahulu agar rancangan Pydantic model-nya akurat dan sesuai dengan struktur data yang sudah ada.



Baik, saya akan merancang keseluruhan Pydantic model untuk aplikasi absensi sekolah ini berdasarkan kode yang sudah kita analisis sebelumnya. Izinkan saya menarik detail spesifik dari dokumen yang tersedia terlebih dahulu.





Baik, saya akan mengambil detail lengkap dari file yang Anda berikan untuk merancang semua Pydantic model secara akurat berdasarkan kode aktual Anda.





# Rancangan Pydantic Model untuk Sistem Manajemen Absensi Sekolah

Berikut adalah rancangan lengkap arsitektur Pydantic model yang mencakup **seluruh layer** aplikasi — mulai dari entitas database, request/response API, WebSocket, PDF generator, konfigurasi, hingga AI agent orchestration.

---

## 1. Base & Utility Models

Model fondasi yang digunakan ulang di seluruh aplikasi:

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime, date
from enum import Enum


# ── Enums ──────────────────────────────────────────────
class StatusAbsensi(str, Enum):
    HADIR = "hadir"
    IZIN = "izin"
    SAKIT = "sakit"
    ALFA = "alfa"
    TERLAMBAT = "terlambat"

class MetodeAbsensi(str, Enum):
    GPS = "gps"
    MANUAL = "manual"
    QR_CODE = "qr_code"
    FACE_RECOGNITION = "face_recognition"

class JenisLaporan(str, Enum):
    HARIAN = "harian"
    MINGGUAN = "mingguan"
    BULANAN = "bulanan"
    SEMESTER = "semester"

class RoleUser(str, Enum):
    GURU = "guru"
    KEPSEK = "kepsek"
    ADMIN = "admin"
    WALI_KELAS = "wali_kelas"


# ── Base Response ──────────────────────────────────────
class BaseResponse(BaseModel):
    success: bool = True
    message: str = "OK"
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseResponse):
    success: bool = False
    error_code: Optional[str] = None
    detail: Optional[str] = None

class PaginationMeta(BaseModel):
    page: int = 1
    per_page: int = 20
    total_items: int
    total_pages: int

class PaginatedResponse(BaseResponse):
    pagination: Optional[PaginationMeta] = None
```

---

## 2. Entity / Domain Models

Representasi data dari tabel database (`siswa`, `kelas`, `absensi`, dll):

```python
# ── Siswa (Student) ────────────────────────────────────
class SiswaBase(BaseModel):
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
    kelas_id: Optional[int] = None

class SiswaRead(SiswaBase):
    id: int
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SiswaDetail(SiswaRead):
    kelas: Optional["KelasRead"] = None
    riwayat_absensi: Optional[List["AbsensiRead"]] = []
    statistik: Optional["StatistikSiswa"] = None


# ── Kelas (Class) ──────────────────────────────────────
class KelasBase(BaseModel):
    nama_kelas: str
    tingkat: Optional[str] = None
    jurusan: Optional[str] = None
    wali_kelas: Optional[str] = None
    tahun_ajaran: Optional[str] = None

class KelasCreate(KelasBase):
    pass

class KelasRead(KelasBase):
    id: int
    is_active: bool = True
    jumlah_siswa: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class KelasDetail(KelasRead):
    daftar_siswa: Optional[List[SiswaRead]] = []
    statistik_absensi: Optional["StatistikKelas"] = None


# ── Absensi (Attendance) ──────────────────────────────
class AbsensiBase(BaseModel):
    siswa_id: int
    tanggal: date
    status: StatusAbsensi
    metode: Optional[MetodeAbsensi] = None
    keterangan: Optional[str] = None
    waktu_masuk: Optional[datetime] = None
    waktu_keluar: Optional[datetime] = None

class AbsensiCreate(AbsensiBase):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    device_info: Optional[str] = None

class AbsensiRead(AbsensiBase):
    id: int
    kelas_id: Optional[int] = None
    nama_siswa: Optional[str] = None
    nama_kelas: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Penempatan Kelas ───────────────────────────────────
class PenempatanKelasRead(BaseModel):
    id: int
    siswa_id: int
    kelas_id: int
    tahun_ajaran: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


# ── Tahun Ajaran ───────────────────────────────────────
class TahunAjaranRead(BaseModel):
    id: int
    nama: str
    tanggal_mulai: date
    tanggal_selesai: date
    is_active: bool = True


# ── Sekolah (School Info) ──────────────────────────────
class SekolahInfo(BaseModel):
    nama_sekolah: str
    npsn: Optional[str] = None
    alamat: Optional[str] = None
    kota: Optional[str] = None
    provinsi: Optional[str] = None
    kepala_sekolah: Optional[str] = None
    nip_kepala_sekolah: Optional[str] = None
    logo_path: Optional[str] = None
    telepon: Optional[str] = None
```

---

## 3. Statistik & Analisis Models

Model untuk hasil perhitungan dan analisis data:

```python
# ── Statistik Per Siswa ────────────────────────────────
class StatistikSiswa(BaseModel):
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
    tren: Optional[str] = None  # "naik", "turun", "stabil"

class StatistikKelas(BaseModel):
    kelas_id: int
    nama_kelas: Optional[str] = None
    jumlah_siswa: int = 0
    rata_rata_kehadiran: float = 0.0
    siswa_teraktif: Optional[str] = None
    siswa_bermasalah: Optional[List[str]] = []
    distribusi_status: Optional[Dict[str, int]] = {}


# ── Trend Data ─────────────────────────────────────────
class TrendDataPoint(BaseModel):
    tanggal: date
    nilai: float
    label: Optional[str] = None

class AttendanceTrendResult(BaseModel):
    siswa_id: Optional[int] = None
    kelas_id: Optional[int] = None
    nama: Optional[str] = None
    periode: str
    data_points: List[TrendDataPoint] = []
    ringkasan: Optional[str] = None
    tren_keseluruhan: Optional[str] = None  # "naik"/"turun"/"stabil"


# ── Geolocation Analysis ──────────────────────────────
class GeoPoint(BaseModel):
    latitude: float
    longitude: float
    timestamp: Optional[datetime] = None
    siswa_id: Optional[int] = None
    nama_siswa: Optional[str] = None

class GeolocationResult(BaseModel):
    total_records: int = 0
    valid_locations: int = 0
    suspicious_locations: int = 0
    anomali_ditemukan: List[Dict[str, Any]] = []
    radius_sekolah_meter: Optional[float] = None
    detail_anomali: Optional[List["AnomalyDetail"]] = []


# ── Anomaly Detection ─────────────────────────────────
class AnomalyDetail(BaseModel):
    siswa_id: int
    nama_siswa: str
    tanggal: date
    jenis_anomali: str  # "lokasi_jauh", "waktu_tidak_wajar", "pola_mencurigakan"
    deskripsi: str
    severity: str = "medium"  # "low", "medium", "high"
    data_pendukung: Optional[Dict[str, Any]] = None

class AnomalyReport(BaseModel):
    total_anomali: int = 0
    anomali_tinggi: int = 0
    anomali_sedang: int = 0
    anomali_rendah: int = 0
    daftar_anomali: List[AnomalyDetail] = []
    rekomendasi: Optional[List[str]] = []


# ── Class Comparison ───────────────────────────────────
class ClassComparisonItem(BaseModel):
    kelas_id: int
    nama_kelas: str
    jumlah_siswa: int
    rata_rata_kehadiran: float
    total_alfa: int
    total_terlambat: int
    peringkat: Optional[int] = None

class ClassComparisonResult(BaseModel):
    periode: str
    kelas_terbaik: Optional[str] = None
    kelas_perlu_perhatian: Optional[str] = None
    data_perbandingan: List[ClassComparisonItem] = []
    ringkasan: Optional[str] = None


# ── Top Students ───────────────────────────────────────
class TopSiswaItem(BaseModel):
    peringkat: int
    siswa_id: int
    nama_siswa: str
    nama_kelas: str
    persentase_kehadiran: float
    total_hadir: int
    total_hari: int

class TopSiswaResult(BaseModel):
    kategori: str  # "terrajin", "paling_sering_alfa", etc.
    periode: str
    data: List[TopSiswaItem] = []


# ── Metode Analysis ───────────────────────────────────
class MetodeAnalisisItem(BaseModel):
    metode: MetodeAbsensi
    total_penggunaan: int
    persentase: float
    rata_rata_akurasi: Optional[float] = None

class MetodeAnalisisResult(BaseModel):
    periode: str
    metode_terpopuler: Optional[str] = None
    distribusi: List[MetodeAnalisisItem] = []
    rekomendasi: Optional[str] = None


# ── Time Statistics ────────────────────────────────────
class TimeStatItem(BaseModel):
    jam: str  # "07:00-07:30"
    jumlah_siswa: int
    persentase: float

class TimeStatResult(BaseModel):
    periode: str
    rata_rata_masuk: Optional[str] = None
    puncak_kehadiran: Optional[str] = None
    distribusi_waktu: List[TimeStatItem] = []
```

---

## 4. API Request Models

Model untuk validasi input di setiap endpoint:

```python
# ── Chat / Query ───────────────────────────────────────
class QueryRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatSDKRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    stream: Optional[bool] = False


# ── Attendance Trends ─────────────────────────────────
class AttendanceTrendsRequest(BaseModel):
    siswa_id: Optional[int] = None
    nama_siswa: Optional[str] = None
    kelas_id: Optional[int] = None
    nama_kelas: Optional[str] = None
    tanggal_mulai: Optional[date] = None
    tanggal_akhir: Optional[date] = None
    periode: Optional[str] = "bulanan"  # "harian", "mingguan", "bulanan"


# ── Geolocation ───────────────────────────────────────
class GeolocationAnalysisRequest(BaseModel):
    kelas_id: Optional[int] = None
    siswa_id: Optional[int] = None
    tanggal_mulai: Optional[date] = None
    tanggal_akhir: Optional[date] = None
    radius_meter: Optional[float] = 100.0


# ── Class Comparison ──────────────────────────────────
class ClassComparisonRequest(BaseModel):
    kelas_ids: Optional[List[int]] = None
    bulan: Optional[int] = None
    tahun: Optional[int] = None
    tanggal_mulai: Optional[date] = None
    tanggal_akhir: Optional[date] = None


# ── Anomaly Detection ─────────────────────────────────
class AnomaliAbsensiRequest(BaseModel):
    kelas_id: Optional[int] = None
    siswa_id: Optional[int] = None
    bulan: Optional[int] = None
    tahun: Optional[int] = None
    severity_minimum: Optional[str] = "low"


# ── Metode Analisis ───────────────────────────────────
class AnalisisMetodeAbsenRequest(BaseModel):
    kelas_id: Optional[int] = None
    bulan: Optional[int] = None
    tahun: Optional[int] = None


# ── Top Siswa ─────────────────────────────────────────
class TopSiswaRequest(BaseModel):
    kategori: Optional[str] = "terrajin"
    kelas_id: Optional[int] = None
    limit: Optional[int] = 10
    bulan: Optional[int] = None
    tahun: Optional[int] = None


# ── Statistik Waktu ───────────────────────────────────
class StatistikWaktuRequest(BaseModel):
    kelas_id: Optional[int] = None
    bulan: Optional[int] = None
    tahun: Optional[int] = None
    interval_menit: Optional[int] = 30


# ── Laporan Kepsek ────────────────────────────────────
class LaporanKepsekRequest(BaseModel):
    bulan: Optional[int] = None
    tahun: Optional[int] = None
    jenis: Optional[JenisLaporan] = JenisLaporan.BULANAN
    include_grafik: Optional[bool] = True


# ── Laporan Guru Harian ──────────────────────────────
class LaporanGuruHarianRequest(BaseModel):
    kelas_id: int
    tanggal: Optional[date] = None
    guru_id: Optional[int] = None


# ── Pagination ────────────────────────────────────────
class PaginationRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
```

---

## 5. API Response Models

```python
# ── Chat Response ─────────────────────────────────────
class QueryResponse(BaseResponse):
    response: str
    data: Optional[Any] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    sources: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None

class ChatSDKResponse(BaseModel):
    id: str
    choices: List[Dict[str, Any]]
    model: Optional[str] = None
    usage: Optional[Dict[str, int]] = None


# ── Analytics Responses ───────────────────────────────
class AttendanceTrendsResponse(BaseResponse):
    data: Optional[AttendanceTrendResult] = None

class GeolocationAnalysisResponse(BaseResponse):
    data: Optional[GeolocationResult] = None

class ClassComparisonResponse(BaseResponse):
    data: Optional[ClassComparisonResult] = None

class AnomaliAbsensiResponse(BaseResponse):
    data: Optional[AnomalyReport] = None

class AnalisisMetodeResponse(BaseResponse):
    data: Optional[MetodeAnalisisResult] = None

class TopSiswaResponse(BaseResponse):
    data: Optional[TopSiswaResult] = None

class StatistikWaktuResponse(BaseResponse):
    data: Optional[TimeStatResult] = None


# ── Report Responses ──────────────────────────────────
class LaporanResponse(BaseResponse):
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_url: Optional[str] = None
    data_ringkasan: Optional[Dict[str, Any]] = None


# ── Kelas List Response ───────────────────────────────
class KelasListResponse(BaseResponse):
    data: List[KelasRead] = []
    total: int = 0


# ── File List Response ────────────────────────────────
class FileItem(BaseModel):
    filename: str
    filepath: str
    size_bytes: Optional[int] = None
    created_at: Optional[datetime] = None
    tipe: Optional[str] = None  # "laporan_kepsek", "surat_peringatan", etc.

class FileListResponse(BaseResponse):
    data: List[FileItem] = []
    total: int = 0
```

---

## 6. WebSocket Models

```python
# ── WebSocket Messages ────────────────────────────────
class WSMessageType(str, Enum):
    CHAT = "chat"
    TYPING = "typing"
    ERROR = "error"
    SYSTEM = "system"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"

class WSIncomingMessage(BaseModel):
    type: WSMessageType = WSMessageType.CHAT
    content: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class WSOutgoingMessage(BaseModel):
    type: WSMessageType
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Optional[Any] = None
    is_final: bool = True  # False jika streaming
    error: Optional[str] = None
```

---

## 7. PDF Generator Models

```python
# ── Surat Peringatan ──────────────────────────────────
class SuratPeringatanData(BaseModel):
    siswa: SiswaRead
    kelas: KelasRead
    sekolah: SekolahInfo
    total_alfa: int
    daftar_tanggal_alfa: List[date]
    tingkat_peringatan: int = 1  # 1, 2, atau 3
    tanggal_surat: date = Field(default_factory=date.today)
    nomor_surat: Optional[str] = None
    nama_wali_kelas: Optional[str] = None
    catatan_tambahan: Optional[str] = None


# ── Laporan Absensi Alfa ──────────────────────────────
class LaporanAlfaData(BaseModel):
    sekolah: SekolahInfo
    kelas: KelasRead
    periode: str
    daftar_siswa_alfa: List[StatistikSiswa]
    total_siswa_bermasalah: int
    tanggal_cetak: date = Field(default_factory=date.today)


# ── Laporan Kepala Sekolah ────────────────────────────
class LaporanKepsekData(BaseModel):
    sekolah: SekolahInfo
    periode: str
    tanggal_cetak: date = Field(default_factory=date.today)
    ringkasan_sekolah: Dict[str, Any]
    data_per_kelas: List[StatistikKelas]
    top_siswa: Optional[List[TopSiswaItem]] = []
    anomali: Optional[List[AnomalyDetail]] = []
    grafik_data: Optional[Dict[str, Any]] = None


# ── Laporan Guru Harian ──────────────────────────────
class LaporanGuruHarianData(BaseModel):
    sekolah: SekolahInfo
    kelas: KelasRead
    tanggal: date
    guru_pengajar: Optional[str] = None
    daftar_absensi: List[AbsensiRead]
    ringkasan: Dict[str, int]  # {"hadir": 28, "alfa": 2, ...}
    catatan: Optional[str] = None


# ── Generic PDF Output ────────────────────────────────
class PDFOutput(BaseModel):
    file_path: str
    file_name: str
    file_size_bytes: Optional[int] = None
    generated_at: datetime = Field(default_factory=datetime.now)
    tipe_laporan: str
```

---

## 8. AI Agent & Tool Models

```python
# ── Tool Definitions ──────────────────────────────────
class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = False
    enum: Optional[List[str]] = None
    default: Optional[Any] = None

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: List[ToolParameter]
    category: Optional[str] = None  # "database", "analysis", "report"


# ── Tool Call & Result ────────────────────────────────
class ToolCall(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    call_id: Optional[str] = None

class ToolResult(BaseModel):
    call_id: Optional[str] = None
    tool_name: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


# ── Agent Interaction ─────────────────────────────────
class AgentInput(BaseModel):
    user_message: str
    session_id: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = []
    context: Optional[Dict[str, Any]] = None
    max_tool_calls: int = 5

class AgentStep(BaseModel):
    step_number: int
    action: str  # "thinking", "tool_call", "response"
    tool_call: Optional[ToolCall] = None
    tool_result: Optional[ToolResult] = None
    reasoning: Optional[str] = None

class AgentOutput(BaseModel):
    response: str
    steps: List[AgentStep] = []
    total_tool_calls: int = 0
    data: Optional[Any] = None
    suggestions: Optional[List[str]] = None
    processing_time_ms: Optional[float] = None


# ── Chat History ──────────────────────────────────────
class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    tool_calls: Optional[List[ToolCall]] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatSession(BaseModel):
    session_id: str
    messages: List[ChatMessage] = []
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    context: Optional[Dict[str, Any]] = None
```

---

## 9. Configuration Models

```python
# ── Database Config ───────────────────────────────────
class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 3306
    username: str
    password: str
    database: str
    pool_size: int = 5
    max_overflow: int = 10

    @property
    def connection_url(self) -> str:
        return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


# ── AI Model Config ───────────────────────────────────
class AIModelConfig(BaseModel):
    model_name: str = "llama3"
    base_url: str = "http://localhost:11434"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = 4096
    timeout_seconds: int = 60
    system_prompt: Optional[str] = None


# ── App Config ────────────────────────────────────────
class AppConfig(BaseModel):
    app_name: str = "Sistem Absensi Sekolah"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = ["*"]
    pdf_output_dir: str = "./pdfs"
    max_upload_size_mb: int = 10
    database: DatabaseConfig
    ai_model: AIModelConfig
    sekolah: SekolahInfo
```

---

## Ringkasan Arsitektur Model

| Layer | Jumlah Model | Fungsi Utama |
|---|---|---|
| **Base & Utility** | 4 | Fondasi response, pagination, error handling |
| **Entity / Domain** | 12 | Representasi data database (siswa, kelas, absensi) |
| **Statistik & Analisis** | 15 | Hasil perhitungan, trend, anomaly, perbandingan |
| **API Request** | 12 | Validasi input setiap endpoint |
| **API Response** | 10 | Struktur output konsisten untuk semua endpoint |
| **WebSocket** | 3 | Validasi pesan real-time chat AI |
| **PDF Generator** | 5 | Data terstruktur untuk setiap jenis laporan |
| **AI Agent & Tool** | 8 | Orkestrasi tool calling dan chat history |
| **Configuration** | 3 | Validasi konfigurasi sistem saat startup |

Rancangan ini mencakup **~72 model** yang saling terhubung dan mencakup seluruh alur data dalam sistem — dari input user, proses AI, query database, hingga output PDF dan response API.

