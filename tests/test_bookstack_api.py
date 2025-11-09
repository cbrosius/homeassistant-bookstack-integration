"""Tests for BookStack API client."""
import unittest
from unittest.mock import Mock, patch

from custom_components.bookstack_integration.bookstack_api import (
    BookStackConfig,
    Book,
    Chapter,
    Page,
    BookStackClient,
    BookStackError,
    BookStackAuthError,
    BookStackNotFoundError,
    BookStackRateLimitError
)


class TestBookStackConfig:
    """Test BookStackConfig dataclass."""
    
    def test_config_creation(self):
        """Test creating a BookStackConfig."""
        config = BookStackConfig(
            base_url="https://example.com",
            token="test_token"
        )
        assert config.base_url == "https://example.com"
        assert config.token == "test_token"
        assert config.timeout == 30  # default value


class TestBookStackDataStructures:
    """Test BookStack data structures."""
    
    def test_book_dataclass(self):
        """Test Book dataclass."""
        book = Book(
            id=1,
            name="Test Book",
            slug="test-book",
            description="A test book"
        )
        assert book.id == 1
        assert book.name == "Test Book"
        assert book.slug == "test-book"
        assert book.description == "A test book"
        assert book.created_at is None
        assert book.updated_at is None
    
    def test_chapter_dataclass(self):
        """Test Chapter dataclass."""
        chapter = Chapter(
            id=1,
            book_id=1,
            name="Test Chapter",
            slug="test-chapter"
        )
        assert chapter.id == 1
        assert chapter.book_id == 1
        assert chapter.name == "Test Chapter"
        assert chapter.slug == "test-chapter"
    
    def test_page_dataclass(self):
        """Test Page dataclass."""
        page = Page(
            id=1,
            book_id=1,
            chapter_id=1,
            name="Test Page",
            slug="test-page",
            markdown="# Test Content"
        )
        assert page.id == 1
        assert page.book_id == 1
        assert page.chapter_id == 1
        assert page.name == "Test Page"
        assert page.markdown == "# Test Content"


class TestBookStackClient:
    """Test BookStackClient class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.config = BookStackConfig(
            base_url="https://example.com",
            token="test_token"
        )
        self.client = BookStackClient(self.config)
    
    def test_client_initialization(self):
        """Test client initialization."""
        assert self.client.config == self.config
        assert "Authorization" in self.client.session.headers
        expected_token = "Token test_token"
        assert self.client.session.headers["Authorization"] == expected_token
        assert self.client._book_cache is None
        assert self.client._chapter_cache == {}
        assert self.client._page_cache == {}
    
    @patch('requests.Session.request')
    def test_test_connection_success(self, mock_request):
        """Test successful connection test."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_request.return_value = mock_response
        
        result = self.client.test_connection()
        assert result is True
    
    @patch('requests.Session.request')
    def test_test_connection_failure(self, mock_request):
        """Test failed connection test."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.content = b'{"error": "Invalid token"}'
        mock_response.json.return_value = {"error": "Invalid token"}
        mock_request.return_value = mock_response
        
        result = self.client.test_connection()
        assert result is False
    
    @patch('requests.Session.request')
    def test_find_book_success(self, mock_request):
        """Test finding an existing book."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": 1, "name": "Test Book", "slug": "test-book"}
            ]
        }
        mock_request.return_value = mock_response
        
        book = self.client.find_book("Test Book")
        assert book is not None
        assert book.id == 1
        assert book.name == "Test Book"
    
    @patch('requests.Session.request')
    def test_find_book_not_found(self, mock_request):
        """Test finding a book that doesn't exist."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_request.return_value = mock_response
        
        book = self.client.find_book("Nonexistent Book")
        assert book is None
    
    def test_book_cache_works(self):
        """Test that book caching works correctly."""
        # Mock a book
        mock_book = Book(id=1, name="Test Book", slug="test-book")
        self.client._book_cache = mock_book
        
        # Should return cached book
        result = self.client.find_or_create_book("Test Book")
        assert result == mock_book
    
    def test_clear_cache(self):
        """Test clearing the client cache."""
        # Set up some cache data
        self.client._book_cache = Book(id=1, name="Test", slug="test")
        chapter = Chapter(id=1, book_id=1, name="Test", slug="test")
        page = Page(id=1, book_id=1, chapter_id=1, name="Test", slug="test")
        self.client._chapter_cache["key"] = chapter
        self.client._page_cache["key"] = page
        
        # Clear cache
        self.client.clear_cache()
        
        assert self.client._book_cache is None
        assert self.client._chapter_cache == {}
        assert self.client._page_cache == {}


class TestBookStackExceptions:
    """Test BookStack exception handling."""
    
    def test_bookstack_error_creation(self):
        """Test creating BookStackError."""
        error = BookStackError("Test error", 500, {"detail": "Server error"})
        assert str(error) == "Test error"
        assert error.status_code == 500
        assert error.response_data == {"detail": "Server error"}
    
    def test_bookstack_auth_error(self):
        """Test BookStackAuthError."""
        error = BookStackAuthError("Auth failed", 401)
        assert str(error) == "Auth failed"
        assert error.status_code == 401
        assert isinstance(error, BookStackError)
    
    def test_bookstack_not_found_error(self):
        """Test BookStackNotFoundError."""
        error = BookStackNotFoundError("Not found", 404)
        assert str(error) == "Not found"
        assert error.status_code == 404
        assert isinstance(error, BookStackError)
    
    def test_bookstack_rate_limit_error(self):
        """Test BookStackRateLimitError."""
        error = BookStackRateLimitError("Rate limited", 429)
        assert str(error) == "Rate limited"
        assert error.status_code == 429
        assert isinstance(error, BookStackError)


if __name__ == "__main__":
    unittest.main()