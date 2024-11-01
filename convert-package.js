import fs from 'fs';
import JSON5 from 'json5';

// Read the package.json5 file
const packageJson5 = fs.readFileSync('./package.json5', 'utf-8');

// Parse the JSON5 content
const packageJson = JSON5.parse(packageJson5);

// Write the standard JSON content to package.json
fs.writeFileSync('./package.json', JSON.stringify(packageJson, null, 2), 'utf-8');

console.log('package.json5 converted to package.json');