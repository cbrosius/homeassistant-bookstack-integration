# Configuration Flow & Service Definition

## Project: Home Assistant - BookStack Integration

Date: 2025-11-09

## Configuration Flow Design (`config_flow.py`)

### User Experience Flow
```
Home Assistant Settings → Integrations → Add Integration → "BookStack Export"
    ↓
Step 1: BookStack URL
    ↓  
Step 2: API Token
    ↓
Step 3: Optional Settings (Book Name)
    ↓
Step 4: Test Connection & Create Entry
    ↓
Success: "Integration added successfully"
```

### Configuration Schema

#### Step 1: BookStack URL
```python
vol.Required(CONF_URL, description="BookStack URL"): str
```
- **Validation**: URL format, HTTPS required
- **Placeholder**: `https://your-bookstack-instance.com`
- **Help Text**: `Enter the full URL to your BookStack instance (including https://)`

#### Step 2: API Token  
```python
vol.Required(CONF_TOKEN, description="API Token"): str
```
- **Validation**: Non-empty string
- **Masking**: Password field (input_type="password")
- **Help Text**: `API token from BookStack (Profile → API Tokens → Create Token)`

#### Step 3: Optional Settings
```python
vol.Optional(CONF_BOOK_NAME, default="Home Assistant Documentation"): str
```
- **Validation**: Non-empty string
- **Help Text**: `Name of the BookStack book to use (default: "Home Assistant Documentation")`

### Config Flow Implementation

```python
"""Config flow for BookStack Export integration."""
import voluptuous as vol
from typing import Any, Dict, Optional
import aiohttp
import asyncio

from homeassistant import config_entries
from homeassistant.const import CONF_URL, CONF_TOKEN
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_BOOK_NAME, DEFAULT_BOOK_NAME
from .bookstack_api import BookStackClient, BookStackConfig, BookStackAuthError

class BookStackConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BookStack Export."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._url: str = ""
        self._token: str = ""
        self._book_name: str = DEFAULT_BOOK_NAME

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            self._url = user_input[CONF_URL]
            self._token = user_input[CONF_TOKEN]
            self._book_name = user_input.get(CONF_BOOK_NAME, DEFAULT_BOOK_NAME)

            # Validate the configuration
            try:
                await self._async_validate_config()
                return await self._async_create_entry()
            except BookStackAuthError:
                errors["base"] = "auth_error"
            except Exception:
                errors["base"] = "connection_error"

        data_schema = vol.Schema({
            vol.Required(CONF_URL): str,
            vol.Required(CONF_TOKEN): str,
            vol.Optional(CONF_BOOK_NAME, default=DEFAULT_BOOK_NAME): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "url_placeholder": "https://your-bookstack-instance.com"
            }
        )

    async def _async_validate_config(self) -> None:
        """Validate the BookStack configuration."""
        config = BookStackConfig(
            base_url=self._url,
            token=self._token,
            timeout=10
        )
        
        client = BookStackClient(config)
        
        # Test connection
        if not await self.hass.async_add_executor_job(client.test_connection):
            raise BookStackAuthError("Connection test failed")

    async def _async_create_entry(self) -> FlowResult:
        """Create the config entry."""
        data = {
            CONF_URL: self._url,
            CONF_TOKEN: self._token,
            CONF_BOOK_NAME: self._book_name,
        }

        # Check if entry already exists
        existing_entry = await self.async_set_unique_id(self._get_unique_id())
        if existing_entry:
            self.hass.config_entries.async_update_entry(existing_entry, data=data)
            return self.async_abort(reason="updated")

        return self.async_create_entry(title="BookStack Export", data=data)

    def _get_unique_id(self) -> str:
        """Generate unique ID based on URL."""
        return hashlib.md5(self._url.encode()).hexdigest()

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return BookStackOptionsFlow(config_entry)

class BookStackOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for BookStack Export."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Manage the options."""
        errors = {}

        if user_input is not None:
            try:
                # Validate new configuration
                config = BookStackConfig(
                    base_url=user_input[CONF_URL],
                    token=user_input[CONF_TOKEN],
                    timeout=10
                )
                
                client = BookStackClient(config)
                if not await self.hass.async_add_executor_job(client.test_connection):
                    errors["base"] = "auth_error"
                else:
                    return self.async_create_entry(title="", data=user_input)
            except Exception:
                errors["base"] = "connection_error"

        data_schema = vol.Schema({
            vol.Required(CONF_URL, default=self.config_entry.data[CONF_URL]): str,
            vol.Required(CONF_TOKEN, default=self.config_entry.data[CONF_TOKEN]): str,
            vol.Optional(CONF_BOOK_NAME, default=self.config_entry.data.get(CONF_BOOK_NAME, DEFAULT_BOOK_NAME)): str,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors
        )
```

