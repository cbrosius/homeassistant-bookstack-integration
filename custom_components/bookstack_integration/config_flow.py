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
    CONF_TOKEN_ID,
    CONF_TOKEN_SECRET,
    CONF_BOOK_NAME,
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
        """Handle the initial step."""
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
                # Store the data
                self._data.update(user_input)

                # Test connection
                return await self.async_step_test()

        # Show the form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_BASE_URL, default=""): str,
                vol.Required(CONF_TOKEN_ID, default=""): str,
                vol.Required(CONF_TOKEN_SECRET, default=""): str,
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
                
                # Create the config entry
                return self.async_create_entry(
                    title="BookStack Custom Integration",
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
            
            # Return to user form with error
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_BASE_URL, default=""): str,
                    vol.Required(CONF_TOKEN_ID, default=""): str,
                    vol.Required(CONF_TOKEN_SECRET, default=""): str,
                    vol.Optional(CONF_BOOK_NAME, default=""): str,
                    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
                }),
                errors={"base": error_message},
            )
        except Exception as e:
            _LOGGER.error(f"Unexpected error during connection test: {e}")
            
            # Return to user form with unknown error
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_BASE_URL, default=""): str,
                    vol.Required(CONF_TOKEN_ID, default=""): str,
                    vol.Required(CONF_TOKEN_SECRET, default=""): str,
                    vol.Optional(CONF_BOOK_NAME, default=""): str,
                    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
                }),
                errors={"base": "unknown"},
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
            token_id = user_input[CONF_TOKEN_ID]
            token_secret = user_input[CONF_TOKEN_SECRET]

            # Basic URL validation
            if not base_url.startswith(("http://", "https://")):
                errors[CONF_BASE_URL] = "invalid_url"
            elif not base_url.endswith("/api"):
                base_url = f"{base_url}/api"
                user_input[CONF_BASE_URL] = base_url

            # Basic token validation
            if not token_id or len(token_id.strip()) < 5:
                errors[CONF_TOKEN_ID] = "invalid_token_id"
            if not token_secret or len(token_secret.strip()) < 10:
                errors[CONF_TOKEN_SECRET] = "invalid_token_secret"

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
                    CONF_TOKEN_ID,
                    default=current_data.get(CONF_TOKEN_ID, "")
                ): str,
                vol.Required(
                    CONF_TOKEN_SECRET,
                    default=current_data.get(CONF_TOKEN_SECRET, "")
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