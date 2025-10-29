#!/bin/bash

# 🚀 Miluv.app Production Build Script
# This script helps you build Android & iOS apps easily

echo "🎯 Miluv.app Production Build Helper"
echo "======================================"
echo ""

# Check if EAS CLI is installed
if ! command -v eas &> /dev/null; then
    echo "❌ EAS CLI not found. Installing..."
    npm install -g eas-cli
    echo "✅ EAS CLI installed"
else
    echo "✅ EAS CLI found"
fi

echo ""
echo "Select build option:"
echo "1) 📱 Build Android APK (for testing)"
echo "2) 📦 Build Android AAB (for Play Store)"
echo "3) 🍎 Build iOS IPA (for App Store)"
echo "4) 🔥 Build Both (Android + iOS)"
echo "5) ⚡ Development Build (Debug mode)"
echo "6) 📊 View Build Status"
echo "7) 🔐 Configure Credentials"
echo "8) 📝 View Build History"
echo "9) ❌ Exit"
echo ""

read -p "Enter option (1-9): " option

cd /app/frontend

case $option in
    1)
        echo ""
        echo "🚀 Building Android APK (Preview)..."
        echo "This will take 15-25 minutes"
        eas build --platform android --profile preview
        ;;
    2)
        echo ""
        echo "🚀 Building Android AAB (Production)..."
        echo "This will take 20-30 minutes"
        eas build --platform android --profile production
        ;;
    3)
        echo ""
        echo "🚀 Building iOS IPA (Production)..."
        echo "⚠️  Requires Apple Developer Account ($99/year)"
        echo "This will take 25-35 minutes"
        eas build --platform ios --profile production
        ;;
    4)
        echo ""
        echo "🚀 Building Android + iOS (Production)..."
        echo "⚠️  iOS requires Apple Developer Account"
        echo "This will take 30-45 minutes"
        eas build --platform all --profile production
        ;;
    5)
        echo ""
        echo "⚡ Building Development APK..."
        echo "This will take 10-15 minutes"
        eas build --platform android --profile development
        ;;
    6)
        echo ""
        echo "📊 Build Status:"
        eas build:list --limit 10
        ;;
    7)
        echo ""
        echo "🔐 Configuring Credentials..."
        eas credentials
        ;;
    8)
        echo ""
        echo "📝 Build History:"
        eas build:list --limit 20
        ;;
    9)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "✅ Command executed!"
echo ""
echo "📱 Monitor your build at:"
echo "https://expo.dev"
echo ""
echo "💡 Tip: Use 'eas build:list' to check build status"
