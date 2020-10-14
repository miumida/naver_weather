"""Support for Naver Weather Sensors."""
import logging
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
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
from homeassistant.const import (CONF_SCAN_INTERVAL)

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

# naver provide infomation
_INFO = {
    'LocationInfo':   ['위치',         '',      'mdi:map-marker-radius'],
    'WeatherCast':    ['현재날씨',     '',      'mdi:weather-cloudy'],
    'NowTemp':        ['현재온도',     '°C',    'mdi:thermometer'],
    'TodayMinTemp':   ['최저온도',     '°C',    'mdi:thermometer-chevron-down'],
    'TodayMaxTemp':   ['최고온도',     '°C',    'mdi:thermometer-chevron-up'],
    'TodayFeelTemp':  ['체감온도',     '°C',    'mdi:thermometer'],
    'Humidity':       ['현재습도',     '%',     'mdi:water-percent'],
    'WindSpeed':      ['현재풍속',     'm/s',   'mdi:weather-windy'],
    'WindState':      ['현재풍향',     '',      'mdi:weather-windy'],
    'Rainfall':       ['시간당강수량', 'mm',    'mdi:weather-pouring'],
    'TodayUV':        ['자외선지수',   '',      'mdi:weather-sunny-alert'],
    'UltraFineDust':  ['초미세먼지',   '㎍/㎥', 'mdi:blur-linear'],
    'FineDust':       ['미세먼지',     '㎍/㎥', 'mdi:blur'],
    'UltraFineDustGrade': ['초미세먼지등급', '', 'mdi:blur-linear'],
    'FineDustGrade':  ['미세먼지등급', '',      'mdi:blur'],
    'Ozon':           ['오존',         'ppm',   'mdi:alpha-o-circle'],
    'OzonGrade':      ['오존등급',     '',      'mdi:alpha-o-circle'],
    'tomorrowAState': ['내일오후날씨', '',      'mdi:weather-cloudy'],
    'tomorrowATemp':  ['내일최고온도', '°C',    'mdi:thermometer-chevron-up'],
    'tomorrowMState': ['내일오전날씨', '',      'mdi:weather-cloudy'],
    'tomorrowMTemp':  ['내일최저온도', '°C',    'mdi:thermometer-chevron-down']
}

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

