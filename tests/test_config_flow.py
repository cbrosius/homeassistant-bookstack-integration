"""Test config flow for BookStack Custom Integration."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.bookstack_integration.config_flow import (
    BookStackIntegrationConfigFlow,
    BookStackIntegrationOptionsFlow
)
from custom_components.bookstack_integration.const import (
    CONF_BASE_URL, 
    CONF_API_TOKEN, 
    CONF_BOOK_NAME, 
    CONF_TIMEOUT
)
from custom_components.bookstack_integration.bookstack_api import (
    BookStackError, 
    BookStackAuthError, 
    BookStackNotFoundError
)


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = Mock()
    hass.data = {}
    return hass


@pytest.fixture
def flow_config(mock_hass):
    """Create a config flow instance."""
    flow = BookStackIntegrationConfigFlow()
    flow.hass = mock_hass
    return flow


@pytest.fixture
def flow_options(mock_hass, mock_config_entry):
    """Create an options flow instance."""
    flow = BookStackIntegrationOptionsFlow(mock_config_entry)
    flow.hass = mock_hass
    return flow


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = Mock()
    entry.entry_id = "test_entry"
    entry.data = {
        CONF_BASE_URL: "https://bookstack.example.com/api",
        CONF_API_TOKEN: "test_token_12345",
        CONF_BOOK_NAME: "Test Book",
        CONF_TIMEOUT: 30
    }
    entry.options = {
        CONF_TIMEOUT: 30
    }
    return entry


class TestBookStackIntegrationConfigFlow:
    """Test the BookStack integration config flow."""

    def test_async_step_user_valid_input(self, flow_config):
        """Test user step with valid input."""
        user_input = {
            CONF_BASE_URL: "https://bookstack.example.com",
            CONF_API_TOKEN: "test_token_12345",
            CONF_BOOK_NAME: "Test Book",
            CONF_TIMEOUT: 30
        }
        
        # Run the async step
        result = flow_config.hass.async_add_executor_job(
            flow_config.async_step_user, user_input
        )
        
        # Should proceed to test step
        assert result.get("step_id") == "test"

    def test_async_step_user_invalid_url(self, flow_config):
        """Test user step with invalid URL."""
        user_input = {
            CONF_BASE_URL: "not_a_valid_url",
            CONF_API_TOKEN: "test_token_12345",
            CONF_BOOK_NAME: "Test Book",
            CONF_TIMEOUT: 30
        }
        
        result = flow_config.hass.async_add_executor_job(
            flow_config.async_step_user, user_input
        )
        
        # Should show form with error
        assert result.get("type") == FlowResultType.FORM
        assert CONF_BASE_URL in result.get("errors", {})

    def test_async_step_user_invalid_token(self, flow_config):
        """Test user step with invalid token."""
        user_input = {
            CONF_BASE_URL: "https://bookstack.example.com",
            CONF_API_TOKEN: "short",
            CONF_BOOK_NAME: "Test Book",
            CONF_TIMEOUT: 30
        }
        
        result = flow_config.hass.async_add_executor_job(
            flow_config.async_step_user, user_input
        )
        
        # Should show form with error
        assert result.get("type") == FlowResultType.FORM
        assert CONF_API_TOKEN in result.get("errors", {})

    @patch('custom_components.bookstack_integration.config_flow.BookStackClient')
    def test_async_step_test_connection_success(self, mock_client_class, flow_config):
        """Test successful connection test."""
        # Mock successful connection
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client_class.return_value = mock_client
        
        # Set up flow data
        flow_config._data = {
            CONF_BASE_URL: "https://bookstack.example.com/api",
            CONF_API_TOKEN: "test_token_12345",
            CONF_BOOK_NAME: "Test Book",
            CONF_TIMEOUT: 30
        }
        
        # Test connection
        result = flow_config.hass.async_add_executor_job(
            flow_config.async_step_test
        )
        
        # Should show success form
        assert result.get("type") == FlowResultType.FORM
        assert result.get("step_id") == "test"
        assert "Successfully connected" in result.get("description", "")

    @patch('custom_components.bookstack_integration.config_flow.BookStackClient')
    def test_async_step_test_connection_auth_error(
        self, mock_client_class, flow_config
    ):
        """Test connection test with authentication error."""
        # Mock auth error
        mock_client = Mock()
        mock_client.test_connection.side_effect = BookStackAuthError("Auth failed")
        mock_client_class.return_value = mock_client
        
        flow_config._data = {
            CONF_BASE_URL: "https://bookstack.example.com/api",
            CONF_API_TOKEN: "test_token_12345",
            CONF_BOOK_NAME: "Test Book",
            CONF_TIMEOUT: 30
        }
        
        result = flow_config.hass.async_add_executor_job(
            flow_config.async_step_test
        )
        
        # Should return to user form with connection error
        assert result.get("type") == FlowResultType.FORM
        assert result.get("step_id") == "user"
        assert "Authentication failed" in result.get("description", "")

    @patch('custom_components.bookstack_integration.config_flow.BookStackClient')
    def test_async_step_test_connection_not_found_error(
        self, mock_client_class, flow_config
    ):
        """Test connection test with not found error."""
        # Mock not found error
        mock_client = Mock()
        mock_client.test_connection.side_effect = BookStackNotFoundError("Not found")
        mock_client_class.return_value = mock_client
        
        flow_config._data = {
            CONF_BASE_URL: "https://bookstack.example.com/api",
            CONF_API_TOKEN: "test_token_12345",
            CONF_BOOK_NAME: "Test Book",
            CONF_TIMEOUT: 30
        }
        
        result = flow_config.hass.async_add_executor_job(
            flow_config.async_step_test
        )
        
        # Should return to user form with not found error
        assert result.get("type") == FlowResultType.FORM
        assert result.get("step_id") == "user"
        assert "not found" in result.get("description", "").lower()


class TestBookStackIntegrationOptionsFlow:
    """Test the BookStack integration options flow."""

    def test_async_step_init_valid_input(self, flow_options, mock_config_entry):
        """Test options flow with valid input."""
        user_input = {
            CONF_BASE_URL: "https://newbookstack.example.com",
            CONF_API_TOKEN: "new_token_12345",
            CONF_BOOK_NAME: "New Test Book",
            CONF_TIMEOUT: 45
        }
        
        with patch.object(flow_options, 'async_create_entry') as mock_create_entry:
            result = flow_options.hass.async_add_executor_job(
                flow_options.async_step_init, user_input
            )
            
            # Should create new entry
            mock_create_entry.assert_called_once()
            assert result is not None

    def test_async_step_init_invalid_url(self, flow_options, mock_config_entry):
        """Test options flow with invalid URL."""
        user_input = {
            CONF_BASE_URL: "invalid_url",
            CONF_API_TOKEN: "test_token_12345",
            CONF_BOOK_NAME: "Test Book",
            CONF_TIMEOUT: 30
        }
        
        result = flow_options.hass.async_add_executor_job(
            flow_options.async_step_init, user_input
        )
        
        # Should show form with error
        assert result.get("type") == FlowResultType.FORM
        assert CONF_BASE_URL in result.get("errors", {})


class TestConfigFlowIntegration:
    """Integration tests for config flow."""

    @patch('custom_components.bookstack_integration.config_flow.BookStackClient')
    def test_full_config_flow_success(self, mock_client_class):
        """Test complete config flow from start to finish."""
        mock_hass = Mock()
        flow = BookStackIntegrationConfigFlow()
        flow.hass = mock_hass
        
        # Mock successful connection
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client_class.return_value = mock_client
        
        with patch.object(flow, 'async_create_entry') as mock_create_entry:
            # Step 1: User input
            user_input = {
                CONF_BASE_URL: "https://bookstack.example.com",
                CONF_API_TOKEN: "test_token_12345",
                CONF_BOOK_NAME: "Test Book",
                CONF_TIMEOUT: 30
            }
            
            result1 = flow.hass.async_add_executor_job(
                flow.async_step_user, user_input
            )
            
            # Should proceed to test step
            assert result1.get("step_id") == "test"
            
            # Step 2: Test connection (show form)
            result2 = flow.hass.async_add_executor_job(
                flow.async_step_test
            )
            
            # Should show success form
            assert result2.get("step_id") == "test"
            
            # Step 3: User confirms
            confirm_input = {"confirm": True}
            result3 = flow.hass.async_add_executor_job(
                flow.async_step_test, confirm_input
            )
            
            # Should create entry
            mock_create_entry.assert_called_once()
            call_args = mock_create_entry.call_args
            assert call_args[1]["title"] == "BookStack Custom Integration"
            assert call_args[1]["data"][CONF_BASE_URL] == "https://bookstack.example.com/api"

    def test_config_flow_import(self, flow_config):
        """Test import from configuration.yaml."""
        import_config = {
            CONF_BASE_URL: "https://bookstack.example.com/api",
            CONF_API_TOKEN: "import_token_12345",
            CONF_BOOK_NAME: "Imported Book",
            CONF_TIMEOUT: 45
        }
        
        with patch.object(flow_config, 'async_step_user') as mock_step_user:
            flow_config.async_step_import(import_config)
            mock_step_user.assert_called_once_with(import_config)