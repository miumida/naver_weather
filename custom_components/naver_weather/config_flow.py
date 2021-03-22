"""Config flow for naver_weather."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN

CONF_AREA          = 'area'
CONF_SENSOR_USE    = 'sensor_use'
CONF_SCAN_INTERVAL = 'scan_interval'

CONF_AREA_SUB          = 'area_sub'
CONF_SCAN_INTERVAL_SUB = 'scan_interval_sub'

_LOGGER = logging.getLogger(__name__)

class NaverWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Naver Weather."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize flow."""
        self._area: Optional[str]          = "날씨"
        self._sensor_use: Optional[bool]   = False
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
        default_sensor_use = self._sensor_use or False
        schema = vol.Schema(
            {
                vol.Optional(CONF_AREA, default=default_area): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=self._interval_time): int,
                vol.Optional(CONF_SENSOR_USE, default=default_sensor_use): bool,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors or {}
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """HACS config flow options handler."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.data      = None

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            self.data = user_input

        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""

        if user_input is not None:

            self.data = {}

            self.data[CONF_AREA]              = user_input.get(CONF_AREA)
            self.data[CONF_SCAN_INTERVAL]     = user_input.get(CONF_SCAN_INTERVAL)
            self.data[CONF_SENSOR_USE]        = user_input.get(CONF_SENSOR_USE)
            self.data[CONF_AREA_SUB]          = user_input.get(CONF_AREA_SUB, "")
            self.data[CONF_SCAN_INTERVAL_SUB] = user_input.get(CONF_SCAN_INTERVAL_SUB, 1020)

            return self.async_create_entry(title="", data=self.data)

        if CONF_AREA in self.config_entry.options:
            area = self.config_entry.options.get(CONF_AREA)
        else:
            area = self.config_entry.data.get(CONF_AREA)

        if CONF_SCAN_INTERVAL in self.config_entry.options:
            scan_interval = self.config_entry.options.get(CONF_SCAN_INTRERVAL)
        else:
            scan_interval = self.config_entry.data.get(CONF_SCAN_INTERVAL)

        if CONF_SENSOR_USE in self.config_entry.options:
            sensor_use = self.config_entry.options.get(CONF_SENSOR_USE)
        else:
            sensor_use = self.config_entry.data.get(CONF_SENSOR_USE)

        if CONF_AREA_SUB in self.config_entry.options:
            area_sub = self.config_entry.options.get(CONF_AREA_SUB)
        else:
            area_sub = self.config_entry.data.get(CONF_AREA_SUB)

        if CONF_SCAN_INTERVAL_SUB in self.config_entry.options:
            scan_interval_sub = self.config_entry.options.get(CONF_SCAN_INTERVAL_SUB)
        else:
            if CONF_SCAN_INTERVAL_SUB in self.config_entry.data:
                scan_interval_sub = self.config_entry.data.get(CONF_SCAN_INTERVAL_SUB)
            else:
                scan_intercal_sub = 1020

        schema = {
                   vol.Optional(CONF_AREA,          default=area): str,
                   vol.Optional(CONF_SCAN_INTERVAL, default=scan_interval): int,
                   vol.Optional(CONF_SENSOR_USE,    default=sensor_use): bool,

                   vol.Optional(CONF_AREA_SUB,          default=area_sub): str,
                   vol.Optional(CONF_SCAN_INTERVAL_SUB, default=scan_interval_sub): int,
                  }

        return self.async_show_form(step_id="user", data_schema=vol.Schema(schema))