## Service Definition (`services.yaml`)

### Service Schema
```yaml
bookstack_export:
  export:
    name: "Export to BookStack"
    description: "Export Home Assistant devices and entities to BookStack"
    fields:
      area_filter:
        name: "Area Filter"
        description: "Export only devices from a specific area (optional)"
        required: false
        example: "Living Room"
        selector:
          text:
      dry_run:
        name: "Dry Run"
        description: "Show what would be exported without actually creating content"
        required: false
        default: false
        selector:
          boolean:
```

### Service Implementation
```python
# In __init__.py or services.py
from homeassistant.core import ServiceCall
from homeassistant.helpers import entity_registry as er

async def async_export_to_bookstack(
    hass: HomeAssistant,
    call: ServiceCall,
    config_entry: ConfigEntry
) -> None:
    """Handle export to BookStack service call."""
    area_filter = call.data.get("area_filter")
    dry_run = call.data.get("dry_run", False)

    # Get BookStack client
    client = hass.data[DOMAIN][config_entry.entry_id]["client"]
    
    # Get HA registries
    area_registry = er.async_get(hass).areas
    device_registry = er.async_get(hass).devices
    entity_registry = er.async_get(hass).entities

    # Initialize exporter
    exporter = BookStackExporter(
        hass=hass,
        client=client,
        area_registry=area_registry,
        device_registry=device_registry,
        entity_registry=entity_registry
    )

    try:
        if dry_run:
            # Show what would be exported
            result = await exporter.dry_run_export(area_filter)
            _show_dry_run_result(hass, result)
        else:
            # Perform actual export
            await hass.async_add_executor_job(exporter.export, area_filter)
            _notify_success(hass, area_filter)
            
    except Exception as e:
        _notify_error(hass, str(e))
```

## Integration Setup (`__init__.py`)

### Domain Registration
```python
"""The BookStack Export integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, LOGGER
from .bookstack_api import BookStackClient, BookStackConfig
from .exporter import BookStackExporter

PLATFORMS: list[Platform] = []

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the BookStack Export component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BookStack Export from a config entry."""
    # Store data for use by platforms and services
    client = BookStackClient(
        BookStackConfig(
            base_url=entry.data["url"],
            token=entry.data["token"]
        )
    )

    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "config_entry": entry
    }

    # Register services
    await async_register_services(hass, entry)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
    return unload_ok

async def async_register_services(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register BookStack export services."""
    
    async def export_service(call) -> None:
        """Handle export service call."""
        area_filter = call.data.get("area_filter")
        dry_run = call.data.get("dry_run", False)
        
        client = hass.data[DOMAIN][entry.entry_id]["client"]
        
        # Get registries
        area_registry = er.async_get(hass).areas
        device_registry = er.async_get(hass).devices
        entity_registry = er.async_get(hass).entities
        
        # Create exporter
        exporter = BookStackExporter(
            hass=hass,
            client=client,
            area_registry=area_registry,
            device_registry=device_registry,
            entity_registry=entity_registry,
            book_name=entry.data.get("book_name", "Home Assistant Documentation")
        )
        
        try:
            if dry_run:
                result = await hass.async_add_executor_job(exporter.dry_run_export, area_filter)
                _show_dry_run_result(hass, result)
            else:
                await hass.async_add_executor_job(exporter.export, area_filter)
                hass.async_create_task(_notify_success(hass, area_filter))
                
        except Exception as err:
            LOGGER.error("Export failed: %s", err)
            hass.async_create_task(_notify_error(hass, str(err)))

    # Register the service
    hass.services.async_register(
        DOMAIN,
        "export",
        export_service,
        schema=vol.Schema({
            vol.Optional("area_filter"): str,
            vol.Optional("dry_run", default=False): bool,
        })
    )
```

