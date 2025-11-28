# SyntaxBridge-iOS 🌉

**Intelligent Context Optimization Tool for Mixed Swift & Objective-C Projects**

Designed to solve **"Context Corruption"** and **"Token Waste"** when using LLMs (Claude, GPT, etc.) in large-scale iOS projects.

## 🚀 Key Features

### 1. Intelligent Summarization
Instead of reading the entire file, it extracts only the **Declarations** while hiding the **Implementations**.
- **Swift**: Uses `SwiftSyntax` to **rewrite** the AST. It strips function bodies, property initializers, and enum values while preserving the original code structure. Unlike `SourceKitten` which outputs JSON documentation, this tool outputs valid, compilable Swift "skeleton code" that is more natural for LLMs to read.
- **Objective-C**: Uses **Regex-based text scanning** (Python) to extract interfaces, implementations, and method signatures. This approach provides robust summarization for legacy codebases without requiring a full build environment or complex dependency resolution (unlike `LibClang`).

### 2. Hybrid Support
- Fully supports both modern **Swift** and legacy **Objective-C** code.
- Parses AST without building (Zero-Build), completing analysis in **under 0.1 seconds**.

### 3. Token Saving
- Saves **approx. 90% of tokens** compared to the original code.
- Efficiently uses the LLM's Context Window, allowing simultaneous analysis of more files.

### 4. Precise Location Tracking
- Automatically injects **Line Number Comments** (`// Line: 123`) into the summarized code.
- Enables the LLM to pinpoint the exact location of functions or properties in the original file.
- Facilitates efficient partial file reading (`read_file` with line ranges).

## 📊 Performance & Verification

### Test Environment
- **Swift**: `LargeManager.swift` (~2,000 lines)
- **Objective-C**: `LegacyManager.m` (~2,000 lines)

### Results
| Metric | Original (Before) | SyntaxBridge (After) | Improvement |
| :--- | :--- | :--- | :--- |
| **Swift (Manager)** | 81 KB | 17 KB | **~79% Reduction** |
| **ObjC (Manager)** | 65 KB | 3 KB | **~95% Reduction** |
| **Analysis Time** | - | < 0.1s | **Instant** |

- **Accuracy**: Verified that all function declarations and properties are extracted without omission.
- **Stability**: Confirmed operation even on files with minor build errors (within AST parsing limits).

## 📦 Installation

### Prerequisites
- **Swift** (installed via Xcode or Toolchain)
- **Python 3**

1. Clone the repository.
2. Run the installation script.
   ```bash
   ./install.sh
   ```
   This script installs necessary Python dependencies (`libclang`) and builds the Swift tool.

3. Register the hook in your Claude config file (`.claude.json` or MCP config).
   ```json
   {
     "hooks": {
       "PreToolUse": "/path/to/SyntaxBridge-iOS/hooks/syntax-bridge-hook.sh"
     }
   }
   ```

## 🛠 How It Works

When the LLM attempts to read a file using the `read_file` tool, the **SyntaxBridge Hook** intervenes.
1. Checks if the file size is over 300 lines.
2. Detects the language (Swift/ObjC) and executes the appropriate summarizer tool (`swift-summarizer` or `objc-summarizer.py`).
3. Delivers the generated **Skeleton Code** to the LLM instead of the raw file.
4. The LLM grasps the overall structure and requests specific implementation details only when needed.

👉 **[See Detailed Examples (Before & After)](docs/DEMO.md)**

## 📝 License
MIT License
