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
    hass.data.setdefault(DOMAIN, {"api": {}})
    api = API(hass, entry, len(hass.data[DOMAIN]["api"]) + 1)
    hass.data[DOMAIN]["api"][entry.entry_id] = api
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    try:
        unload_ok = all(
            await asyncio.gather(
                *[
                    hass.config_entries.async_forward_entry_unload(entry, component)
                    for component in PLATFORMS
                ]
            )
        )
        if unload_ok:
            hass.data[DOMAIN]["api"].pop(entry.entry_id)

        return unload_ok
    except Exception:
        return True
