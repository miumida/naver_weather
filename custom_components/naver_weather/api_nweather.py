"""API for naver weather component."""

import asyncio
from datetime import datetime, timedelta
import logging
import re

from bs4 import BeautifulSoup

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    BRAND,
    BSE_URL,
    SW_VERSION,
    CONDITION,
    CONDITIONS,
    CONF_AREA,
    CONF_TODAY,
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
    NOW_WEATHER,
    NOW_HUMI,
    NOW_TEMP,
    OZON_GRADE,
    CO_GRADE,
    SO2_GRADE,
    NO2_GRADE,
    CAI_GRADE,
    RAINFALL,
    TOMORROW_AM,
    TOMORROW_MAX,
    TOMORROW_MIN,
    TOMORROW_PM,
    UDUST,
    UDUST_GRADE,
    UV_GRADE,
    WEATHER_INFO,
    WIND_DIR,
    WIND_SPEED,
    RAINY_START,
    RAINY_START_TMR,
    RAIN_PERCENT,
    DEVICE_UNREG,
)

_LOGGER = logging.getLogger(__name__)


def re2num(val):
    if val is None:
        return None

    r = re.compile(r"-?\d+")
    rtn = r.findall(val)

    if len(rtn) > 0:
        return rtn[0]
    else:
        return None

def re2float(val):
    if val is None:
        return None

    r = re.compile(r"-?\d+\.?\d*")
    rtn = r.findall(val)

    if len(rtn) > 0:
        return rtn[0]
    else:
        return None


def re2key(key,val):
    if val is None:
        return None

    r = re.compile(f"{key} -?\\d+\\.?\\d*")
    rtn = r.findall(val)

    if len(rtn) > 0:
        return rtn[0]
    else:
        return None

def re2keyW(val):
    if val is None:
        return None

    r = re.compile(r"바람\(\w+풍\) \d+\.?\d*m/s")
    rtn = r.findall(val)

    if len(rtn) > 0:
        return rtn[0]
    else:
        r = re.compile(r"\d+\.?\d*m/s")
        rtn = r.findall(val)
        
        if len(rtn) > 0:
            return rtn[0]
        else:
            return None

def re2keyWD(val):
    if val is None:
        return None

    r = re.compile(r"[동|서|남|북]+")
    rtn = r.findall(val)

    if len(rtn) > 0:
        return rtn[0]
    else:
        return None

