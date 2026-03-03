import { useState, useCallback } from 'react';
import { ApiService } from '../services/ApiService';
import type { TranscriptionResponse } from '../models/types';

async function waitForBackend(maxRetries = 15, intervalMs = 2000): Promise<boolean> {
    for (let i = 0; i < maxRetries; i++) {
        const ok = await ApiService.checkHealth();
        if (ok) return true;
        await new Promise(r => setTimeout(r, intervalMs));
    }
    return false;
}

export function useTranscriptionViewModel() {
    const [isProcessing, setIsProcessing] = useState(false);
    const [result, setResult] = useState<TranscriptionResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const processAudio = useCallback(async (filePath: string, numSpeakers: number = 0, language: string = 'es', hfToken: string = '') => {
        setIsProcessing(true);
        setError(null);
        setResult(null);

        try {
            // Wait for the backend to be ready before sending the request
            const backendReady = await waitForBackend();
            if (!backendReady) {
                setError('No se pudo conectar con el backend local. Asegúrate de que el servidor esté corriendo en el puerto 8000.');
                return;
            }

            const response = await ApiService.transcribe(filePath, numSpeakers, language, hfToken);
            setResult(response);
        } catch (err: unknown) {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const error = err as any;
            const detail = error.response?.data?.detail || error.message || '';
            if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
                setError('Error de red: No se pudo conectar con el backend. Verifica que el servidor esté activo en http://127.0.0.1:8000');
            } else {
                setError(detail || 'Ocurrió un error en el backend local.');
            }
        } finally {
            setIsProcessing(false);
        }
    }, []);

    const reset = useCallback(() => {
        setResult(null);
        setError(null);
    }, []);

    return {
        isProcessing,
        result,
        error,
        processAudio,
        reset
    };
}
