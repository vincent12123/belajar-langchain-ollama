from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import os
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
    expose_headers=["X-Vercel-AI-Data-Stream"],
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

class AnomaliAbsensiRequest(BaseModel):
    kelas_id: Optional[int] = None
    nama_kelas: Optional[str] = None
    tanggal_mulai: Optional[str] = None
    tanggal_akhir: Optional[str] = None

class AnalisisMetodeAbsenRequest(BaseModel):
    kelas_id: Optional[int] = None
    nama_kelas: Optional[str] = None
    tanggal_mulai: Optional[str] = None
    tanggal_akhir: Optional[str] = None

class TopSiswaRequest(BaseModel):
    kelas_id: Optional[int] = None
    nama_kelas: Optional[str] = None
    tanggal_mulai: Optional[str] = None
    tanggal_akhir: Optional[str] = None
    status: Optional[str] = "Alfa"
    limit: Optional[int] = 10

class StatistikWaktuRequest(BaseModel):
    kelas_id: Optional[int] = None
    nama_kelas: Optional[str] = None
    tanggal_mulai: Optional[str] = None
    tanggal_akhir: Optional[str] = None
    jam_telat: Optional[str] = "07:15:00"
    limit: Optional[int] = 10

# Import your existing functions
try:
    from agent import run_agent, run_agent_with_history
    from db_functions import (
        cari_siswa,
        get_absensi_by_siswa,
        get_attendance_trends,
        get_geolocation_analysis,
        compare_class_attendance,
        get_anomali_absensi,
        get_analisis_metode_absen,
        get_top_siswa_absensi,
        get_statistik_waktu_absen,
    )
    BACKEND_READY = True
except ImportError as e:
    logger.warning(f"Backend modules not available: {e}")
    BACKEND_READY = False

@app.get("/")
def read_root():
    return {"status": "online", "message": "Server Absensi AI siap. Gunakan endpoint /chat untuk bertanya."}


@app.post("/api/chat")
async def chat_ai_sdk(request: Request):
    """
    Endpoint compatible with Vercel AI SDK useChat hook.
    Receives messages in AI SDK format, returns plain text stream.
    """
    if not BACKEND_READY:
        raise HTTPException(status_code=503, detail="Backend services not available")

    try:
        data = await request.json()
        messages = data.get("messages", [])

        # Extract last user message (support both AI SDK v4 and v5 formats)
        last_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                # AI SDK v5+ uses 'parts' format
                parts = msg.get("parts", [])
                if parts:
                    text_parts = [p.get("text", "") for p in parts if p.get("type") == "text"]
                    last_message = " ".join(filter(None, text_parts))
                # AI SDK v4 or fallback to 'content'
                if not last_message:
                    last_message = msg.get("content", "")
                break

        if not last_message:
            raise HTTPException(status_code=400, detail="No user message found")

        # Build chat history from previous messages (exclude the last user message)
        chat_history = []
        for msg in messages:
            role = msg.get("role", "")
            if role not in ("user", "assistant"):
                continue
            # Extract text content
            content = ""
            parts = msg.get("parts", [])
            if parts:
                text_parts = [p.get("text", "") for p in parts if p.get("type") == "text"]
                content = " ".join(filter(None, text_parts))
            if not content:
                content = msg.get("content", "")
            if content:
                chat_history.append({"role": role, "content": content})
        
        # Remove the last user message from history (it will be passed separately)
        if chat_history and chat_history[-1]["role"] == "user":
            chat_history = chat_history[:-1]

        logger.info(f"AI SDK chat request: {last_message[:100]}... (history: {len(chat_history)} msgs)")

        # Run agent with history in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, run_agent_with_history, last_message, chat_history
        )

        # Return as plain text stream (for TextStreamChatTransport)
        async def generate():
            yield result

        return StreamingResponse(
            generate(),
            media_type="text/plain",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI SDK chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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

@app.post("/api/anomali/absensi")
async def get_anomali_absensi_api(request: AnomaliAbsensiRequest):
    """Get anomaly analysis for attendance"""
    if not BACKEND_READY:
        raise HTTPException(status_code=503, detail="Backend services not available")

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            get_anomali_absensi,
            request.kelas_id,
            request.nama_kelas,
            request.tanggal_mulai,
            request.tanggal_akhir
        )
        return result
    except Exception as e:
        logger.error(f"Anomali absensi error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analisis/metode")
