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

# Node.js build process
npm install
npm run prestart
npm run build
