"""Naver Weather Sensor for Homeassistant."""
import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .api_nweather import NWeatherAPI as API

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up naver_weather from configuration.yaml."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up naver_weather from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    api = API(hass, entry, len(hass.data[DOMAIN]) + 1)
    await api.update()
    hass.data[DOMAIN][entry.entry_id] = api
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    try:
        # hass.data[DOMAIN][entry.entry_id].stop(False)
        unload_ok = all(
            await asyncio.gather(
                *[
                    hass.config_entries.async_forward_entry_unload(entry, component)
                    for component in PLATFORMS
                ]
            )
        )
        if unload_ok:
            hass.data[DOMAIN].pop(entry.entry_id)

        return unload_ok
    except Exception:
        return True
