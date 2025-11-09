# BookStack API Client Design

## Project: Home Assistant - BookStack Integration

Date: 2025-11-09

## BookStackClient Architecture

### Core Design Principles
- **Idempotent Operations**: Re-exports should update existing content
- **Error Recovery**: Graceful handling of API failures
- **Rate Limit Respect**: Implement appropriate delays
- **Thread Safety**: Safe for Home Assistant's async environment

### Client Class Design

```python
from typing import Optional, Dict, List, Tuple
import requests
from dataclasses import dataclass
import logging

@dataclass
class BookStackConfig:
    """Configuration for BookStack client"""
    base_url: str
    token: str
    timeout: int = 30

@dataclass
class Book:
    """BookStack Book data structure"""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class Chapter:
    """BookStack Chapter data structure"""
    id: int
    book_id: int
    name: str
    slug: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class Page:
    """BookStack Page data structure"""
    id: int
    book_id: int
    chapter_id: int
    name: str
    slug: str
    html: Optional[str] = None
    markdown: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class BookStackError(Exception):
    """Base exception for BookStack API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class BookStackNotFoundError(BookStackError):
    """Raised when a requested resource is not found"""

class BookStackAuthError(BookStackError):
    """Raised when authentication fails"""

class BookStackRateLimitError(BookStackError):
    """Raised when rate limits are exceeded"""

class BookStackClient:
    """Client for interacting with BookStack API"""
    
    def __init__(self, config: BookStackConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {config.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.logger = logging.getLogger(__name__)
    
    def test_connection(self) -> bool:
        """Test if we can connect to BookStack and authenticate"""
        try:
            response = self.session.get(f"{self.config.base_url}/api/books", timeout=self.config.timeout)
            return response.status_code == 200
        except requests.RequestException as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def find_book(self, name: str) -> Optional[Book]:
        """Find a book by name (case-insensitive)"""
        try:
            response = self.session.get(
                f"{self.config.base_url}/api/books",
                params={'search': name},
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                for book in data.get('data', []):
                    if book['name'].lower() == name.lower():
                        return Book(**book)
            elif response.status_code == 401:
                raise BookStackAuthError("Authentication failed - check your token")
            
            return None
            
        except requests.RequestException as e:
            raise BookStackError(f"Failed to search for book: {e}")
    
    def create_book(self, name: str, description: str = "") -> Book:
        """Create a new book"""
        try:
            payload = {
                'title': name,
                'description': description
            }
            response = self.session.post(
                f"{self.config.base_url}/api/books",
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 201:
                return Book(**response.json())
            elif response.status_code == 401:
                raise BookStackAuthError("Authentication failed - check your token")
            else:
                error_data = response.json() if response.content else {}
                raise BookStackError(f"Failed to create book: {response.status_code} {error_data}")
                
        except requests.RequestException as e:
            raise BookStackError(f"Network error creating book: {e}")
    
    def find_or_create_book(self, name: str, description: str = "") -> Book:
        """Find existing book or create new one"""
        book = self.find_book(name)
        if book:
            self.logger.info(f"Found existing book: {name} (ID: {book.id})")
            return book
        
        self.logger.info(f"Creating new book: {name}")
        return self.create_book(name, description)
    
    def find_chapter(self, book_id: int, name: str) -> Optional[Chapter]:
        """Find a chapter by name within a book"""
        try:
            response = self.session.get(
                f"{self.config.base_url}/api/books/{book_id}/chapters",
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                for chapter in data.get('data', []):
                    if chapter['name'].lower() == name.lower():
                        return Chapter(**chapter)
            
            return None
            
        except requests.RequestException as e:
            raise BookStackError(f"Failed to search for chapter: {e}")
    
    def create_chapter(self, book_id: int, name: str, description: str = "") -> Chapter:
        """Create a new chapter within a book"""
        try:
            payload = {
                'title': name,
                'description': description
            }
            response = self.session.post(
                f"{self.config.base_url}/api/books/{book_id}/chapters",
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 201:
                return Chapter(**response.json())
            else:
                error_data = response.json() if response.content else {}
                raise BookStackError(f"Failed to create chapter: {response.status_code} {error_data}")
                
        except requests.RequestException as e:
            raise BookStackError(f"Network error creating chapter: {e}")
    
    def find_or_create_chapter(self, book_id: int, name: str, description: str = "") -> Chapter:
        """Find existing chapter or create new one"""
        chapter = self.find_chapter(book_id, name)
        if chapter:
            self.logger.info(f"Found existing chapter: {name} (ID: {chapter.id})")
            return chapter
        
        self.logger.info(f"Creating new chapter: {name}")
        return self.create_chapter(book_id, name, description)
    
    def find_page(self, chapter_id: int, name: str) -> Optional[Page]:
        """Find a page by name within a chapter"""
        try:
            response = self.session.get(
                f"{self.config.base_url}/api/chapters/{chapter_id}/pages",
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                for page in data.get('data', []):
                    if page['name'].lower() == name.lower():
                        return Page(**page)
            
            return None
            
        except requests.RequestException as e:
            raise BookStackError(f"Failed to search for page: {e}")
    
    def create_page(self, chapter_id: int, name: str, markdown_content: str) -> Page:
        """Create a new page within a chapter"""
        try:
            payload = {
                'title': name,
                'markdown': markdown_content
            }
            response = self.session.post(
                f"{self.config.base_url}/api/chapters/{chapter_id}/pages",
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 201:
                return Page(**response.json())
            else:
                error_data = response.json() if response.content else {}
                raise BookStackError(f"Failed to create page: {response.status_code} {error_data}")
                
        except requests.RequestException as e:
            raise BookStackError(f"Network error creating page: {e}")
    
    def update_page(self, page_id: int, name: str, markdown_content: str) -> Page:
        """Update an existing page"""
        try:
            payload = {
                'title': name,
                'markdown': markdown_content
            }
            response = self.session.put(
                f"{self.config.base_url}/api/pages/{page_id}",
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                return Page(**response.json())
            else:
                error_data = response.json() if response.content else {}
                raise BookStackError(f"Failed to update page: {response.status_code} {error_data}")
                
        except requests.RequestException as e:
            raise BookStackError(f"Network error updating page: {e}")
    
    def create_or_update_page(self, chapter_id: int, name: str, markdown_content: str) -> Page:
        """Find existing page or create/update as needed"""
        existing_page = self.find_page(chapter_id, name)
        
        if existing_page:
            self.logger.info(f"Updating existing page: {name} (ID: {existing_page.id})")
            return self.update_page(existing_page.id, name, markdown_content)
        else:
            self.logger.info(f"Creating new page: {name}")
            return self.create_page(chapter_id, name, markdown_content)
```

