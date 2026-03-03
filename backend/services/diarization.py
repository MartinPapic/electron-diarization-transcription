from pyannote.audio import Pipeline
import os

class DiarizationService:
    def __init__(self, auth_token=None):
        """
        Initializes the pyannote.audio diarization pipeline.
        Requires a HuggingFace auth token.
        """
        self.auth_token = auth_token or os.environ.get("HF_AUTH_TOKEN")
        
        if not self.auth_token:
            print("WARNING: No HF_AUTH_TOKEN provided. Diarization will fail.")
            self.pipeline = None
        else:
            print("Loading Pyannote diarization pipeline...")
            try:
                self.pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=self.auth_token
                )
                print("Pyannote pipeline loaded successfully.")
            except Exception as e:
                print(f"Failed to load Pyannote pipeline: {e}")
                self.pipeline = None

    def diarize(self, file_path: str, num_speakers: int = None):
        """
        Diarizes the audio file and returns a list of segments with speaker labels.
        """
        if not self.pipeline:
            raise RuntimeError("Diarization pipeline is not initialized. Check HF_AUTH_TOKEN.")
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
            
        print(f"Starting diarization for {file_path}...")
        
        diarization = self.pipeline(file_path, num_speakers=num_speakers)
        
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })
            
        return segments

# Expose a singleton-like instance creation function
def get_diarization_service(auth_token=None):
    return DiarizationService(auth_token)
