import os
from services.transcription import transcription_service
from services.diarization import get_diarization_service
from services.merge import merge_segments

class JobManager:
    def __init__(self):
        # Transciption initialized globally to save load time
        self.transcription = transcription_service
        # Diarization lazy loaded or initialized here
        self.diarization = get_diarization_service()
        
    def process_request(self, file_path: str, num_speakers: int = None, language: str = None):
        """
        Orchestrates the entire diarization & transcription workflow.
        """
        print(f"JobManager: Starting processing for {file_path}")
        
        # 1. Transcribe the audio
        print("JobManager: 1/3 Starting Transcription...")
        t_segments, full_text = self.transcription.transcribe(file_path, language)
        
        # 2. Diarize the audio (if token is available)
        final_segments = t_segments
        if self.diarization.pipeline:
            print("JobManager: 2/3 Starting Diarization...")
            try:
                d_segments = self.diarization.diarize(file_path, num_speakers)
                print("JobManager: 3/3 Merging Segments...")
                final_segments = merge_segments(d_segments, t_segments)
            except Exception as e:
                print(f"JobManager: Diarization failed ({e}). Falling back to regular transcription.")
        else:
            print("JobManager: Skipping Diarization (No Pipeline or Error)")
            
        return final_segments, full_text

job_manager = JobManager()
