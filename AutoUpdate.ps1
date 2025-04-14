$projectDir = "C:\ECCC-IMWEBs-Viewer"
$backendScript = "$projectDir\backend\apppy.py"

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

# Stop existing Flask process on port 5000
$existingProcess = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | Select-Object OwningProcess
if ($existingProcess) {
    Stop-Process -Id $existingProcess.OwningProcess -Force
}

# Start the Flask server in a new process
Start-Process -FilePath "conda" -ArgumentList "run -n venv python $backendScript" -RedirectStandardOutput "$projectDir\flask.log" -RedirectStandardError "$projectDir\flask_error.log"

# Node.js build process
npm install
npm run prestart
npm run build
