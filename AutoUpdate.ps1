$projectDir = "C:\Users\YourUser\Documents\GitHub\ECCC-IMWEBs-Viewer"
$backendScript = "$projectDir\backend\apppy.py"

if (-not (Test-Path $projectDir)) {
    Write-Host "Repository not found. Cloning..."
    git clone $repoUrl $projectDir
}

Write-Host "Navigating to project directory: $projectDir"
Set-Location $projectDir

Write-Host "Checking for updates..."
$localHash = git rev-parse HEAD
git fetch origin
$remoteHash = git rev-parse origin/main

if ($localHash -eq $remoteHash) {
    Write-Host "Repository is already up to date. Exiting script."
    exit 0
}

Write-Host "Pulling latest changes from GitHub..."
git pull 

# Stop existing Flask process on port 5000
Write-Host "Checking for existing Flask process on port 5000..."
$existingProcess = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | Select-Object OwningProcess
if ($existingProcess) {
    Write-Host "Stopping existing process with PID: $($existingProcess.OwningProcess)"
    Stop-Process -Id $existingProcess.OwningProcess -Force
} else {
    Write-Host "No existing process found on port 5000."
}

Write-Host "Activating Conda environment and restarting Flask production server..."
Start-Process -NoNewWindow -FilePath "conda" -ArgumentList "run -n venv python $backendScript" -PassThru | Out-Null

Write-Host "Running npm prestart..."
npm run prestart

Write-Host "Installing npm dependencies..."
npm install

Write-Host "Building Vue frontend..."
npm run build

Write-Host "Moving built files to IIS directory..."
$sourceDir = "$projectDir\dist"
$destDir = "C:\inetpub\wwwroot\IMWEBs-Viewer"
if (Test-Path $destDir) {
    Remove-Item "$destDir\*" -Recurse -Force
} else {
    New-Item -ItemType Directory -Path $destDir
}

Write-Host "Update complete!"
