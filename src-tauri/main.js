const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const ext = process.platform === "win32" ? ".exe" : "";

const rustInfo = execSync("rustc -vV");
const targetTriple = /host: (\S+)/g.exec(rustInfo)[1];
if (!targetTriple) {
  console.error("Failed to determine platform target triple");
  process.exit(1);
}

// Rename the binary using the target triple
const oldPath = `../backend/dist/app/apppy${ext}`;
const newPath = `../backend/dist/app/apppy-${targetTriple}${ext}`;

try {
  if (fs.existsSync(oldPath)) {
    fs.renameSync(oldPath, newPath);
    console.log(`Renamed sidecar to ${newPath}`);
  } else {
    console.error(`File ${oldPath} does not exist`);
  }
} catch (error) {
  console.error("Error renaming file:", error);
}

// Source paths for the bundled MSI and EXE files
const msiSource = path.join(
  __dirname,
  "target",
  "release",
  "bundle",
  "msi"
);
const nsisSource = path.join(
  __dirname,
  "target",
  "release",
  "bundle",
  "nsis"
);

// Destination path
const destination = path.join(__dirname, "target");

// Move files function
function moveFiles(sourcePath, destPath) {
  fs.readdir(sourcePath, (err, files) => {
    if (err) {
      console.error("Failed to read directory: ${sourcePath}");
      return;
    }
    files.forEach((file) => {
      const oldPath = path.join(sourcePath, file);
      const newPath = path.join(destPath, file);
      fs.rename(oldPath, newPath, (renameErr) => {
        if (renameErr) {
          console.error(`Failed to move file ${file}:`, renameErr);
        } else {
          console.log(`Moved ${file} to ${destPath}`);
        }
      });
    });
  });
}

// Move MSI and NSIS files 
moveFiles(msiSource, destination); 
moveFiles(nsisSource, destination);

