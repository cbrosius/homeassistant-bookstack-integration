"""The BookStack Custom Integration integration."""
import logging
from typing import Any, Dict

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_SHELF_NAME
from .bookstack_api import BookStackError

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


async def _discover_home_assistant_areas(
    hass: HomeAssistant,
) -> Dict[str, Any]:
    """Discover all areas from Home Assistant."""
    from homeassistant.helpers import area_registry as ar
    
    try:
        _LOGGER.debug("Starting Home Assistant area discovery")
        area_registry = ar.async_get(hass)
        
        if not area_registry.areas:
            _LOGGER.warning("No areas found in Home Assistant area registry")
            return {}
        
        areas = {}
        for area in area_registry.areas.values():
            areas[area.id] = {
                "name": area.name,
                "normalized_name": area.normalized_name,
                "picture": area.picture,
                "aliases": list(area.aliases) if area.aliases else []
            }
            _LOGGER.debug(
                f"Discovered area: {area.name} (ID: {area.id})"
            )
        
        _LOGGER.info(
            f"Successfully discovered {len(areas)} areas from Home Assistant"
        )
        return areas
        
    except Exception as e:
        _LOGGER.error(
            f"Failed to discover Home Assistant areas: {e}",
            exc_info=True
        )
        raise BookStackError(f"Area discovery failed: {e}")


async def _get_area_devices_and_entities(
    hass: HomeAssistant, area_id: str
) -> Dict[str, Any]:
    """Get all devices and entities for a specific area."""
    from homeassistant.helpers import device_registry as dr
    
    try:
        _LOGGER.debug(f"Discovering devices and entities for area {area_id}")
        device_registry = dr.async_get(hass)
        
        # Get devices for this area
        devices = []
        for device in device_registry.devices.values():
            if device.area_id == area_id:
                devices.append({
                    "id": device.id,
                    "name": device.name,
                    "name_by_user": device.name_by_user,
                    "manufacturer": device.manufacturer,
                    "model": device.model,
                    "identifiers": list(device.identifiers),
                    "area_id": device.area_id
                })
        
        # Get entities for this area
        entities = []
        for entity in hass.states.async_all():
            if entity.attributes.get("area_id") == area_id:
                friendly_name = entity.attributes.get("friendly_name", "")
                unit_of_measurement = entity.attributes.get(
                    "unit_of_measurement"
                )
                entities.append({
                    "entity_id": entity.entity_id,
                    "friendly_name": friendly_name,
                    "device_class": entity.attributes.get("device_class"),
                    "unit_of_measurement": unit_of_measurement
                })
        
        result = {
            "devices": devices,
            "entities": entities,
            "device_count": len(devices),
            "entity_count": len(entities)
        }
        
        _LOGGER.debug(
            f"Found {len(devices)} devices and {len(entities)} "
            f"entities for area {area_id}"
        )
        return result
        
    except Exception as e:
        _LOGGER.error(
            f"Failed to get devices and entities for area {area_id}: {e}",
            exc_info=True
        )
        return {
            "devices": [],
            "entities": [],
            "device_count": 0,
            "entity_count": 0
        }


def _map_areas_to_floors(areas: Dict[str, Any]) -> Dict[str, Any]:
    """Map discovered areas to floor chapters."""
    floor_mapping = {
        "Ground Floor": [
            "living", "kitchen", "garage", "entrance", "dining"
        ],
        "First Floor": [
            "bedroom", "bathroom", "office", "guest"
        ],
        "Basement": ["basement", "cellar"],
        "Attic": ["attic", "loft"],
        "Outside": [
            "garden", "patio", "balcony", "driveway", "outside"
        ]
    }
    
    areas_by_floor = {
        "Ground Floor": [],
        "First Floor": [],
        "Basement": [],
        "Attic": [],
        "Outside": []
    }
    
    unmapped_areas = []
    
    for area_id, area_info in areas.items():
        area_name_lower = area_info["name"].lower()
        mapped = False
        
        for floor_name, floor_keywords in floor_mapping.items():
            if any(keyword in area_name_lower for keyword in floor_keywords):
                areas_by_floor[floor_name].append(area_id)
                _LOGGER.debug(
                    f"Mapped area '{area_info['name']}' "
                    f"to floor '{floor_name}'"
                )
                mapped = True
                break
        
        if not mapped:
            unmapped_areas.append(area_id)
            _LOGGER.debug(
                f"Area '{area_info['name']}' "
                f"could not be mapped to a floor"
            )
    
    # Add unmapped areas to "Other" or create new chapters
    if unmapped_areas:
        areas_by_floor["Other Areas"] = unmapped_areas
        _LOGGER.info(
            f"{len(unmapped_areas)} areas placed in "
            f"'Other Areas' category"
        )
    
    total_areas = sum(len(areas) for areas in areas_by_floor.values())
    active_floors = len([k for k, v in areas_by_floor.items() if v])
    _LOGGER.info(
        f"Area mapping complete: {total_areas} areas "
        f"mapped to {active_floors} floors"
    )
    
    return areas_by_floor


