$projectDir = "C:\Users\YourUser\Documents\GitHub\ECCC-IMWEBs-Viewer"
$backendScript = "$projectDir\backend\apppy.py"

# Check if the project directory exists, if not, clone the repository
if (-not (Test-Path $projectDir)) {    
    git clone $repoUrl $projectDir
}

Set-Location $projectDir

$localHash = git rev-parse HEAD
git fetch origin
$remoteHash = git rev-parse origin/main

# Check if the local and remote hashes are the same
if ($localHash -eq $remoteHash) {    
    exit 0
}

git pull 

# Stop existing Flask process on port 5000
$existingProcess = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | Select-Object OwningProcess
if ($existingProcess) {
    Stop-Process -Id $existingProcess.OwningProcess -Force
}

# Start the Flask server in a new process
Start-Process -NoNewWindow -FilePath "conda" -ArgumentList "run -n venv python $backendScript" -PassThru | Out-Null

# Node.js build process
npm run prestart
npm install
npm run build

# Copy the built files to the web server directory
# TODO: Update the destination directory as per web server configuration
$sourceDir = "$projectDir\dist"
$destDir = "C:\inetpub\wwwroot\IMWEBs-Viewer"
if (Test-Path $destDir) {
    Remove-Item "$destDir\*" -Recurse -Force
} else {
    New-Item -ItemType Directory -Path $destDir
}
