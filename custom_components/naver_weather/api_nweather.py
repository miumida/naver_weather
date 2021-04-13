"""API for naver weather component."""

from datetime import datetime, timedelta
import logging

from bs4 import BeautifulSoup

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    BRAND,
    BSE_URL,
    CONDITION,
    CONDITIONS,
    CONF_AREA,
    DEVICE_REG,
    DEVICE_UPDATE,
    FEEL_TEMP,
    LOCATION,
    MAX_TEMP,
    MIN_TEMP,
    MODEL,
    NDUST,
    NDUST_GRADE,
    NOW_CAST,
    NOW_HUMI,
    NOW_TEMP,
    OZON,
    OZON_GRADE,
    RAINFALL,
    SW_VERSION,
    TOMORROW_AM,
    TOMORROW_MAX,
    TOMORROW_MIN,
    TOMORROW_PM,
    UDUST,
    UDUST_GRADE,
    UV,
    WEATHER_INFO,
    WIND_DIR,
    WIND_SPEED,
    RAINY_START,
    RAINY_START_TMR,
    DEVICE_UNREG,
)

_LOGGER = logging.getLogger(__name__)


class NWeatherAPI:
    """NWeather API."""

    def __init__(self, hass, entry, count):
        """Initialize the NWeather API.."""
        self.hass = hass
        self.entry = entry
        self.count = count
        self.result = {}
        self.version = SW_VERSION
        self.model = MODEL
        self.brand = BRAND.lower()
        self.brand_name = BRAND
        self.unique = {}

        _LOGGER.debug(f"[{BRAND}] Initialize -> {self.area}")

    @property
    def area(self):
        """Return area."""
        data = self.entry.options.get(CONF_AREA, self.entry.data.get(CONF_AREA))
        if data == "날씨":
            return data
        else:
            return data + " 날씨"

    def set_data(self, name, value):
        """Set entry data."""
        self.hass.config_entries.async_update_entry(
            entry=self.entry, data={**self.entry.data, name: value}
        )

    def get_data(self, name, default=False):
        """Get entry data."""
        return self.entry.data.get(name, default)

    def init_device(self, unique_id):
        """Initialize device."""
        self.unique[unique_id] = {
            DEVICE_UPDATE: None,
            DEVICE_REG: self.register_update_state,
            DEVICE_UNREG: self.unregister_update_state,
        }

    def get_device(self, unique_id, key):
        """Get device info."""
        return self.unique.get(unique_id, {}).get(key)

    def device_update(self, device_id):
        """Update device state."""
        unique_id = self.area + ":" + device_id
        device_update = self.unique.get(unique_id, {}).get(DEVICE_UPDATE)
        if device_update is not None:
            device_update()

    def register_update_state(self, unique_id, cb):
        """Register device update function to update entity state."""
        if not self.unique[unique_id].get(DEVICE_UPDATE):
            _LOGGER.info(f"[{BRAND}] Register device => {unique_id} [{self.area}]")
            self.unique[unique_id][DEVICE_UPDATE] = cb

    def unregister_update_state(self, unique_id):
        """Unregister device update function."""
        if self.unique[unique_id][DEVICE_UPDATE] is not None:
            _LOGGER.info(f"[{BRAND}] Unregister device => {unique_id} [{self.area}]")
            self.unique[unique_id][DEVICE_UPDATE] = None

    async def update(self):
        """Update function for updating api information."""
        try:
            url = BSE_URL.format(self.area)

            hdr = {
                "User-Agent": (
                    "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/78.0.3904.70 safari/537.36"
                )
            }

            session = async_get_clientsession(self.hass)

            # response = requests.get(url, headers=hdr, timeout=10)
            response = await session.get(url, headers=hdr, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(await response.text(), "html.parser")

            NowTemp = ""
            CheckDust = []

            # 지역
            LocationInfo = soup.find("span", {"class": "btn_select"}).text

            # 현재 온도
            NowTemp = soup.find("span", {"class": "todaytemp"}).text

            # 날씨 캐스트
            WeatherCast = soup.find("p", {"class": "cast_txt"}).text

            # 오늘 오전온도, 오후온도, 체감온도
            TodayMinTemp = (
                soup.find("span", {"class": "min"}).select("span.num")[0].text
            )
            TodayMaxTemp = (
                soup.find("span", {"class": "max"}).select("span.num")[0].text
            )
            TodayFeelTemp = (
                soup.find("span", {"class": "sensible"}).select("em > span.num")[0].text
            )

            # 시간당 강수량
            TodayRainfall = soup.find("span", {"class": "rainfall"})
            Rainfall = "-"

            if TodayRainfall is not None:
                TodayRainfallSelect = TodayRainfall.select("em > span.num")

                for rain in TodayRainfallSelect:
                    Rainfall = rain.text

            # 자외선 지수
            TodayUVSelect = soup.find("span", {"class": "indicator"}).select(
                "span > span.num"
            )
            TodayUV = "-"

            for uv in TodayUVSelect:
                TodayUV = uv.text

            # 미세먼지, 초미세먼지, 오존 지수
            CheckDust1 = soup.find("div", {"class": "sub_info"})
            CheckDust2 = CheckDust1.find("div", {"class": "detail_box"})

            for i in CheckDust2.select("dd"):
                CheckDust.append(i.text)

            FineDust = CheckDust[0].split("㎍/㎥")[0]
            FineDustGrade = CheckDust[0].split("㎍/㎥")[1]
            UltraFineDust = CheckDust[1].split("㎍/㎥")[0]
            UltraFineDustGrade = CheckDust[1].split("㎍/㎥")[1]

            # 오존
            Ozon = CheckDust[2].split("ppm")[0]
            OzonGrade = CheckDust[2].split("ppm")[1]

            # condition
            today_area = soup.find("div", {"class": "today_area _mainTabContent"})

            condition_main = today_area.select("div.main_info > span.ico_state")[0][
                "class"
            ][1]
            condition = CONDITIONS[condition_main][0]

            # 현재 습도
            humi_tab = soup.find(
                "div", {"class": "info_list humidity _tabContent _center"}
            )
            Humidity = humi_tab.select(
                "ul > li.on.now > dl > dd.weather_item._dotWrapper > span"
            )[0].text

            # 현재풍속
            wind_tab = soup.find("div", {"class": "info_list wind _tabContent _center"})
            WindSpeed = wind_tab.select(
                "ul > li.on.now > dl > dd.weather_item._dotWrapper > span"
            )[0].text
            WindState = wind_tab.select(
                "ul > li.on.now > dl > dd.item_condition > span.wt_status"
            )[0].text

            # 내일 오전, 오후 온도 및 상태 체크
            tomorrowArea = soup.find("div", {"class": "tomorrow_area"})
            tomorrowCheck = tomorrowArea.find_all(
                "div", {"class": "main_info morning_box"}
            )

            # 내일 오전온도
            tomorrowMTemp = tomorrowCheck[0].find("span", {"class": "todaytemp"}).text

            # 내일 오전상태
            tomorrowMState1 = tomorrowCheck[0].find("div", {"class": "info_data"})
            tomorrowMState2 = tomorrowMState1.find("ul", {"class": "info_list"})
            tomorrowMState = tomorrowMState2.find("p", {"class": "cast_txt"}).text

            # 내일 오후온도
            tomorrowATemp1 = tomorrowCheck[1].find("p", {"class": "info_temperature"})
            tomorrowATemp = tomorrowATemp1.find("span", {"class": "todaytemp"}).text

            # 내일 오후상태
            tomorrowAState1 = tomorrowCheck[1].find("div", {"class": "info_data"})
            tomorrowAState2 = tomorrowAState1.find("ul", {"class": "info_list"})
            tomorrowAState = tomorrowAState2.find("p", {"class": "cast_txt"}).text

            # 주간날씨
            weekly = soup.find("div", {"class": "table_info weekly _weeklyWeather"})

            date_info = weekly.find_all("li", {"class": "date_info today"})

            # 비시작시간
            rain_tab = soup.find(
                "div", {"class": "info_list weather_condition _tabContent"}
            )
            rainyStart = "-"
            rainyStartTmr = "-"

            if rain_tab is not None:
                # 오늘
                rainyStart = "비안옴"
                for rain_li in rain_tab.select("ul > li"):
                    if (
                        rain_li.select("dl > dd.item_time")[0].find(
                            "span", {"class": "tomorrow"}
                        )
                        is not None
                    ):
                        break

                    if rain_li.select("dl > dd.item_condition > span")[0].text == "비":
                        rainyStart = (
                            rain_li.select("dl > dd.item_time")[0]
                            .find("span", {"class": None})
                            .text
                        )
                        break

                # 오늘 ~ 내일
                rainyStartTmr = "비안옴"
                for rain_li in rain_tab.select("ul > li"):
                    if rain_li.select("dl > dd.item_condition > span")[0].text == "비":
                        rainyStartTmr = (
                            rain_li.select("dl > dd.item_time")[0]
                            .find("span", {"class": None})
                            .text
                        )
                        break

            forecast = []

            reftime = datetime.now()

            for di in date_info:
                data = {}

                # day
                day = di.select("span.day_info")

                dayInfo = ""

                for t in day:
                    dayInfo = t.text.strip()
                    # data['datetime'] = dayInfo

                data["datetime"] = reftime

                # temp
                temp = di.select("dl > dd > span")
                temptext = ""

                for t in temp:
                    temptext += t.text

                arrTemp = temptext.split("/")

                data["templow"] = float(arrTemp[0])
                data["temperature"] = float(arrTemp[1])

                # condition
                condition_am = di.select("span.point_time.morning > span.ico_state2")[0]
                condition_pm = di.select("span.point_time.afternoon > span.ico_state2")[
                    0
                ]

                data["condition"] = CONDITIONS[condition_pm["class"][1]][0]
                data["condition_am"] = CONDITIONS[condition_am["class"][1]][2]
                data["condition_pm"] = CONDITIONS[condition_pm["class"][1]][2]

                # rain_rate
                rain_m = di.select(
                    "span.point_time.morning > span.rain_rate > span.num"
                )
                for t in rain_m:
                    data["rain_rate_am"] = int(t.text)

                rain_a = di.select(
                    "span.point_time.afternoon > span.rain_rate > span.num"
                )
                for t in rain_a:
                    data["rain_rate_pm"] = int(t.text)

                if dayInfo.split(" ")[1] != "오늘":
                    forecast.append(data)

                reftime = reftime + timedelta(days=1)

            self.forecast = forecast

            self.result = {
                LOCATION[0]: LocationInfo,
                NOW_CAST[0]: WeatherCast,
                NOW_TEMP[0]: NowTemp,
                NOW_HUMI[0]: Humidity,
                CONDITION[0]: condition,
                WIND_SPEED[0]: WindSpeed,
                WIND_DIR[0]: WindState,
                MIN_TEMP[0]: TodayMinTemp,
                MAX_TEMP[0]: TodayMaxTemp,
                FEEL_TEMP[0]: TodayFeelTemp,
                RAINFALL[0]: Rainfall,
                UV[0]: TodayUV,
                NDUST[0]: FineDust,
                NDUST_GRADE[0]: FineDustGrade,
                UDUST[0]: UltraFineDust,
                UDUST_GRADE[0]: UltraFineDustGrade,
                OZON[0]: Ozon,
                OZON_GRADE[0]: OzonGrade,
                TOMORROW_AM[0]: tomorrowAState,
                TOMORROW_MIN[0]: tomorrowATemp,
                TOMORROW_PM[0]: tomorrowMState,
                TOMORROW_MAX[0]: tomorrowMTemp,
                RAINY_START[0]: rainyStart,
                RAINY_START_TMR[0]: rainyStartTmr,
            }
            _LOGGER.info(f"[{BRAND}] Update weather information -> {self.result}")
            for id in WEATHER_INFO.keys():
                try:
                    self.device_update(id)
                except Exception as ex:
                    _LOGGER.info(f"[{BRAND}] Update weather fail -> {ex}")
        except Exception as ex:
            _LOGGER.error("Failed to update NWeather API status Error: %s", ex)
            raise
