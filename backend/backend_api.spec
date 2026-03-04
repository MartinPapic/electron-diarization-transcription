# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules
import os

monkey_patch = """
import sys
import types
import torchaudio

# Crear modulo virtual torchaudio.backend
if 'torchaudio.backend' not in sys.modules:
    dummy_backend = types.ModuleType('torchaudio.backend')
    sys.modules['torchaudio.backend'] = dummy_backend
    torchaudio.backend = dummy_backend

if 'torchaudio.backend.common' not in sys.modules:
    dummy_common = types.ModuleType('torchaudio.backend.common')
    sys.modules['torchaudio.backend.common'] = dummy_common
    torchaudio.backend.common = dummy_common

# Inyectar clase AudioMetaData faltante para pyannote/speechbrain
class DummyAudioMetaData:
    def __init__(self, sample_rate=16000, num_frames=0, num_channels=1, bits_per_sample=16, encoding="PCM_S"):
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

if not hasattr(torchaudio, 'AudioMetaData'):
    torchaudio.AudioMetaData = DummyAudioMetaData
if not hasattr(torchaudio.backend.common, 'AudioMetaData'):
    torchaudio.backend.common.AudioMetaData = DummyAudioMetaData

# Inyectar funciones faltantes de torchaudio en las versiones > 2.1.0
if not hasattr(torchaudio, 'set_audio_backend'):
    torchaudio.set_audio_backend = lambda x: None
if not hasattr(torchaudio, 'get_audio_backend'):
    torchaudio.get_audio_backend = lambda: "soundfile"
if not hasattr(torchaudio, 'list_audio_backends'):
    torchaudio.list_audio_backends = lambda: ["soundfile", "sox_io"]
if not hasattr(torchaudio, 'info'):
    torchaudio.info = custom_torchaudio_info

# Deshabilitar torchcodec para forzar el uso de soundfile en pyannote
if hasattr(torchaudio, 'USE_TORCHCODEC'):
    torchaudio.USE_TORCHCODEC = False
else:
    # Fuerza la bandera si torchaudio la busca dinamicamente
    import os
    os.environ['TORCHAUDIO_USE_TORCHCODEC'] = '0'

import soundfile
import torch
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
    except ImportError:
        pass
        
    try:
        from pytorch_lightning.callbacks.model_checkpoint import ModelCheckpoint
        safe_classes.append(ModelCheckpoint)
    except ImportError:
        pass
    
    add_safe_globals(safe_classes)
except Exception:
    pass
"""
with open('app_entry.py', 'w') as f:
    f.write(monkey_patch + open('main.py').read())


datas = []
binaries = []
hiddenimports = []
tmp_ret = collect_all('faster_whisper')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pyannote.audio')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pyannote.core')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pyannote.metrics')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pyannote.pipeline')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('torch')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('torchaudio')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('torchvision')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('speechbrain')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('audioop')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pydub')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('lightning_fabric')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pytorch_lightning')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pytorch_metric_learning')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Explicitly add local application modules as hidden imports
hiddenimports += [
    'audioop',
    'job_manager',
    'api',
    'api.__init__',
    'models',
    'models.__init__',
    'services',
    'services.__init__',
    'services.diarization',
    'services.transcription',
    'asteroid_filterbanks',
    'asteroid_filterbanks.encoders',
    'asteroid_filterbanks.filters',
    'huggingface_hub',
    'speechbrain.lobes.models.huggingface_transformers.huggingface',
    'soundfile',
]

# Get the absolute path to the backend directory
backend_dir = os.path.abspath('.')

a = Analysis(
    ['app_entry.py'],
    pathex=[backend_dir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='backend_api',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='backend_api',
)
