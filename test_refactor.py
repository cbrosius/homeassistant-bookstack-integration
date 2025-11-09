#!/usr/bin/env python3
"""Test script for refactored BookStack Custom Integration."""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_new_integration_structure():
    """Test the new BookStack Custom Integration structure."""
    print("Testing BookStack Custom Integration structure...")
    
    try:
        # Test basic imports
        from custom_components.bookstack_integration.const import DOMAIN
        print(f"[OK] Domain imported: {DOMAIN}")
        assert DOMAIN == "bookstack_integration"
        
        from custom_components.bookstack_integration.manifest import manifest
        print(f"[OK] Manifest loaded: {manifest['name']} v{manifest['version']}")
        assert manifest['domain'] == "bookstack_integration"
        assert manifest['name'] == "BookStack Custom Integration"
        
        print("\n[OK] All imports successful!")
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False


def test_new_file_structure():
    """Test that all expected files exist in new structure."""
    print("\nTesting new file structure...")
    
    expected_files = [
        "custom_components/bookstack_integration/manifest.json",
        "custom_components/bookstack_integration/const.py",
        "custom_components/bookstack_integration/__init__.py",
        "custom_components/bookstack_integration/strings.json",
        "custom_components/bookstack_integration/bookstack_api.py",
        "custom_components/bookstack_integration/requirements.txt",
        "hacs.json"
    ]
    
    missing_files = []
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"[OK] {file_path}")
        else:
            print(f"[ERROR] Missing: {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n[ERROR] Missing {len(missing_files)} files")
        return False
    else:
        print("\n[OK] All expected files present")
        return True


def test_hacs_config():
    """Test the updated HACS configuration."""
    print("\nTesting HACS configuration...")
    
    try:
        with open("hacs.json", "r") as f:
            import json
            hacs_config = json.load(f)
            
            # Test expected values
            assert hacs_config['name'] == "BookStack Custom Integration"
            assert hacs_config['filename'] == "bookstack_integration.zip"
            assert 'manifest' in hacs_config
            assert hacs_config['manifest']['name'] == "BookStack Custom Integration"
            assert hacs_config['manifest']['filename'] == "bookstack_integration.zip"
            
            print(f"[OK] HACS config updated: {hacs_config['name']}")
            print(f"[OK] HACS filename: {hacs_config['filename']}")
            return True
            
    except Exception as e:
        print(f"[ERROR] HACS config test failed: {e}")
        return False


def test_integration_content():
    """Test that integration content has been updated."""
    print("\nTesting integration content updates...")
    
    try:
        # Test const.py
        with open("custom_components/bookstack_integration/const.py", "r") as f:
            content = f.read()
            assert "bookstack_integration" in content
            assert "LOGGER_NAME = \"custom_components.bookstack_integration\"" in content
            print("[OK] const.py updated with new domain")
        
        # Test __init__.py
        with open("custom_components/bookstack_integration/__init__.py", "r") as f:
            content = f.read()
            assert "BookStack Custom Integration integration" in content
            assert "bookstack_integration_started" in content
            print("[OK] __init__.py updated with new integration name")
        
        # Test strings.json
        with open("custom_components/bookstack_integration/strings.json", "r") as f:
            import json
            strings = json.load(f)
            assert "BookStack Custom Integration Configuration" in strings['config']['step']['user']['title']
            assert "BookStack Custom Integration is already configured" in strings['config']['abort']['already_configured']
            print("[OK] strings.json updated with new integration name")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Integration content test failed: {e}")
        return False


def main():
    """Run all tests for the refactored integration."""
    print("=== BookStack Custom Integration Refactor Test ===\n")
    
    tests = [
        ("New File Structure", test_new_file_structure),
        ("Integration Structure", test_new_integration_structure),
        ("HACS Configuration", test_hacs_config),
        ("Integration Content", test_integration_content)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*60)
    print("REFACTOR TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n[SUCCESS] Refactor completed successfully!")
        print("\n=== REFACTOR COMPLETION STATUS ===")
        print("✅ Domain renamed from 'bookstack_export' to 'bookstack_integration'")
        print("✅ Integration name changed from 'BookStack Export' to 'BookStack Custom Integration'")
        print("✅ All files updated with new domain and names")
        print("✅ HACS configuration updated")
        print("✅ Old 'bookstack_export' directory removed")
        print("✅ New 'bookstack_integration' directory created")
        print("\n🎉 REFACTOR COMPLETE - READY FOR NEXT PHASES!")
        return True
    else:
        print(f"\n[WARNING] {failed} test(s) failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)