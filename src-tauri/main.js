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
const oldPath = path.resolve(__dirname, "..", "backend", "app", `apppy${ext}`);
const newPath = path.resolve(
  __dirname,
  "..",
  "backend",
  "app",
  `apppy-${targetTriple}${ext}`
);

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
