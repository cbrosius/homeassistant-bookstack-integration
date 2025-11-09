"""Constants for BookStack Custom Integration integration."""

DOMAIN = "bookstack_integration"

# Default values
DEFAULT_TIMEOUT = 30
DEFAULT_BOOK_NAME = "Automated Smarthome Documentation"
DEFAULT_SHELF_NAME = "Home Assistant Documentation"
DEFAULT_BOOK_DESCRIPTION = (
    "Exported documentation of Home Assistant devices and entities"
)

# API endpoints
API_BASE_SUFFIX = "/api"

# Configuration keys
CONF_BASE_URL = "base_url"
CONF_TOKEN_ID = "token_id"
CONF_TOKEN_SECRET = "token_secret"
CONF_SHELF_NAME = "shelf_name"
CONF_BOOK_NAME = "book_name"
CONF_TIMEOUT = "timeout"

# Service data keys
SERVICE_EXPORT = "export"
SERVICE_DATA_AREA_FILTER = "area_filter"

# Configuration for area mapping
DEFAULT_AREA_MAPPING = {
    "ground_floor_keywords": [
        "living", "kitchen", "garage", "entrance", "dining"
    ],
    "first_floor_keywords": [
        "bedroom", "bathroom", "office", "guest"
    ],
    "basement_keywords": ["basement", "cellar"],
    "attic_keywords": ["attic", "loft"],
    "outside_keywords": [
        "garden", "patio", "balcony", "driveway", "outside"
    ]
}

# Create chapters for individual rooms
CREATE_ROOM_PAGES = True

# Book creation options
DEFAULT_BOOK_DESCRIPTION = (
    "Home Assistant device and entity documentation "
    "organized by physical areas"
)

# Logging
LOGGER_NAME = "custom_components.bookstack_integration"