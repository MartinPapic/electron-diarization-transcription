import { useState, useCallback } from 'react';
import { ApiService } from '../services/ApiService';
import type { TranscriptionResponse } from '../models/types';

export function useTranscriptionViewModel() {
    const [isProcessing, setIsProcessing] = useState(false);
    const [result, setResult] = useState<TranscriptionResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const processAudio = useCallback(async (filePath: string, numSpeakers: number = 0, language: string = 'es', hfToken: string = '') => {
        setIsProcessing(true);
        setError(null);
        setResult(null);

        try {
            const response = await ApiService.transcribe(filePath, numSpeakers, language, hfToken);
            setResult(response);
        } catch (err: unknown) {
            const error = err as any;
            setError(
                error.response?.data?.detail ||
                error.message ||
                'Ocurrió un error en el backend local.'
            );
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
