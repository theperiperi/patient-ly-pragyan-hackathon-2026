import sharp from 'sharp';
import { readFileSync, mkdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const iconsDir = join(__dirname, '..', 'public', 'icons');

// Standard PWA icon sizes
const sizes = [72, 96, 128, 144, 152, 192, 384, 512];

// Read SVG file
const svgBuffer = readFileSync(join(iconsDir, 'icon.svg'));

async function generateIcons() {
  // Ensure icons directory exists
  if (!existsSync(iconsDir)) {
    mkdirSync(iconsDir, { recursive: true });
  }

  console.log('Generating PWA icons...');

  // Generate standard icons
  for (const size of sizes) {
    await sharp(svgBuffer)
      .resize(size, size)
      .png()
      .toFile(join(iconsDir, `icon-${size}x${size}.png`));
    console.log(`  Generated icon-${size}x${size}.png`);
  }

  // Generate maskable icons (with padding for safe area)
  // Maskable icons need 10-20% padding to be safe
  for (const size of [192, 512]) {
    const padding = Math.round(size * 0.1);
    const innerSize = size - (padding * 2);

    await sharp(svgBuffer)
      .resize(innerSize, innerSize)
      .extend({
        top: padding,
        bottom: padding,
        left: padding,
        right: padding,
        background: { r: 15, g: 23, b: 42, alpha: 1 } // #0f172a
      })
      .png()
      .toFile(join(iconsDir, `icon-maskable-${size}x${size}.png`));
    console.log(`  Generated icon-maskable-${size}x${size}.png`);
  }

  // Generate apple-touch-icon (180x180)
  await sharp(svgBuffer)
    .resize(180, 180)
    .png()
    .toFile(join(iconsDir, 'apple-touch-icon.png'));
  console.log('  Generated apple-touch-icon.png');

  // Generate favicon (32x32)
  await sharp(svgBuffer)
    .resize(32, 32)
    .png()
    .toFile(join(iconsDir, 'favicon-32x32.png'));
  console.log('  Generated favicon-32x32.png');

  // Generate favicon (16x16)
  await sharp(svgBuffer)
    .resize(16, 16)
    .png()
    .toFile(join(iconsDir, 'favicon-16x16.png'));
  console.log('  Generated favicon-16x16.png');

  console.log('Done! All icons generated successfully.');
}

generateIcons().catch(console.error);
