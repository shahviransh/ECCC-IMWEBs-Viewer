# ECCC-IMWEBs-Viewer

This application is built with Tauri, Vue 3 as the frontend, and Flask as the backend. The project includes Tauri for desktop app development, Vue 3 for the user interface, and Flask for handling backend logic. After packaging the application, users can download and run the release package from the designated folder.

## Installation

**Go to the GitHub Releases page: Access the latest release package from this [link](https://github.com/shahviransh/ECCC-IMWEBs-Viewer/releases/latest)**.

### Download for your platform:

#### **Linux**:
- **Available Packages**: `.deb`, `.rpm`, or `.AppImage`
  - **`.deb`**: Suitable for Debian-based distributions like **Ubuntu**, **Linux Mint**, or **Kali**. Install with:
    ```bash
    sudo apt install ./<filename>.deb
    ```
  - **`.rpm`**: Suitable for RPM-based distributions like **Fedora**, **Red Hat Enterprise Linux (RHEL)**, or **openSUSE**. Install with:
    ```bash
    sudo rpm -i <filename>.rpm
    ```
  - **`.AppImage`**: Universal package for most distributions. Make it executable using:
    ```bash
    chmod +x <filename>.AppImage
    ./<filename>.AppImage
    ```
- Once installed, you can launch the application from your application menu or terminal.

#### **Windows**:
- **Available Packages**: `.msi` or `.exe`
  - **`.msi`**: Requires admin privileges for installation. Double-click the file and follow the setup instructions. The application will launch automatically after installation.
  - **`.exe`**: Suitable for users without admin rights. Run the `.exe` file, and the application will launch immediately.
- After installation, you can find the application in your Start Menu or Desktop.

#### **macOS**:
- **Available Packages**: `.dmg` or `.app.tar.gz`
  - **Intel vs ARM**: Check your Mac's architecture before downloading.  
    - **Intel Macs**: Download the **x64** package.  
    - **Apple Silicon (M1/M2)**: Download the **aarch64** package.
  - **`.dmg`**: Open the `.dmg` file, then drag and drop the application into your **Applications** folder. Launch the application from the Applications folder or via Spotlight Search.
  - **`.app.tar.gz`**: Extract the file using:
    ```bash
    tar -xzf <filename>.app.tar.gz
    ```
    Then move the extracted application to your **Applications** folder. Launch the application as usual.

### Application Data Path
If you would like to change the installation location for the app during installation, please keep it to the following default directory based on your platform:
- Windows: `C:\Users\{your_user}\AppData\Local\IMWEBs-Viewer`
- Linux: `/usr/lib/IMWEBs-Viewer`
- macOS: `/Users/{your_user}/Library/Application Support/IMWEBs-Viewer`

Launch the Application: The application connects the Vue 3 frontend with the Flask backend and should be ready to use.
