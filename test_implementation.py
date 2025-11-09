#!/usr/bin/env python3
"""Test script to validate the BookStack integration implementation."""

import ast
import sys
from pathlib import Path


def check_python_syntax(file_path: Path) -> bool:
    """Check if a Python file has valid syntax."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file to check for syntax errors
        ast.parse(content)
        print(f"[OK] {file_path.name}: Syntax valid")
        return True
    except SyntaxError as e:
        print(f"[ERROR] {file_path.name}: Syntax error - {e}")
        return False
    except Exception as e:
        print(f"[ERROR] {file_path.name}: Error - {e}")
        return False


def check_imports():
    """Check if imports work correctly."""
    try:
        # Add the custom_components directory to the Python path
        sys.path.insert(0, str(Path(__file__).parent / 'custom_components'))
        
        # Test importing the BookStack API
        from bookstack_integration.bookstack_api import (
            BookStackClient, BookStackConfig, Book, Chapter, Page, Shelf
        )
        print("[OK] BookStack API imports successful")
        
        # Test importing constants
        from bookstack_integration.const import DOMAIN, DEFAULT_TIMEOUT
        print("[OK] Constants import successful")
        
        # Test importing the main module
        from bookstack_integration import __init__
        print("[OK] Main module import successful")
        
        return True
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error during import test: {e}")
        return False


def main():
    """Run all validation tests."""
    print("BookStack Integration Implementation Test")
    print("=" * 50)
    
    # Files to check
    files_to_check = [
        Path("custom_components/bookstack_integration/__init__.py"),
        Path("custom_components/bookstack_integration/bookstack_api.py"),
        Path("custom_components/bookstack_integration/const.py"),
        Path("custom_components/bookstack_integration/config_flow.py"),
        Path("custom_components/bookstack_integration/device.py"),
    ]
    
    print("\n1. Syntax Validation:")
    syntax_ok = True
    for file_path in files_to_check:
        if file_path.exists():
            if not check_python_syntax(file_path):
                syntax_ok = False
        else:
            print(f"[ERROR] {file_path.name}: File not found")
            syntax_ok = False
    
    print("\n2. Import Test:")
    imports_ok = check_imports()
    
    print("\n3. Summary:")
    if syntax_ok and imports_ok:
        print("[OK] All tests passed! Implementation appears to be valid.")
        return 0
    else:
        print("[ERROR] Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())