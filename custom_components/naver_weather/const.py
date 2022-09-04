"""Const for Naver Weather."""
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
    PERCENTAGE,
    SPEED_METERS_PER_SECOND,
    CONCENTRATION_PARTS_PER_MILLION,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PRECIPITATION_MILLIMETERS_PER_HOUR,
)

DOMAIN = "naver_weather"
BRAND = "Naver Weather"
MODEL = "NWeather"
PLATFORMS = ["weather", "sensor"]

DEVICE_STATE = "state"
DEVICE_UPDATE = "update"
DEVICE_REG = "register"
DEVICE_UNREG = "unregister"

SW_VERSION = "2.2.3"
BSE_URL = "https://search.naver.com/search.naver?query={}"
BSE_URL_MOBILE = "https://m.search.naver.com/search.naver?query={}"

# area
CONF_AREA = "area"
DEFAULT_AREA = "날씨"

OPT_SCAN_INT = "scan_interval"
DEFAULT_SCAN_INT = 15


def int_between(min_int, max_int):
    """Return an integer between 'min_int' and 'max_int'."""
    return vol.All(vol.Coerce(int), vol.Range(min=min_int, max=max_int))


NW_OPTIONS = [
    (CONF_AREA, DEFAULT_AREA, cv.string),
]


CONDITIONS = {
    "wt1": ["sunny", "맑음", "맑음(낮)"],
    "wt2": ["clear-night", "맑음 (밤)", "맑음(밤)"],
    "wt3": ["partlycloudy", "대체로 흐림", "구름조금(낮)"],
    "wt4": ["partlycloudy", "대체로 흐림", "구름조금(밤)"],
    "wt5": ["partlycloudy", "대체로 흐림", "구름많음(낮)"],
    "wt6": ["partlycloudy", "대체로 흐림", "구름많음(밤)"],
    "wt7": ["cloudy", "흐림", "흐림"],
    "wt8": ["rainy", "비", "약한비"],
    "wt9": ["rainy", "비", "비"],
    "wt10": ["pouring", "호우", "강한비"],
    "wt11": ["svnowy", "눈", "약한눈"],
    "wt12": ["snowy", "눈", "눈"],
    "wt13": ["snowy", "눈", "강한눈"],
    "wt14": ["snowy", "눈", "진눈깨비"],
    "wt15": ["rainy", "비", "소나기"],
    "wt16": ["snowy-rainy", "진눈개비", "소낙 눈"],
    "wt17": ["fog", "안개", "안개"],
    "wt18": ["lightning", "번개", "번개,뇌우"],
    "wt19": ["snowy", "눈", "우박"],
    "wt20": ["fog", "안개", "황사"],
    "wt21": ["snowy-rainy", "진눈개비", "비 또는 눈"],
    "wt22": ["rainy", "비", "가끔 비"],
    "wt23": ["snowy", "눈", "가끔 눈"],
    "wt24": ["snowy-rainy", "진눈개비", "가끔 비 또는 눈"],
    "wt25": ["partlycloudy", "대체로 흐림", "흐린 후 갬"],
    "wt26": ["partlycloudy", "대체로 흐림", "뇌우 후 갬"],
    "wt27": ["partlycloudy", "대체로 흐림", "비 후 갬"],
    "wt28": ["partlycloudy", "대체로 흐림", "눈 후 갬"],
    "wt29": ["rainy", "비", "흐려져 비"],
    "wt30": ["snowy", "눈", "흐려져 눈"],
    "wt31": ["rainy", "비", "가끔 비(밤)"],
    "wt32": ["snowy", "눈", "가끔 눈(밤)"],
    "wt33": ["snowy-rainy", "진눈개비", "가끔 비 또는 눈(밤)"],
    "wt34": ["partlycloudy", "대체로 흐림", "흐린 후, 갬(밤)"],
    "wt35": ["partlycloudy", "대체로 흐림", "뇌우 후 갬(밤)"],
    "wt36": ["partlycloudy", "대체로 흐림", "비 후 갬(밤)"],
    "wt37": ["partlycloudy", "대체로 흐림", "눈 후 갬(밤)"],
    "wt38": ["rainy", "비", "흐려져 (밤)"],
    "wt39": ["snowy", "눈", "흐려져 눈(밤)"],
    "wt40": ["fog", "안개", "안개(밤)"],
    "wt41": ["fog", "안개", "황사(밤)"],
}

