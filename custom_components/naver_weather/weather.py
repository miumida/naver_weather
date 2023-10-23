"""Support for Naver Weather Sensors."""
from datetime import timedelta
import logging

from homeassistant.components.weather import WeatherEntity
from homeassistant.const import TEMP_CELSIUS

from .const import (
    CONDITION,
    DOMAIN,
    LOCATION,
    NOW_HUMI,
    NOW_TEMP,
    WIND_DIR,
    WIND_SPEED,
)
from .nweather_device import NWeatherDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=10)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add a entity from a config_entry."""

    api = hass.data[DOMAIN]["api"][config_entry.entry_id]

    def async_add_entity():
        """Add sensor from sensor."""
        entities = []
        device = ["Naver Weather Custom", "네이버날씨Custom", "", ""]
        entities.append(NWeatherMain(device, api))

        if entities:
            async_add_entities(entities)

    async_add_entity()


class NWeatherMain(NWeatherDevice, WeatherEntity):
    """Representation of a weather condition."""
    _attr_native_temperature_unit = TEMP_CELSIUS
    
    @property
    def name(self) -> str:
        """Return the name of the device."""
        if not self.api.get_data(self.unique_id):
            self.api.set_data(self.unique_id, True)
            return self.device[0] + " " + str(self.api.count)
        elif self.area != "날씨":
            return self.area.split(" 날씨")[0]
        else:
            return self.device[1]

    @property
    def native_temperature(self):
        """Return the temperature."""
        try:
            return float(self.api.result.get(NOW_TEMP[0]))
        except Exception:
            return

    @property
    def humidity(self):
        """Return the humidity."""
        try:
            return int(self.api.result.get(NOW_HUMI[0]))
        except Exception:
            return

    @property
    def native_wind_speed(self):
        """Return the wind speed."""
        try:
            return float(self.api.result.get(WIND_SPEED[0])) * 3.6
        except Exception:
            return

    @property
    def wind_bearing(self):
        """Return the wind bearing."""
        return self.api.result.get(WIND_DIR[0])

    @property
    def condition(self):
        """Return the weather condition."""
        return self.api.result.get(CONDITION[0])

    @property
    def state(self):
        """Return the weather state."""
        return self.api.result.get(CONDITION[0])

    @property
    def attribution(self):
        """Return the attribution."""
        return f"{self.api.weathertype}, {self.api.result.get(LOCATION[0])} - Weather forecast from Naver, Powered by miumida, Custom by ninthsword"

    @property
    def forecast(self) -> list[Forecast] | None:
        """Return the forecast."""
        return self.api.forecast

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        """Return the hourly forecast in native units.
        
        Only implement this method if `WeatherEntityFeature.FORECAST_HOURLY` is set
        """

    @property
    def should_poll(self) -> bool:
        """No polling needed for this device."""
        return True

    async def async_update(self):
        """Update current conditions."""
        await self.api.update()
