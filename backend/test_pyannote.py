import sys
import types
import torchaudio

class DummyAudioMetaData:
    def __init__(self, sample_rate=16000, num_frames=0, num_channels=1, bits_per_sample=16, encoding='PCM_S'):
        self.sample_rate = sample_rate
        self.num_frames = num_frames
        self.num_channels = num_channels
        self.bits_per_sample = bits_per_sample
        self.encoding = encoding

def custom_torchaudio_info(uri, *args, **kwargs):
    import soundfile
    
    # torchaudio.info sometimes receives file-like objects or strings
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

if hasattr(torchaudio, 'USE_TORCHCODEC'):
    torchaudio.USE_TORCHCODEC = False
else:
    import os
    os.environ['TORCHAUDIO_USE_TORCHCODEC'] = '0'

import soundfile
import torch

def custom_torchaudio_load(uri, frame_offset=0, num_frames=-1, normalize=True, channels_first=True, format=None, buffer_size=4096, backend=None):
    # Pyannote chunking relies heavily on exact num_frames slice semantics
    data, sample_rate = soundfile.read(uri, dtype='float32', always_2d=True)
    tensor = torch.from_numpy(data)
    
    if channels_first:
        tensor = tensor.t()
        
    start = max(0, frame_offset)
    if num_frames == -1:
        tensor = tensor[:, start:]
    else:
        tensor = tensor[:, start:start + num_frames]
        
    print(f"[DEBUG load] uri={str(uri)[-20:]} offset={frame_offset} num_frames={num_frames} sr={sample_rate} -> shape={tensor.shape}")
    return tensor, sample_rate

torchaudio.load = custom_torchaudio_load

sys.path.insert(0, ".") # To ensure we can import from backend services
import traceback

print("Starting custom diagnostic script to test pyannote pipeline loading...")

try:
    from services.diarization import DiarizationService
except ImportError as e:
    print(f"Failed to import DiarizationService: {e}")
    sys.exit(1)

# Initialize service (it will pull HF_AUTH_TOKEN from env or require it)
service = DiarizationService()

if not service.auth_token:
    print("WARNING: HF_AUTH_TOKEN is not set in the environment.")
    print("Please run this script with your token, e.g.:")
    print("  $env:HF_AUTH_TOKEN=\"your_token\"; python test_pyannote.py")
    sys.exit(1)

print("Attempting to load the pyannote pipeline...")
try:
    service.load_model()
    if service.pipeline is not None:
        print("✅ SUCCESS: Pyannote pipeline loaded successfully! The weights_only error is fixed.")
        import os
        if os.path.exists('dummy.wav'):
            print("Attempting to run diarization on dummy.wav...")
            res = service.diarize('dummy.wav')
            print(f"✅ SUCCESS: Diarization complete. Found {len(res)} segments.")
        else:
            print("⚠️ WARNING: dummy.wav not found, skipping diarization test.")
    else:
        print("❌ FAILED: Pipeline is None. Did you accept the HF terms?")
except Exception as e:
    print(f"❌ ERROR loading or running pipeline: {e}")
    traceback.print_exc()
