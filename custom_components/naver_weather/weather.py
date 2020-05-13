"""Support for Naver Weather Sensors."""
import logging
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,
    PLATFORM_SCHEMA,
    WeatherEntity,
)
from homeassistant.const import (CONF_SCAN_INTERVAL,TEMP_CELSIUS, TEMP_FAHRENHEIT)

REQUIREMENTS = ["beautifulsoup4==4.9.0"]

_LOGGER = logging.getLogger(__name__)

# naver conditions
_CONDITIONS = {
    'ws1'  : ['sunny',        '맑음',        '맑음(낮)'],
    'ws2'  : ['clear-night',  '맑음 (밤)',   '맑음(밤)'],
    'ws3'  : ['partlycloudy', '대체로 흐림', '구름조금(낮)'],
    'ws4'  : ['partlycloudy', '대체로 흐림', '구름조금(밤)'],
    'ws5'  : ['partlycloudy', '대체로 흐림', '구름많음(낮)'],
    'ws6'  : ['partlycloudy', '대체로 흐림', '구름많음(밤)'],
    'ws7'  : ['cloudy',       '흐림',        '흐림'],
    'ws8'  : ['rainy',        '비',          '약한비'],
    'ws9'  : ['rainy',        '비',          '비'],
    'ws10' : ['pouring',      '호우',        '강한비'],
    'ws11' : ['snowy',        '눈',          '약한눈'],
    'ws12' : ['snowy',        '눈',          '눈'],
    'ws13' : ['snowy',        '눈',          '강한눈'],
    'ws14' : ['snowy',        '눈',          '진눈깨비'],
    'ws15' : ['rainy',        '비',          '소나기'],
    'ws16' : ['snowy-rainy',  '진눈개비',    '소낙 눈'],
    'ws17' : ['fog',          '안개',        '안개'],
    'ws18' : ['lightning',    '번개',        '번개,뇌우'],
    'ws19' : ['snowy',        '눈',          '우박'],
    'ws20' : ['fog',          '안개',        '황사'],
    'ws21' : ['snowy-rainy',  '진눈개비',    '비 또는 눈'],
    'ws22' : ['rainy',        '비',          '가끔 비'],
    'ws23' : ['snowy',        '눈',          '가끔 눈'],
    'ws24' : ['snowy-rainy',  '진눈개비',    '가끔 비 또는 눈'],
    'ws25' : ['partlycloudy', '대체로 흐림', '흐린 후 갬'],
    'ws26' : ['partlycloudy', '대체로 흐림', '뇌우 후 갬'],
    'ws27' : ['partlycloudy', '대체로 흐림', '비 후 갬'],
    'ws28' : ['partlycloudy', '대체로 흐림', '눈 후 갬'],
    'ws29' : ['rainy',        '비',          '흐려져 비'],
    'ws30' : ['snowy',        '눈',          '흐려져 눈']
}

CONF_AREA = 'area'
DEFAULT_AREA = '날씨'

BSE_URL = 'https://search.naver.com/search.naver?query={}'

