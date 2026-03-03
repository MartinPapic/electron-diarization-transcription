import { app, BrowserWindow } from 'electron';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn, ChildProcess } from 'node:child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let mainWindow: BrowserWindow | null;
let apiProcess: ChildProcess | null = null;

// Production flag
const isDev = !app.isPackaged;

function startBackend() {
  if (isDev) {
    // En desarrollo, lanzar a través de Python directamente usando el venv local
    apiProcess = spawn(path.join(__dirname, '../../backend/venv/Scripts/python.exe'), ['-m', 'uvicorn', 'main:app', '--port', '8000'], {
      cwd: path.join(__dirname, '../../backend'),
      env: process.env
    });
  } else {
    // En producción, el .exe de PyInstaller estará empaquetado como Extra Resource
    const backendPath = path.join(process.resourcesPath, 'backend_api', 'backend_api.exe');
    apiProcess = spawn(backendPath, [], { env: process.env });
  }

  apiProcess.stdout?.on('data', (data) => console.log(`[FastAPI]: ${data}`));
  apiProcess.stderr?.on('data', (data) => console.error(`[FastAPI Error]: ${data}`));
}

function killBackend() {
  if (apiProcess) {
    console.log("Terminando proceso FastAPI...");
    apiProcess.kill();
    apiProcess = null;
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1024,
    height: 768,
    title: "Diarization & Transcription App",
    backgroundColor: '#ffffff',
    webPreferences: {
      preload: path.join(__dirname, 'preload.mjs'),
      // Security settings
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  // In development, load from Vite dev server
  if (isDev) {
    // Vite Dev server usually runs on 5173
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL || 'http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    // In production, load the local index.html
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  startBackend();
  createWindow();

  app.on('activate', () => {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  killBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', () => {
  killBackend();
});
