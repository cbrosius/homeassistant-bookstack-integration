#!/usr/bin/env python3
"""Direct test for BookStack API components without package imports."""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "custom_components/bookstack_integration")


def test_bookstack_api_directly():
    """Test BookStack API components directly from file."""
    print("Testing BookStack API components directly...")
    
    try:
        # Import directly from the file
        from bookstack_api import (
            BookStackClient,
            BookStackConfig,
            Book,
            Chapter,
            Page,
            BookStackError,
            BookStackAuthError,
            BookStackNotFoundError,
            BookStackRateLimitError
        )
        print("[OK] All BookStack API components imported directly")
        
        # Test data structures
        book = Book(
            id=1,
            name="Test Book",
            slug="test-book",
            description="A test book"
        )
        assert book.id == 1
        assert book.name == "Test Book"
        print("[OK] Book data structure works")
        
        chapter = Chapter(
            id=1,
            book_id=1,
            name="Test Chapter",
            slug="test-chapter"
        )
        assert chapter.id == 1
        assert chapter.book_id == 1
        print("[OK] Chapter data structure works")
        
        page = Page(
            id=1,
            book_id=1,
            chapter_id=1,
            name="Test Page",
            slug="test-page",
            markdown="# Test Content"
        )
        assert page.id == 1
        assert page.markdown == "# Test Content"
        print("[OK] Page data structure works")
        
        # Test configuration
        config = BookStackConfig(
            base_url="https://example.com",
            token="test_token",
            timeout=30
        )
        assert config.base_url == "https://example.com"
        assert config.token == "test_token"
        assert config.timeout == 30
        print("[OK] BookStackConfig works")
        
        # Test client initialization
        client = BookStackClient(config)
        assert client.config == config
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == "Token test_token"
        assert client._book_cache is None
        assert client._chapter_cache == {}
        assert client._page_cache == {}
        print("[OK] BookStackClient initialized successfully")
        
        # Test exception classes
        error = BookStackError("Test error", 500)
        assert str(error) == "Test error"
        assert error.status_code == 500
        
        auth_error = BookStackAuthError("Auth failed", 401)
        assert isinstance(auth_error, BookStackError)
        
        not_found_error = BookStackNotFoundError("Not found", 404)
        assert isinstance(not_found_error, BookStackError)
        
        rate_limit_error = BookStackRateLimitError("Rate limited", 429)
        assert isinstance(rate_limit_error, BookStackError)
        print("[OK] Exception classes work correctly")
        
        # Test cache operations
        client._book_cache = book
        client.clear_cache()
        assert client._book_cache is None
        assert client._chapter_cache == {}
        assert client._page_cache == {}
        print("[OK] Cache operations work correctly")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] BookStack API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_files():
    """Test that all integration files can be read."""
    print("\nTesting integration files...")
    
    try:
        # Test manifest.json
        with open("custom_components/bookstack_integration/manifest.json", "r") as f:
            import json
            manifest = json.load(f)
            assert "domain" in manifest
            assert "name" in manifest
            assert "version" in manifest
            print(f"[OK] manifest.json: {manifest['name']} v{manifest['version']}")
        
        # Test const.py can be imported (basic test)
        with open("custom_components/bookstack_integration/const.py", "r") as f:
            content = f.read()
            assert "DOMAIN" in content
            assert "bookstack_integration" in content
            print("[OK] const.py structure looks correct")
        
        # Test requirements.txt
        with open("custom_components/bookstack_integration/requirements.txt", "r") as f:
            requirements = f.read().strip()
            assert "requests" in requirements
            print(f"[OK] requirements.txt: {requirements}")
        
        # Test hacs.json
        with open("hacs.json", "r") as f:
            import json
            hacs_config = json.load(f)
            assert "name" in hacs_config
            assert "repository" in hacs_config
            print(f"[OK] hacs.json: {hacs_config['name']}")
        
        # Test strings.json
        with open("custom_components/bookstack_integration/strings.json", "r") as f:
            import json
            strings = json.load(f)
            assert "config" in strings
            assert "services" in strings
            print("[OK] strings.json structure looks correct")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Integration files test failed: {e}")
        return False


def test_file_structure():
    """Test that all expected files exist."""
    print("\nTesting file structure...")
    
    expected_files = [
        "custom_components/bookstack_integration/manifest.json",
        "custom_components/bookstack_integration/const.py",
        "custom_components/bookstack_integration/__init__.py",
        "custom_components/bookstack_integration/strings.json",
        "custom_components/bookstack_integration/bookstack_api.py",
        "custom_components/bookstack_integration/requirements.txt",
        "hacs.json",
        ".gitignore",
        "tests/test_bookstack_api.py"
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


def main():
    """Run all tests."""
    print("=== BookStack Export Integration Test (Direct) ===\n")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Integration Files", test_integration_files),
        ("BookStack API (Direct)", test_bookstack_api_directly)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
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
        print("\n[SUCCESS] All core tests passed!")
        print("\n=== PHASE 1 COMPLETION STATUS ===")
        print("✅ Project structure created")
        print("✅ manifest.json with metadata")
        print("✅ const.py - Constants and domain")
        print("✅ __init__.py - Integration setup")
        print("✅ strings.json - UI localization")
        print("✅ bookstack_api.py - BookStack client implementation")
        print("✅ requirements.txt - Dependencies")
        print("✅ hacs.json - HACS compatibility")
        print("✅ .gitignore - Version control")
        print("✅ Basic unit tests for BookStack client")
        print("\n🎉 PHASE 1 (FOUNDATION SETUP) IS COMPLETE!")
        print("\nNext steps:")
        print("- Phase 2: Configuration Flow (config_flow.py)")
        print("- Phase 3: Data Export Engine (exporter.py)")
        print("- Phase 4: Service Integration (services.yaml)")
        return True
    else:
        print(f"\n[WARNING] {failed} test(s) failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)