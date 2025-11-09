#!/usr/bin/env python3
"""Simple test for BookStack client without Home Assistant dependencies."""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_bookstack_client_standalone():
    """Test BookStackClient without Home Assistant dependencies."""
    print("Testing BookStack client (standalone)...")
    
    try:
        # Import only the BookStack client components
        from custom_components.bookstack_integration.bookstack_api import (
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
        print("[OK] All BookStack client components imported successfully")
        
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
        print(f"[ERROR] BookStack client test failed: {e}")
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
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Integration files test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=== BookStack Export Integration Test (Simplified) ===\n")
    
    tests = [
        ("Integration Files", test_integration_files),
        ("BookStack Client (Standalone)", test_bookstack_client_standalone)
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
        print("\n[SUCCESS] All core tests passed! Integration structure is correct.")
        print("\nNext steps:")
        print("- Phase 1 (Foundation) is COMPLETE!")
        print("- Ready to proceed with Phase 2 (Config Flow)")
        print("- Ready to proceed with Phase 3 (Data Export Engine)")
        return True
    else:
        print(f"\n[WARNING] {failed} test(s) failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)