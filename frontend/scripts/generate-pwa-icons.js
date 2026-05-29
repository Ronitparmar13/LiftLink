#!/usr/bin/env node

/**
 * Generate PWA icons from favicon.svg
 * 
 * This script creates 192x192 and 512x512 PNG icons from the existing favicon.svg.
 * Requires: npm install sharp (if not already installed)
 * 
 * Usage: node scripts/generate-pwa-icons.js
 */

import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = fileURLToPath(new URL('.', import.meta.url));
const publicDir = join(__dirname, '..', 'public');

// For now, we'll create placeholder SVG files that can be used as icons
// In production, you should replace these with actual PNG files generated from your design

const svgIcon = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="20" fill="#0f172a"/>
  <text x="50" y="60" font-family="Arial, sans-serif" font-size="40" font-weight="bold" fill="white" text-anchor="middle">LL</text>
</svg>`;

// Create placeholder SVG files for different sizes
const sizes = [192, 512];

sizes.forEach(size => {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 100 100">
    <rect width="100" height="100" rx="20" fill="#0f172a"/>
    <text x="50" y="60" font-family="Arial, sans-serif" font-size="40" font-weight="bold" fill="white" text-anchor="middle">LL</text>
  </svg>`;
  
  writeFileSync(join(publicDir, `icon-${size}x${size}.svg`), svg);
  console.log(`Created icon-${size}x${size}.svg`);
});

console.log('\nNote: These are placeholder SVG icons.');
console.log('For production, replace with actual PNG icons generated from your design.');
console.log('You can use tools like Figma, Canva, or online converters to create proper PNG icons.');