async def _register_services(hass: HomeAssistant) -> None:
    """Register services for the integration."""
    from homeassistant.core import ServiceCall
    
    async def handle_export(call: ServiceCall) -> None:
        """Handle the export service call with full implementation."""
        area_filter = call.data.get("area_filter")
        _LOGGER.info(f"Exporting to BookStack (area_filter: {area_filter})")
        
        try:
            # Get all config entries for BookStack
            bookstack_entries = [
                entry for entry in
                hass.config_entries.async_entries(DOMAIN)
            ]
            
            if not bookstack_entries:
                _LOGGER.error("No BookStack configuration found")
                return
            
            # Use the first config entry
            entry = bookstack_entries[0]
            
            # Get BookStack client
            from .bookstack_api import BookStackClient, BookStackConfig
            
            config = BookStackConfig(
                base_url=entry.data["base_url"],
                token_id=entry.data["token_id"],
                token_secret=entry.data["token_secret"],
                timeout=entry.data.get("timeout", 30)
            )
            client = BookStackClient(config)
            
            # Discover areas
            areas = await _discover_home_assistant_areas(hass)
            _LOGGER.info(
                f"Discovered {len(areas)} areas in Home Assistant"
            )
            
            if not areas:
                _LOGGER.error("No areas found in Home Assistant")
                return
            
            # Create or get the configured shelf
            from .const import CONF_SHELF_NAME
            shelf_name = entry.data.get(
                CONF_SHELF_NAME, "Home Assistant Documentation"
            )
            shelf = await hass.async_add_executor_job(
                client.find_or_create_shelf, shelf_name
            )
            
            # Create or get Areas book
            areas_book = await hass.async_add_executor_job(
                client.find_or_create_areas_book
            )
            
            # Assign book to shelf
            shelf_assigned = await hass.async_add_executor_job(
                client.assign_book_to_shelf, areas_book.id, shelf.id
            )
            
            _LOGGER.info(
                f"Using Areas book: {areas_book.name} "
                f"(ID: {areas_book.id})"
            )
            if shelf_assigned:
                _LOGGER.info(
                    f"Assigned Areas book to shelf: {shelf.name} "
                    f"(ID: {shelf.id})"
                )
            
            # Map areas to floors
            areas_by_floor = _map_areas_to_floors(areas)
            
            # Create structure and pages
            created_chapters = 0
            created_pages = 0
            
            for floor_name, floor_area_ids in areas_by_floor.items():
                if area_filter:
                    if area_filter.lower() not in floor_name.lower():
                        continue
                
                if not floor_area_ids:
                    continue
                
                # Create floor chapter
                floor_chapter = await hass.async_add_executor_job(
                    client.create_area_chapter,
                    areas_book.id,
                    floor_name,
                    {}
                )
                created_chapters += 1
                
                # Create pages for each area in floor
                for area_id in floor_area_ids:
                    area_info = await _get_area_devices_and_entities(
                        hass, area_id
                    )
                    await hass.async_add_executor_job(
                        client.create_area_page,
                        floor_chapter.id,
                        areas[area_id]["name"],
                        area_info
                    )
                    created_pages += 1
            
            _LOGGER.info(
                f"Successfully exported {len(areas)} areas to BookStack "
                f"({created_chapters} chapters, {created_pages} pages)"
            )
            
        except BookStackError as e:
            _LOGGER.error(f"BookStack API error during export: {e}")
        except Exception as e:
            _LOGGER.error(f"Export failed: {e}", exc_info=True)
    
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
        for entry in hass.config_entries.async_entries(DOMAIN):
            entry_id = entry.entry_id
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