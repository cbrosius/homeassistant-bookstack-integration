"""Constants for BookStack Custom Integration integration."""

DOMAIN = "bookstack_integration"

# Default values
DEFAULT_TIMEOUT = 30
DEFAULT_BOOK_NAME = "Home Assistant Documentation"
DEFAULT_BOOK_DESCRIPTION = (
    "Exported documentation of Home Assistant devices and entities"
)

# API endpoints
API_BASE_SUFFIX = "/api"

# Configuration keys
CONF_BASE_URL = "base_url"
CONF_API_TOKEN = "api_token"
CONF_BOOK_NAME = "book_name"
CONF_TIMEOUT = "timeout"

# Service data keys
SERVICE_EXPORT = "export"
SERVICE_DATA_AREA_FILTER = "area_filter"

# Logging
LOGGER_NAME = "custom_components.bookstack_integration"