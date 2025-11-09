"""Config flow for BookStack Custom Integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_BASE_URL,
    CONF_API_TOKEN,
    CONF_BOOK_NAME,
    CONF_TIMEOUT,
    DEFAULT_TIMEOUT,
    LOGGER_NAME
)

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
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the user input
            base_url = user_input[CONF_BASE_URL].rstrip("/")
            api_token = user_input[CONF_API_TOKEN]
            timeout = user_input.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)

            # Basic URL validation
            if not base_url.startswith(("http://", "https://")):
                errors[CONF_BASE_URL] = "invalid_url"
            elif not base_url.endswith("/api"):
                # Ensure URL has /api for API calls
                base_url = f"{base_url}/api"
                user_input[CONF_BASE_URL] = base_url

            # Basic token validation
            if not api_token or len(api_token.strip()) < 10:
                errors[CONF_API_TOKEN] = "invalid_token"

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
                # Store the data
                self._data.update(user_input)

                # Test connection (async, will be implemented in Phase 2)
                # For now, we'll just proceed to the next step
                return await self.async_step_test()

        # Show the form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_BASE_URL, default=""): str,
                vol.Required(CONF_API_TOKEN, default=""): str,
                vol.Optional(CONF_BOOK_NAME, default=""): str,
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
            }),
            errors=errors,
            description_placeholders={
                "base_url_example": "https://bookstack.example.com",
                "timeout_note": "Request timeout in seconds (5-300)",
            },
        )

    async def async_step_test(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Test the BookStack connection."""
        if user_input is not None:
            # Create the config entry
            return self.async_create_entry(
                title="BookStack Custom Integration",
                data=self._data,
                description="BookStack Custom Integration configuration",
            )

        # For now, skip the test step and go directly to creation
        return self.async_create_entry(
            title="BookStack Custom Integration",
            data=self._data,
            description="BookStack Custom Integration configuration",
        )

    async def async_step_import(
        self, import_config: Dict[str, Any]
    ) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_config)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "BookStackIntegrationOptionsFlow":
        """Get the options flow for this handler."""
        return BookStackIntegrationOptionsFlow(config_entry)


class BookStackIntegrationOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for BookStack Custom Integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # Validate the user input (similar to config flow)
            base_url = user_input[CONF_BASE_URL].rstrip("/")
            api_token = user_input[CONF_API_TOKEN]

            # Basic URL validation
            if not base_url.startswith(("http://", "https://")):
                errors[CONF_BASE_URL] = "invalid_url"
            elif not base_url.endswith("/api"):
                base_url = f"{base_url}/api"
                user_input[CONF_BASE_URL] = base_url

            # Basic token validation
            if not api_token or len(api_token.strip()) < 10:
                errors[CONF_API_TOKEN] = "invalid_token"

            # Validate timeout
            try:
                timeout_int = int(user_input[CONF_TIMEOUT])
                if timeout_int < 5 or timeout_int > 300:
                    errors[CONF_TIMEOUT] = "invalid_timeout"
            except ValueError:
                errors[CONF_TIMEOUT] = "invalid_timeout"

            if not errors:
                # Update the config entry
                return self.async_create_entry(
                    title="",
                    data=user_input,
                )

        # Get current data
        current_data = self.config_entry.data
        current_options = self.config_entry.options

        # Show the form
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_BASE_URL, 
                    default=current_data.get(CONF_BASE_URL, "")
                ): str,
                vol.Required(
                    CONF_API_TOKEN, 
                    default=current_data.get(CONF_API_TOKEN, "")
                ): str,
                vol.Optional(
                    CONF_BOOK_NAME, 
                    default=current_data.get(CONF_BOOK_NAME, "")
                ): str,
                vol.Optional(
                    CONF_TIMEOUT, 
                    default=current_options.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
                ): int,
            }),
            errors=errors,
            description_placeholders={
                "base_url_example": "https://bookstack.example.com",
                "timeout_note": "Request timeout in seconds (5-300)",
            },
        )