"""Config flow for naver_weather."""
import voluptuous as vol
import homeassistant.helpers.config_validation as cv


from homeassistant import config_entries
from homeassistant.core import callback

from .const import CONF_AREA, CONF_TODAY, DOMAIN, NW_OPTIONS


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Naver Weather."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            area = user_input.get(CONF_AREA, "날씨")
            user_input[CONF_AREA] = area
            await self.async_set_unique_id()
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=area, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_AREA): cv.string,
                    vol.Optional(CONF_TODAY, default=False): bool,
                }
            ),
            errors=errors,
        )

    async def async_step_import(self, user_input=None):
        """Handle configuration by yaml file."""
        await self.async_set_unique_id(user_input[CONF_AREA])
        for entry in self._async_current_entries():
            if entry.unique_id == self.unique_id:
                self.hass.config_entries.async_update_entry(entry, data=user_input)
                self._abort_if_unique_id_configured()
        return self.async_create_entry(title=user_input[CONF_AREA], data=user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Handle a option flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow for Naver Weather."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        conf = self.config_entry
        if conf.source == config_entries.SOURCE_IMPORT:
            return self.async_show_form(step_id="init", data_schema=None)
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = {}
        data_list = [CONF_AREA]
        for name, default, validation in NW_OPTIONS:
            to_default = conf.options.get(name, default)
            if name in data_list and conf.options.get(name, default) == default:
                to_default = conf.data.get(name, default)
            key = vol.Optional(name, default=to_default)
            options_schema[key] = validation
        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(options_schema)
        )
