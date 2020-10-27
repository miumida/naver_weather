"""Config flow for naver_weather."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import (CONF_SCAN_INTERVAL)

from .const import DOMAIN

CONF_AREA    = 'area'
CONF_SENSOR_USE  = 'sensor_use'

_LOGGER = logging.getLogger(__name__)

class NaverWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Naver Weather."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize flow."""
        self._area: Optional[str] = "날씨"
        self._sensor_use: Optional[str] = "N"
        self._interval_time: Optional[int] = 900
 
    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            self._area          = user_input[CONF_AREA]
            self._sensor_use    = user_input[CONF_SENSOR_USE]
            self._interval_time = user_input[CONF_SCAN_INTERVAL]

            return self.async_create_entry(title=DOMAIN, data=user_input)

        #if self._async_current_entries():
        #    return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            return self._show_user_form(errors)

        #return self.async_create_entry(title=DOMAIN, data=user_input)

    async def async_step_import(self, import_info):
        """Handle import from config file."""
        return await self.async_step_user(import_info)

    @callback
    def _show_user_form(self, errors=None):
        default_area       = self._area or '날씨'
        default_sensor_use = self._sensor_use or 'N'
        schema = vol.Schema(
            {
                vol.Optional(CONF_AREA, default=default_area): str,
                vol.Optional(CONF_SENSOR_USE, default=default_sensor_use): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=self._interval_time): int,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors or {}
        )
