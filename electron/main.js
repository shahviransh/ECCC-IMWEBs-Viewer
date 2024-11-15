import { app, BrowserWindow } from "electron";
import path from "path";
import { dirname } from "path";
import { fileURLToPath } from "url";
import exec from "child_process";
import os from "os";
import axios from "axios";

let pythonProcess = null;
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: false,
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
  const backendPath = path.join(app.getAppPath(), "..", "backend");
  if (os.platform() === "win32") {
    command = `start /B "" ${path.join(
      backendPath,
      "apppy-x86_64-pc-windows-msvc.exe"
    )}`; // Use 'start' for Windows
  } else {
    command = `./apppy-x86_64-pc-windows-msvc &`; // Direct execution for Linux/macOS
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

  // Wait for the backend to start before creating the window
  setTimeout(createWindow, 3000);
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
  axios.get("http://localhost:5000/shutdown");
  pythonProcess.kill();
});
