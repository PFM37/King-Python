const path = require('path');
const args = process.argv.slice(2);

if (args.length === 0) {
    console.log('Usage: kpc path/to/file.kp');
    process.exit(1);
}

const filePath = path.resolve(args[0]);

if (!filePath.endsWith('.kp')) {
    console.error('Error: File must have .kp extension');
    process.exit(1);
}

// Replace dynamic require with this:
const KpJS = require('../src/index');  // Static path

KpJS.runFile(filePath).catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
});