# naver provide infomation
LOCATION    = ["LocationInfo", "위치", "", "mdi:map-marker-radius", ""]
CONDITION   = ["Condition",    "날씨", "", "", ""]
NOW_CAST    = ["WeatherCast",  "현재날씨정보", "", "mdi:weather-cloudy", ""]
NOW_WEATHER = ["NowWeather",   "현재날씨",     "", "mdi:weather-cloudy", ""]
NOW_TEMP = [
    "NowTemp",
    "현재온도",
    TEMP_CELSIUS,
    "mdi:thermometer",
    DEVICE_CLASS_TEMPERATURE,
]
MIN_TEMP = [
    "TodayMinTemp",
    "최저온도",
    TEMP_CELSIUS,
    "mdi:thermometer-chevron-down",
    DEVICE_CLASS_TEMPERATURE,
]
MAX_TEMP = [
    "TodayMaxTemp",
    "최고온도",
    TEMP_CELSIUS,
    "mdi:thermometer-chevron-up",
    DEVICE_CLASS_TEMPERATURE,
]
FEEL_TEMP = [
    "TodayFeelTemp",
    "체감온도",
    TEMP_CELSIUS,
    "mdi:thermometer",
    DEVICE_CLASS_TEMPERATURE,
]
NOW_HUMI = ["Humidity", "현재습도", PERCENTAGE, "mdi:water-percent", DEVICE_CLASS_HUMIDITY]
WIND_SPEED = ["WindSpeed", "현재풍속", SPEED_METERS_PER_SECOND, "mdi:weather-windy", ""]
WIND_DIR = ["WindBearing", "현재풍향", "", "mdi:weather-windy", ""]
RAINFALL = [
    "Rainfall",
    "시간당강수량",
    PRECIPITATION_MILLIMETERS_PER_HOUR,
    "mdi:weather-pouring",
    "",
]
UV = ["TodayUV", "자외선지수", "", "mdi:weather-sunny-alert", ""]
UV_GRADE = ["TodayUVGrade", "자외선등급", "", "mdi:weather-sunny-alert", ""]
UDUST = [
    "UltraFineDust",
    "초미세먼지",
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    "mdi:blur-linear",
    "",
]
NDUST = ["FineDust", "미세먼지", CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, "mdi:blur", ""]
UDUST_GRADE = ["UltraFineDustGrade", "초미세먼지등급", "", "mdi:blur-linear", ""]
NDUST_GRADE = ["FineDustGrade", "미세먼지등급", "", "mdi:blur", ""]
OZON = ["Ozon", "오존", CONCENTRATION_PARTS_PER_MILLION, "mdi:alpha-o-circle", ""]
OZON_GRADE = ["OzonGrade", "오존등급", "", "mdi:alpha-o-circle", ""]
TOMORROW_PM = ["tomorrowAState", "내일오후날씨", "", "mdi:weather-cloudy", ""]
TOMORROW_MAX = [
    "tomorrowATemp",
    "내일최고온도",
    TEMP_CELSIUS,
    "mdi:thermometer-chevron-up",
    DEVICE_CLASS_TEMPERATURE,
]
TOMORROW_AM = ["tomorrowMState", "내일오전날씨", "", "mdi:weather-cloudy", ""]
TOMORROW_MIN = [
    "tomorrowMTemp",
    "내일최저온도",
    TEMP_CELSIUS,
    "mdi:thermometer-chevron-down",
    DEVICE_CLASS_TEMPERATURE,
]
RAINY_START = [
    "rainyStart",
    "오늘비시작시간",
    "",
    "mdi:weather-rainy",
    "",
]
RAINY_START_TMR = [
    "rainyStartTmr",
    "오늘내일비시작시간",
    "",
    "mdi:weather-rainy",
    "",
]

RAIN_PERCENT = [
    "rainPercent",
    "강수확률",
    "%",
    "mdi:weather-rainy",
    "",
]

PUBLIC_TIME_C = ["publicTimeC", "현재날씨 발표시간",   "", "mdi:time", ""]
PUBLIC_TIME_H = ["publicTimeH", "시간별날씨 발표시간", "", "mdi:time", ""]
PUBLIC_TIME_W = ["publicTimeW", "주간날씨 발표시간",   "", "mdi:time", ""]

WEATHER_INFO = {
    LOCATION[0]: LOCATION,
    NOW_CAST[0]: NOW_CAST,
    NOW_TEMP[0]: NOW_TEMP,
    MIN_TEMP[0]: MIN_TEMP,
    MAX_TEMP[0]: MAX_TEMP,
    FEEL_TEMP[0]: FEEL_TEMP,
    NOW_HUMI[0]: NOW_HUMI,
    WIND_SPEED[0]: WIND_SPEED,
    WIND_DIR[0]: WIND_DIR,
    RAINFALL[0]: RAINFALL,
    UV[0]: UV,
    UV_GRADE[0]: UV_GRADE,
    UDUST[0]: UDUST,
    NDUST[0]: NDUST,
    UDUST_GRADE[0]: UDUST_GRADE,
    NDUST_GRADE[0]: NDUST_GRADE,
    OZON[0]: OZON,
    OZON_GRADE[0]: OZON_GRADE,
    TOMORROW_PM[0]: TOMORROW_PM,
    TOMORROW_MAX[0]: TOMORROW_MAX,
    TOMORROW_AM[0]: TOMORROW_AM,
    TOMORROW_MIN[0]: TOMORROW_MIN,
    RAINY_START[0]: RAINY_START,
    RAINY_START_TMR[0]: RAINY_START_TMR,
    RAIN_PERCENT[0]: RAIN_PERCENT,
    NOW_WEATHER[0]: NOW_WEATHER,
}
