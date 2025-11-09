"""Config flow for BookStack Custom Integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_BASE_URL,
    CONF_TOKEN_ID,
    CONF_TOKEN_SECRET,
    CONF_SHELF_NAME,
    CONF_TIMEOUT,
    DEFAULT_TIMEOUT,
    LOGGER_NAME
)
from .bookstack_api import BookStackClient, BookStackConfig, BookStackError

_LOGGER = logging.getLogger(LOGGER_NAME)


class BookStackIntegrationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BookStack Custom Integration."""

    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: Dict[str, Any] = {}
        self._errors: Dict[str, str] = {}

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step - Base Settings."""
        errors = {}

        if user_input is not None:
            # Validate the user input
            base_url = user_input[CONF_BASE_URL].rstrip("/")
            token_id = user_input[CONF_TOKEN_ID]
            token_secret = user_input[CONF_TOKEN_SECRET]
            timeout = user_input.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)

            # Basic URL validation
            if not base_url.startswith(("http://", "https://")):
                errors[CONF_BASE_URL] = "invalid_url"
            elif not base_url.endswith("/api"):
                # Ensure URL has /api for API calls
                base_url = f"{base_url}/api"
                user_input[CONF_BASE_URL] = base_url

            # Basic token validation
            if not token_id or len(token_id.strip()) < 5:
                errors[CONF_TOKEN_ID] = "invalid_token_id"
            if not token_secret or len(token_secret.strip()) < 10:
                errors[CONF_TOKEN_SECRET] = "invalid_token_secret"

            # Validate timeout
            try:
                timeout_int = int(timeout)
                if timeout_int < 5 or timeout_int > 300:
                    errors[CONF_TIMEOUT] = "invalid_timeout"
                else:
                    user_input[CONF_TIMEOUT] = timeout_int
            except ValueError:
                errors[CONF_TIMEOUT] = "invalid_timeout"

            if not errors:
                # Store the base settings data
                self._data.update(user_input)

                # Move to shelf selection step
                return await self.async_step_shelf_selection()

        # Show the form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_BASE_URL, default=""): str,
                vol.Required(CONF_TOKEN_ID, default=""): str,
                vol.Required(CONF_TOKEN_SECRET, default=""): str,
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
            }),
            errors=errors,
            description_placeholders={
                "base_url_example": "https://bookstack.example.com",
                "timeout_note": "Request timeout in seconds (5-300)",
            },
        )

    async def async_step_shelf_selection(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the shelf selection step."""
        errors = {}

        if user_input is not None:
            # Check if user wants to use existing shelf or create new
            if "existing_shelf" in user_input:
                if user_input["existing_shelf"] == "__create_new__":
                    # User wants to create a new shelf
                    return await self.async_step_create_shelf()
                elif user_input["existing_shelf"]:
                    # User selected an existing shelf
                    selected_shelf = user_input["existing_shelf"]
                    self._data[CONF_SHELF_NAME] = selected_shelf
                    return await self.async_step_test()

        # Get available shelves
        available_shelves = []
        try:
            config = BookStackConfig(
                base_url=self._data[CONF_BASE_URL],
                token_id=self._data[CONF_TOKEN_ID],
                token_secret=self._data[CONF_TOKEN_SECRET],
                timeout=self._data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
            )
            client = BookStackClient(config)
            
            # Fetch shelves in executor to avoid blocking
            available_shelves = await self.hass.async_add_executor_job(
                client.get_shelves
            )
            _LOGGER.info(
                f"Retrieved {len(available_shelves)} shelves for selection"
            )
            
        except Exception as e:
            _LOGGER.warning(f"Could not fetch available shelves: {e}")
            # Continue without shelves list

        # Create choices for available shelves
        shelf_choices = {}
        if available_shelves:
            for shelf in available_shelves:
                shelf_choices[shelf.name] = shelf.name

        # Add option to create new shelf
        shelf_choices["__create_new__"] = "Create New Shelf"

        # Show the shelf selection form
        return self.async_show_form(
            step_id="shelf_selection",
            data_schema=vol.Schema({
                vol.Required("existing_shelf", default=""): vol.In(
                    shelf_choices
                ),
            }),
            errors=errors,
            description_placeholders={
                "shelf_note": (
                    "Select an existing shelf or choose to create a new one"
                ),
            },
        )

    async def async_step_create_shelf(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle creating a new shelf."""
        errors = {}

        if user_input is not None:
            # Validate new shelf input
            shelf_name = user_input[CONF_SHELF_NAME]

            if not shelf_name or len(shelf_name.strip()) < 2:
                errors[CONF_SHELF_NAME] = "invalid_shelf_name"

            if not errors:
                # Store the new shelf information
                self._data[CONF_SHELF_NAME] = shelf_name.strip()
                return await self.async_step_test()

        # Show the new shelf creation form
        return self.async_show_form(
            step_id="create_shelf",
            data_schema=vol.Schema({
                vol.Required(CONF_SHELF_NAME, default=""): str,
            }),
            errors=errors,
            description_placeholders={
                "shelf_note": "Name for the new shelf",
            },
        )

    async def async_step_test(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Test the BookStack connection and setup."""
        # Test the BookStack connection
        try:
            config = BookStackConfig(
                base_url=self._data[CONF_BASE_URL],
                token_id=self._data[CONF_TOKEN_ID],
                token_secret=self._data[CONF_TOKEN_SECRET],
                timeout=self._data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
            )
            client = BookStackClient(config)
            
            # Run the test in executor to avoid blocking
            connection_result = await self.hass.async_add_executor_job(
                client.test_connection
            )
            
            if connection_result:
                _LOGGER.info("BookStack connection test successful")
                
                # Create or verify shelf
                try:
                    await self.hass.async_add_executor_job(
                        client.find_or_create_shelf,
                        self._data[CONF_SHELF_NAME]
                    )
                    _LOGGER.info(
                        f"Shelf '{self._data[CONF_SHELF_NAME]}' ready"
                    )
                except Exception as e:
                    _LOGGER.warning(f"Could not verify/create shelf: {e}")
                    # Continue anyway, shelf can be created later
                
                # Create the config entry
                return self.async_create_entry(
                    title="My Bookstack Instance",
                    data=self._data,
                )
            else:
                raise BookStackError("Connection test failed")
                
        except BookStackError as e:
            _LOGGER.error(f"BookStack connection test failed: {e}")
            error_message = "connection_failed"
            
            if "authentication" in str(e).lower() or "401" in str(e):
                error_message = "auth_failed"
            elif "not found" in str(e).lower() or "404" in str(e):
                error_message = "connection_failed"
            elif "timeout" in str(e).lower() or "time" in str(e).lower():
                error_message = "timeout"
            elif "rate" in str(e).lower() or "429" in str(e):
                error_message = "connection_failed"
            
            # Return to shelf selection form with error
            return self.async_show_form(
                step_id="shelf_selection",
                data_schema=vol.Schema({
                    vol.Required(CONF_SHELF_NAME, default=""): str,
                }),
                errors={"base": error_message},
            )
        except Exception as e:
            _LOGGER.error(f"Unexpected error during connection test: {e}")
            
            # Return to shelf selection form with unknown error
            return self.async_show_form(
                step_id="shelf_selection",
                data_schema=vol.Schema({
                    vol.Required(CONF_SHELF_NAME, default=""): str,
                }),
                errors={"base": "unknown"},
            )

    async def async_step_import(
        self, import_config: Dict[str, Any]
    ) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_config)
