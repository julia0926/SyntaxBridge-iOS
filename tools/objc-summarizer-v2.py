#!/usr/bin/env python3
"""
Enhanced Objective-C Summarizer v2
Uses regex-based parsing for better method extraction
since libclang has limitations parsing method implementations.
"""
import sys
import os
import re

def extract_methods_from_source(content):
    """Extract Objective-C method signatures from source using regex."""
    methods = []

    # Pattern for instance/class methods
    # Matches: - (ReturnType)methodName:(Type)param1 otherParam:(Type)param2
    method_pattern = r'^[\s]*([+-])\s*\(([^)]+)\)\s*([^{;]+?)(?:\s*\{|\s*;)'

    lines = content.split('\n')
    current_line_num = 0

    for i, line in enumerate(lines):
        current_line_num = i + 1

        # Skip comments and preprocessor directives
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('#'):
            continue

        match = re.match(method_pattern, line)
        if match:
            prefix = match.group(1)  # + or -
            return_type = match.group(2).strip()
            signature = match.group(3).strip()

            methods.append({
                'prefix': prefix,
                'return_type': return_type,
                'signature': signature,
                'line': current_line_num
            })

    return methods

def extract_properties_from_source(content):
    """Extract @property declarations from source."""
    properties = []

    # Pattern for @property
    property_pattern = r'^\s*@property\s*(\([^)]*\))?\s*([^;]+);'

    lines = content.split('\n')

    for i, line in enumerate(lines):
        match = re.match(property_pattern, line)
        if match:
            attributes = match.group(1) if match.group(1) else ''
            declaration = match.group(2).strip()

            properties.append({
                'attributes': attributes,
                'declaration': declaration,
                'line': i + 1
            })

    return properties

def extract_ivars_from_implementation(content):
    """Extract instance variables from @implementation or @interface blocks."""
    ivars = []

    # Look for blocks like:
    # @interface ClassName {
    #   ivar declarations
    # }
    # or
    # @implementation ClassName {
    #   ivar declarations
    # }

    ivar_block_pattern = r'@(?:interface|implementation)[^{]*\{([^}]*)\}'

    for match in re.finditer(ivar_block_pattern, content, re.MULTILINE | re.DOTALL):
        block_content = match.group(1)
        lines = block_content.split('\n')

        for line in lines:
            stripped = line.strip()

            # Skip empty lines and comments
            if not stripped or stripped.startswith('//') or stripped.startswith('/*'):
                continue

            # Simple ivar pattern: Type *name; or Type name;
            ivar_pattern = r'^\s*(\w+\s*\*?)\s+(\w+)\s*;'
            match = re.match(ivar_pattern, stripped)
            if match:
                type_name = match.group(1).strip()
                var_name = match.group(2).strip()
                ivars.append({
                    'type': type_name,
                    'name': var_name
                })

    return ivars

