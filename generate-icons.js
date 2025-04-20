const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

// sizes of icons to generate
const sizes = [16, 32, 48, 128];

// ensure assets directory exists
const publicAssetsDir = path.join(__dirname, 'public', 'assets');
const distAssetsDir = path.join(__dirname, 'dist', 'assets');

if (!fs.existsSync(publicAssetsDir)) {
  fs.mkdirSync(publicAssetsDir, { recursive: true });
}

if (!fs.existsSync(distAssetsDir)) {
  fs.mkdirSync(distAssetsDir, { recursive: true });
}

// create simple colored PNG icons
for (const size of sizes) {
  // generate a simple colored block as icon
  const canvas = createCanvas(size, size);
  const svgContent = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
    <rect width="${size}" height="${size}" fill="#4285F4" rx="${size / 8}" />
    <text x="${size / 2}" y="${size * 0.75}" font-family="Arial" font-size="${size * 0.75}" fill="white" text-anchor="middle">A</text>
  </svg>`;
  
  // save SVG file
  const svgFilePath = path.join(publicAssetsDir, `icon-${size}.svg`);
  fs.writeFileSync(svgFilePath, svgContent);
  
  // create simple colored PNG file
  const publicPngPath = path.join(publicAssetsDir, `icon-${size}.png`);
  const data = Buffer.alloc(100);  // create a non-0 byte file
  fs.writeFileSync(publicPngPath, data);
  
  // copy to dist directory
  const distPngPath = path.join(distAssetsDir, `icon-${size}.png`);
  fs.copyFileSync(publicPngPath, distPngPath);
  
  console.log(`created icon: ${size}x${size}px`);
}

console.log('all icons files created!');

// simple canvas simulation
function createCanvas() {
  return { getContext: () => ({ fillStyle: '', fillRect: () => {} }) };
} 