import {contextBridge, ipcRenderer} from 'electron';

// Expose some functionality to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  sendData: (data) => ipcRenderer.send('sendData', data),
});