SCAN_INTERVAL = timedelta(seconds=900)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_AREA, default=DEFAULT_AREA): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Demo weather."""
    area = config.get(CONF_AREA)
    SCAN_INTERVAL = config.get(CONF_SCAN_INTERVAL)

    #API
    api = NWeatherAPI(area)

    api.update()

    rslt = api.result
    cur  = api.forecast

    condition  = rslt['NowTemp']
    temp       = float(rslt['NowTemp'])
    wind_speed = int(rslt['WindSpeed'])
    humidity   = int(rslt['Humidity'])

    add_entities([NaverWeather(condition, temp, humidity, wind_speed, TEMP_CELSIUS, cur, api)])

class NWeatherAPI:
    """NWeather API."""

    def __init__(self, area):
        """Initialize the NWeather API.."""
        self.area   = area
        self.result = {}
        self.forecast = []

    def update(self):
        """Update function for updating api information."""
        try:
            url = BSE_URL.format(self.area)

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            NowTemp = ""

            # 지역
            LocationInfo = soup.find('span', {'class':'btn_select'}).text

            # 현재 온도
            NowTemp = soup.find('span', {'class': 'todaytemp'}).text

            # 날씨 캐스트
            WeatherCast = soup.find('p', {'class' : 'cast_txt'}).text

            # condition
            today_area = soup.find('div', {'class' : 'today_area _mainTabContent'})

            condition_main = today_area.select('div.main_info > span.ico_state')[0]["class"][1]
            condition = _CONDITIONS[condition_main][0]

            # 현재 습도
            humi_tab = soup.find('div', {'class': 'info_list humidity _tabContent'})
            Humidity = humi_tab.select('ul > li.on.now > dl > dd.weather_item._dotWrapper > span')[0].text

            # 현재풍속
            wind_tab = soup.find('div', {'class': 'info_list wind _tabContent'})
            windspeed   = wind_tab.select('ul > li.on.now > dl > dd.weather_item._dotWrapper > span')[0].text
            windbearing = wind_tab.select('ul > li.on.now > dl > dd.item_condition > span.wt_status')[0].text

            #주간날씨
            weekly = soup.find('div', {'class': 'table_info weekly _weeklyWeather'})

            date_info = weekly.find_all('li', {'class': 'date_info today'})

            forecast = []

            reftime = datetime.now()

            for di in date_info:
                data = {}

                #day
                day = di.select('span.day_info')

                dayInfo = ""

                for t in day:
                    dayInfo = t.text.strip()
                    #data['datetime'] = dayInfo

                data['datetime'] = reftime

                #temp
                temp = di.select('dl > dd > span')
                temptext = ''

                for t in temp:
                    temptext += t.text

                arrTemp = temptext.split('/')

                data['templow']     = float(arrTemp[0])
                data['temperature'] = float(arrTemp[1])

                #condition
                condition_am = di.select('span.point_time.morning > span.ico_state2')[0]
                condition_pm = di.select('span.point_time.afternoon > span.ico_state2')[0]

                data['condition'] = _CONDITIONS[condition_pm["class"][1]][0]
                data['condition_am'] = _CONDITIONS[condition_am["class"][1]][2]
                data['condition_pm'] = _CONDITIONS[condition_pm["class"][1]][2]

                #rain_rate
                rain_m = di.select('span.point_time.morning > span.rain_rate > span.num')
                for t in rain_m:
                    data['rain_rate_am'] = int(t.text)

                rain_a = di.select('span.point_time.afternoon > span.rain_rate > span.num')
                for t in rain_a:
                    data['rain_rate_pm'] = int(t.text)

                if ( dayInfo.split(' ')[1] != "오늘" ):
                    forecast.append(data)

                reftime = reftime + timedelta(days=1)

            self.forecast = forecast

            #날씨
            weather = dict()
            weather["LocationInfo"]   = LocationInfo
            weather["NowTemp"]        = NowTemp
            weather["Humidity"]       = Humidity
            weather["Condition"]      = condition
            weather["WeatherCast"]    = WeatherCast
            weather["WindSpeed"]      = windspeed
            weather["WindBearing"]    = windbearing

            self.result = weather
        except Exception as ex:
            _LOGGER.error('Failed to update NWeather API status Error: %s', ex)
            raise



class NaverWeather(WeatherEntity):
    """Representation of a weather condition."""
    def __init__(self, condition, temperature, humidity, wind_speed, temperature_unit, forecast, api):
        """Initialize the Demo weather."""
        self._name = 'NaverWeather'
        self._condition        = condition
        self._temperature      = temperature
        self._temperature_unit = temperature_unit
        self._humidity         = humidity
        self._wind_speed       = wind_speed
        self._forecast         = forecast
        self._api              = api

    @Throttle(SCAN_INTERVAL)
    def update(self):
        """Update current conditions."""
        print ('weather updateing')

        self._api.update()

        self._forecast = self._api.forecast

        if not self._forecast:
            _LOGGER.info("Don't receive weather data from NAVER!")

    @property
    def name(self):
        """Return the name of the sensor."""
        return '{}'.format(self._name)

    @property
    def temperature(self):
        """Return the temperature."""
        return float(self._api.result["NowTemp"])

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._temperature_unit

    @property
    def humidity(self):
        """Return the humidity."""
        return int(self._api.result["Humidity"])

    @property
    def wind_speed(self):
        """Return the wind speed."""
        return ( float(self._api.result["WindSpeed"]) * 3.6 )

    @property
    def wind_bearing(self):
        """Return the wind bearing."""
        return self._api.result["WindBearing"]

    @property
    def condition(self):
        """Return the weather condition."""
        return self._api.result["Condition"]

    @property
    def state(self):
        """Return the weather state."""
        return self._api.result["Condition"]

    @property
    def attribution(self):
        """Return the attribution."""
        return '{} - Weather forecast from Naver, Powered by miumida'.format(self._api.result["LocationInfo"])

    @property
    def forecast(self):
        """Return the forecast."""
        return self._forecast
