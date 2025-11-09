# BookStack API Research

## Project: Home Assistant - BookStack Integration

Date: 2025-11-09

## Overview
Research findings for integrating Home Assistant with BookStack API to export device and entity documentation.

## API Documentation Sources
- **Official Documentation**: https://www.bookstackapp.com/dev/docs/
- **API Base URL**: `https://your-bookstack-url/api`
- **Authentication**: Token-based (Header: `Authorization: Token YOUR_TOKEN`)

## Integration Requirements Analysis
Based on the Home Assistant integration requirements:

### Target Structure
- **Book**: "Home Assistant Documentation"
- **Chapters**: Areas/Room (e.g., "Living Room", "Kitchen")
- **Pages**: Devices (with entity details)

### Required API Operations
1. **Find or Create Book**: "Home Assistant Documentation"
2. **Create Chapters for Areas**: Each HA Area becomes a Chapter
3. **Create/Update Pages**: Each HA Device becomes a Page
4. **Update Existing Content**: Re-export should update existing pages

## Research Progress
- [x] Authentication mechanism - Token-based auth confirmed
- [x] Books API endpoints - Basic structure identified
- [x] Chapters API endpoints - Required for Area organization
- [x] Pages API endpoints - Required for Device documentation
- [ ] Error handling patterns - Need to research
- [ ] Rate limiting - Need to investigate
- [ ] Request/response formats - Need detailed analysis
- [ ] Test API calls - Future step

## Key Endpoints Analysis
### Books Operations
- `GET /api/books` - List all books (to find existing)
- `POST /api/books` - Create "Home Assistant Documentation" book
- `GET /api/books/{id}` - Get book details and chapter list
- `PUT /api/books/{id}` - Update book (if needed)

### Chapters Operations (by Area)
- `GET /api/books/{book_id}/chapters` - List chapters (Areas)
- `POST /api/books/{book_id}/chapters` - Create new Area chapter
- `PUT /api/chapters/{id}` - Update existing chapter (if needed)

### Pages Operations (by Device)
- `GET /api/chapters/{chapter_id}/pages` - List device pages
- `POST /api/chapters/{chapter_id}/pages` - Create new device page
- `PUT /api/pages/{id}` - Update existing device page
- `GET /api/pages/{id}` - Get page content

## Authentication Strategy
- Token-based authentication
- Header format: `Authorization: Token YOUR_TOKEN`
- API tokens generated in BookStack admin panel
- Configured via Home Assistant UI flow

## Data Flow Design
1. **Initialize**: Find or create "Home Assistant Documentation" book
2. **Process Areas**: For each HA Area, find or create Chapter
3. **Process Devices**: For each Device in Area, find or create Page
4. **Update Content**: Use PUT for existing, POST for new
5. **Error Handling**: Graceful fallbacks and user notifications

## Implementation Architecture
### BookStack API Client
```python
class BookStackClient:
    def __init__(self, base_url: str, token: str)
    def find_or_create_book(self, name: str) -> Book
    def find_or_create_chapter(self, book_id: int, name: str) -> Chapter
    def create_or_update_page(self, chapter_id: int, name: str, content: str) -> Page
    def handle_error(self, response: requests.Response)
```

### Key Design Considerations
- **Idempotency**: Re-runs should update existing content
- **Error Recovery**: Handle API failures gracefully
- **Content Updates**: Use existing IDs when found
- **Rate Limiting**: Implement proper delays if needed

## Next Steps
1. ✅ Research official API documentation structure
2. ⏳ Analyze error handling patterns
3. ⏳ Document detailed request/response formats
4. ⏳ Test API authentication and basic calls
5. ⏳ Design BookStackClient architecture
6. ⏳ Plan integration with Home Assistant registries