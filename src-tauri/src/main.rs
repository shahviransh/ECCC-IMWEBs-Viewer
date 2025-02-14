// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use reqwest::Client;
use std::{ env, process::Command, thread::sleep, time::Duration };
use std::fs;
use std::path::{ Path };

#[cfg(target_os = "windows")]
const CREATE_NO_WINDOW: u32 = 0x08000000;

fn copy_dir_recursive(src: &Path, dst: &Path) -> std::io::Result<()> {
    if !dst.exists() {
        fs::create_dir_all(dst)?;
    }

    for entry in fs::read_dir(src)? {
        let entry = entry?;
        let entry_path = entry.path();
        let dest_path = dst.join(entry.file_name());

        if entry_path.is_dir() {
            copy_dir_recursive(&entry_path, &dest_path)?;
        } else {
            fs::copy(&entry_path, &dest_path)?;
        }
    }
    Ok(())
}

#[tauri::command]
async fn start_server() {
    // Get the current executable's directory
    let current_exe = env::current_exe().expect("Failed to get current executable path");
    let exe_dir = current_exe.parent().expect("Failed to get parent directory");
    let up_folder = exe_dir.join("_up_");

    // Get the AppData\Local directory
    let local_appdata = env::var("LOCALAPPDATA").expect("Failed to get LOCALAPPDATA");
    let mut backend_dir = std::path::Path::new(&local_appdata).join("Imwebs-Viewer").join("_up_");

    // Copy _up_ folder to AppData\Local if it doesn't exist
    if !backend_dir.exists() {
        copy_dir_recursive(&up_folder, &backend_dir).expect(
            "Failed to copy _up_ folder recursively"
        );
    } else {
        backend_dir = up_folder;
    }

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
    let server_path = backend_dir
        .join("backend")
        .join("apppy")
        .join(format!("apppy-{}{}", target_triple, extension));

    println!("Starting server at {:?}", server_path);

    let mut command = Command::new(server_path);

    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        command.creation_flags(CREATE_NO_WINDOW);
    }
    #[cfg(target_family = "unix")]
    {
        // Redirect output to avoid a visible terminal on Linux/Unix
        command.stdout(std::process::Stdio::null()).stderr(std::process::Stdio::null());
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

fn remove_appdata_folder() {
    if let Ok(local_appdata) = env::var("LOCALAPPDATA") {
        let appdata_path = std::path::Path::new(&local_appdata).join("IMWEBs-Viewer");
        if appdata_path.exists() {
            fs::remove_dir_all(&appdata_path).expect("Failed to remove AppData folder");
            println!("Removed AppData folder: {:?}", appdata_path);
        }
    }
}

fn main() {
    tauri::Builder
        ::default()
        .plugin(tauri_plugin_dialog::init())
        .setup(|_app| {
            tauri::async_runtime::spawn(async move {
                start_server().await;
            });
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
