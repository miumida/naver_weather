"""API for naver weather component."""

from datetime import datetime, timedelta, timezone
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
    OZON,
    OZON_GRADE,
    CO, SO2, NO2, CAI,
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

    r = re.compile(r"-?\d+\.?\d?")
    rtn = r.findall(val)

    if len(rtn) > 0:
        return rtn[0]
    else:
        return None


def re2key(key,val):
    if val is None:
        return None
        
    r = re.compile(f"{key} -?\\d+\\.?\\d?")
    rtn = r.findall(val)

    if len(rtn) > 0:
        return rtn[0]
    else:
        return None

def re2keyW(val):
    if val is None:
        return None

    r = re.compile(r"바람\(\w+풍\) \d+\.?\d?m/s")
    rtn = r.findall(val)

    if len(rtn) > 0:
        return rtn[0]
    else:
        r = re.compile(r"\d+\.?\d?m/s")
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
        try:
            url = BSE_URL.format(self.area)
            url_air = url.replace("날씨", "미세먼지")

            hdr = {
                "User-Agent": (
                    "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/78.0.3904.70 safari/537.36"
                ),
                "Referer": (
                    "https://naver.com"
                )
            }

            session = async_get_clientsession(self.hass)

            response = await session.get(url, headers=hdr, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(await response.text(), "html.parser")

            #미세먼지
            air = await session.get(url_air, headers=hdr, timeout=30)
            air.raise_for_status()

            bs4air = BeautifulSoup(await air.text(), "html.parser")

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
            summ = self._bs4_select_one(soup, "div.weather_info > div > div > div.temperature_info > dl")

            # 체감온도
            TodayFeelTemp = re2float(re2key("체감", summ))

            # 습도
            Humidity      = re2num(re2key("습도", summ))

            # 현재풍속/풍향
            wind      = re2keyW(summ)
            WindSpeed = re2float(wind)
            WindState = re2keyWD(summ)

            # 강수
            Rainfall    = self._bs4_select_one(soup, "div.climate_box > div.graph_wrap > ul > li > div")
            
            # 자외선 지수
            rainPercentVal = soup.select("div.climate_box > div.icon_wrap > ul > li > em")

            nCnt = 0
            rainSum = 0

            for em in rainPercentVal:

                if nCnt > 11:
                    continue

                if '%' in em.text:
                    rainSum += int(em.text[:-1])

                nCnt += 1

            rainPercent = str(( round(rainSum/11, 1) if rainSum > 0 else 0 ))
            
            # 미세먼지/초미세먼지/자외선(등급)/일몰일출
            reportCardWrap = soup.select("div.report_card_wrap > ul.today_chart_list > li.item_today")
           
            arrReportCard = []

            TodayUVGrade = "데이터 없음"

            for li in reportCardWrap:
                gb    = self._bs4_select_one(li, "strong.title")
                gbVal = self._bs4_select_one(li, "span.txt")
            
                tmp = {"id": gb, "val": gbVal}

                arrReportCard.append(tmp)

                if "자외선" in gb:
                    TodayUVGrade = gbVal

                if ( "일몰" in gb or "일출" in gb ):
                    sunflux = gbVal
                    #eLog(gb + " / " + sunflux)

            # condition
            condition_raw  = soup.select("div.weather_info > div > div > div.weather_graphic > div.weather_main > i.wt_icon")

            if condition_raw is not None:
                condition_main = condition_raw[0]["class"][1]
                            
                if condition_main is not None:
                    weathertype = condition_main.replace("ico_", "")
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

            for h in hourly:

                time = self._bs4_select_one(h, "dt.time")
                
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

                        if ("비" in wt or "소나기" in wt ) and hourly_today:
                            hourly_today = False
                            rainyStart = tm

                        if ( "비" in wt or "소나기" in wt ) and hourly_tmr:
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
            date_info = weekly.find_all("li", {"class": "week_item"})
            
            # 시간별날씨
            daily = soup.find("div", {"class": "graph_inner _hourly_weather"})
            day_info = daily.find_all("li", {"class": "_li"})
            
            dayrainpercent = soup.select("div.open > div > div > div> div > div > div._hourly_rain > div > div.climate_box > div.icon_wrap > ul > li.data > em.value")
            dayrainfall = soup.select("div.open > div > div > div> div > div > div._hourly_rain > div > div.climate_box > div.rainfall > ul > li.data > div.data_inner")
            dayhumidity = soup.select("div.open > div > div > div> div > div > div._hourly_humidity > div > div.climate_box > div.graph_wrap > ul > li.data > div.data_inner > span.base_bar > span.num")
            
            # 시간설정 및 예보 정의
            forecast = []
            forecast_hour = []
            
            oritime = datetime.utcnow() + timedelta(hours=9)
            timezone_kst = timezone(timedelta(hours=9))
            reftime = datetime(oritime.year, oritime.month, oritime.day, hour=0, minute=0, second=0, tzinfo=timezone_kst)
            reftimeday = datetime(oritime.year, oritime.month, oritime.day, oritime.hour, minute=0, second=0, tzinfo=timezone_kst)
            
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
                comptime = reftime.strftime("%m.%d.")
                if comptime[0] == "0":
                    comptime = comptime[1:]
                    
                try:
                    # temp
                    low  = re2num(self._bs4_select_one(di, "span.lowest"))
                    high = re2num(self._bs4_select_one(di, "span.highest"))
                    data["templow"]     = float(low)
                    data["temperature"] = float(high)

                    # condition
                    cell_w = di.select("div.cell_weather > span > i.wt_icon > span")

                    conditionRaw = di.select("div.cell_weather > span > i")

                    condition_am = conditionRaw[0]["class"][1].replace("ico_", "")
                    condition_pm = conditionRaw[1]["class"][1].replace("ico_", "")

                    data["condition"]    = CONDITIONS[condition_pm][0]
                    data["condition_am"] = CONDITIONS[condition_am][0]
                    data["condition_pm"] = CONDITIONS[condition_pm][0]

                    # rain_rate
                    rainRaw = di.select("div.cell_weather > span > span.weather_left > span.rainfall")

                    rain_m = rainRaw[0].text
                    data["rain_rate_am"] = int(re2num(rain_m))

                    rain_a = rainRaw[1].text
                    data["rain_rate_pm"] = int(re2num(rain_a))

                    if di.select_one("div > div.cell_date > span > span.date").text == comptime:
                        forecast.append(data)
                        
                    #내일 날씨
                    if di.select_one("div > div.cell_date > span > strong.day").text == "내일":
                        # 내일 오전온도
                        tomorrowMTemp = low

                        # 내일 오전상태
                        rain_a = rainRaw[1].text

                        # 내일 오후온도
                        tomorrowATemp = high

                        # 내일 오후상태
                        tomorrowAState = cell_w[1].text

                except Exception as ex:
                    eLog(ex)

                reftime = reftime + timedelta(days=1)
            
            # 시간별
            daycast = []
            for dayi in day_info:
                daydata = {}
                reftimeday = reftimeday + timedelta(hours=1)
                daydata["datetime"] = reftimeday
                
                comptimeday = reftimeday.strftime("%H시")
                    
                try:
                    hourlytime = dayi.select_one("dt.time").text
                    if "내일" in hourlytime or "모레" in hourlytime or "." in hourlytime:
                        hourlytime = "00시"
                    
                    # temp
                    hourlytemp = re2num(dayi.select_one("span.num").text)
                    daydata["native_temperature"] = float(hourlytemp)

                    # condition
                    condition_hourly = dayi.select("dd.weather_box > i")[0]["class"][1].replace("ico_", "")

                    daydata["condition"] = CONDITIONS[condition_hourly][0]
                    daydata["condition_hour"] = condition_hourly
                    
                    if hourlytime == comptimeday:
                        daycast.append(daydata)
                    
                except Exception as ex:
                    eLog(ex)
            
            daycastlength = len(daycast)

            for i in range(0, daycastlength, 1): 
              daydata={}
              try:
                hourlyrainpercent = dayrainpercent[i].text

                if hourlyrainpercent == "-":
                  hourlyrainpercent = "0%"

                hourlyrainfall = dayrainfall[i].text
                hourlydumidity = dayhumidity[i].text
                
                daydata = daycast[i]

                daydata["precipitation_probability"] = int(re2num(hourlyrainpercent))
                daydata["native_precipitation"] = float(re2num(hourlyrainfall.strip()))
                daydata["humidity"] = float(hourlydumidity)
                
                forecast_hour.append(daydata)
                
              except Exception as ex:
                eLog(ex)
            
            publicTime = self._bs4_select_one(soup, "div.relate_info > dl > dd")

            # 미세먼지, 초미세먼지, 오존 지수
            FineDust           = self._bs4_select_one(bs4air, "div.state_info._fine_dust > div.grade > span.num")
            FineDustGrade      = self._bs4_select_one(bs4air, "div.state_info._fine_dust > div.grade > span.text")
            UltraFineDust      = self._bs4_select_one(bs4air, "div.state_info._ultrafine_dust > div.grade > span.num")
            UltraFineDustGrade = self._bs4_select_one(bs4air, "div.state_info._ultrafine_dust > div.grade > span.text")

            # 오염물질(오존/일산화탄소/아황산가스/이산화질소/통합대기)
            pollution = bs4air.find("div", {"class": "pollutant_content"})

            # 초기화
            Ozon = OzonGrade = None
            co   = coGrade   = None
            so2  = so2Grade  = None
            no2  = no2Grade  = None
            cai  = caiGrade  = None

            if pollution is not None:
                survey = pollution.select("ul.survey_result")

                arrSurveyRslt = []

                for ul in survey:
                    tmp1 = self._bs4_select_one(ul, "span.state") #구분
                    tmp2 = self._bs4_select_one(ul, "div.figure_box") #수치
                    tmp3 = self._bs4_select_one(ul, "strong.figure_text") #등급

                    tmpDict = { "id": tmp1, "val": tmp2, "grd": tmp3}            
            
                    arrSurveyRslt.append(tmpDict)

                for arr in arrSurveyRslt:
                    if arr["id"] == OZON[1]:
                        Ozon      = arr["val"]
                        OzonGrade = arr["grd"]

                    if arr["id"] == CO[1]:
                        co      = arr["val"]
                        coGrade = arr["grd"]

                    if arr["id"] == SO2[1]:
                        so2      = arr["val"]
                        so2Grade = arr["grd"]

                    if arr["id"] == NO2[1]:
                        no2      = arr["val"]
                        no2Grade = arr["grd"]

                    if arr["id"] == CAI[1]:
                        cai      = arr["val"]
                        caiGrade = arr["grd"]

            # 오염물질 제공
            offerInfo = self._bs4_select_one(bs4air, "div.inner > div.offer_info > span.update")

            if FineDust is None:
                FineDust = '0'

            if UltraFineDust is None:
                UltraFineDust = '0'

            if Rainfall is None:
                Rainfall = '0'

            self.forecast = forecast
            self.forecast_hour = forecast_hour
            self.weathertype = weathertype

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
                OZON[0]: Ozon,
                OZON_GRADE[0]: OzonGrade,
                CO[0]:  co,
                SO2[0]: so2,
                NO2[0]: no2,
                CAI[0]: cai,
                TOMORROW_AM[0]: tomorrowMState,
                TOMORROW_MIN[0]: tomorrowMTemp,
                TOMORROW_PM[0]: tomorrowAState,
                TOMORROW_MAX[0]: tomorrowATemp,
                RAINY_START[0]: rainyStart,
                RAINY_START_TMR[0]: rainyStartTmr,
                RAIN_PERCENT[0]: rainPercent,
                "airOfferInfoUpdate": offerInfo
            }
            
            _LOGGER.info(f"[{BRAND}] Update weather information -> {self.result}")
            
            for id in WEATHER_INFO.keys():
                try:
                    self.device_update(id)
                except Exception as ex:
                    _LOGGER.info(f"[{BRAND}] Update weather fail -> {ex}")
        except Exception as ex:
            _LOGGER.error(f"[{BRAND}] Failed to update NWeather API status Error: {ex}")
            raise
