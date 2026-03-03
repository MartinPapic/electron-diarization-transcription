# 🎙️ Desktop Transcription App (Electron + Pyannote + Whisper)

Aplicación desktop para **diarización y transcripción automática de
audio** utilizando arquitectura **MVVM** y procesamiento 100% local.

------------------------------------------------------------------------

# 🧠 Descripción General

La aplicación permite:

-   Diarizar hablantes en un archivo de audio\
-   Transcribir cada segmento identificado\
-   Asociar texto a cada hablante con timestamps\
-   Exportar resultados en múltiples formatos

### Arquitectura

Electron + React (MVVM) + FastAPI + pyannote.audio + faster-whisper

Todo el procesamiento se realiza localmente.

------------------------------------------------------------------------

# 🏗 Arquitectura General

## Component Diagram

``` mermaid
flowchart LR

subgraph Desktop_App
    View[TranscriptionView\n(React)]
    ViewModel[TranscriptionViewModel\n(TypeScript)]
    IPC[Electron IPC]
end

subgraph Backend_Python
    API[FastAPI API]
    JobManager[Job Manager]
    Diarization[DiarizationService\npyannote.audio]
    Transcription[TranscriptionService\nfaster-whisper]
    Merge[MergeService]
end

View --> ViewModel
ViewModel --> IPC
IPC --> API

API --> JobManager
JobManager --> Diarization
JobManager --> Transcription
Diarization --> Merge
Transcription --> Merge

Merge --> API
API --> ViewModel
ViewModel --> View
```

------------------------------------------------------------------------

# 🧩 Patrón Arquitectónico: MVVM

## Frontend

-   **View (React)** → Renderiza estado\
-   **ViewModel (TypeScript)** → Maneja estado y lógica de UI\
-   **Model (Backend API)** → Procesamiento ML

## Backend

Separación por servicios:

-   DiarizationService\
-   TranscriptionService\
-   MergeService\
-   JobManager

------------------------------------------------------------------------

# 📐 UML -- Backend

``` mermaid
classDiagram

class TranscriptionRequest {
    +file_path: str
    +num_speakers: int
    +language: str
}

class TranscriptionResponse {
    +segments: List~Segment~
    +full_text: str
}

class Segment {
    +start: float
    +end: float
    +speaker: str
    +text: str
}

class DiarizationService {
    -pipeline
    +diarize(file_path, num_speakers)
}

class TranscriptionService {
    -model
    +transcribe_segment(waveform)
}

class MergeService {
    +merge_segments(List~Segment~)
}

class JobManager {
    +process(request)
}

JobManager --> DiarizationService
JobManager --> TranscriptionService
JobManager --> MergeService
JobManager --> TranscriptionRequest
JobManager --> TranscriptionResponse
```

------------------------------------------------------------------------

# 🖥 UML -- Frontend

``` mermaid
classDiagram

class TranscriptionView {
    +render()
    +onUpload()
}

class TranscriptionViewModel {
    +segments
    +fullText
    +isProcessing
    +process(file)
}

class ApiService {
    +upload(file)
}

TranscriptionView --> TranscriptionViewModel
TranscriptionViewModel --> ApiService
```

------------------------------------------------------------------------

# 🎯 Requerimientos Funcionales

## Procesamiento

-   **RF1:** Cargar archivos WAV, MP3 o M4A.\
-   **RF2:** Permitir definir número de hablantes.\
-   **RF3:** Realizar diarización.\
-   **RF4:** Transcribir cada segmento.\
-   **RF5:** Asociar texto a hablante con timestamps.

## Exportación

-   **RF6:** Exportar en TXT.\
-   **RF7:** Exportar en SRT.\
-   **RF8:** Exportar en JSON.\
-   **RF9:** Copiar texto completo al portapapeles.

## Visualización

-   **RF10:** Mostrar progreso en tiempo real.\
-   **RF11:** Visualizar segmentos por hablante.\
-   **RF12:** Permitir renombrar hablantes manualmente.

## Configuración

-   **RF13:** Seleccionar modelo Whisper.\
-   **RF14:** Seleccionar idioma.\
-   **RF15:** Detectar GPU automáticamente.

------------------------------------------------------------------------

# 🛡 Requerimientos No Funcionales

## Rendimiento

-   **RNF1:** Procesar 1 hora de audio en \< 25 minutos con GPU 4GB.\
-   **RNF2:** Evitar uso simultáneo intensivo de GPU.\
-   **RNF3:** Uso máximo de RAM \< 20GB.

## Seguridad

-   **RNF4:** Procesamiento 100% local.\
-   **RNF5:** Tokens almacenados como variables de entorno.

## Arquitectura

-   **RNF6:** Seguir patrón MVVM en frontend.\
-   **RNF7:** Backend modular por servicios.\
-   **RNF8:** Permitir reemplazo del motor ASR sin modificar UI.

## Escalabilidad

-   **RNF9:** Soporte para despliegue en Docker.\
-   **RNF10:** Soporte futuro para procesamiento batch.

## Usabilidad

-   **RNF11:** Interfaz simple para usuarios no técnicos.\
-   **RNF12:** Indicador de progreso en tiempo real.

------------------------------------------------------------------------

# ⚡ Pipeline de Procesamiento

1.  Usuario carga archivo\
2.  FastAPI recibe request\
3.  Diarización en CPU\
4.  Transcripción en GPU\
5.  Merge de segmentos\
6.  Respuesta JSON estructurada\
7.  Renderizado en UI

------------------------------------------------------------------------

# 📦 Stack Tecnológico

## Frontend

-   Electron\
-   React\
-   TypeScript\
-   IPC

## Backend

-   FastAPI\
-   pyannote.audio\
-   faster-whisper\
-   PyTorch\
-   FFmpeg

------------------------------------------------------------------------

# 🚀 Roadmap Futuro

-   Persistencia con SQLite\
-   Historial de proyectos\
-   Sistema de licencias\
-   Cola de trabajos asíncronos\
-   Arquitectura plugin para motores ASR\
-   Versión SaaS futura

------------------------------------------------------------------------

# 📌 Objetivo del Proyecto

Construir una herramienta profesional de **transcripción y análisis
cualitativo automatizado**, con arquitectura limpia, escalable y
preparada para comercialización.
