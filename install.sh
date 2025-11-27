#!/bin/bash
set -e

echo "🌉 SyntaxBridge-iOS Installer"
echo "============================="

# Check dependencies
if ! command -v swift &> /dev/null; then
    echo "❌ Error: Swift is not installed."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    exit 1
fi



# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Build Swift Tool
echo "🔨 Building Swift Summarizer..."
cd tools/swift-summarizer
swift build -c release
cd ../..

echo "✅ Build Complete!"
echo ""
echo "To use this hook, configure your MCP server or Claude config to point to:"
echo "$(pwd)/hooks/syntax-bridge-hook.sh"
echo ""
echo "Example (.claude.json):"
echo "{"
echo "  \"hooks\": {"
echo "    \"PreToolUse\": \"$(pwd)/hooks/syntax-bridge-hook.sh\""
echo "  }"
echo "}"
