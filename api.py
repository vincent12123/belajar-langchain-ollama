from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import run_agent

app = FastAPI(
    title="Sistem Absensi Sekolah API",
    description="API untuk mengakses agent AI absensi",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    query: str
    model: str = None  # Optional, will use default if None

class QueryResponse(BaseModel):
    answer: str

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

if __name__ == "__main__":
    import uvicorn
    # Jalankan dengan: python api.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
