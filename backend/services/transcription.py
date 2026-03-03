from faster_whisper import WhisperModel
import os

class TranscriptionService:
    def __init__(self, model_size="tiny", device="cpu", compute_type="int8"):
        """
        Initializes the faster-whisper model.
        For Phase 2 testing, we use 'tiny' and 'cpu' to ensure it runs anywhere quickly.
        In production, this should be configurable (e.g., 'base', 'cuda', 'float16').
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None

    def load_model(self):
        """Loads the faster-whisper model into memory."""
        if self.model is not None:
            return # Already loaded
            
        print(f"Loading Whisper model '{self.model_size}' on {self.device} into memory...")
        self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        print("Whisper model loaded successfully.")

    def unload_model(self):
        """Forces the model out of memory and clears caches."""
        if self.model is not None:
            print("Unloading Whisper model from memory...")
            del self.model
            self.model = None
            
        import gc
        gc.collect()
        # Even if CPU, try to clear CUDA if it exists to be completely safe
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                print("CUDA cache cleared after Whisper unload.")
        except ImportError:
            pass

    def transcribe(self, file_path: str, language: str = None):
        """
        Transcribes an audio file.
        Returns a generator of segments.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
            
        if not self.model:
            raise RuntimeError("Whisper model is not loaded. Call load_model() first.")
            
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
