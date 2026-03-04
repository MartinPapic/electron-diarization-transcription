import os
import torch
import torchaudio

import sys
import types

# Monkey-patch para retrocompatibilidad con Pyannote y Speechbrain en torchaudio >= 2.1.0
class DummyAudioMetaData:
    def __init__(self, sample_rate=16000, num_frames=0, num_channels=1, bits_per_sample=16, encoding='PCM_S'):
        self.sample_rate = sample_rate
        self.num_frames = num_frames
        self.num_channels = num_channels
        self.bits_per_sample = bits_per_sample
        self.encoding = encoding

def custom_torchaudio_info(uri, *args, **kwargs):
    import soundfile
    try:
        if isinstance(uri, str):
            info = soundfile.info(uri)
            return DummyAudioMetaData(
                sample_rate=info.samplerate,
                num_frames=info.frames,
                num_channels=info.channels,
                encoding=info.subtype
            )
    except Exception:
        pass
    return DummyAudioMetaData()

setattr(torchaudio, "info", custom_torchaudio_info)
setattr(torchaudio, "AudioMetaData", DummyAudioMetaData)

if 'torchaudio.backend' not in sys.modules:
    virtual_backend = types.ModuleType('torchaudio.backend')
    setattr(virtual_backend, 'common', types.ModuleType('torchaudio.backend.common'))
    setattr(virtual_backend.common, 'AudioMetaData', DummyAudioMetaData)
    sys.modules['torchaudio.backend'] = virtual_backend
    sys.modules['torchaudio.backend.common'] = virtual_backend.common
    setattr(torchaudio, 'backend', virtual_backend)

if not hasattr(torchaudio, "list_audio_backends"):
    torchaudio.list_audio_backends = lambda: ["soundfile", "sox_io"]
if not hasattr(torchaudio, "get_audio_backend"):
    torchaudio.get_audio_backend = lambda: "soundfile"
if not hasattr(torchaudio, "set_audio_backend"):
    torchaudio.set_audio_backend = lambda x: None

if hasattr(torchaudio, 'USE_TORCHCODEC'):
    torchaudio.USE_TORCHCODEC = False
else:
    os.environ['TORCHAUDIO_USE_TORCHCODEC'] = '0'

import soundfile
def custom_torchaudio_load(uri, frame_offset=0, num_frames=-1, normalize=True, channels_first=True, format=None, buffer_size=4096, backend=None):
    data, sample_rate = soundfile.read(uri, dtype='float32', always_2d=True)
    tensor = torch.from_numpy(data)
    if channels_first:
        tensor = tensor.t()
        
    start = max(0, frame_offset)
    if num_frames == -1:
        tensor = tensor[:, start:]
    else:
        tensor = tensor[:, start:start + num_frames]
        
    return tensor, sample_rate

torchaudio.load = custom_torchaudio_load

from pyannote.audio import Pipeline

class DiarizationService:
    def __init__(self, auth_token=None):
        """
        Initializes the pyannote.audio diarization pipeline.
        Requires a HuggingFace auth token.
        """
        self.auth_token = auth_token or os.environ.get("HF_AUTH_TOKEN")
        self.pipeline = None

    def load_model(self):
        """Loads the pyannote pipeline into memory."""
        if self.pipeline is not None:
            return # Already loaded
            
        if not self.auth_token:
            print("WARNING: No HF_AUTH_TOKEN provided. Diarization will fail.")
            return

        print("Loading Pyannote diarization pipeline into memory...")
        try:
            # PyTorch 2.6 security patch for weights_only=True
            try:
                from torch.serialization import add_safe_globals
                from torch.torch_version import TorchVersion
                safe_classes = [TorchVersion]
                
                try:
                    import pyannote.audio.core.task as patask
                    for cls_name in ["Specifications", "Problem", "Resolution", "Timing"]:
                        if hasattr(patask, cls_name):
                            safe_classes.append(getattr(patask, cls_name))
                except ImportError as e:
                    print("Debug: Failed to import pyannote.audio.core.task:", e)
                    
                try:
                    from pytorch_lightning.callbacks.model_checkpoint import ModelCheckpoint
                    safe_classes.append(ModelCheckpoint)
                except ImportError:
                    pass
                
                add_safe_globals(safe_classes)
            except Exception as import_err:
                print("Nota: No se pudo habilitar safe_globals (ignorar si PyTorch < 2.6):", import_err)

            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.auth_token
            )
            if self.pipeline is None:
                # Esto ocurre si el token es válido pero no se aceptaron los términos en HF
                print("FAILED: Pipeline.from_pretrained returned None.")
                return
            print("Pyannote pipeline loaded successfully.")
        except Exception as e:
            print(f"Failed to load Pyannote pipeline: {e}")
            self.pipeline = None
            # Re-lanzar para que JobManager sepa que la carga con token falló intencionalmente
            if self.auth_token:
                raise RuntimeError(f"Error al cargar el modelo de diarización (¿Aceptaste los términos en HuggingFace?): {str(e)}")

    def unload_model(self):
        """Forces the model out of memory and clears caches."""
        if self.pipeline is not None:
            print("Unloading Pyannote pipeline from memory...")
            del self.pipeline
            self.pipeline = None
            
        import gc
        import torch
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print("CUDA cache cleared after Pyannote unload.")

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
