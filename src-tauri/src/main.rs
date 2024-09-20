// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::Command;
use tauri::Builder;

fn main() {
    Builder::default()
        .invoke_handler(tauri::generate_handler![run_python_backend])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

#[tauri::command]
async fn run_python_backend() -> Result<String, String> {
    let output = Command::new("python") // or "python3" depending on the environment
        .arg("..\\target\\release\\bundle\\msi\\app.py") // Path to your Python script
        .output()
        .expect("Failed to start Python backend");

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).into())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).into())
    }
}