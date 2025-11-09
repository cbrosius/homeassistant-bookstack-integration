"""BookStack API client for Home Assistant integration."""
import logging
import time
from dataclasses import dataclass
from typing import Dict, Optional
from urllib.parse import urljoin

import requests

from .const import LOGGER_NAME, DEFAULT_TIMEOUT

_LOGGER = logging.getLogger(LOGGER_NAME)


@dataclass
class BookStackConfig:
    """Configuration for BookStack client."""
    base_url: str
    token_id: str
    token_secret: str
    timeout: int = DEFAULT_TIMEOUT


@dataclass
class Book:
    """BookStack Book data structure."""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class Chapter:
    """BookStack Chapter data structure."""
    id: int
    book_id: int
    name: str
    slug: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class Page:
    """BookStack Page data structure."""
    id: int
    book_id: int
    chapter_id: int
    name: str
    slug: str
    html: Optional[str] = None
    markdown: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class Shelf:
    """BookStack Shelf data structure."""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class BookStackError(Exception):
    """Base exception for BookStack API errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        response_data: Optional[Dict] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class BookStackNotFoundError(BookStackError):
    """Raised when a requested resource is not found."""


class BookStackAuthError(BookStackError):
    """Raised when authentication fails."""


class BookStackRateLimitError(BookStackError):
    """Raised when rate limits are exceeded."""


class BookStackClient:
    """Client for interacting with BookStack API."""
    
    def __init__(self, config: BookStackConfig):
        """Initialize the BookStack client."""
        self.config = config
        self.session = requests.Session()
        # Use TokenID and TokenSecret for authentication as per BookStack API
        self.session.headers.update({
            "Authorization": f"Token {config.token_id}:{config.token_secret}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        
        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 0.5  # 500ms between requests
        
        # Cache for lookups during export
        self._book_cache: Optional[Book] = None
        self._chapter_cache: Dict[str, Chapter] = {}
        self._page_cache: Dict[str, Page] = {}
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> requests.Response:
        """Make a request to the BookStack API with rate limiting."""
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_request_interval:
            time.sleep(self._min_request_interval - time_since_last)
        
        url = urljoin(self.config.base_url, endpoint)
        _LOGGER.debug(f"Making {method} request to {url}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.config.timeout,
                **kwargs
            )
            self._last_request_time = time.time()
            return response
            
        except requests.RequestException as e:
            raise BookStackError(f"Network error: {e}")
    
    def _handle_response(self, response: requests.Response) -> Dict:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 201:
            return response.json()
        elif response.status_code == 401:
            raise BookStackAuthError(
                "Authentication failed - check your token", 
                response.status_code
            )
        elif response.status_code == 404:
            raise BookStackNotFoundError(
                f"Resource not found: {response.url}", 
                response.status_code
            )
        elif response.status_code == 429:
            raise BookStackRateLimitError(
                "Rate limit exceeded", 
                response.status_code
            )
        else:
            try:
                error_data = response.json() if response.content else {}
                error_message = error_data.get("error", "Unknown error")
            except (ValueError, TypeError):
                error_data = {}
                error_message = f"HTTP {response.status_code}"
            
            raise BookStackError(
                f"API error: {error_message}", 
                response.status_code, 
                error_data
            )
    
    def test_connection(self) -> bool:
        """Test if we can connect to BookStack and authenticate."""
        try:
            response = self._make_request("GET", "/api/books")
            self._handle_response(response)
            _LOGGER.info("BookStack connection test successful")
            return True
        except BookStackError as e:
            _LOGGER.error(f"BookStack connection test failed: {e}")
            return False
    
    def find_book(self, name: str) -> Optional[Book]:
        """Find a book by name (case-insensitive)."""
        try:
            response = self._make_request(
                "GET", "/api/books", params={"search": name}
            )
            data = self._handle_response(response)
            
            for book_data in data.get("data", []):
                if book_data["name"].lower() == name.lower():
                    return Book(**book_data)
            
            return None
            
        except BookStackError as e:
            _LOGGER.error(f"Failed to search for book: {e}")
            raise BookStackError(f"Failed to search for book: {e}")
    
    def create_book(self, name: str, description: str = "") -> Book:
        """Create a new book."""
        try:
            payload = {"title": name, "description": description}
            response = self._make_request(
                "POST", "/api/books", json=payload
            )
            book_data = self._handle_response(response)
            _LOGGER.info(f"Created new book: {name} (ID: {book_data['id']})")
            return Book(**book_data)
            
        except BookStackError as e:
            _LOGGER.error(f"Failed to create book: {e}")
            raise
    
    def find_or_create_book(self, name: str, description: str = "") -> Book:
        """Find existing book or create new one."""
        if self._book_cache:
            if self._book_cache.name.lower() == name.lower():
                return self._book_cache
        
        book = self.find_book(name)
        if book:
            self._book_cache = book
            _LOGGER.info(f"Using existing book: {name} (ID: {book.id})")
            return book
        
        book = self.create_book(name, description)
        self._book_cache = book
        return book
    
    def find_chapter(self, book_id: int, name: str) -> Optional[Chapter]:
        """Find a chapter by name within a book."""
        cache_key = f"{book_id}:{name.lower()}"
        if cache_key in self._chapter_cache:
            return self._chapter_cache[cache_key]
        
        try:
            response = self._make_request(
                "GET", f"/api/books/{book_id}/chapters"
            )
            data = self._handle_response(response)
            
            for chapter_data in data.get("data", []):
                if chapter_data["name"].lower() == name.lower():
                    chapter = Chapter(**chapter_data)
                    self._chapter_cache[cache_key] = chapter
                    return chapter
            
            return None
            
        except BookStackError as e:
            _LOGGER.error(f"Failed to search for chapter: {e}")
            raise BookStackError(f"Failed to search for chapter: {e}")
    
    def create_chapter(
        self,
        book_id: int,
        name: str,
        description: str = ""
    ) -> Chapter:
        """Create a new chapter within a book."""
        try:
            payload = {"title": name, "description": description}
            response = self._make_request(
                "POST", f"/api/books/{book_id}/chapters", json=payload
            )
            chapter_data = self._handle_response(response)
            _LOGGER.info(
                f"Created new chapter: {name} (ID: {chapter_data['id']})"
            )
            return Chapter(**chapter_data)
            
        except BookStackError as e:
            _LOGGER.error(f"Failed to create chapter: {e}")
            raise
    
    def find_or_create_chapter(
        self,
        book_id: int,
        name: str,
        description: str = ""
    ) -> Chapter:
        """Find existing chapter or create new one."""
        cache_key = f"{book_id}:{name.lower()}"
        if cache_key in self._chapter_cache:
            return self._chapter_cache[cache_key]
        
        chapter = self.find_chapter(book_id, name)
        if chapter:
            self._chapter_cache[cache_key] = chapter
            _LOGGER.info(f"Using existing chapter: {name} (ID: {chapter.id})")
            return chapter
        
        chapter = self.create_chapter(book_id, name, description)
        self._chapter_cache[cache_key] = chapter
        return chapter
    
    def find_page(self, chapter_id: int, name: str) -> Optional[Page]:
        """Find a page by name within a chapter."""
        cache_key = f"{chapter_id}:{name.lower()}"
        if cache_key in self._page_cache:
            return self._page_cache[cache_key]
        
        try:
            response = self._make_request(
                "GET", f"/api/chapters/{chapter_id}/pages"
            )
            data = self._handle_response(response)
            
            for page_data in data.get("data", []):
                if page_data["name"].lower() == name.lower():
                    page = Page(**page_data)
                    self._page_cache[cache_key] = page
                    return page
            
            return None
            
        except BookStackError as e:
            _LOGGER.error(f"Failed to search for page: {e}")
            raise BookStackError(f"Failed to search for page: {e}")
    
    def create_page(
        self,
        chapter_id: int,
        name: str,
        markdown_content: str
    ) -> Page:
        """Create a new page within a chapter."""
        try:
            payload = {"title": name, "markdown": markdown_content}
            response = self._make_request(
                "POST", f"/api/chapters/{chapter_id}/pages", json=payload
            )
            page_data = self._handle_response(response)
            _LOGGER.info(f"Created new page: {name} (ID: {page_data['id']})")
            return Page(**page_data)
            
        except BookStackError as e:
            _LOGGER.error(f"Failed to create page: {e}")
            raise
    
    def update_page(
        self,
        page_id: int,
        name: str,
        markdown_content: str
    ) -> Page:
        """Update an existing page."""
        try:
            payload = {"title": name, "markdown": markdown_content}
            response = self._make_request(
                "PUT", f"/api/pages/{page_id}", json=payload
            )
            page_data = self._handle_response(response)
            _LOGGER.info(f"Updated page: {name} (ID: {page_id})")
            return Page(**page_data)
            
        except BookStackError as e:
            _LOGGER.error(f"Failed to update page: {e}")
            raise
    
    def create_or_update_page(
        self,
        chapter_id: int,
        name: str,
        markdown_content: str
    ) -> Page:
        """Find existing page or create/update as needed."""
        cache_key = f"{chapter_id}:{name.lower()}"
        
        existing_page = self.find_page(chapter_id, name)
        if existing_page:
            page = self.update_page(existing_page.id, name, markdown_content)
            self._page_cache[cache_key] = page
            return page
        else:
            page = self.create_page(chapter_id, name, markdown_content)
            self._page_cache[cache_key] = page
            return page
    
    def clear_cache(self) -> None:
        """Clear the client cache."""
        self._book_cache = None
        self._chapter_cache.clear()
        self._page_cache.clear()
        _LOGGER.debug("BookStack client cache cleared")
    
    def get_shelves(self) -> list[Shelf]:
        """Get all available shelves."""
        try:
            response = self._make_request("GET", "/api/shelves")
            data = self._handle_response(response)
            
            shelves = []
            for shelf_data in data.get("data", []):
                shelves.append(Shelf(**shelf_data))
            
            _LOGGER.info(f"Retrieved {len(shelves)} shelves")
            return shelves
            
        except BookStackError as e:
            _LOGGER.error(f"Failed to get shelves: {e}")
            raise BookStackError(f"Failed to get shelves: {e}")
    
    def find_shelf(self, name: str) -> Optional[Shelf]:
        """Find a shelf by name (case-insensitive)."""
        try:
            response = self._make_request(
                "GET", "/api/shelves", params={"search": name}
            )
            data = self._handle_response(response)
            
            for shelf_data in data.get("data", []):
                if shelf_data["name"].lower() == name.lower():
                    return Shelf(**shelf_data)
            
            return None
            
        except BookStackError as e:
            _LOGGER.error(f"Failed to search for shelf: {e}")
            raise BookStackError(f"Failed to search for shelf: {e}")
    
    def create_shelf(self, name: str, description: str = "") -> Shelf:
        """Create a new shelf."""
        try:
            payload = {"title": name, "description": description}
            response = self._make_request(
                "POST", "/api/shelves", json=payload
            )
            shelf_data = self._handle_response(response)
            _LOGGER.info(f"Created new shelf: {name} (ID: {shelf_data['id']})")
            return Shelf(**shelf_data)
            
        except BookStackError as e:
            _LOGGER.error(f"Failed to create shelf: {e}")
            raise
    
    def find_or_create_shelf(self, name: str, description: str = "") -> Shelf:
        """Find existing shelf or create new one."""
        shelf = self.find_shelf(name)
        if shelf:
            _LOGGER.info(f"Using existing shelf: {name} (ID: {shelf.id})")
            return shelf
        
        shelf = self.create_shelf(name, description)
        return shelf