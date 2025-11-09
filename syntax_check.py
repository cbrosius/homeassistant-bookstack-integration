#!/usr/bin/env python3
"""Simple syntax check for config flow."""

import ast
import os

def check_syntax(file_path):
    """Check if a Python file has valid syntax."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Check syntax of key files."""
    print("Checking config flow syntax...")
    
    files_to_check = [
        "custom_components/bookstack_integration/config_flow.py",
        "custom_components/bookstack_integration/const.py",
        "custom_components/bookstack_integration/__init__.py"
    ]
    
    all_ok = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            is_ok, message = check_syntax(file_path)
            status = "OK" if is_ok else "FAIL"
            print(f"{file_path}: {status} - {message}")
            if not is_ok:
                all_ok = False
        else:
            print(f"{file_path}: NOT FOUND")
            all_ok = False
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    exit(main())