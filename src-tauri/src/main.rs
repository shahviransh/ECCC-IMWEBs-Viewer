// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::{env, os::windows::process::CommandExt, process::Command, time::Duration, thread::sleep};

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
    .join(format!("_up_\\backend\\app\\apppy-{}{}", target_triple, extension));

  println!("Starting server at {:?}", server_path);
  // Spawn the server as a background process
  let mut command = Command::new(server_path);
  command.creation_flags(CREATE_NO_WINDOW) // hide console window on Windows
  .spawn()  
  .expect("Failed to start server");

  // Wait a few seconds for the server to start
  sleep(Duration::from_secs(3));
}

fn main() {
  tauri::Builder::default()
    .setup(|_app| {
      tauri::async_runtime::spawn(async move {
        start_server().await;
      });
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}