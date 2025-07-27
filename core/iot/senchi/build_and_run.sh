#!/bin/bash

# SwitchBot Leak Detector iOS App - Build and Run Script
# This script helps build and run the iOS app for testing

echo "🔧 SwitchBot Leak Detector iOS App - Build Script"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "senchi.xcodeproj/project.pbxproj" ]; then
    echo "❌ Error: senchi.xcodeproj not found. Please run this script from the senchi directory."
    exit 1
fi

# Check if Xcode is available
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Error: Xcode command line tools not found. Please install Xcode."
    exit 1
fi

echo "✅ Xcode found"
echo "📱 Building SwitchBot Leak Detector app..."

# List available simulators
echo "📋 Available iOS Simulators:"
xcrun simctl list devices available | grep "iPhone\|iPad" | head -5

# Build the project
echo "🔨 Building project..."
xcodebuild -project senchi.xcodeproj -scheme senchi -destination 'platform=iOS Simulator,name=iPhone 15' build

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "🎯 Next Steps:"
    echo "1. Open senchi.xcodeproj in Xcode"
    echo "2. Select your target device (iPhone/iPad or Simulator)"
    echo "3. Press Cmd+R to build and run"
    echo ""
    echo "📱 App Features:"
    echo "- Bluetooth device scanning"
    echo "- SwitchBot leak detector connection"
    echo "- Real-time sensor data monitoring"
    echo "- Leak detection alerts"
    echo ""
    echo "🔧 Target Device:"
    echo "- MAC Address: ECD25189-92D0-6712-8C02-86B4D17BA636"
    echo "- Device Type: SwitchBot Leak Detector"
    echo "- Service UUID: 0000fd3d-0000-1000-8000-00805f9b34fb"
else
    echo "❌ Build failed. Please check the error messages above."
    exit 1
fi

echo ""
echo "📖 For more information, see README.md" 