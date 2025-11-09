#!/usr/bin/env python3
"""Basic test script to verify BookStack Export integration structure."""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_integration_structure():
    """Test that all integration files can be imported correctly."""
    print("Testing BookStack Export integration structure...")
    
    try:
        # Test basic imports
        from custom_components.bookstack_export.const import DOMAIN
        print(f"[OK] Domain imported: {DOMAIN}")
        
        from custom_components.bookstack_export.manifest import manifest
        print(f"[OK] Manifest loaded: {manifest['name']} v{manifest['version']}")
        
        from custom_components.bookstack_export.bookstack_api import (
            BookStackClient,
            BookStackConfig,
            Book,
            Chapter,
            Page
        )
        print("[OK] BookStack API client components imported")
        
        print("\nAll imports successful!")
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False


def test_bookstack_client():
    """Test BookStackClient initialization."""
    print("\nTesting BookStackClient initialization...")
    
    try:
        from custom_components.bookstack_export.bookstack_api import (
            BookStackClient, BookStackConfig
        )
        
        # Test with valid config
        config = BookStackConfig(
            base_url="https://example.com",
            token="test_token",
            timeout=30
        )
        
        client = BookStackClient(config)
        print("[OK] BookStackClient initialized successfully")
        
        # Test client properties
        assert client.config.base_url == "https://example.com"
        assert client.config.token == "test_token"
        assert "Authorization" in client.session.headers
        print("[OK] Client configuration correct")
        
        # Test cache initialization
        assert client._book_cache is None
        assert client._chapter_cache == {}
        assert client._page_cache == {}
        print("[OK] Client cache properly initialized")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] BookStackClient test failed: {e}")
        return False


def test_data_structures():
    """Test data structure creation."""
    print("\nTesting data structures...")
    
    try:
        from custom_components.bookstack_export.bookstack_api import (
            Book, Chapter, Page
        )
        
        # Test Book
        book = Book(
            id=1,
            name="Test Book",
            slug="test-book",
            description="A test book"
        )
        assert book.id == 1
        assert book.name == "Test Book"
        print("[OK] Book data structure works")
        
        # Test Chapter
        chapter = Chapter(
            id=1,
            book_id=1,
            name="Test Chapter",
            slug="test-chapter"
        )
        assert chapter.id == 1
        assert chapter.book_id == 1
        print("[OK] Chapter data structure works")
        
        # Test Page
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
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Data structure test failed: {e}")
        return False


def test_file_structure():
    """Test that all expected files exist."""
    print("\nTesting file structure...")
    
    expected_files = [
        "custom_components/bookstack_export/manifest.json",
        "custom_components/bookstack_export/const.py",
        "custom_components/bookstack_export/__init__.py",
        "custom_components/bookstack_export/strings.json",
        "custom_components/bookstack_export/bookstack_api.py",
        "custom_components/bookstack_export/requirements.txt",
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
    print("=== BookStack Export Integration Test ===\n")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Integration Structure", test_integration_structure),
        ("BookStackClient", test_bookstack_client),
        ("Data Structures", test_data_structures)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("TEST RESULTS SUMMARY")
    print("="*50)
    
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
        print("\n[SUCCESS] All tests passed! Integration structure is correct.")
        return True
    else:
        print(f"\n[WARNING] {failed} test(s) failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)