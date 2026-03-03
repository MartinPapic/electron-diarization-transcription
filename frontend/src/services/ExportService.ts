import type { TranscriptionResponse } from '../models/types';

export class ExportService {
    static downloadFile(content: string, filename: string, contentType: string) {
        const blob = new Blob([content], { type: contentType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    static exportTXT(result: TranscriptionResponse, baseFilename: string = 'transcription') {
        let content = 'TRANSCRIPCIÓN:\n\n';
        result.segments.forEach(seg => {
            content += `[${this.formatTime(seg.start)} - ${this.formatTime(seg.end)}] ${seg.speaker}: ${seg.text}\n`;
        });
        this.downloadFile(content, `${baseFilename}.txt`, 'text/plain;charset=utf-8');
    }

    static exportJSON(result: TranscriptionResponse, baseFilename: string = 'transcription') {
        const content = JSON.stringify(result, null, 2);
        this.downloadFile(content, `${baseFilename}.json`, 'application/json;charset=utf-8');
    }

    static exportSRT(result: TranscriptionResponse, baseFilename: string = 'transcription') {
        let content = '';
        result.segments.forEach((seg, index) => {
            content += `${index + 1}\n`;
            content += `${this.formatTimeSRT(seg.start)} --> ${this.formatTimeSRT(seg.end)}\n`;
            content += `${seg.speaker}: ${seg.text.trim()}\n\n`;
        });
        this.downloadFile(content, `${baseFilename}.srt`, 'text/plain;charset=utf-8');
    }

    private static formatTime(seconds: number): string {
        return new Date(seconds * 1000).toISOString().substring(11, 19);
    }

    private static formatTimeSRT(seconds: number): string {
        const d = new Date(seconds * 1000);
        const hr = String(d.getUTCHours()).padStart(2, '0');
        const min = String(d.getUTCMinutes()).padStart(2, '0');
        const sec = String(d.getUTCSeconds()).padStart(2, '0');
        const ms = String(d.getUTCMilliseconds()).padStart(3, '0');
        return `${hr}:${min}:${sec},${ms}`;
    }
}
