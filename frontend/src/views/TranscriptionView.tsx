import React, { useState, useRef } from 'react';
import { useTranscriptionViewModel } from '../viewmodels/TranscriptionViewModel';
import { ExportService } from '../services/ExportService';
import { FileAudio, UploadCloud, Settings, Loader2, PlayCircle, AlertCircle, FileText, FileJson, FileType2 } from 'lucide-react';

// Declare the electronAPI exposed by preload
declare global {
    interface Window {
        electronAPI: {
            getPathForFile: (file: File) => string;
        };
    }
}

export function TranscriptionView() {
    const { isProcessing, result, error, processAudio, reset } = useTranscriptionViewModel();

    // Local state for the selected file and options
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [numSpeakers, setNumSpeakers] = useState<number>(0);
    const [language, setLanguage] = useState<string>('es');
    const [hfToken, setHfToken] = useState<string>(() => localStorage.getItem('hf_token') || '');

    const handleHfTokenChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = e.target.value;
        setHfToken(val);
        localStorage.setItem('hf_token', val);
    };

    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setSelectedFile(e.target.files[0]);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            setSelectedFile(e.dataTransfer.files[0]);
        }
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
    };

    const startTranscription = () => {
        if (!selectedFile) return;

        // Use Electron's webUtils via preload to get the absolute path securely
        let filePath: string | undefined;
        try {
            filePath = window.electronAPI.getPathForFile(selectedFile);
        } catch {
            filePath = undefined;
        }

        if (!filePath) {
            alert("Error: No se pudo obtener la ruta absoluta del archivo.");
            return;
        }

        processAudio(filePath, numSpeakers, language, hfToken);
    };

    return (
        <div className="min-h-screen bg-background p-6 flex flex-col items-center">
            <div className="max-w-4xl w-full space-y-6">

                {/* Header */}
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex items-center gap-4">
                    <div className="bg-blue-50 p-3 rounded-xl text-blue-600 flex-shrink-0">
                        <FileAudio size={28} />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-slate-800">Diarización y Transcripción</h1>
                        <p className="text-slate-500 text-sm">Procesa archivos de audio localmente usando IA.</p>
                    </div>
                </div>

                {/* Main Content Area */}
                {!isProcessing && !result && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Options Panel */}
                        <div className="md:col-span-1 bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4 h-fit">
                            <h2 className="font-semibold text-slate-700 flex items-center gap-2">
                                <Settings size={18} /> Opciones
                            </h2>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-600">Número de Hablantes (Opcional)</label>
                                <input
                                    type="number"
                                    min="0"
                                    max="10"
                                    value={numSpeakers || ''}
                                    onChange={(e) => setNumSpeakers(parseInt(e.target.value) || 0)}
                                    placeholder="Automático (0)"
                                    className="w-full p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all"
                                />
                                <p className="text-xs text-slate-400">Deja en 0 o vacío para detección automática.</p>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-600">Idioma Principal</label>
                                <select
                                    value={language}
                                    onChange={(e) => setLanguage(e.target.value)}
                                    className="w-full p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all"
                                >
                                    <option value="es">Español</option>
                                    <option value="en">Inglés</option>
                                    <option value="fr">Francés</option>
                                </select>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-600">HuggingFace Token</label>
                                <input
                                    type="password"
                                    value={hfToken}
                                    onChange={handleHfTokenChange}
                                    placeholder="hf_..."
                                    className="w-full p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all font-mono text-sm"
                                />
                            </div>
                        </div>

                        {/* Dropzone */}
                        <div className="md:col-span-2 space-y-4">
                            <div
                                className="bg-white border-2 border-dashed border-slate-300 rounded-2xl p-10 flex flex-col items-center justify-center text-center hover:bg-slate-50 hover:border-blue-500 cursor-pointer transition-all group min-h-[300px]"
                                onClick={() => fileInputRef.current?.click()}
                                onDrop={handleDrop}
                                onDragOver={handleDragOver}
                            >
                                <input
                                    type="file"
                                    className="hidden"
                                    ref={fileInputRef}
                                    onChange={handleFileChange}
                                    accept="audio/*,video/*"
                                />

                                <div className="bg-blue-50 p-4 rounded-full text-blue-600 mb-4 group-hover:scale-110 transition-transform flex items-center justify-center">
                                    {selectedFile ? <FileAudio size={40} /> : <UploadCloud size={40} />}
                                </div>

                                {selectedFile ? (
                                    <div>
                                        <p className="font-medium text-slate-700 text-lg">{selectedFile.name}</p>
                                        <p className="text-slate-500 text-sm mt-1">
                                            {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                                        </p>
                                    </div>
                                ) : (
                                    <div>
                                        <p className="font-medium text-slate-700 text-lg">Haz click o arrastra un archivo aquí</p>
                                        <p className="text-slate-500 text-sm mt-2">Soporta WAV, MP3, MP4, etc.</p>
                                    </div>
                                )}
                            </div>

                            {selectedFile && (
                                <button
                                    onClick={startTranscription}
                                    className="w-full py-4 bg-primary text-white rounded-xl font-medium tracking-wide shadow-sm hover:shadow-md hover:bg-blue-600 transition-all flex items-center justify-center gap-2"
                                >
                                    <PlayCircle size={20} />
                                    Iniciar Procesamiento AI
                                </button>
                            )}

                            {error && (
                                <div className="p-4 bg-red-50 text-red-700 rounded-xl border border-red-100 flex items-start gap-3">
                                    <AlertCircle className="shrink-0 mt-0.5" size={18} />
                                    <p className="text-sm">{error}</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Loading State */}
                {isProcessing && (
                    <div className="bg-white p-12 rounded-2xl shadow-sm border border-slate-200 flex flex-col items-center justify-center space-y-6">
                        <Loader2 size={48} className="text-blue-600 animate-spin" />
                        <div className="text-center">
                            <h3 className="text-xl font-semibold text-slate-800">Procesando Audio...</h3>
                            <p className="text-slate-500 mt-2 max-w-md">
                                Los modelos de IA están trabajando localmente. Pyannote está detectando a los hablantes y Whisper transcribiendo los segmentos. Esto puede tomar varios minutos.
                            </p>
                        </div>
                    </div>
                )}

                {/* Result State */}
                {result && !isProcessing && (
                    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                        <div className="border-b border-slate-100 p-4 bg-slate-50 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                            <h3 className="font-semibold text-slate-700">Resultados de Transcripción</h3>

                            <div className="flex flex-wrap items-center gap-2">
                                <button
                                    onClick={() => ExportService.exportTXT(result)}
                                    className="px-3 py-1.5 bg-white border border-slate-200 text-slate-600 rounded-lg text-sm hover:bg-slate-50 flex items-center gap-1.5 transition-colors"
                                >
                                    <FileText size={16} /> .TXT
                                </button>
                                <button
                                    onClick={() => ExportService.exportSRT(result)}
                                    className="px-3 py-1.5 bg-white border border-slate-200 text-slate-600 rounded-lg text-sm hover:bg-slate-50 flex items-center gap-1.5 transition-colors"
                                >
                                    <FileType2 size={16} /> .SRT
                                </button>
                                <button
                                    onClick={() => ExportService.exportJSON(result)}
                                    className="px-3 py-1.5 bg-white border border-slate-200 text-slate-600 rounded-lg text-sm hover:bg-slate-50 flex items-center gap-1.5 transition-colors"
                                >
                                    <FileJson size={16} /> .JSON
                                </button>
                                <div className="w-px h-6 bg-slate-200 mx-2 hidden md:block"></div>
                                <button
                                    onClick={() => { reset(); setSelectedFile(null); }}
                                    className="text-sm px-3 py-1.5 bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-lg font-medium transition-colors"
                                >
                                    Procesar nuevo archivo
                                </button>
                            </div>
                        </div>

                        <div className="p-6">
                            <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2">
                                {result.segments.map((seg, idx) => (
                                    <div key={idx} className="flex gap-4 p-4 rounded-xl hover:bg-slate-50 border border-transparent hover:border-slate-100 transition-colors">
                                        <div className="pt-1 flex-shrink-0 w-24">
                                            <span className="inline-block px-3 py-1 bg-indigo-100 text-indigo-700 text-xs font-bold rounded-full w-full text-center truncate">
                                                {seg.speaker}
                                            </span>
                                            <div className="text-xs text-slate-400 mt-2 font-mono text-center">
                                                {new Date(seg.start * 1000).toISOString().substr(14, 5)} - {new Date(seg.end * 1000).toISOString().substr(14, 5)}
                                            </div>
                                        </div>
                                        <p className="text-slate-700 leading-relaxed flex-1">
                                            {seg.text}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
}