def eLog(val):
    _LOGGER.error(f"[{BRAND}] error : {val}")

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
        self.last_update = None
        self._lock = asyncio.Lock()
        self.forecast = []

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

    @property
    def today(self):
        """Return area."""
        today = self.entry.options.get(CONF_TODAY, self.entry.data.get(CONF_TODAY))

        return today


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

    def _bs4_select_one(self, bs4, selector, bText=True, tag=""):

        try:
            tmp = bs4.select_one(selector)

            if tmp is not None:
                if bText:
                    val = tmp.text.strip()
                else:
                    val = tmp
            else:
                val = None

            return val;
        except Exception as e:
            _LOGGER.error( f"[{BRAND}] _bs4_select_one Error {tag} : {e}" )


    async def update(self):
        """Update function for updating api information."""
        async with self._lock:
            if self.last_update and (datetime.now() - self.last_update) < timedelta(minutes=10):
                _LOGGER.debug(f"[{BRAND}] Skipping update, last update was {self.last_update}")
                return

            try:
                url = BSE_URL.format(self.area)
                url_air = url.replace("날씨", "미세먼지")

                hdr = {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (khtml, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                    ),
                    "Referer": (
                        "https://search.naver.com"
                    ),
                    "Accept": (
                        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
                    ),
                    "Accept-Language": (
                        "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
                    )
                }

                session = async_get_clientsession(self.hass)

                tasks = [
                    session.get(url, headers=hdr, timeout=30),
                    session.get(url_air, headers=hdr, timeout=30)
                ]
                responses = await asyncio.gather(*tasks, return_exceptions=True)

                # Weather page response
                if isinstance(responses[0], Exception):
                    _LOGGER.error(f"[{BRAND}] Failed to fetch weather page: {responses[0]}")
                    raise responses[0]
                
                responses[0].raise_for_status()
                soup = BeautifulSoup(await responses[0].text(), "html.parser")

                # Air quality page response
                bs4air = None
                if isinstance(responses[1], Exception):
                    _LOGGER.warning(f"[{BRAND}] Failed to fetch air quality page: {responses[1]}")
                else:
                    try:
                        responses[1].raise_for_status()
                        bs4air = BeautifulSoup(await responses[1].text(), "html.parser")
                    except Exception as ex:
                        _LOGGER.warning(f"[{BRAND}] Error parsing air quality page: {ex}")


                # 지역
                LocationInfo = self._bs4_select_one(soup, "div.title_area._area_panel > h2.title")

                # 현재 온도
                NowTempRaw = self._bs4_select_one(soup, "div.temperature_text")
                NowTemp    = re2float(NowTempRaw)

                # 날씨 캐스트
                WeatherCast = None
                NowWeather  = None

                wCast = self._bs4_select_one(soup, "div.temperature_info > p", False)

                if wCast is not None:
                    cWeather = self._bs4_select_one(wCast, "span.weather")
                    blind    = self._bs4_select_one(wCast, "span.blind")

                    WeatherCast = wCast.text.strip()

                    arrCastTmp = WeatherCast.split(blind)

                    convCast = "{}, {}{}".format(arrCastTmp[1].strip(), arrCastTmp[0], blind)

                    WeatherCast = convCast

                    #현재날씨
                    NowWeather = cWeather


                # 오늘 오전온도, 오후온도
                TodayMinTemp = self._bs4_select_one(soup, "div.list_box > ul > li.week_item.today > div > div.cell_temperature > span > span.lowest")
                TodayMaxTemp = self._bs4_select_one(soup, "div.list_box > ul > li.week_item.today > div > div.cell_temperature > span > span.highest")
                
                TodayMinTemp = re2num(TodayMinTemp)
                TodayMaxTemp = re2num(TodayMaxTemp)


                # 요약
                summ_dl = soup.select_one("div.temperature_info dl.summary_list")
                summary_data = {}
                if summ_dl:
                    terms = summ_dl.select("dt.term")
                    descs = summ_dl.select("dd.desc")
                    for dt, dd in zip(terms, descs):
                        summary_data[dt.text.strip()] = dd.text.strip()

                # 체감온도
                TodayFeelTemp = re2float(summary_data.get("체감"))
                
                # 습도
                Humidity      = re2num(summary_data.get("습도"))

                # 현재풍속/풍향
                WindSpeed = None
                WindState = None
                # "남서풍", "북풍" 등 풍향이 키이고 "1.2m/s"가 값임
                for key, val in summary_data.items():
                    if "풍" in key:
                        WindState = key.replace("풍", "")
                        WindSpeed = re2float(val)
                        break


                # 강수
                RainfallRaw = self._bs4_select_one(soup, "div.climate_box > div.graph_wrap > ul > li > div")
                Rainfall    = re2float(RainfallRaw)

                rainPercentVal = soup.select("div.climate_box > div.icon_wrap > ul > li > em")
                rainPercentList = []
                for em in rainPercentVal:
                    if len(rainPercentList) >= 12:
                        continue

                    if '%' in em.text:
                        rainPercentList.append(int(em.text[:-1]))
                
                rainPercent = str(max(rainPercentList) if rainPercentList else 0)
                

                # 미세먼지/초미세먼지/자외선(등급)/일몰일출
                reportCardWrap = soup.select("div.report_card_wrap > ul.today_chart_list > li.item_today")

                arrReportCard = []
                
                TodayUVGrade = "데이터 없음"

                for li in reportCardWrap:
                    gb    = self._bs4_select_one(li, "strong.title")
                    gbVal = self._bs4_select_one(li, "span.txt")

                    tmp = {"id": gb, "val": gbVal}

                    arrReportCard.append(tmp)

                    if gb and "자외선" in gb:
                        TodayUVGrade = gbVal

                    if gb and ( "일몰" in gb or "일출" in gb ):
                        sunflux = gbVal
                        #eLog(gb + " / " + sunflux)


                # condition
                condition_raw  = soup.select("div.weather_info > div > div > div.weather_graphic > div.weather_main > i.wt_icon")

                if condition_raw is not None and len(condition_raw) > 0:
                    condition_main = condition_raw[0]["class"][1]

                    if condition_main is not None:
                        condition = CONDITIONS[condition_main.replace("ico_", "")][0]
                    else:
                        condition = None
                else:
                    condition = None

                contdition_blind_text = self._bs4_select_one(soup, "div.weather_info > div > div > div.weather_graphic > div.weather_main > i > span.blind")
                #eLog(contdition_blind_text)
                
                # 비시작시간
                rainyStart    = "비안옴"
                rainyStartTmr = "비안옴"

                #시간별 날씨
                hourly = soup.select("div > div.graph_inner._hourly_weather > ul > li > dl.graph_content")

                hourly_today = True
                hourly_tmr   = True
                tommorow     = False

                if hourly:
                    for h in hourly:

                        time = self._bs4_select_one(h, "dt.time")
                        if not time: continue

                        if "내일" in time:
                            hourly_today = False
                            tommorow     = True

                        if "모레" in time:
                            hourly_tmr = False
                            tommorow   = False

                        if "시" in time or "내일" in time or "모레" in time:
                            try:
                                wt = self._bs4_select_one(h, "i.wt_icon")
                                tm = self._bs4_select_one(h, "dt.time")

                                if wt and ("비" in wt or "소나기" in wt ) and hourly_today:
                                    hourly_today = False
                                    rainyStart = tm

                                if wt and ( "비" in wt or "소나기" in wt ) and hourly_tmr:
                                    hourly_tmr = False
                                    if "내일" in tm:
                                        rainyStartTmr = "내일 00시"
                                    else:
                                        if tommorow:
                                            rainyStartTmr = "내일 {}".format(tm)
                                        else:
                                            rainyStartTmr = tm
                            except Exception as exx:
                                _LOGGER.info("except")

                # 내일 오전온도/오전상태
                tomorrowMTemp = '-'
                tomorrowMState = '-'

                # 내일 오후온도/오후상태
                tomorrowATemp = '-'
                tomorrowAState = '-'

                # 주간날씨
                weekly = soup.find("div", {"class": "weekly_forecast_area _toggle_panel"})

                if weekly:
                    date_info = weekly.find_all("li", {"class": "week_item"})

                    forecast = []

                    reftime = datetime.now()

                    bStart = False

                    for di in date_info:
                        data = {}

                        # day
                        dayDesc = self._bs4_select_one(di, "div > div.cell_date > span > strong.day")

                        if (dayDesc == "오늘"):
                            bStart = True

                        if ( not bStart ):
                            continue

                        dayInfo = ""

                        day = di.select("span.date")

                        for t in day:
                            dayInfo = t.text.strip()

                        data["datetime"] = reftime

                        try:
                            # temp
                            low  = re2num(self._bs4_select_one(di, "span.lowest"))
                            high = re2num(self._bs4_select_one(di, "span.highest")) 
                            if low: data["templow"]     = float(low)
                            if high: data["temperature"] = float(high)

                            # condition
                            cell_w = di.select("div.cell_weather > span > i.wt_icon > span")

                            conditionRaw = di.select("div.cell_weather > span > i")

                            if len(conditionRaw) >= 2:
                                condition_am = conditionRaw[0]["class"][1].replace("ico_", "")
                                condition_pm = conditionRaw[1]["class"][1].replace("ico_", "")

                                data["condition"]    = CONDITIONS[condition_pm][0]
                                data["condition_am"] = CONDITIONS[condition_am][0]
                                data["condition_pm"] = CONDITIONS[condition_pm][0]

                            # rain_rate
                            rainRaw = di.select("div.cell_weather > span > span.weather_left > span.rainfall")

                            if len(rainRaw) >= 2:
                                rain_m = rainRaw[0].text
                                data["rain_rate_am"] = int(re2num(rain_m))

                                rain_a = rainRaw[1].text
                                data["rain_rate_pm"] = int(re2num(rain_a))


                            if self.today:
                                forecast.append(data)
                            else:
                                if dayDesc != "오늘":
                                    forecast.append(data)

                            #내일 날씨
                            if dayDesc == "내일":
                                # 내일 오전온도
                                tomorrowMTemp = low

                                # 내일 오전상태
                                if len(cell_w) > 0:
                                    tomorrowMState = cell_w[0].text

                                # 내일 오후온도
                                tomorrowATemp = high

                                # 내일 오후상태
                                if len(cell_w) > 1:
                                    tomorrowAState = cell_w[1].text

                        except Exception as ex:
                            eLog(ex)

                        reftime = reftime + timedelta(days=1)

                    self.forecast = forecast

                publicTime = self._bs4_select_one(soup, "div.relate_info > dl > dd")


                # 미세먼지, 초미세먼지, 오존 지수
                FineDust = '0'
                FineDustGrade = '점검중'
                UltraFineDust = '0'
                UltraFineDustGrade = '점검중'
                OzonGrade = coGrade = so2Grade = no2Grade = caiGrade = None

                # Fallback values from weather page report card
                for item in arrReportCard:
                    if item["id"] == "미세먼지":
                        FineDustGrade = item["val"]
                    elif item["id"] == "초미세먼지":
                        UltraFineDustGrade = item["val"]

                if bs4air:
                    try:
                        # Try to get numeric values from air page if available
                        fd_num = self._bs4_select_one(bs4air, "div.state_info:nth-of-type(1) div.grade div.text_box > span.num")
                        fd_grd = self._bs4_select_one(bs4air, "div.state_info:nth-of-type(1) div.grade > span.text")
                        if fd_num: FineDust = fd_num
                        if fd_grd: FineDustGrade = fd_grd

                        ufd_num = self._bs4_select_one(bs4air, "div.state_info:nth-of-type(2) div.grade div.text_box > span.num")
                        ufd_grd = self._bs4_select_one(bs4air, "div.state_info:nth-of-type(2) div.grade > span.text")
                        if ufd_num: UltraFineDust = ufd_num
                        if ufd_grd: UltraFineDustGrade = ufd_grd

                        # 오염물질(오존/일산화탄소/아황산가스/이산화질소/통합대기)
                        pollution = bs4air.find("div", {"class": "other_air_info"})

                        if pollution is not None:
                            survey = pollution.select("ul.air_info_list > li")
                            arrSurveyRslt = []

                            for li in survey:
                                tmp1 = self._bs4_select_one(li, "span.info_title") #구분
                                tmp2 = self._bs4_select_one(li, "span.state") #등급
                                tmpDict = { "id": tmp1, "grd": tmp2}
                                arrSurveyRslt.append(tmpDict)

                            for arr in arrSurveyRslt:
                                if arr["id"] == OZON_GRADE[1]:
                                    OzonGrade = arr["grd"]
                                if arr["id"] == CO_GRADE[1]:
                                    coGrade = arr["grd"]
                                if arr["id"] == SO2_GRADE[1]:
                                    so2Grade = arr["grd"]
                                if arr["id"] == NO2_GRADE[1]:
                                    no2Grade = arr["grd"]
                                if arr["id"] == CAI_GRADE[1]:
                                    caiGrade = arr["grd"]
                    except Exception as ex:
                        _LOGGER.warning(f"[{BRAND}] Error parsing pollution data: {ex}")

                # 오염물질 제공
                offerInfo = self._bs4_select_one(bs4air, "div.inner > div.offer_info > span.update") if bs4air else None

                if FineDust is None:
                    FineDust = '0'

                if UltraFineDust is None:
                    UltraFineDust = '0'

                if Rainfall is None or Rainfall == "" or Rainfall == "-":
                    Rainfall = '0'


                self.result = {
                    LOCATION[0]: LocationInfo,
                    NOW_CAST[0]: WeatherCast,
                    NOW_WEATHER[0]: NowWeather,
                    NOW_TEMP[0]: NowTemp,
                    NOW_HUMI[0]: Humidity,
                    CONDITION[0]: condition,
                    WIND_SPEED[0]: WindSpeed,
                    WIND_DIR[0]: WindState,
                    MIN_TEMP[0]: TodayMinTemp,
                    MAX_TEMP[0]: TodayMaxTemp,
                    FEEL_TEMP[0]: TodayFeelTemp,
                    RAINFALL[0]: Rainfall,
                    UV_GRADE[0]: TodayUVGrade,
                    NDUST[0]: FineDust,
                    NDUST_GRADE[0]: FineDustGrade,
                    UDUST[0]: UltraFineDust,
                    UDUST_GRADE[0]: UltraFineDustGrade,
                    OZON_GRADE[0]: OzonGrade,
                    CO_GRADE[0]: coGrade,
                    SO2_GRADE[0]: so2Grade,
                    NO2_GRADE[0]: no2Grade,
                    CAI_GRADE[0]: caiGrade,
                    TOMORROW_AM[0]: tomorrowMState,
                    TOMORROW_MIN[0]: tomorrowMTemp,
                    TOMORROW_PM[0]: tomorrowAState,
                    TOMORROW_MAX[0]: tomorrowATemp,
                    RAINY_START[0]: rainyStart,
                    RAINY_START_TMR[0]: rainyStartTmr,
                    RAIN_PERCENT[0]: rainPercent,
                    "airOfferInfoUpdate": offerInfo
                }

                self.last_update = datetime.now()
                _LOGGER.info(f"[{BRAND}] Update weather information -> {self.result}")
                
                for id in WEATHER_INFO.keys():
                    try:
                        self.device_update(id)
                    except Exception as ex:
                        _LOGGER.info(f"[{BRAND}] Update weather fail -> {ex}")
            except Exception as ex:
                _LOGGER.error(f"[{BRAND}] Failed to update NWeather API status Error: {ex}")
                raise
