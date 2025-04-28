$projectDir = "C:\ECCC-IMWEBs-Viewer"
$sourceDir = "$projectDir\dist"
$destDir = "C:\inetpub\wwwroot\IMWEBs-Viewer"

Set-Location $projectDir

# Copy the built files to the web server directory
Copy-Item -Path $sourceDir -Destination $destDir -Recurse -Force

# Stop existing apppy.py process if running on port 5000
$existingProcess = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | Select-Object OwningProcess
if ($existingProcess) {
    Stop-Process -Id $existingProcess.OwningProcess -Force
}

# Start the Flask backend detached
Start-Process `
    -FilePath "powershell.exe" `
    -ArgumentList "-ExecutionPolicy Bypass -NoProfile -NoLogo -Command conda run -n venv python $projectDir\backend\apppy.py" `
    -WindowStyle Hidden `
    -NoNewWindow `
    -WorkingDirectory "$projectDir\backend"
