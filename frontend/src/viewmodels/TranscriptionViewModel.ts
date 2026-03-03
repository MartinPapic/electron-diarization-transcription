import { useState, useCallback } from 'react';
import { ApiService } from '../services/ApiService';
import { TranscriptionResponse } from '../models/types';

export function useTranscriptionViewModel() {
    const [isProcessing, setIsProcessing] = useState(false);
    const [result, setResult] = useState<TranscriptionResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const processAudio = useCallback(async (filePath: string, numSpeakers: number = 0, language: string = 'es') => {
        setIsProcessing(true);
        setError(null);
        setResult(null);

        try {
            const response = await ApiService.transcribe({
                file_path: filePath,
                num_speakers: numSpeakers,
                language
            });
            setResult(response);
        } catch (err: any) {
            setError(
                err.response?.data?.detail ||
                err.message ||
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
