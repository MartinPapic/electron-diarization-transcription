import { contextBridge, webUtils } from 'electron';

// Expose protected methods that allow the renderer process to use
// Electron APIs without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    getPathForFile: (file: File) => webUtils.getPathForFile(file),
});