async def get_analisis_metode_api(request: AnalisisMetodeAbsenRequest):
    """Get analysis of attendance methods"""
    if not BACKEND_READY:
        raise HTTPException(status_code=503, detail="Backend services not available")

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            get_analisis_metode_absen,
            request.kelas_id,
            request.nama_kelas,
            request.tanggal_mulai,
            request.tanggal_akhir
        )
        return result
    except Exception as e:
        logger.error(f"Analisis metode error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/top/siswa")
async def get_top_siswa_api(request: TopSiswaRequest):
    """Get top students based on attendance status"""
    if not BACKEND_READY:
        raise HTTPException(status_code=503, detail="Backend services not available")

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            get_top_siswa_absensi,
            request.kelas_id,
            request.nama_kelas,
            request.tanggal_mulai,
            request.tanggal_akhir,
            request.status,
            request.limit
        )
        return result
    except Exception as e:
        logger.error(f"Top siswa error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ── Missing endpoints for frontend api.js ──

@app.get("/api/students/search")
async def search_students_api(name: str):
    """Search students by name"""
    if not BACKEND_READY:
        raise HTTPException(status_code=503, detail="Backend services not available")

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, cari_siswa, name)
        return result
    except Exception as e:
        logger.error(f"Student search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/students/{student_id}/attendance")
async def get_student_attendance_api(student_id: int, start_date: str = None, end_date: str = None):
    """Get attendance data for specific student"""
    if not BACKEND_READY:
        raise HTTPException(status_code=503, detail="Backend services not available")

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            get_absensi_by_siswa,
            student_id,
            None,
            start_date,
            end_date
        )
        return result
    except Exception as e:
        logger.error(f"Student attendance error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/statistik/waktu")
async def get_statistik_waktu_api(request: StatistikWaktuRequest):
    """Get attendance time statistics"""
    if not BACKEND_READY:
        raise HTTPException(status_code=503, detail="Backend services not available")

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            get_statistik_waktu_absen,
            request.kelas_id,
            request.nama_kelas,
            request.tanggal_mulai,
            request.tanggal_akhir,
            request.jam_telat,
            request.limit
        )
        return result
    except Exception as e:
        logger.error(f"Statistik waktu error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        await websocket.send_text(f"Connected to EduAttendAI as {client_id}")
        while True:
            data = await websocket.receive_text()
            
            # Proses pesan menggunakan AI Agent
            if BACKEND_READY:
                # Gunakan executor agar tidak memblokir event loop async
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, run_agent, data)
                await websocket.send_text(response)
            else:
                await websocket.send_text("Maaf, layanan backend AI sedang tidak tersedia.")
                
    except WebSocketDisconnect:
        logger.info(f"Client #{client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_text(f"Error: {str(e)}")
        except:
            pass


# ── File download endpoint for generated PDFs ──
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

@app.get("/files")
def list_files():
    """List available files in the output directory."""
    if not os.path.exists(OUTPUT_DIR):
        return {"files": []}
    files = [f for f in os.listdir(OUTPUT_DIR) if os.path.isfile(os.path.join(OUTPUT_DIR, f))]
    return {"files": files}

@app.get("/download/{filename}")
def download_file(filename: str):
    """Download a generated file (PDF, etc.) from the output directory."""
    # Sanitize: prevent path traversal
    safe_name = os.path.basename(filename)
    filepath = os.path.join(OUTPUT_DIR, safe_name)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File '{safe_name}' not found")
    return FileResponse(
        path=filepath,
        filename=safe_name,
        media_type="application/octet-stream",
    )

if __name__ == "__main__":
    import uvicorn
    # Jalankan dengan: python api.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
