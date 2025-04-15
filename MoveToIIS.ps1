$projectDir = "C:\ECCC-IMWEBs-Viewer"
$sourceDir = "$projectDir\dist"
$destDir = "C:\inetpub\wwwroot\IMWEBs-Viewer"

Set-Location $projectDir

$localHash = git rev-parse HEAD
git fetch origin
$remoteHash = git rev-parse origin/main

# Check if the local and remote hashes are the same
if ($localHash -eq $remoteHash) {
    exit 0   
}

# Copy the built files to the web server directory
Copy-Item -Path $sourceDir -Destination $destDir -Recurse -Force
