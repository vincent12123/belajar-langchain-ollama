# models/__init__.py
# Arsitektur Pydantic Models untuk Sistem Manajemen Absensi Sekolah
#
# Package ini berisi ~72 model yang mencakup seluruh layer aplikasi:
#   - enums      : Enum types (StatusAbsensi, MetodeAbsensi, dll)
#   - base       : Base response, pagination, error handling
#   - entities   : Domain models (Siswa, Kelas, Absensi, dll)
#   - statistics : Statistik, analisis, trend, anomali
#   - requests   : Validasi input API endpoints
#   - responses  : Struktur output API endpoints
#   - websocket  : Model pesan WebSocket
#   - pdf        : Data terstruktur untuk PDF generator
#   - agent      : AI agent, tool calling, chat history
#   - config     : Validasi konfigurasi sistem

from models.enums import *
from models.base import *
from models.entities import *
from models.statistics import *
from models.requests import *
from models.responses import *
from models.websocket import *
from models.pdf import *
from models.agent import *
