import fs from "fs";
import path from "path";
import os from "os";
import { execSync } from "child_process";
import { dirname } from "path";
import { fileURLToPath } from "url";
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);


const ext = process.platform === "win32" ? ".exe" : "";

const rustInfo = execSync("rustc -vV");
let targetTriple = /host: (\S+)/g.exec(rustInfo)[1];
if (!targetTriple) {
  console.error("Failed to determine platform target triple");
  process.exit(1);
}

if (targetTriple.includes("apple")) {
  targetTriple = os.arch() === "arm64" ? targetTriple : "x86_64-apple-darwin";
}

// Rename the binary using the target triple
const oldPath = path.resolve(__dirname, "..", "backend", "apppy", `apppy${ext}`);
const newPath = path.resolve(
  __dirname,
  "..",
  "backend",
  "apppy",
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
  alert("Error renaming file:", error.message);
}
