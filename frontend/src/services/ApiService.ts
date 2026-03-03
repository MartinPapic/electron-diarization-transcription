import axios from 'axios';
import { TranscriptionRequest, TranscriptionResponse } from '../models/types';

// En desarrollo el backend FastAPI correrá en el 8000.
// En producción, el .exe empaquetado del backend también debería usar el mismo u otro dinámico.
const API_BASE_URL = 'http://127.0.0.1:8000';

export class ApiService {
    static async transcribe(request: TranscriptionRequest): Promise<TranscriptionResponse> {
        const response = await axios.post<TranscriptionResponse>(`${API_BASE_URL}/transcribe`, request);
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
