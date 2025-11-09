"""The BookStack Custom Integration integration."""
import logging

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_SHELF_NAME

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the BookStack Custom Integration component."""
    hass.data.setdefault(DOMAIN, {})
    
    # Ensure all existing config entries have devices created
    await _ensure_all_devices_exist(hass)
    
    # Register the domain for config entries
    # Note: The config flow handles the setup, no import flow needed
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up BookStack Custom Integration from a config entry."""
    _LOGGER.info("Setting up BookStack Custom Integration integration")
    
    # Store the config entry in hass.data for later use
    hass.data[DOMAIN][entry.entry_id] = entry
    
    # Create device for the configured shelf
    await _create_shelf_device(hass, entry)
    
    # Forward the setup to the config flow handler
    # Note: This integration doesn't have sensor entities
    # await hass.config_entries.async_forward_entry_setup(entry, "sensor")
    
    # Register services
    await _register_services(hass)
    
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading BookStack Custom Integration integration")
    
    # Forward the unload to the config flow handler
    # Note: This integration doesn't have entities to unload
    # unload_ok = await hass.config_entries.async_forward_entry_unload(
    #     entry, "sensor"
    # )
    
    # Always return True since we don't have entities
    unload_ok = True
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def _register_services(hass: HomeAssistant) -> None:
    """Register services for the integration."""
    from homeassistant.core import ServiceCall
    from homeassistant.components.persistent_notification import async_create
    
    async def handle_export(call: ServiceCall) -> None:
        """Handle the export service call."""
        area_filter = call.data.get("area_filter")
        _LOGGER.info(f"Exporting to BookStack (area_filter: {area_filter})")
        
        # TODO: Implement actual export logic
        # This will be implemented in Phase 3
        message = (
            "Export to BookStack started. This is a placeholder "
            "for the actual implementation."
        )
        await async_create(
            hass, message, title="BookStack Custom Integration",
            notification_id="bookstack_integration_started"
        )
    
    # Register the export service
    hass.services.async_register(DOMAIN, "export", handle_export)
    
    _LOGGER.info("BookStack Custom Integration services registered")


async def _create_shelf_device(
    hass: HomeAssistant, entry: config_entries.ConfigEntry
) -> None:
    """Create a device for the selected shelf."""
    try:
        from homeassistant.helpers import device_registry as dr
        
        device_registry = dr.async_get(hass)
        
        shelf_name = entry.data.get(CONF_SHELF_NAME, "Unknown Shelf")
        
        device_info = {
            "identifiers": {(DOMAIN, f"{entry.entry_id}_{shelf_name}")},
            "name": f"BookStack Shelf: {shelf_name}",
            "manufacturer": "BookStack",
            "model": "Shelf",
            "sw_version": "1.0",
        }
        
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            **device_info
        )
        
        _LOGGER.info(f"Device registered for shelf: {shelf_name}")
        
    except Exception as e:
        _LOGGER.error(f"Failed to register device for shelf: {e}")


async def _ensure_all_devices_exist(hass: HomeAssistant) -> None:
    """Ensure all config entries have devices created."""
    try:
        from homeassistant.helpers import device_registry as dr
        
        device_registry = dr.async_get(hass)
        
        # Get all BookStack config entries
        for entry_id, entry in hass.config_entries.async_entries(DOMAIN):
            shelf_name = entry.data.get(CONF_SHELF_NAME, "Unknown Shelf")
            
            device_info = {
                "identifiers": {(DOMAIN, f"{entry_id}_{shelf_name}")},
                "name": f"BookStack Shelf: {shelf_name}",
                "manufacturer": "BookStack",
                "model": "Shelf",
                "sw_version": "1.0",
            }
            
            device_registry.async_get_or_create(
                config_entry_id=entry_id,
                **device_info
            )
            
            _LOGGER.info(f"Ensured device exists for shelf: {shelf_name}")
            
    except Exception as e:
        _LOGGER.error(f"Failed to ensure devices exist: {e}")
        # Continue anyway, device registration failure shouldn't break the flow