import os
import tempfile
from pydub import AudioSegment
from services.transcription import transcription_service
from services.diarization import get_diarization_service

class JobManager:
    def __init__(self):
        # We don't load models here anymore. They stay in disk until needed.
        self.transcription = transcription_service
        self.diarization = get_diarization_service()
        
    def process_request(self, file_path: str, num_speakers: int = None, language: str = None):
        """
        Orchestrates the entire diarization & transcription workflow 
        using the Diarize -> Slice -> Transcribe pattern.
        """
        print(f"JobManager: Starting processing for {file_path}")
        
        final_segments = []
        full_text = ""
        
        # 1. Diarization (Find when people are talking)
        # Load diarization model only
        self.diarization.load_model()
        
        if self.diarization.pipeline:
            print("JobManager: 1/3 Starting Diarization...")
            try:
                base_segments = self.diarization.diarize(file_path, num_speakers)
            except Exception as e:
                print(f"JobManager: Diarization failed ({e}). Falling back to whole-file transcription.")
                base_segments = [{"start": 0.0, "end": float('inf'), "speaker": "UNKNOWN"}]
        else:
            print("JobManager: 1/3 Skipping Diarization (No Pipeline or Error). Defaulting to whole-file.")
            base_segments = [{"start": 0.0, "end": float('inf'), "speaker": "UNKNOWN"}]
            
        # IMPORTANT: Force unload Pyannote to free RAM/VRAM before loading Whisper
        self.diarization.unload_model()

        # 2. Slice and Transcribe
        print("JobManager: 2/3 Slicing and Transcribing...")
        try:
            audio = AudioSegment.from_file(file_path)
            audio_duration_ms = len(audio)
        except Exception as e:
             raise RuntimeError(f"Could not load audio file with pydub: {str(e)}")

        temp_dir = tempfile.mkdtemp()
        
        # Load Transcription model only after Diarization is completely wiped from RAM
        self.transcription.load_model()
        
        try:
            for i, seg in enumerate(base_segments):
                # Pyannote times are in seconds, pydub uses milliseconds
                start_ms = int(seg["start"] * 1000)
                # Handle the fallback case where end is infinity
                end_ms = int(seg["end"] * 1000) if seg["end"] != float('inf') else audio_duration_ms
                
                # Prevent negative or out-of-bounds slicing
                start_ms = max(0, start_ms)
                end_ms = min(end_ms, audio_duration_ms)
                
                # Slicing
                chunk = audio[start_ms:end_ms]
                chunk_path = os.path.join(temp_dir, f"chunk_{i}.wav")
                chunk.export(chunk_path, format="wav")
                
                # Transcribe this specific chunk
                print(f"Transcribing segment {i+1}/{len(base_segments)} ({seg['start']:.2f}s - {seg['end']:.2f}s)...")
                # We expect the transcription service to return the text.
                # Since the transcription service itself returns its own segments based on the chunk,
                # we just need the full text for this chunk.
                _, chunk_text = self.transcription.transcribe(chunk_path, language)
                
                if chunk_text.strip():
                    final_segments.append({
                        "start": seg["start"],
                        "end": seg["end"] if seg["end"] != float('inf') else audio_duration_ms / 1000.0,
                        "speaker": seg["speaker"],
                        "text": chunk_text.strip()
                    })
                    full_text += chunk_text.strip() + " "
                    
        finally:
            print("JobManager: 3/3 Cleaning up temporary files and unloading models...")
            # Unload Whisper model strictly to preserve memory for the OS
            self.transcription.unload_model()
            
            # Clean up temp files
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
            
        return final_segments, full_text.strip()

job_manager = JobManager()
