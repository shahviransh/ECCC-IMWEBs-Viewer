const { app, BrowserWindow } = require("electron");
const path = require("path");
const { exec } = require("child_process");
const os = require("os");
const axios = require("axios");

let pythonProcess = null;

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: true,
    },
    icon: __dirname + "/icon.ico",
  });

  // mainWindow.loadURL('http://localhost:1420'); // Pointing to Vue's dev server
  // Load the Vue app's index.html from the dist folder
  mainWindow.loadFile(path.join("dist", "index.html")); // Ensure this path is correct

  // Open the DevTools.
  mainWindow.webContents.openDevTools();
}

app.on("ready", () => {
  // Determine the backend executable based on the operating system
  let command;
  const backendPath = path.join(app.getAppPath(), '..', "backend");
  if (os.platform() === "win32") {
    command = `start /B "" ${path.join(backendPath, "app.exe")}`; // Use 'start' for Windows
  } else {
    command = `./app &`; // Direct execution for Linux/macOS
    // Change directory to the backend folder before running the command
    process.chdir(backendPath);
  }

  // Start the Python backend
  pythonProcess = exec(command, function (err, data) {
    if (err) {
      console.error(err);
      return;
    }
    console.log(data.toString());
  });

  createWindow();  
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
  axios.get("http://localhost:5000/shutdown");
  pythonProcess.kill();
});
