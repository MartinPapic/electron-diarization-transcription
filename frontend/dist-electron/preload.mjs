"use strict";
const electron = require("electron");
electron.contextBridge.exposeInMainWorld("electronAPI", {
  // Example IPC channel mapping:
  // sendMessage: (message: string) => ipcRenderer.send('message', message),
});
