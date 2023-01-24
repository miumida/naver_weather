"""Device class."""

import logging

from homeassistant.core import callback
from homeassistant.helpers.entity import Entity

from .const import DEVICE_REG, DEVICE_UNREG, DOMAIN

_LOGGER = logging.getLogger(__name__)


class NWeatherBase:
    """Base class."""

    def __init__(self, device, api):
        """Init device class."""
        self.device = device
        self.api = api
        self.area = api.area
        self.api.init_device(self.unique_id)
        self.register = self.api.get_device(self.unique_id, DEVICE_REG)
        self.unregister = self.api.get_device(self.unique_id, DEVICE_UNREG)

    @property
    def unique_id(self) -> str:
        """Get unique ID."""
        return self.area + ":" + self.device[0]

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "connections": {(self.area, self.unique_id)},
            "identifiers": {
                (
                    DOMAIN,
                    self.area,
                )
            },
            "manufacturer": f"{self.api.brand_name}",
            "model": f"{self.api.model}_{self.api.version}",
            "name": f"{self.api.brand_name} {self.area}",
            "sw_version": self.api.version,
            "via_device": (DOMAIN, self.area),
            "DeviceEntryType": "service",
        }


class NWeatherDevice(NWeatherBase, Entity):
    """Defines a Pad Device entity."""

    TYPE = ""

    def __init__(self, device, api):
        """Initialize the instance."""
        super().__init__(device, api)
        self.api.unique[self.unique_id] = {}
        self.api.hass.data[DOMAIN][self.unique_id] = True

    @property
    def entity_registry_enabled_default(self):
        """entity_registry_enabled_default."""
        return True

    async def async_added_to_hass(self):
        """Subscribe to device events."""
        self.register(self.unique_id, self.async_update_callback)
        if self.device[0] == "Naver Weather Custom":
            await self.api.update()
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        """Disconnect device object when removed."""
        if self.unique_id in self.api.hass.data[DOMAIN]:
            self.api.hass.data[DOMAIN].pop(self.unique_id)
        self.unregister(self.unique_id)

    @callback
    def async_update_callback(self):
        """Update the device's state."""
        self.async_write_ha_state()

    @property
    def available(self):
        """Return True if device is available."""
        return True

    @property
    def should_poll(self) -> bool:
        """No polling needed for this device."""
        return False

    @property
    def extra_state_attributes (self):
        """Return the state attributes of the sensor."""
        attr = {}
        return attr
