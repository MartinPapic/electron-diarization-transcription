import { app as t, BrowserWindow as l } from "electron";
import n from "node:path";
import { fileURLToPath as p } from "node:url";
import { spawn as r } from "node:child_process";
const f = p(import.meta.url), a = n.dirname(f);
let e, o = null;
const c = !t.isPackaged;
function m() {
  if (c)
    o = r(n.join(a, "../../backend/venv/Scripts/python.exe"), ["-m", "uvicorn", "main:app", "--port", "8000"], {
      cwd: n.join(a, "../../backend"),
      env: process.env
    });
  else {
    const i = n.join(process.resourcesPath, "backend_api", "backend_api.exe");
    o = r(i, [], { env: process.env });
  }
  o.stdout?.on("data", (i) => console.log(`[FastAPI]: ${i}`)), o.stderr?.on("data", (i) => console.error(`[FastAPI Error]: ${i}`));
}
function d() {
  o && (console.log("Terminando proceso FastAPI..."), o.kill(), o = null);
}
function s() {
  e = new l({
    width: 1024,
    height: 768,
    title: "Diarization & Transcription App",
    backgroundColor: "#ffffff",
    webPreferences: {
      preload: n.join(a, "preload.mjs"),
      // Security settings
      nodeIntegration: !1,
      contextIsolation: !0
    }
  }), c ? (e.loadURL(process.env.VITE_DEV_SERVER_URL || "http://localhost:5173"), e.webContents.openDevTools()) : e.loadFile(n.join(a, "../dist/index.html")), e.on("closed", () => {
    e = null;
  });
}
t.whenReady().then(() => {
  m(), s(), t.on("activate", () => {
    l.getAllWindows().length === 0 && s();
  });
});
t.on("window-all-closed", () => {
  d(), process.platform !== "darwin" && t.quit();
});
t.on("will-quit", () => {
  d();
});