## Error Handling Strategy

### HTTP Status Code Handling
- **200 OK**: Success (GET, PUT)
- **201 Created**: Success (POST)
- **400 Bad Request**: Invalid data
- **401 Unauthorized**: Authentication failure
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limited
- **500+ Server Errors**: Retry with exponential backoff

### Exception Hierarchy
```
BookStackError (base)
├── BookStackAuthError
├── BookStackNotFoundError  
├── BookStackRateLimitError
└── BookStackValidationError
```

### Retry Logic (for 429, 500+)
- Exponential backoff (1s, 2s, 4s, 8s...)
- Max 3 retries
- Log all retry attempts
- Notify user on final failure

## Home Assistant Integration Points

### Data Flow
1. **Export Service Call** → `exporter.py`
2. **Get HA Registries** → `area_registry`, `device_registry`, `entity_registry`
3. **Build Markdown** → Device details + entity information
4. **BookStack Operations** → `bookstack_api.py` client
5. **User Notification** → Success/error messages

### Async Support
```python
# In Home Assistant context
import aiohttp
import asyncio

class AsyncBookStackClient:
    """Async version for Home Assistant"""
    
    async def create_or_update_page(self, session: aiohttp.ClientSession, chapter_id: int, name: str, markdown: str) -> Page:
        # Async implementation using aiohttp
        pass
```

## Performance Considerations

### Batch Operations
- Create all chapters first, then pages
- Minimize API calls by finding existing resources
- Use search parameters when available

### Caching Strategy
- Cache book/chapter/page lookups during single export
- Invalidate cache on successful operations
- Consider in-memory cache for session duration

### Rate Limiting
- BookStack typically allows 1000 requests/hour
- Add 0.5s delay between operations
- Monitor for 429 responses

## Testing Strategy

### Unit Tests
- Mock HTTP responses
- Test all client methods
- Validate error handling

### Integration Tests  
- Test with real BookStack instance
- Create test book/chapters/pages
- Verify idempotency (create → update → create)

### Home Assistant Tests
- Mock HA registries
- Test service calls
- Validate notifications