#!/bin/bash

echo "🔍 Debugging Vite setup..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Not in frontend directory. Please run from frontend/ directory"
    exit 1
fi

echo "📦 Clearing caches and reinstalling..."

# Clear npm cache
npm cache clean --force

# Remove node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Clear Vite cache
rm -rf .vite

# Reinstall dependencies
echo "Installing dependencies..."
npm install

echo "✅ Setup complete. Try running 'npm run dev' again."
echo ""
echo "If you still get MIME type errors, try:"
echo "1. Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)"
echo "2. Clear browser cache"
echo "3. Try a different browser"
echo "4. Check if any browser extensions are interfering"
