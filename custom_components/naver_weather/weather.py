"""Support for Naver Weather Sensors."""
from datetime import timedelta
import logging

from homeassistant.components.weather import WeatherEntity
from homeassistant.const import UnitOfTemperature, UnitOfSpeed, UnitOfLength

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_HAIL,
    ATTR_CONDITION_LIGHTNING,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SUNNY,

    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,

    DOMAIN as SENSOR_DOMAIN,
    Forecast,
    WeatherEntityFeature,
)

from .const import (
    CONDITION,
    DOMAIN,
    FEEL_TEMP,
    LOCATION,
    NOW_HUMI,
    NOW_TEMP,
    NOW_WEATHER,
    RAINFALL,
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
        device = ["Naver Weather", "네이버날씨", "", ""]
        entities.append(NWeatherMain(device, api))

        if entities:
            async_add_entities(entities)

    async_add_entity()


class NWeatherMain(NWeatherDevice, WeatherEntity):
    """Representation of a weather condition."""
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND
    _attr_native_precipitation_unit = UnitOfLength.MILLIMETERS
    _attr_supported_features = ( WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_TWICE_DAILY )
    
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
            return float(self.api.result.get(WIND_SPEED[0]))
        except Exception:
            return

    @property
    def wind_bearing(self):
        """Return the wind bearing."""
        return self.api.result.get(WIND_DIR[0])

    @property
    def native_apparent_temperature(self):
        """Return the apparent temperature."""
        try:
            return float(self.api.result.get(FEEL_TEMP[0]))
        except Exception:
            return

    @property
    def native_precipitation(self):
        """Return the precipitation."""
        try:
            val = self.api.result.get(RAINFALL[0])
            if val is None or val == "":
                return 0.0
            return float(val)
        except Exception:
            return 0.0

    @property
    def condition(self):
        """Return the weather condition."""
        return self.api.result.get(CONDITION[0])

    @property
    def state(self):
        """Return the weather state."""
        return self.api.result.get(CONDITION[0])


    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast in native units.
        
        Only implement this method if `WeatherEntityFeature.FORECAST_DAILY` is set
        """
        return self._forecast(WeatherEntityFeature.FORECAST_DAILY)

    async def async_forecast_twice_daily(self) -> list[Forecast] | None:
        """Return the daily forecast in native units.
        
        Only implement this method if `WeatherEntityFeature.FORECAST_DAILY` is set
        """
        return self._forecast(WeatherEntityFeature.FORECAST_TWICE_DAILY)

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        # 제거할 속성 목록 (표준 속성으로 이동했거나 불필요한 것들)
        exclude_keys = [
            "airOfferInfoUpdate",
            NOW_TEMP[0],    # NowTemp
            NOW_HUMI[0],    # Humidity
            NOW_WEATHER[0], # NowWeather
            CONDITION[0],   # Condition
            WIND_SPEED[0],  # WindSpeed
            WIND_DIR[0],    # WindBearing
            # FEEL_TEMP와 RAINFALL은 하단에서 표준 속성으로 이미 제공되므로 중복 필요 없음
            FEEL_TEMP[0],
            # RAINFALL[0], # 웨더 카드 호환성을 위해 속성에 유지
        ]
        return {k: v for k, v in self.api.result.items() if k not in exclude_keys}

    @property
    def should_poll(self) -> bool:
        """No polling needed for this device."""
        return True

    async def async_update(self):
        """Update current conditions."""
        await self.api.update()


    @property
    def forecast(self) -> list[Forecast] | None:
        """Return the forecast."""
        return self._forecast(WeatherEntityFeature.FORECAST_DAILY)

    def _forecast(self, feature) -> list[Forecast] | None:
        forecast = []

        for data in self.api.forecast:
            #주간
            next_day = {
                ATTR_FORECAST_TIME: data["datetime"],
                ATTR_FORECAST_CONDITION: self._condition_daily(data["condition_am"], data["condition_pm"]),
                ATTR_FORECAST_TEMP_LOW: data["templow"],
                ATTR_FORECAST_TEMP: data["temperature"],
                ATTR_FORECAST_PRECIPITATION_PROBABILITY: data["rain_rate_am"],
                #ATTR_FORECAST_WIND_BEARING: data[""],
                #ATTR_FORECAST_WIND_SPEED: data[""],
                
                # Not officially supported, but nice additions.
                "condition_am": data["condition_am"],
                "condition_pm": data["condition_pm"],

                "rain_rate_am": data["rain_rate_am"],
                "rain_rate_pm": data["rain_rate_pm"]
            }

            if feature == WeatherEntityFeature.FORECAST_TWICE_DAILY:
                next_day[ATTR_FORECAST_CONDITION] = data["condition_am"]
                next_day["is_daytime"] = True

            forecast.append(next_day)

            # FORECAST_TWICE_DAILY 일때만
            if feature == WeatherEntityFeature.FORECAST_TWICE_DAILY:
                #야간
                next_day = {
                    ATTR_FORECAST_TIME: data["datetime"],
                    ATTR_FORECAST_CONDITION: data["condition_pm"],
                    ATTR_FORECAST_TEMP_LOW: data["templow"],
                    ATTR_FORECAST_TEMP: data["temperature"],
                    ATTR_FORECAST_PRECIPITATION_PROBABILITY: data["rain_rate_pm"],
                    #ATTR_FORECAST_WIND_BEARING: data[""],
                    #ATTR_FORECAST_WIND_SPEED: data[""],
                    "is_daytime" : False,
                    
                    # Not officially supported, but nice additions.
                    "condition_am": data["condition_am"],
                    "condition_pm": data["condition_pm"],

                    "rain_rate_am": data["rain_rate_am"],
                    "rain_rate_pm": data["rain_rate_pm"]
                }
                forecast.append(next_day)

        return forecast

    def _condition_daily(self, am, pm):

        list = ["snowy", "pouring", "rainy", "cloudy", "windy"]
        
        for feature in list:
            if ( feature in am or feature in pm ):
                if feature in am:
                    return am
                else:
                    return pm

        return am