def summarize_objc_file(file_path):
    """Summarize an Objective-C file showing structure without implementations."""

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Print header with file path for disambiguation
    print("// SyntaxBridge Summary")
    print(f"// File: {file_path}")
    print("// ─────────────────────────────────────────")
    print()

    # Extract different elements
    methods = extract_methods_from_source(content)
    properties = extract_properties_from_source(content)

    # Find @interface and @implementation blocks
    interface_pattern = r'@interface\s+(\w+)(?:\s*:\s*(\w+))?(?:\s*<([^>]+)>)?'
    implementation_pattern = r'@implementation\s+(\w+)'
    category_pattern = r'@(?:interface|implementation)\s+(\w+)\s*\(([^)]*)\)'
    protocol_pattern = r'@protocol\s+(\w+)'

    # Track what we're currently in
    in_interface = False
    in_implementation = False
    current_class = None

    lines = content.split('\n')

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()

        # Check for @interface
        interface_match = re.search(interface_pattern, stripped)
        if interface_match:
            class_name = interface_match.group(1)
            superclass = interface_match.group(2) if interface_match.group(2) else 'NSObject'
            protocols = interface_match.group(3) if interface_match.group(3) else ''

            print(f"// Line: {line_num}")
            print(f"@interface {class_name} : {superclass}", end='')
            if protocols:
                print(f" <{protocols}>", end='')
            print()

            in_interface = True
            current_class = class_name

            # Find the next @end to know where interface ends
            next_end_line = line_num
            for j in range(i+1, len(lines)):
                if lines[j].strip() == '@end':
                    next_end_line = j + 1
                    break

            # Get properties within this interface block
            class_properties = [p for p in properties if line_num < p['line'] < next_end_line]

            # Get methods within this interface block
            class_methods = [m for m in methods if line_num < m['line'] < next_end_line]

            # Print properties first
            for prop in class_properties:
                print(f"  // Line: {prop['line']}")
                print(f"  @property {prop['attributes']}{prop['declaration']};")

            # Print method declarations
            for method in class_methods:
                print(f"  // Line: {method['line']}")
                print(f"  {method['prefix']} ({method['return_type']}){method['signature']};")

            print(f"@end")
            print()
            in_interface = False
            continue

        # Check for @implementation
        impl_match = re.search(implementation_pattern, stripped)
        if impl_match:
            class_name = impl_match.group(1)

            print(f"// Line: {line_num}")
            print(f"@implementation {class_name}")

            in_implementation = True
            current_class = class_name

            # Print methods for this implementation
            # Find the next @end to know where implementation ends
            next_end_line = line_num
            for j in range(i+1, len(lines)):
                if lines[j].strip() == '@end':
                    next_end_line = j + 1
                    break

            # Get methods within this implementation block
            class_methods = [m for m in methods if line_num < m['line'] < next_end_line]

            for method in class_methods:
                print(f"  // Line: {method['line']}")
                print(f"  {method['prefix']} ({method['return_type']}){method['signature']};")

            print(f"@end")
            print()
            in_implementation = False
            continue

        # Check for category
        category_match = re.search(category_pattern, stripped)
        if category_match:
            class_name = category_match.group(1)
            category_name = category_match.group(2) if category_match.group(2) else '(anonymous)'

            print(f"// Line: {line_num}")
            print(f"@interface {class_name} (Category: {category_name})")
            print(f"@end")
            print()
            continue

        # Check for @protocol
        protocol_match = re.search(protocol_pattern, stripped)
        if protocol_match:
            protocol_name = protocol_match.group(1)

            print(f"// Line: {line_num}")
            print(f"@protocol {protocol_name}")
            print(f"@end")
            print()
            continue

        # Check for @end
        # Note: @interface and @implementation blocks now handle their own @end output
        # This is kept for cleanup of state flags in case of parsing issues
        if stripped == '@end':
            in_interface = False
            in_implementation = False
            current_class = None

def generate_map(file_path):
    """Generate a JSON map of symbols in the file."""
    if not os.path.exists(file_path):
        print("{}", end='')
        return

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    methods = extract_methods_from_source(content)
    
    # Simple regex scanning for classes/protocols
    symbols = []
    
    # Interfaces
    for match in re.finditer(r'@interface\s+(\w+)', content):
        symbols.append({
            "name": match.group(1),
            "type": "interface",
            "line": content[:match.start()].count('\n') + 1
        })
        
    # Implementations
    for match in re.finditer(r'@implementation\s+(\w+)', content):
        symbols.append({
            "name": match.group(1),
            "type": "implementation",
            "line": content[:match.start()].count('\n') + 1
        })
        
    # Protocols
    for match in re.finditer(r'@protocol\s+(\w+)', content):
        symbols.append({
            "name": match.group(1),
            "type": "protocol",
            "line": content[:match.start()].count('\n') + 1
        })

    # Add methods
    for method in methods:
        symbols.append({
            "name": f"{method['prefix']}{method['signature']}",
            "type": "method",
            "line": method['line']
        })
        
    # Sort by line number
    symbols.sort(key=lambda x: x['line'])
    
    import json
    output = {
        "filePath": file_path,
        "symbols": symbols
    }
    print(json.dumps(output, indent=2))

def main():
    if len(sys.argv) < 2:
        print("Usage: objc-summarizer-v2.py <file-path> OR objc-summarizer-v2.py --map <file-path>", file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] == "--map":
        if len(sys.argv) < 3:
            print("Usage: objc-summarizer-v2.py --map <file-path>", file=sys.stderr)
            sys.exit(1)
        generate_map(sys.argv[2])
    else:
        file_path = sys.argv[1]
        summarize_objc_file(file_path)

if __name__ == "__main__":
    main()
