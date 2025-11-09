"""BookStack API client for Home Assistant integration."""
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
from urllib.parse import urljoin

import requests

from .const import (
    LOGGER_NAME, DEFAULT_TIMEOUT, DEFAULT_BOOK_DESCRIPTION
)

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
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    owned_by: Optional[int] = None
    cover: Optional[str] = None
    
    def __init__(self, **kwargs):
        """Initialize Book with all available fields from BookStack API."""
        # Required fields
        self.id = kwargs["id"]
        self.name = kwargs["name"]
        self.slug = kwargs["slug"]
        
        # Optional fields with defaults
        self.description = kwargs.get("description")
        self.created_at = kwargs.get("created_at")
        self.updated_at = kwargs.get("updated_at")
        self.created_by = kwargs.get("created_by")
        self.updated_by = kwargs.get("updated_by")
        self.owned_by = kwargs.get("owned_by")
        self.cover = kwargs.get("cover")
        
        # Store any additional fields for future use
        for key, value in kwargs.items():
            if key not in [
                "id", "name", "slug", "description", "created_at",
                "updated_at", "created_by", "updated_by", "owned_by", "cover"
            ]:
                setattr(self, key, value)
    
    def __repr__(self):
        """String representation of the Book."""
        return f"Book(id={self.id}, name='{self.name}', slug='{self.slug}')"


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
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    def __init__(self, **kwargs):
        """Initialize Chapter with all available fields from BookStack API."""
        # Required fields
        self.id = kwargs["id"]
        self.book_id = kwargs["book_id"]
        self.name = kwargs["name"]
        self.slug = kwargs["slug"]
        
        # Optional fields with defaults
        self.description = kwargs.get("description")
        self.created_at = kwargs.get("created_at")
        self.updated_at = kwargs.get("updated_at")
        self.created_by = kwargs.get("created_by")
        self.updated_by = kwargs.get("updated_by")
        
        # Store any additional fields for future use
        for key, value in kwargs.items():
            if key not in [
                "id", "book_id", "name", "slug", "description",
                "created_at", "updated_at", "created_by", "updated_by"
            ]:
                setattr(self, key, value)
    
    def __repr__(self):
        """String representation of the Chapter."""
        return (
            f"Chapter(id={self.id}, name='{self.name}', "
            f"slug='{self.slug}', book_id={self.book_id})"
        )


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
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    owned_by: Optional[int] = None
    
    def __init__(self, **kwargs):
        """Initialize Page with all available fields from BookStack API."""
        # Required fields
        self.id = kwargs["id"]
        self.book_id = kwargs["book_id"]
        self.chapter_id = kwargs["chapter_id"]
        self.name = kwargs["name"]
        self.slug = kwargs["slug"]
        
        # Optional fields with defaults
        self.html = kwargs.get("html")
        self.markdown = kwargs.get("markdown")
        self.created_at = kwargs.get("created_at")
        self.updated_at = kwargs.get("updated_at")
        self.created_by = kwargs.get("created_by")
        self.updated_by = kwargs.get("updated_by")
        self.owned_by = kwargs.get("owned_by")
        
        # Store any additional fields for future use
        for key, value in kwargs.items():
            if key not in [
                "id", "book_id", "chapter_id", "name", "slug", "html",
                "markdown", "created_at", "updated_at", "created_by",
                "updated_by", "owned_by"
            ]:
                setattr(self, key, value)
    
    def __repr__(self):
        """String representation of the Page."""
        return (
            f"Page(id={self.id}, name='{self.name}', "
            f"slug='{self.slug}', chapter_id={self.chapter_id})"
        )


