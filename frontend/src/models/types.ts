export interface Segment {
    start: number;
    end: number;
    speaker: string;
    text: string;
}

export interface TranscriptionResponse {
    segments: Segment[];
    full_text: string;
}

export interface TranscriptionRequest {
    file_path: string;
    num_speakers: number;
    language: string;
    hf_token?: string;
}
