$projectDir = "C:\ECCC-IMWEBs-Viewer"
$backendScript = "$projectDir\backend\apppy.py"
$serviceName = "IMWEBs-Viewer-Backend"

Set-Location $projectDir

$localHash = git rev-parse HEAD
git fetch origin
$remoteHash = git rev-parse origin/main

# Check if the local and remote hashes are the same
if ($localHash -eq $remoteHash) {
    exit 0   
}

# Attempt to pull changes
git pull
if ($LASTEXITCODE -ne 0) {
    # If merge conflicts occur, reset the local branch to match the remote branch
    Write-Host "Merge conflict detected. Resetting local branch to match remote..." -ForegroundColor Yellow
    git fetch origin
    git reset --hard origin/main
}

# Install pip packages in conda env
conda run -n venv pip install --no-cache-dir -r backend/requirements.txt

# Stop existing apppy.py process if running on port 5000
$existingProcess = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | Select-Object OwningProcess
if ($existingProcess) {
    Stop-Process -Id $existingProcess.OwningProcess -Force
}

# Start the Flask backend detached
Start-Process `
    -FilePath "powershell.exe" `
    -ArgumentList "-ExecutionPolicy Bypass -NoProfile -NoLogo -Command conda run -n venv python $projectDir\backend\apppy.py" `
    -NoNewWindow `
    -WorkingDirectory "$projectDir\backend"

# Node.js build process
npm install
npm run prestart
npm run build
