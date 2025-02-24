import fs from "fs";
import path from "path";
import { dirname } from "path";
import { fileURLToPath } from "url";
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Paths to package.json and Cargo.toml
const packageJsonPath = path.join(__dirname, "package.json");
const cargoTomlPath = path.join(__dirname, "src-tauri", "Cargo.toml");

// Read version from package.json
const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, "utf8"));
const version = packageJson.version;

// Read Cargo.toml and update the version
let cargoToml = fs.readFileSync(cargoTomlPath, "utf8");
cargoToml = cargoToml.replace(/version = ".*"/, `version = "${version}"`);
fs.writeFileSync(cargoTomlPath, cargoToml);

console.log(`✅ Synced Cargo.toml version to ${version}`);