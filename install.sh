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


# ---------------------------------------------------------
# Agent Configuration Injection
# ---------------------------------------------------------

RULES_CONTENT='
# SyntaxBridge Integration Rules

1. **Reading Files**: When reading large Swift or Objective-C files, the system will automatically provide a summarized version via SyntaxBridge. If you need the full implementation of a specific function, use `read_file` with the specific line range indicated by `// Line: ...` comments.

2. **Project Navigation**: When asked to explore the project structure or find specific classes/symbols, DO NOT use `ls -R` or `find`. Instead, execute:
   `./tools/generate-map.sh`
   This provides a high-level map of all classes, structs, and protocols without reading file contents.
'

echo "🤖 Configuring Agent Rules..."

# List of target configuration files
CONFIG_FILES=(".cursorrules" ".windsurfrules" "CLAUDE.md")
INJECTED=false

for FILE in "${CONFIG_FILES[@]}"; do
    if [ -f "$FILE" ]; then
        # Check if rules already exist to avoid duplication
        if grep -q "SyntaxBridge Integration Rules" "$FILE"; then
            echo "  - $FILE: Rules already present. Skipping."
        else
            echo "" >> "$FILE"
            echo "$RULES_CONTENT" >> "$FILE"
            echo "  - $FILE: ✅ Rules injected successfully."
            INJECTED=true
        fi
    fi
done

if [ "$INJECTED" = false ]; then
    echo "  ℹ️  No existing agent configuration files found (or rules already present)."
    echo "      If you use Cursor, Windsurf, or Claude Code, consider creating a"
    echo "      .cursorrules or CLAUDE.md file and running this script again,"
    echo "      or manually adding the rules from README.md."
fi

echo ""

# Set execution permissions
echo "🔑 Setting permissions..."
chmod +x tools/objc-summarizer-v2.py
chmod +x tools/generate-map.sh
chmod +x hooks/syntax-bridge-hook.sh

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
