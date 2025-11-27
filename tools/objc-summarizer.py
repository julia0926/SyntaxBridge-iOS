#!/usr/bin/env python3
import sys
import os
from clang.cindex import Index, CursorKind, Config

def setup_libclang():
    # Try to find libclang if not in path
    # On macOS with Xcode, it's often in the developer tools
    try:
        from clang.cindex import Config
        # If library_file is not set, it might fail on some systems
        # But let's assume the user has a working environment or we might need to point to Xcode's libclang
        pass
    except ImportError:
        print("Error: python-clang bindings not found. Please install with `pip install libclang`")
        sys.exit(1)

def summarize_cursor(cursor, depth=0):
    # We only want to print the interface/implementation structure
    # and method declarations, but hide the implementation details.
    
    try:
        # Filter out system headers: only process cursors from the main file
        # cursor.location.file can be None for TranslationUnit
        if cursor.kind != CursorKind.TRANSLATION_UNIT:
            if cursor.location.file and cursor.location.file.name != sys.argv[1] and not cursor.location.file.name.endswith(sys.argv[1]):
                return

        if cursor.kind == CursorKind.TRANSLATION_UNIT:
            for child in cursor.get_children():
                summarize_cursor(child, depth)
            return

        # Handle Interface and Implementation
        if cursor.kind in [CursorKind.OBJC_INTERFACE_DECL, CursorKind.OBJC_IMPLEMENTATION_DECL, CursorKind.OBJC_PROTOCOL_DECL, CursorKind.OBJC_CATEGORY_DECL, CursorKind.OBJC_CATEGORY_IMPL_DECL]:
            print(f"{'  ' * depth}// Line: {cursor.location.line}")
            print(f"{'  ' * depth}{cursor.spelling} ({cursor.kind.name}) {{")
            for child in cursor.get_children():
                summarize_cursor(child, depth + 1)
            print(f"{'  ' * depth}}}")
            return

        # Handle Methods
        if cursor.kind in [CursorKind.OBJC_INSTANCE_METHOD_DECL, CursorKind.OBJC_CLASS_METHOD_DECL]:
            # Reconstruct method signature roughly
            # This is complex to do perfectly from cursor, but we can print the displayname
            print(f"{'  ' * depth}// Line: {cursor.location.line}")
            print(f"{'  ' * depth}{cursor.displayname};")
            return

        # Handle Properties
        if cursor.kind == CursorKind.OBJC_PROPERTY_DECL:
            print(f"{'  ' * depth}// Line: {cursor.location.line}")
            print(f"{'  ' * depth}@property {cursor.displayname};")
            return
            
    except ValueError:
        # Skip unknown cursor kinds
        return
    except Exception as e:
        # print(f"Error processing cursor: {e}", file=sys.stderr)
        return
        
    # Ignore other details inside implementation (like variable decls in methods, etc.)
    # But wait, methods in @implementation have bodies. We want to skip the bodies.
    # The children of a method decl in implementation are the statements.
    # So we just print the method name and stop recursing.
    
    # If we are here, it's likely something else we might want to ignore or print
    # For now, let's only recurse if it's a container
    pass

def main():
    if len(sys.argv) < 2:
        print("Usage: objc-summarizer.py <file-path>")
        sys.exit(1)

    file_path = sys.argv[1]
    
    # Initialize index
    index = Index.create()
    
    # Parse file
    # We might need to pass some basic args like -ObjC
    tu = index.parse(file_path, args=['-x', 'objective-c', '-ObjC'])
    
    summarize_cursor(tu.cursor)

if __name__ == "__main__":
    main()
