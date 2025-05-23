$projectDir = "C:\ECCC-IMWEBs-Viewer"
$sourceDir = "$projectDir\dist"
$destDir = "C:\inetpub\wwwroot\IMWEBs-Viewer"

Set-Location $projectDir

# Remove the destination folder entirely
if (Test-Path $destDir) {
    Remove-Item -Path $destDir -Recurse -Force
}

# Copy the entire dist folder's contents, preserving structure
Copy-Item -Path $sourceDir -Destination $destDir -Recurse -Force