class Shelf:
    """BookStack Shelf data structure."""
    
    def __init__(self, **kwargs):
        """Initialize Shelf with dynamic fields from BookStack API."""
        # Required fields
        self.id = kwargs["id"]
        self.name = kwargs["name"]
        self.slug = kwargs["slug"]
        
        # Optional fields
        self.description = kwargs.get("description")
        self.created_at = kwargs.get("created_at")
        self.updated_at = kwargs.get("updated_at")
        
        # Store any additional fields for future use
        for key, value in kwargs.items():
            excluded_keys = [
                "id", "name", "slug", "description",
                "created_at", "updated_at"
            ]
            if key not in excluded_keys:
                setattr(self, key, value)
    
    def __repr__(self):
        """String representation of the Shelf."""
        return f"Shelf(id={self.id}, name='{self.name}', slug='{self.slug}')"


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
            payload = {"name": name, "description": description}
            response = self._make_request(
                "POST", "/api/books", json=payload
            )
            book_data = self._handle_response(response)
            _LOGGER.info(f"Created new book: {name} (ID: {book_data['id']})")
            return Book(**book_data)
            
        except BookStackError as e:
            _LOGGER.error(f"Failed to create book: {e}")
            raise
    
    def assign_book_to_shelf(self, book_id: int, shelf_id: int) -> bool:
        """Assign a book to a shelf."""
        try:
            payload = {"books": [book_id]}
            response = self._make_request(
                "PUT", f"/api/shelves/{shelf_id}/books", json=payload
            )
            self._handle_response(response)
            _LOGGER.info(f"Assigned book {book_id} to shelf {shelf_id}")
            return True
            
        except BookStackError as e:
            _LOGGER.error(f"Failed to assign book to shelf: {e}")
            return False
    
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
            
        except BookStackNotFoundError:
            # Book might be empty (no chapters yet), return None instead
            _LOGGER.debug(f"No chapters found in book {book_id}")
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
            # BookStack uses /api/chapters endpoint with book_id in payload
            payload = {
                "name": name,
                "description": description,
                "book_id": book_id
            }
            response = self._make_request(
                "POST", "/api/chapters", json=payload
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
            payload = {"name": name, "description": description}
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

    def find_or_create_areas_book(self) -> Book:
        """Find or create the Areas book."""
        areas_book = self.find_book("Areas")
        if areas_book:
            return areas_book
        
        description = (
            "Home Assistant device and entity documentation "
            "organized by physical areas"
        )
        return self.create_book("Areas", description)

    def create_area_chapter(
        self, book_id: int, area_name: str, area_info: Dict
    ) -> Chapter:
        """Create a chapter for an area/floor."""
        device_count = area_info.get('device_count', 0)
        entity_count = area_info.get('entity_count', 0)
        description = (
            f"Documentation for {area_name} area "
            f"({device_count} devices, {entity_count} entities)"
        )
        return self.find_or_create_chapter(book_id, area_name, description)

    def create_area_page(
        self, chapter_id: int, area_name: str, area_info: Dict
    ) -> Page:
        """Create a detailed page for an area."""
        content = self._generate_area_page_content(area_name, area_info)
        return self.create_or_update_page(
            chapter_id, f"{area_name} Overview", content
        )

    def _generate_area_page_content(
        self, area_name: str, area_info: Dict
    ) -> str:
        """Generate markdown content for an area page."""
        content = f"""# {area_name} - Home Assistant Area Overview

## Overview
This page documents the Home Assistant devices and entities
located in the **{area_name}** area.

## Statistics
- **Devices**: {area_info.get('device_count', 0)}
- **Entities**: {area_info.get('entity_count', 0)}

## Devices

| Device | Manufacturer | Model | Status |
|--------|-------------|-------|--------|
"""
        
        for device in area_info.get('devices', []):
            name = device.get('name', 'Unknown')
            manufacturer = device.get('manufacturer', 'Unknown')
            model = device.get('model', 'Unknown')
            content += f"| {name} | {manufacturer} | {model} | Active |\n"
        
        content += """
## Entities

| Entity ID | Friendly Name | Device Class | Unit |
|-----------|--------------|--------------|------|
"""
        
        for entity in area_info.get('entities', []):
            unit = entity.get('unit_of_measurement', '-')
            device_class = entity.get('device_class', '-')
            friendly_name = entity.get('friendly_name', '')
            if not friendly_name:
                friendly_name = entity.get('entity_id', 'Unknown')
            entity_id = entity.get('entity_id', 'Unknown')
            content += (
                f"| {entity_id} | {friendly_name} | "
                f"{device_class} | {unit} |\n"
            )
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content += f"""
## Last Updated
Generated on: {timestamp}

---
*This documentation is automatically generated by the
Home Assistant BookStack Integration*
"""
        
        return content