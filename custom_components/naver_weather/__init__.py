"""Naver Weather Sensor for Homeassistant"""
import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from datetime import datetime, timedelta

from .const import DOMAIN, PLATFORM

# area
CONF_AREA    = 'area'
DEFAULT_AREA = '날씨'

SCAN_INTERVAL = timedelta(seconds=900)

# area_sub
CONF_AREA_SUB    = 'area_sub'
DEFAULT_AREA_SUB = ''

CONF_SCAN_INTERVAL_SUB = 'scan_interval_sub'
SCAN_INTERVAL_SUB = timedelta(seconds=1020)

# sensor 사용여부
CONF_SENSOR_USE = 'sensor_use'
DEFAULT_SENSOR_USE = 'N'


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            cv.deprecated(CONF_NAME, invalidation_version="0.110"),
            vol.Schema({vol.Optional(CONF_AREA, default=DEFAULT_AREA): cv.string}),
            vol.Schema({vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period}),
            vol.Schema({vol.Optional(CONF_AREA_SUB, default=DEFAULT_AREA_SUB): cv.string}),
            vol.Schema({vol.Optional(CONF_SCAN_INTERVAL_SUB, default=SCAN_INTERVAL_SUB): cv.time_period}),
            vol.Schema({vol.Optional(CONF_SENSOR_USE, default=DEFAULT_SENSOR_USE): cv.string}),
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up naver_weather from configuration.yaml."""
    conf = config.get(DOMAIN)
    if conf:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, data=conf, context={"source": SOURCE_IMPORT}
            )
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up naver_weather from a config entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, PLATFORM)
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, PLATFORM)
