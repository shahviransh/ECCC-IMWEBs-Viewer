const { contextBridge, ipcRenderer } = require('electron');

// Expose some functionality to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  sendData: (data) => ipcRenderer.send('sendData', data),
});