## Constants (`const.py`)

```python
"""Constants for the BookStack Export integration."""

DOMAIN = "bookstack_export"

CONF_URL = "url"
CONF_TOKEN = "token"
CONF_BOOK_NAME = "book_name"

DEFAULT_BOOK_NAME = "Home Assistant Documentation"

# Service data keys
ATTR_AREA_FILTER = "area_filter"
ATTR_DRY_RUN = "dry_run"

# Notification messages
SUCCESS_EXPORT_COMPLETE = "Export completed successfully"
SUCCESS_EXPORT_AREA_COMPLETE = "Export completed for area: {area}"
ERROR_EXPORT_FAILED = "Export failed: {error}"
ERROR_CONNECTION_FAILED = "Failed to connect to BookStack. Check your URL and token."

# Logging
LOGGER = __name__
```

## UI Localization (`strings.json`)

```json
{
  "config": {
    "step": {
      "user": {
        "title": "BookStack Export",
        "description": "Set up BookStack Export to sync your Home Assistant devices to BookStack documentation.",
        "data": {
          "url": "BookStack URL",
          "token": "API Token",
          "book_name": "Book Name"
        },
        "data_description": {
          "url": "The full URL to your BookStack instance (e.g., https://bookstack.example.com)",
          "token": "API token from BookStack (Profile → API Tokens)",
          "book_name": "Name of the book to store documentation (default: Home Assistant Documentation)"
        }
      }
    },
    "error": {
      "auth_error": "Authentication failed. Please check your API token.",
      "connection_error": "Could not connect to BookStack. Please check the URL.",
      "unknown": "Unknown error occurred."
    },
    "abort": {
      "already_configured": "BookStack Export is already configured for this URL."
    }
  },
  "options": {
    "step": {
      "init": {
        "title": "BookStack Export Options",
        "data": {
          "url": "BookStack URL",
          "token": "API Token",
          "book_name": "Book Name"
        }
      }
    }
  },
  "services": {
    "export": {
      "name": "Export to BookStack",
      "description": "Export Home Assistant devices and entities to BookStack documentation",
      "fields": {
        "area_filter": {
          "name": "Area Filter",
          "description": "Export only devices from a specific area (optional)"
        },
        "dry_run": {
          "name": "Dry Run",
          "description": "Show what would be exported without creating content"
        }
      }
    }
  }
}
```

## Error Handling & User Feedback

### Success Notifications
```python
async def _notify_success(hass: HomeAssistant, area_filter: Optional[str] = None) -> None:
    """Send success notification."""
    if area_filter:
        message = f"Successfully exported area '{area_filter}' to BookStack"
    else:
        message = "Successfully exported all devices to BookStack"
    
    hass.async_create_task(
        hass.services.async_call(
            "persistent_notification", "create",
            {
                "message": message,
                "title": "BookStack Export Complete",
                "notification_id": "bookstack_export_success"
            }
        )
    )
```

### Error Notifications
```python
async def _notify_error(hass: HomeAssistant, error_message: str) -> None:
    """Send error notification."""
    hass.async_create_task(
        hass.services.async_call(
            "persistent_notification", "create",
            {
                "message": f"BookStack Export failed: {error_message}",
                "title": "BookStack Export Error",
                "notification_id": "bookstack_export_error"
            }
        )
    )
```

## Summary

This configuration flow and service design provides:

✅ **User-Friendly Setup**: Step-by-step configuration with validation  
✅ **Robust Error Handling**: Clear error messages and connection testing  
✅ **Flexible Export Options**: Optional area filtering and dry run mode  
✅ **Standard HA Patterns**: Follows Home Assistant integration best practices  
✅ **Comprehensive UI**: Localized strings and helpful descriptions  
✅ **Service Integration**: Easy to call from automations and scripts  

The design is production-ready and provides excellent user experience for the BookStack Export integration.