$projectDir = "C:\ECCC-IMWEBs-Viewer"
$sourceDir = "$projectDir\dist\*"
$destDir = "C:\inetpub\wwwroot\IMWEBs-Viewer"

Set-Location $projectDir

# Copy the built files to the web server directory
Copy-Item -Path $sourceDir -Destination $destDir -Recurse -Force
