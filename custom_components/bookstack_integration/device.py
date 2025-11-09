"""Device entity for BookStack shelf."""
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, CONF_SHELF_NAME, LOGGER_NAME

_LOGGER = logging.getLogger(LOGGER_NAME)


class BookStackShelfDevice(CoordinatorEntity):
    """Device entity for BookStack shelf."""

    def __init__(
        self,
        hass: HomeAssistant,
        shelf_name: str,
        entry_id: str,
        coordinator: DataUpdateCoordinator,
    ) -> None:
        """Initialize the device."""
        super().__init__(coordinator)
        self._hass = hass
        self._shelf_name = shelf_name
        self._entry_id = entry_id
        self._attr_name = f"BookStack Shelf: {shelf_name}"
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{shelf_name}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry_id}_{self._shelf_name}")},
            name=self._attr_name,
            manufacturer="BookStack",
            model="Shelf",
            sw_version="1.0",
            via_device=(DOMAIN, self._entry_id),
        )

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self._attr_name

    @property
    def unique_id(self) -> str:
        """Return the unique id of the device."""
        return self._attr_unique_id