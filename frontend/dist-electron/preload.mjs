"use strict";const e=require("electron");e.contextBridge.exposeInMainWorld("electronAPI",{getPathForFile:t=>e.webUtils.getPathForFile(t)});
