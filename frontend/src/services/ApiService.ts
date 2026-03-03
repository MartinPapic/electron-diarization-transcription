import axios from 'axios';
import type { TranscriptionRequest, TranscriptionResponse } from '../models/types';

// En desarrollo el backend FastAPI correrá en el 8000.
// En producción, el .exe empaquetado del backend también debería usar el mismo u otro dinámico.
const API_BASE_URL = 'http://127.0.0.1:8000';

export class ApiService {
    static async transcribe(filePath: string, numSpeakers: number, language: string, hfToken?: string): Promise<TranscriptionResponse> {
        const payload: TranscriptionRequest = {
            file_path: filePath,
            num_speakers: numSpeakers,
            language: language,
            hf_token: hfToken
        };
        const response = await axios.post<TranscriptionResponse>(`${API_BASE_URL}/transcribe`, payload);
        return response.data;
    }

    static async checkHealth(): Promise<boolean> {
        try {
            const res = await axios.get(`${API_BASE_URL}/`);
            return res.status === 200;
        } catch {
            return false;
        }
    }
}
