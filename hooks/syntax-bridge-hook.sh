#!/bin/bash
# SyntaxBridge-iOS Hook
# Intelligent Context Provision for Mixed Swift & Objective-C Projects

set -eo pipefail

# Threshold: only activate for files with this many lines or more
LINE_THRESHOLD=300

# Read input JSON from stdin
INPUT=$(cat)

# Extract parameters
# Extract parameters using Python (to avoid jq dependency)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('tool_input', {}).get('file_path', ''))")
CURRENT_OFFSET=$(echo "$INPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('tool_input', {}).get('offset', 0))")
CURRENT_LIMIT=$(echo "$INPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('tool_input', {}).get('limit', 2000))")
CWD=$(echo "$INPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('cwd', ''))")

# Determine script directory to find tools
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOOLS_DIR="$SCRIPT_DIR/../tools"

# Detect file type
IS_SWIFT=false
IS_OBJC=false

if [[ "$FILE_PATH" =~ \.swift$ ]]; then
  IS_SWIFT=true
elif [[ "$FILE_PATH" =~ \.(m|h)$ ]]; then
  IS_OBJC=true
else
  # Pass through for other file types
  echo '{
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "allow"
    }
  }'
  exit 0
fi

# Make absolute path
if [[ ! "$FILE_PATH" =~ ^/ ]]; then
  FILE_PATH="$CWD/$FILE_PATH"
fi

# Validate file exists
if [ ! -f "$FILE_PATH" ]; then
  echo '{
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "allow",
      "permissionDecisionReason": "File not found, proceeding with original parameters"
    }
  }'
  exit 0
fi

# Count total lines
TOTAL_LINES=$(wc -l < "$FILE_PATH" | tr -d ' ')

# Only run optimization for large files
if [ "$TOTAL_LINES" -lt "$LINE_THRESHOLD" ]; then
  echo "{
    \"hookSpecificOutput\": {
      \"hookEventName\": \"PreToolUse\",
      \"permissionDecision\": \"allow\",
      \"permissionDecisionReason\": \"Small file ($TOTAL_LINES lines) - no optimization needed\"
    }
  }"
  exit 0
fi

# Run Analysis Tools
SUMMARY_FILE=""
REASON=""

if [ "$IS_SWIFT" = "true" ]; then
  TOOL_PATH="$TOOLS_DIR/swift-summarizer/.build/release/swift-summarizer"
  
  if [ -f "$TOOL_PATH" ]; then
    SUMMARY_FILE=$(mktemp)
    "$TOOL_PATH" "$FILE_PATH" > "$SUMMARY_FILE" 2>/dev/null
    
    if [ -s "$SUMMARY_FILE" ]; then
      REASON="Large file ($TOTAL_LINES lines). Providing intelligent summary (declarations only) via SyntaxBridge (Swift)."
    fi
  fi

elif [ "$IS_OBJC" = "true" ]; then
  TOOL_PATH="$TOOLS_DIR/objc-summarizer.py"
  
  if [ -f "$TOOL_PATH" ]; then
    SUMMARY_FILE=$(mktemp)
    python3 "$TOOL_PATH" "$FILE_PATH" > "$SUMMARY_FILE" 2>/dev/null
    
    if [ -s "$SUMMARY_FILE" ]; then
      REASON="Large file ($TOTAL_LINES lines). Providing intelligent summary (interface only) via SyntaxBridge (ObjC)."
    fi
  fi
fi

# Output Decision
if [ -n "$SUMMARY_FILE" ] && [ -s "$SUMMARY_FILE" ]; then
  # Return the summary file path
  echo "{
    \"hookSpecificOutput\": {
      \"hookEventName\": \"PreToolUse\",
      \"permissionDecision\": \"allow\",
      \"permissionDecisionReason\": \"$REASON\",
      \"updatedInput\": {
        \"file_path\": \"$SUMMARY_FILE\"
      }
    }
  }"
else
  # Fallback
  echo '{
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "allow",
      "permissionDecisionReason": "Analysis tools unavailable or failed, proceeding with original file"
    }
  }'
fi
