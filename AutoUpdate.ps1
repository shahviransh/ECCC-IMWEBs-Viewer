$projectDir = "C:\Users\{user}\Documents\GitHub\ECCC-IMWEBs-Viewer"
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

Write-Host "Activating Conda environment..."
conda activate venv

Write-Host "Restarting Flask production server..."
Start-Process -NoNewWindow -FilePath "conda" -ArgumentList "run -n venv python $backendScript" -PassThru | Out-Null

Write-Host "Running npm prestart..."
npm run prestart

Write-Host "Installing npm dependencies..."
npm install

Write-Host "Building Vue frontend..."
npm run build

Write-Host "Update complete!"
