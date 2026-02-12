from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sistem Absensi Sekolah API",
    description="API untuk mengakses agent AI absensi",
    version="1.0.0"
)

# Configure CORS to allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class QueryRequest(BaseModel):
    query: str
    model: Optional[str] = None  # Optional, will use default if None

class QueryResponse(BaseModel):
    answer: str

# Models for new endpoints
class AttendanceTrendsRequest(BaseModel):
    siswa_id: Optional[int] = None
    nama_siswa: Optional[str] = None
    kelas_id: Optional[int] = None
    nama_kelas: Optional[str] = None
    months: Optional[int] = 6

class GeolocationAnalysisRequest(BaseModel):
    kelas_id: Optional[int] = None
    nama_kelas: Optional[str] = None
    tanggal: Optional[str] = None

class ClassComparisonRequest(BaseModel):
    tingkat: Optional[int] = None
    jurusan: Optional[str] = None

# Import your existing functions
try:
    from agent import run_agent
    from db_functions import (
        get_attendance_trends,
        get_geolocation_analysis,
        compare_class_attendance
    )
    BACKEND_READY = True
except ImportError as e:
    logger.warning(f"Backend modules not available: {e}")
    BACKEND_READY = False

@app.get("/")
def read_root():
    return {"status": "online", "message": "Server Absensi AI siap. Gunakan endpoint /chat untuk bertanya."}

@app.post("/chat", response_model=QueryResponse)
def chat_endpoint(request: QueryRequest):
    """
    Endpoint utama untuk mengirim pertanyaan ke AI Agent.
    """
    try:
        # Panggil fungsi run_agent
        jawaban = run_agent(request.query, request.model)
        return QueryResponse(answer=jawaban)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New endpoints for React frontend
@app.post("/api/attendance/trends")
async def get_attendance_trends_api(request: AttendanceTrendsRequest):
    """Get attendance trends for student or class"""
    if not BACKEND_READY:
        raise HTTPException(status_code=503, detail="Backend services not available")

    try:
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            get_attendance_trends,
            request.siswa_id,
            request.nama_siswa,
            request.kelas_id,
            request.nama_kelas,
            request.months
        )
        return result
    except Exception as e:
        logger.error(f"Attendance trends error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/geolocation/analysis")
async def get_geolocation_analysis_api(request: GeolocationAnalysisRequest):
    """Get geolocation analysis for attendance validation"""
    if not BACKEND_READY:
        raise HTTPException(status_code=503, detail="Backend services not available")

    try:
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            get_geolocation_analysis,
            request.kelas_id,
            request.nama_kelas,
            request.tanggal
        )
        return result
    except Exception as e:
        logger.error(f"Geolocation analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/class/comparison")
async def compare_class_attendance_api(request: ClassComparisonRequest):
    """Compare attendance rates between classes"""
    if not BACKEND_READY:
        raise HTTPException(status_code=503, detail="Backend services not available")

    try:
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            compare_class_attendance,
            request.tingkat,
            request.jurusan
        )
        return result
    except Exception as e:
        logger.error(f"Class comparison error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Jalankan dengan: python api.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
