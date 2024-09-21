const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let pythonProcess = null;

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
    },
    icon: __dirname + '/icon.ico',
  });

  // mainWindow.loadURL('http://localhost:1420'); // Pointing to Vue's dev server
  // Load the Vue app's index.html from the dist folder
  mainWindow.loadFile(path.join('dist', 'index.html'));  // Ensure this path is correct

  // Open the DevTools.
  mainWindow.webContents.openDevTools();
}

app.on('ready', () => {

  createWindow();

  // Start the Python backend
  const backendPath = path.join(__dirname, '..', 'backend', 'app.py');
  pythonProcess = spawn('python', [backendPath]);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`);
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
  if (pythonProcess) {
    pythonProcess.kill();
  }
});
