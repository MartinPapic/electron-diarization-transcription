from faster_whisper import WhisperModel
import os

class TranscriptionService:
    def __init__(self, model_size="tiny", device="cpu", compute_type="int8"):
        """
        Initializes the faster-whisper model.
        For Phase 2 testing, we use 'tiny' and 'cpu' to ensure it runs anywhere quickly.
        In production, this should be configurable (e.g., 'base', 'cuda', 'float16').
        """
        print(f"Loading Whisper model '{model_size}' on {device}...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print("Whisper model loaded successfully.")

    def transcribe(self, file_path: str, language: str = None):
        """
        Transcribes an audio file.
        Returns a generator of segments.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
            
        print(f"Starting transcription for {file_path}...")
        segments, info = self.model.transcribe(file_path, beam_size=5, language=language)
        
        print(f"Detected language '{info.language}' with probability {info.language_probability}")
        
        result_segments = []
        full_text = ""
        
        for segment in segments:
            # We don't have speaker info yet (that's for pyannote)
            # So we assign a default speaker "UNKNOWN" for now
            seg_data = {
                "start": segment.start,
                "end": segment.end,
                "speaker": "UNKNOWN", 
                "text": segment.text.strip()
            }
            result_segments.append(seg_data)
            full_text += segment.text + " "
            
        return result_segments, full_text.strip()

# Singleton instance for the app
transcription_service = TranscriptionService()
