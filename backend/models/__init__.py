from typing import List
from pydantic import BaseModel

class TranscriptionRequest(BaseModel):
    file_path: str
    num_speakers: int = 1
    language: str = "es"

class Segment(BaseModel):
    start: float
    end: float
    speaker: str
    text: str

class TranscriptionResponse(BaseModel):
    segments: List[Segment]
    full_text: str
