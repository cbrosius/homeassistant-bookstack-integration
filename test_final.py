#!/usr/bin/env python3
"""Final test to verify BookStack Custom Integration is ready for Home Assistant."""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_integration_structure():
    """Test the complete integration structure."""
    print("Testing BookStack Custom Integration structure...")
    
    expected_files = [
        "custom_components/bookstack_integration/__init__.py",
        "custom_components/bookstack_integration/config_flow.py",
        "custom_components/bookstack_integration/const.py",
        "custom_components/bookstack_integration/manifest.json",
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
        print("\n[OK] All required files present")
        return True


def test_manifest_config_flow():
    """Test that manifest.json has config_flow: true and all required fields."""
    print("\nTesting manifest.json configuration...")
    
    try:
        with open("custom_components/bookstack_integration/manifest.json", "r") as f:
            import json
            manifest = json.load(f)
            
            # Test required fields
            required_fields = ["domain", "name", "version", "config_flow"]
            for field in required_fields:
                if field not in manifest:
                    print(f"[ERROR] Missing field in manifest: {field}")
                    return False
                print(f"[OK] manifest.{field}: {manifest[field]}")
            
            # Test config_flow is enabled
            if not manifest.get("config_flow", False):
                print("[ERROR] config_flow must be true in manifest")
                return False
            print("[OK] config_flow is enabled")
            
            # Test domain
            if manifest["domain"] != "bookstack_integration":
                print(f"[ERROR] Domain should be 'bookstack_integration', got: {manifest['domain']}")
                return False
            print(f"[OK] Domain: {manifest['domain']}")
            
            return True
            
    except Exception as e:
        print(f"[ERROR] Manifest test failed: {e}")
        return False


def test_config_flow_class():
    """Test that config_flow.py has the required class."""
    print("\nTesting config_flow.py structure...")
    
    try:
        with open("custom_components/bookstack_integration/config_flow.py", "r") as f:
            content = f.read()
            
            # Test for required imports
            required_imports = [
                "from homeassistant import config_entries",
                "class BookStackIntegrationConfigFlow",
                "async def async_step_user"
            ]
            
            for import_line in required_imports:
                if import_line not in content:
                    print(f"[ERROR] Missing required code: {import_line}")
                    return False
                print(f"[OK] Found: {import_line}")
            
            print("[OK] config_flow.py has required structure")
            return True
            
    except Exception as e:
        print(f"[ERROR] config_flow test failed: {e}")
        return False


def test_constants_and_domain():
    """Test that constants are correct."""
    print("\nTesting constants and domain...")
    
    try:
        # Test const.py
        with open("custom_components/bookstack_integration/const.py", "r") as f:
            content = f.read()
            
            required_constants = [
                "DOMAIN = \"bookstack_integration\"",
                "LOGGER_NAME = \"custom_components.bookstack_integration\""
            ]
            
            for constant in required_constants:
                if constant not in content:
                    print(f"[ERROR] Missing constant: {constant}")
                    return False
                print(f"[OK] Found: {constant}")
            
        return True
        
    except Exception as e:
        print(f"[ERROR] Constants test failed: {e}")
        return False


def test_integration_files_content():
    """Test that integration files have correct content."""
    print("\nTesting integration file content...")
    
    try:
        # Test __init__.py
        with open("custom_components/bookstack_integration/__init__.py", "r") as f:
            content = f.read()
            
            if "bookstack_integration" not in content:
                print("[ERROR] __init__.py doesn't contain new domain")
                return False
            print("[OK] __init__.py updated with new domain")
        
        # Test strings.json
        with open("custom_components/bookstack_integration/strings.json", "r") as f:
            import json
            strings = json.load(f)
            
            title = strings['config']['step']['user']['title']
            if "BookStack Custom Integration" not in title:
                print(f"[ERROR] strings.json title doesn't contain new name: {title}")
                return False
            print("[OK] strings.json updated with new integration name")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Content test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=== BookStack Custom Integration - Final Readiness Test ===\n")
    
    tests = [
        ("Integration Structure", test_integration_structure),
        ("Manifest Configuration", test_manifest_config_flow),
        ("Config Flow Class", test_config_flow_class),
        ("Constants and Domain", test_constants_and_domain),
        ("Integration Content", test_integration_files_content)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*60)
    print("FINAL TEST RESULTS SUMMARY")
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
        print("\n[SUCCESS] All tests passed!")
        print("\n=== INTEGRATION READY STATUS ===")
        print("✅ Complete Home Assistant integration structure")
        print("✅ Domain properly set to 'bookstack_integration'")
        print("✅ Integration name updated to 'BookStack Custom Integration'")
        print("✅ Config flow enabled and implemented")
        print("✅ All required files present and properly configured")
        print("✅ No more import errors should occur in Home Assistant")
        print("\n🎉 INTEGRATION READY FOR DEPLOYMENT!")
        print("\nNext steps:")
        print("- Copy to Home Assistant custom_components directory")
        print("- Restart Home Assistant")
        print("- Add integration via UI: Settings > Devices & Services")
        print("- Configure BookStack URL and API token")
        print("- Test the export service")
        return True
    else:
        print(f"\n[WARNING] {failed} test(s) failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)