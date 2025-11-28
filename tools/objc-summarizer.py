#!/usr/bin/env python3
"""
Enhanced Objective-C Summarizer for SyntaxBridge
Extracts class/protocol interfaces, method signatures, and properties
while hiding implementation details for efficient token usage.
"""
import sys
import os
from clang.cindex import Index, CursorKind, Config

# Global variable to store the main file path (absolute)
MAIN_FILE_PATH = None

def setup_libclang():
    # Try to find libclang if not in path
    # On macOS with Xcode, it's often in the developer tools
    try:
        from clang.cindex import Config
        # If library_file is not set, it might fail on some systems
        # But let's assume the user has a working environment or we might need to point to Xcode's libclang
        pass
    except ImportError:
        print("Error: python-clang bindings not found. Please install with `pip install libclang`", file=sys.stderr)
        sys.exit(1)

def is_from_main_file(cursor):
    """Check if cursor is from the main file we're analyzing."""
    if not cursor.location.file:
        return False

    cursor_file = os.path.abspath(cursor.location.file.name)
    return cursor_file == MAIN_FILE_PATH

def summarize_cursor(cursor, depth=0, parent_kind=None):
    # We only want to print the interface/implementation structure
    # and method declarations, but hide the implementation details.

    try:
        # Filter out system headers: only process cursors from the main file
        # cursor.location.file can be None for TranslationUnit
        if cursor.kind != CursorKind.TRANSLATION_UNIT:
            if not is_from_main_file(cursor):
                return

        indent = '  ' * depth

        if cursor.kind == CursorKind.TRANSLATION_UNIT:
            for child in cursor.get_children():
                summarize_cursor(child, depth, cursor.kind)
            return

        # Handle @interface declarations
        if cursor.kind == CursorKind.OBJC_INTERFACE_DECL:
            print(f"{indent}// Line: {cursor.location.line}")
            print(f"{indent}@interface {cursor.spelling}")
            for child in cursor.get_children():
                summarize_cursor(child, depth + 1, cursor.kind)
            print(f"{indent}@end")
            print()
            return

        # Handle @implementation declarations
        if cursor.kind == CursorKind.OBJC_IMPLEMENTATION_DECL:
            print(f"{indent}// Line: {cursor.location.line}")
            print(f"{indent}@implementation {cursor.spelling}")
            for child in cursor.get_children():
                summarize_cursor(child, depth + 1, cursor.kind)
            print(f"{indent}@end")
            print()
            return

        # Handle @protocol declarations
        if cursor.kind == CursorKind.OBJC_PROTOCOL_DECL:
            print(f"{indent}// Line: {cursor.location.line}")
            print(f"{indent}@protocol {cursor.spelling}")
            for child in cursor.get_children():
                summarize_cursor(child, depth + 1, cursor.kind)
            print(f"{indent}@end")
            print()
            return

        # Handle category declarations
        if cursor.kind in [CursorKind.OBJC_CATEGORY_DECL, CursorKind.OBJC_CATEGORY_IMPL_DECL]:
            print(f"{indent}// Line: {cursor.location.line}")
            category_name = cursor.spelling if cursor.spelling else "(anonymous)"
            decl_type = "@interface" if cursor.kind == CursorKind.OBJC_CATEGORY_DECL else "@implementation"
            print(f"{indent}{decl_type} (Category: {category_name})")
            for child in cursor.get_children():
                summarize_cursor(child, depth + 1, cursor.kind)
            print(f"{indent}@end")
            print()
            return

        # Handle properties
        if cursor.kind == CursorKind.OBJC_PROPERTY_DECL:
            print(f"{indent}// Line: {cursor.location.line}")
            print(f"{indent}@property {cursor.displayname};")
            return

        # Handle instance variables (ivars) - both FIELD_DECL and OBJC_IVAR_DECL
        if cursor.kind in [CursorKind.FIELD_DECL, CursorKind.OBJC_IVAR_DECL] and parent_kind in [
            CursorKind.OBJC_INTERFACE_DECL,
            CursorKind.OBJC_IMPLEMENTATION_DECL,
            CursorKind.OBJC_CATEGORY_DECL,
            CursorKind.OBJC_CATEGORY_IMPL_DECL
        ]:
            type_spelling = cursor.type.spelling if cursor.type else "id"
            print(f"{indent}// Line: {cursor.location.line}")
            print(f"{indent}{type_spelling} {cursor.spelling};")
            return

        # Handle methods - show signature only, hide implementation
        if cursor.kind in [CursorKind.OBJC_INSTANCE_METHOD_DECL, CursorKind.OBJC_CLASS_METHOD_DECL]:
            prefix = "-" if cursor.kind == CursorKind.OBJC_INSTANCE_METHOD_DECL else "+"
            return_type = cursor.result_type.spelling if cursor.result_type else "id"

            print(f"{indent}// Line: {cursor.location.line}")
            print(f"{indent}{prefix} ({return_type}){cursor.displayname};")
            # Don't recurse into method body - this saves tokens!
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
    global MAIN_FILE_PATH

    if len(sys.argv) < 2:
        print("Usage: objc-summarizer.py <file-path>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Store absolute path for filtering
    MAIN_FILE_PATH = os.path.abspath(file_path)

    # Initialize clang index
    index = Index.create()

    # Parse with minimal args to avoid compilation errors
    # -x objective-c forces Objective-C mode
    # -Wno-everything suppresses warnings that might clutter output
    tu = index.parse(
        file_path,
        args=[
            '-x', 'objective-c',
            '-Wno-everything',
            '-fsyntax-only'
        ]
    )

    # Check for fatal errors (but still try to output what we can)
    has_fatal_errors = any(
        diag.severity >= 4  # 4 = Error, 5 = Fatal
        for diag in tu.diagnostics
    )

    if has_fatal_errors:
        # Still try to output what we can parse
        pass

    # Summarize the AST
    summarize_cursor(tu.cursor)

if __name__ == "__main__":
    main()
