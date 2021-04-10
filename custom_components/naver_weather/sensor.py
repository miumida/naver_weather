"""Support for Naver Weather Sensors."""
import logging

from homeassistant.helpers.entity import Entity

from .nweather_device import NWeatherDevice

from .const import DOMAIN, WEATHER_INFO


_LOGGER = logging.getLogger(__name__)


def isfloat(v):
    try:
        float(v)
        return True
    except ValueError:
        return False


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensor for Naver Weather sensors."""

    api = hass.data[DOMAIN]["api"][config_entry.entry_id]

    def async_add_entity():
        """Add sensor from sensor."""
        entities = []
        for device in WEATHER_INFO.values():
            entities.append(NWeatherSensor(device, api))

        if entities:
            async_add_entities(entities)

    async_add_entity()
    await api.update()


class NWeatherSensor(NWeatherDevice, Entity):
    """Defines a NaverWeather Device entity."""

    @property
    def state(self):
        """Return the state of the sensor."""
        value = self.api.result.get(self.device[0])
        if value.isdigit():
            if isfloat(value):
                return float(value)
            else:
                return int(value)
        return value

    @property
    def name(self) -> str:
        """Return the name of the device."""
        if not self.api.get_data(self.unique_id):
            self.api.set_data(self.unique_id, True)
            return DOMAIN + " " + self.device[0] + " " + str(self.api.count)
        else:
            return self.device[1]

    @property
    def icon(self):
        """Return the icon of the sensor."""
        dicon = WEATHER_INFO.get(self.device[0])[3]
        if dicon != "":
            return dicon

    @property
    def device_class(self):
        """Return the class of the sensor."""
        dclass = WEATHER_INFO.get(self.device[0])[4]
        if dclass != "":
            return dclass

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this sensor."""
        unit = WEATHER_INFO.get(self.device[0])[2]
        if unit != "":
            return unit