BSE_URL = 'https://search.naver.com/search.naver?query={}'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_AREA, default=DEFAULT_AREA): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
    vol.Optional(CONF_AREA_SUB, default=DEFAULT_AREA_SUB): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL_SUB, default=SCAN_INTERVAL_SUB): cv.time_period,
    vol.Optional(CONF_SENSOR_USE, default=DEFAULT_SENSOR_USE): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Demo weather."""
    # sensor use
    sensor_use    = config.get(CONF_SENSOR_USE)
    
    # area config
    area          = config.get(CONF_AREA)
    SCAN_INTERVAL = config.get(CONF_SCAN_INTERVAL)

    #API
    api = NWeatherAPI(area)

    api.update()

    rslt = api.result
    cur  = api.forecast

    # sensor add
    if sensor_use == 'Y':
        sensors = []
        child   = []

        for key, value in api._sensor.items():
            sensor = childSensor('naver_weather', key, value, 'M')
            child   += [sensor]
            sensors += [sensor]

        sensors += [NWeatherSensor('naver_weather', api, child, 'M')]

        add_entities(sensors, True)

    add_entities([NaverWeather(cur, api, 'M')])


    #sub
    area_sub = config.get(CONF_AREA_SUB)
    SCAN_INTERVAL_SUB = config.get(CONF_SCAN_INTERVAL)

    if (len(area_sub) > 0):
        sub = NWeatherAPI(area_sub)
        sub.update()

        rslt_sub = sub.result
        cur_sub  = sub.forecast

        add_entities([NaverWeather(cur_sub, sub, 'S')])


class NWeatherAPI:
    """NWeather API."""

    def __init__(self, area):
        """Initialize the NWeather API.."""
        self.area     = area
        self.result   = {}
        self.forecast = []

        self._sensor  = {}

    def update(self):
        """Update function for updating api information."""
        try:
            url = BSE_URL.format(self.area)

            hdr = {'User-Agent': ('mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/78.0.3904.70 safari/537.36')}

            response = requests.get(url, headers=hdr, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            NowTemp = ""
            CheckDust = []

            # 지역
            LocationInfo = soup.find('span', {'class':'btn_select'}).text

            # 현재 온도
            NowTemp = soup.find('span', {'class': 'todaytemp'}).text

            # 날씨 캐스트
            WeatherCast = soup.find('p', {'class' : 'cast_txt'}).text

            # 오늘 오전온도, 오후온도, 체감온도
            TodayMinTemp  = soup.find('span', {'class' : 'min'}).select('span.num')[0].text
            TodayMaxTemp  = soup.find('span', {'class' : 'max'}).select('span.num')[0].text
            TodayFeelTemp = soup.find('span', {'class' : 'sensible'}).select('em > span.num')[0].text

            # 시간당 강수량
            TodayRainfall = soup.find('span', {'class' : 'rainfall'})
            Rainfall = '-'

            if TodayRainfall is not None:
                TodayRainfallSelect = TodayRainfall.select('em > span.num')

                for rain in TodayRainfallSelect:
                    Rainfall = rain.text

            # 자외선 지수
            TodayUVSelect = soup.find('span', {'class' : 'indicator'}).select('span > span.num')
            TodayUV = '-'

            for uv in TodayUVSelect:
                TodayUV = uv.text

            # 미세먼지, 초미세먼지, 오존 지수
            CheckDust1 = soup.find('div', {'class': 'sub_info'})
            CheckDust2 = CheckDust1.find('div', {'class': 'detail_box'})

            for i in CheckDust2.select('dd'):
                CheckDust.append(i.text)

            FineDust      = CheckDust[0].split('㎍/㎥')[0]
            FineDustGrade = CheckDust[0].split('㎍/㎥')[1]
            UltraFineDust = CheckDust[1].split('㎍/㎥')[0]
            UltraFineDustGrade = CheckDust[1].split('㎍/㎥')[1]
            Ozon      = CheckDust[2].split('ppm')[0]
            OzonGrade = CheckDust[2].split('ppm')[1]

            # condition
            today_area = soup.find('div', {'class' : 'today_area _mainTabContent'})

            condition_main = today_area.select('div.main_info > span.ico_state')[0]["class"][1]
            condition = _CONDITIONS[condition_main][0]

            # 현재 습도
            humi_tab = soup.find('div', {'class': 'info_list humidity _tabContent _center'})
            Humidity = humi_tab.select('ul > li.on.now > dl > dd.weather_item._dotWrapper > span')[0].text

            # 현재풍속
            wind_tab = soup.find('div', {'class': 'info_list wind _tabContent _center'})
            WindSpeed  = wind_tab.select('ul > li.on.now > dl > dd.weather_item._dotWrapper > span')[0].text
            WindState  = wind_tab.select('ul > li.on.now > dl > dd.item_condition > span.wt_status')[0].text

            # 내일 오전, 오후 온도 및 상태 체크
            tomorrowArea = soup.find('div', {'class': 'tomorrow_area'})
            tomorrowCheck = tomorrowArea.find_all('div', {'class': 'main_info morning_box'})

            # 내일 오전온도
            tomorrowMTemp = tomorrowCheck[0].find('span', {'class': 'todaytemp'}).text

            # 내일 오전상태
            tomorrowMState1 = tomorrowCheck[0].find('div', {'class' : 'info_data'})
            tomorrowMState2 = tomorrowMState1.find('ul', {'class' : 'info_list'})
            tomorrowMState  = tomorrowMState2.find('p', {'class' : 'cast_txt'}).text

            # 내일 오후온도
            tomorrowATemp1 = tomorrowCheck[1].find('p', {'class' : 'info_temperature'})
            tomorrowATemp  = tomorrowATemp1.find('span', {'class' : 'todaytemp'}).text

            # 내일 오후상태
            tomorrowAState1 = tomorrowCheck[1].find('div', {'class' : 'info_data'})
            tomorrowAState2 = tomorrowAState1.find('ul', {'class' : 'info_list'})
            tomorrowAState  = tomorrowAState2.find('p', {'class' : 'cast_txt'}).text

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
            weather["WindSpeed"]      = WindSpeed
            weather["WindBearing"]    = WindState

            self.result = weather

            #sensor
            ws = dict()
            ws["LocationInfo"]   = LocationInfo
            ws["WeatherCast"]    = WeatherCast
            ws["NowTemp"]        = NowTemp
            ws["TodayMinTemp"]   = TodayMinTemp
            ws["TodayMaxTemp"]   = TodayMaxTemp
            ws["TodayFeelTemp"]  = TodayFeelTemp
            ws["Humidity"]       = Humidity

            ws["WindSpeed"]      = WindSpeed
            ws["WindState"]      = WindState

            ws['Rainfall']       = Rainfall
            ws["TodayUV"]        = TodayUV

            ws["FineDust"]           = FineDust
            ws["FineDustGrade"]      = FineDustGrade
            ws["UltraFineDust"]      = UltraFineDust
            ws["UltraFineDustGrade"] = UltraFineDustGrade
            ws["Ozon"]               = Ozon
            ws["OzonGrade"]          = OzonGrade

            ws["tomorrowMTemp"]  = tomorrowMTemp
            ws["tomorrowMState"] = tomorrowMState
            ws["tomorrowATemp"]  = tomorrowATemp
            ws["tomorrowAState"] = tomorrowAState

            self._sensor = ws

        except Exception as ex:
            _LOGGER.error('Failed to update NWeather API status Error: %s', ex)
            raise



class NaverWeather(WeatherEntity):
    """Representation of a weather condition."""
    def __init__(self, forecast, api, gb):
        """Initialize the Demo weather."""
        self._name = 'NaverWeather'
        self._condition        = api.result["NowTemp"]
        self._temperature      = float(api.result["NowTemp"])
        self._temperature_unit = '°C'
        self._humidity         = int(api.result["Humidity"])
        self._wind_speed       = (float(api.result["WindSpeed"]) * 3.6)
        self._forecast         = forecast
        self._api              = api
        self._gb               = gb

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
        if self._gb == 'M':
            return '{}'.format(self._name)
        else:
            return '{}_sub'.format(self._name)

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

class childSensor(Entity):
    """Representation of a NWeather Sensor."""
    _STATE = None

    def __init__(self, name, key, value, gb):
        """Initialize the NWeather sensor."""
        self._name  = name
        self._key   = key
        self._value = value
        self._STATE = value
        self._gb    = gb

    @property
    def entity_id(self):
        """Return the entity ID."""
        if self._gb == 'M':
            return 'sensor.nw_{}'.format(self._key.lower())
        else:
            return 'sensor.nw_sub_{}'.format(self._key.lower())

    @property
    def name(self):
        """Return the name of the sensor, if any."""
        return _INFO[self._key][0]

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return _INFO[self._key][2]

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._value

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return _INFO[self._key][1]


    def update(self):
        """Get the latest state of the sensor."""
        self._value = self._STATE

    def setValue(self, value):
        self._STATE = value

        self.update()

    @property
    def device_info(self):
        """Return information about the device."""
        return {
            "identifiers": {('naver_weather', self.unique_id)},
            'name': 'Naver Weather',
            'manufacturer': 'naver.com',
            'model': 'naver_weather',
            'sw_version': '1.1.4'
        }

    @property
    def device_state_attributes(self):
        """Attributes."""
        data = {}

        data[self._key] = self._value

        return data


class NWeatherSensor(Entity):
    """Representation of a NWeather Sensor."""

    def __init__(self, name, api, child, gb):
        """Initialize the NWeather sensor."""
        self._name = name
        self._api   = api
        self._child = child
        self._icon  = 'mdi:weather-partly-cloudy'
        self._gb    = gb

    @property
    def entity_id(self):
        """Return the entity ID."""
        if self._gb == 'M':
            return 'sensor.naver_weather'
        else:
            return 'sensor.naver_weather_sub'

    @property
    def name(self):
        """Return the name of the sensor, if any."""
        return '네이버 날씨'

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._api._sensor["WeatherCast"]

#    @Throttle(SCAN_INTERVAL)
    def update(self):
        """Get the latest state of the sensor."""
        if self._api is None:
            return

        self._api.update()

        for sensor in self._child:
            sensor.setValue( self._api._sensor[sensor._key] )

    @property
    def device_state_attributes(self):
        """Attributes."""

        data = {}

        for key, value in self._api._sensor.items():
            data[_INFO[key][0]] = '{}{}'.format(value, _INFO[key][1])

        return data

    @property
    def device_info(self):
        """Return information about the device."""
        return {
            "identifiers": {('naver_weather', 'quality')},
            'name': 'Naver Weather',
            'manufacturer': 'naver.com',
            'model': 'naver_weather'
        }
