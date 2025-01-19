// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::{env, process::Command, time::Duration, thread::sleep};
use reqwest::Client;
use tauri::Manager;

#[cfg(target_os = "windows")]
const CREATE_NO_WINDOW: u32 = 0x08000000;

#[tauri::command]
async fn start_server() {
  // Get the current executable's directory
  let current_exe = env::current_exe().expect("Failed to get current executable path");
  let exe_dir = current_exe.parent().expect("Failed to get parent directory");

  // Fetch the target triple using the environment variables or a fallback
  let target_triple = format!(
    "{}-{}-{}-{}",
    std::env::consts::ARCH,
    "pc",
    std::env::consts::OS,
    if cfg!(target_env = "gnu") {
        "gnu"
    } else if cfg!(target_env = "msvc") {
        "msvc"
    } else {
        "unknown"
    }
  );
  // Determine the server path using the fetched target triple
  let extension = if cfg!(target_os = "windows") { ".exe" } else { "" };
  let server_path = exe_dir
    .join("_up_")
    .join("backend")
    .join("apppy")
    .join(format!("apppy-{}{}", target_triple, extension));

  println!("Starting server at {:?}", server_path);
  // Spawn the server as a background process
  let mut command = Command::new(server_path);
  // Only apply CREATE_NO_WINDOW on Windows to suppress console
  #[cfg(target_os = "windows")]
  {
      use std::os::windows::process::CommandExt;
      command.creation_flags(CREATE_NO_WINDOW);
  }
  command.spawn().expect("Failed to start server");
  
  // Wait a few seconds for the server to start
  sleep(Duration::from_secs(5));
}

async fn shutdown_flask() {
  let client = Client::new();
  // Send a shutdown request to the Flask server when Tauri closes
  if let Err(_err) = client.get("http://127.0.0.1:5000/shutdown").send().await {
    println!("Flask server shutdown request success.");
  } else {
    println!("Flask server shutdown request failed.");
  }
}

fn main() {
  tauri::Builder::default()
    .setup(|app| {
      tauri::async_runtime::spawn(async move {
        start_server().await;
      });
      #[cfg(debug_assertions)] // only include this code on debug builds
      {
        let window = app.get_webview_window("main").unwrap();
        window.open_devtools();
        window.close_devtools();
      }
      Ok(())
    })
    .on_window_event(|_app_handle, event| {
      if let tauri::WindowEvent::CloseRequested { .. } = event {
        // Trigger the Flask shutdown function on close request
        tauri::async_runtime::block_on(shutdown_flask());
      }
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}