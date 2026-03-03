from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import TranscriptionRequest, TranscriptionResponse
from job_manager import job_manager
import os

app = FastAPI(title="Diarization & Transcription API")

# Setup CORS for Electron frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Backend API is running"}

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(request: TranscriptionRequest):
    try:
        # We need an absolute path to the audio file
        if not os.path.isabs(request.file_path):
            raise HTTPException(status_code=400, detail="file_path must be an absolute path")
            
        segments, full_text = job_manager.process_request(
            file_path=request.file_path, 
            num_speakers=request.num_speakers if request.num_speakers > 0 else None,
            language=request.language if request.language != "auto" else None,
            hf_token=request.hf_token
        )
        
        return TranscriptionResponse(
            segments=segments,
            full_text=full_text
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
