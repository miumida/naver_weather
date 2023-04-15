"""API for naver weather component."""

from datetime import datetime, timedelta, timezone
import logging
import re

from bs4 import BeautifulSoup

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    BRAND,
    BSE_URL,
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
    RAINFALL,
    SW_VERSION,
    TOMORROW_AM,
    TOMORROW_MAX,
    TOMORROW_MIN,
    TOMORROW_PM,
    UDUST,
    UDUST_GRADE,
    UV,
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

    r = re.compile("-?\d+")
    rtn = r.findall(val)

    if len(rtn) > 0:
        return rtn[0]
    else:
        return None

def re2float(val):
    if val is None:
        return None

    r = re.compile("-?\d+\.?\d?")
    rtn = r.findall(val)

    if len(rtn) > 0:
        return rtn[0]
    else:
        return None


def re2key(key,val):
    r = re.compile(f"{key} -?\d+\.?\d?")
    rtn = r.findall(val)
    #eLog(rtn)

    if len(rtn) > 0:
        return rtn[0]
    else:
        return None

def re2keyW(val):
    r = re.compile("바람\(\w+풍\) \d+\.?\d?m/s")
    rtn = r.findall(val)

    if len(rtn) > 0:
        return rtn[0]
    else:
        r = re.compile("\d+\.?\d?m/s")
        rtn = r.findall(val)

        if len(rtn) > 0:
            return rtn[0]
        else:
            return None

def re2keyWD(val):
    r = re.compile("[동|서|남|북]+")
    rtn = r.findall(val)

    if len(rtn) > 0:
        return rtn[0]
    else:
        return None

def eLog(val):
    _LOGGER.error("[naver_weather] error : %s", val)

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

    async def update(self):
        """Update function for updating api information."""
        try:
            url = BSE_URL.format(self.area)
            url_air = url.replace("날씨", "미세먼지")

            hdr = {
                "User-Agent": (
                    "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/78.0.3904.70 safari/537.36"
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

            NowTemp = ""

            # 지역
            LocationInfo = '-'
            try:
                LocationInfo = soup.select_one("section.sc_new.cs_weather_new._cs_weather > div._tab_flicking > div.top_wrap > div.title_area._area_panel > h2.title").text.strip()
                #eLog(LocationInfo)
            except Exception as ex:
                LocationInfo = 'Error'
                _LOGGER.error("Failed to update NWeather API NowTemp Error : %s", ex )


            # 현재 온도
            try:
                NowTemp = soup.select_one("section.sc_new.cs_weather_new._cs_weather > div._tab_flicking > div.content_wrap > div.open > div > div > div.weather_info > div > div > div.weather_graphic > div.temperature_text").text
                #eLog(NowTemp)
                NowTemp = re2float(NowTemp)
            except Exception as ex:
                NowTemp = 'Error'
                _LOGGER.error("Failed to update NWeather API NowTemp Error : %s", ex )


            # 날씨 캐스트
            WeatherCast = '-'
            NowWeather  = '-'
            try:
                wCast    = soup.select_one("section.sc_new.cs_weather_new._cs_weather > div._tab_flicking > div.content_wrap > div.open > div > div > div.weather_info > div > div > div.temperature_info > p")
                cWeather = wCast.select_one("span.weather").text
                blind    = wCast.select_one("span.blind").text

                WeatherCast = wCast.text.strip()

                arrCastTmp = WeatherCast.split(blind)

                convCast = "{}, {}{}".format(arrCastTmp[1].strip(), arrCastTmp[0], blind)

                WeatherCast = convCast

                #현재날씨
                NowWeather = cWeather.strip()

                #eLog(WeatherCast)
            except Exception as ex:
                WeatherCast = 'Error'
                NowWeather  = 'Error'
                _LOGGER.error("Failed to update NWeather API WeatherCast Error : %s", ex )


            # 오늘 오전온도, 오후온도, 체감온도
            TodayMinTemp = '-'
            TodayMaxTemp = '-'
            TodayFeelTemp = '-'

            try:
                TodayMinTemp = (
                    soup.select_one("section.sc_new.cs_weather_new._cs_weather > div._tab_flicking > div.content_wrap > div.content_area > div.inner > div > div.list_box > ul > li.week_item.today > div > div.cell_temperature > span > span.lowest").text
                )
                TodayMinTemp = re2num(TodayMinTemp)
            except Exception as ex:
                TodayMinTemp = 'Error'
                _LOGGER.error("Failed to update NWeather API TodayMinTemp Error : %s", ex )

            try:
                TodayMaxTemp = (
                    soup.select_one("section.sc_new.cs_weather_new._cs_weather > div._tab_flicking > div.content_wrap > div.content_area > div.inner > div > div.list_box > ul > li.week_item.today > div > div.cell_temperature > span > span.highest").text
                )
                TodayMaxTemp = re2num(TodayMaxTemp)
            except Exception as ex:
                TodayMaxTemp = 'Error'
                _LOGGER.error("Failed to update NWeather API TodayMaxTemp Error : %s", ex )

            try:
                TodayFeelTemp = 0
            except Exception as ex:
                TodayFeelTemp = 'Error'
                _LOGGER.error("Failed to update NWeather API TodayFeelTemp Error : %s", ex )


            # 시간당 강수량
            TodayRainfall = soup.find("span", {"class": "rainfall"})
            Rainfall = "-"

            try:
                if TodayRainfall is not None:
                    TodayRainfallSelect = TodayRainfall.select("em > span.num")

                    for rain in TodayRainfallSelect:
                        Rainfall = rain.text
            except Exception as ex:
                Rainfall = 'Error'
                _LOGGER.error("Failed to update NWeather API Rainfall Error : %s", ex )

            # 자외선 지수
            TodayUV = "-"

            # 자외선 등급
            TodayUVGrade = "-"

            reportCardWrap = soup.select("div.report_card_wrap > ul.today_chart_list > li.item_today")

            for li in reportCardWrap:
                gb    = li.select_one("strong.title").text
                gbVal = li.select_one("span.txt").text

                if "자외선" in gb:
                    TodayUVGrade = gbVal

                #_LOGGER.error(f"[{BRAND}] {gb}, {gbVal}")


            # 미세먼지, 초미세먼지, 오존 지수
            FineDust = '0'
            FineDustGrade = '-'
            UltraFineDust = '0'
            UltraFineDustGrade = '-'

            try:
                FineDust      = bs4air.select_one("div > div.detail_content > div.state_info._fine_dust > div.grade > span.num").text
                FineDustGrade = bs4air.select_one("div > div.detail_content > div.state_info._fine_dust > div.grade > span.text").text
                UltraFineDust      = bs4air.select_one("div > div.detail_content > div.state_info._ultrafine_dust > div.grade > span.num").text
                UltraFineDustGrade = bs4air.select_one("div > div.detail_content > div.state_info._ultrafine_dust > div.grade > span.text").text
            except Exception as ex:
                _LOGGER.error("Failed to update NWeather API Dust Info Error :  %s", ex)

            # 오존
            Ozon = '-'
            OzonGrade = '-'

            Ozon      = bs4air.select("div.inner > div.pollutant_content > ul > li > div.graph_area > div > span")[0].text
            OzonGrade = bs4air.select("div.inner > div.pollutant_content > ul > li > div.graph_area > strong")[0].text


            # condition
            condition_main = soup.select("section.sc_new.cs_weather_new._cs_weather > div._tab_flicking > div.content_wrap > div.open > div > div > div.weather_info > div > div > div.weather_graphic > div.weather_main > i.wt_icon")[0]["class"][1]
            condition = CONDITIONS[condition_main.replace("ico_", "")][0]
            weathertype = condition_main.replace("ico_", "")
            
            # 현재풍속/풍향
            summ = soup.select_one("section.sc_new.cs_weather_new._cs_weather > div._tab_flicking > div.content_wrap > div.open > div > div > div.weather_info > div > div > div.temperature_info > dl").text
            #eLog(summ)

            TodayFeelTemp = re2float(re2key("체감", summ))
            rainPercent = re2num(re2key("강수확률", summ))
            Humidity = re2num(re2key("습도", summ))

            #eLog('체감 ' + str(TodayFeelTemp))
            #eLog('강수확률 ' + str(rainPercent))
            #eLog('습도 ' + str(Humidity))

            wind     = re2keyW(summ)
            WindSpeed = re2float(wind)
            WindState = re2keyWD(summ)

            # 내일 오전온도
            tomorrowMTemp = '-'

            # 내일 오전상태
            tomorrowMState = '-'

            # 내일 오후온도
            tomorrowATemp = '-'

            # 내일 오후상태
            tomorrowAState = '-'

            # 비시작시간
            rainyStart = "비안옴"
            rainyStartTmr = "비안옴"

            #시간별 날씨
            hourly = soup.select("div > div.graph_inner._hourly_weather > ul > li > dl.graph_content")

            hourly_today = True
            hourly_tmr   = True
            tommorow     = False

            for h in hourly:

                time = h.select_one("dt.time").text

                if "내일" in time:
                    hourly_today = False
                    tommorow     = True

                if "모레" in time:
                    hourly_tmr = False
                    tommorow   = False

                if "시" in time or "내일" in time or "모레" in time:
                    #eLog(h.select_one("i.wt_icon"))
                    try:
                        wt = h.select_one("i.wt_icon").text
                        tm = h.select_one("dt.time").text

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

                #eLog( '{} {}'.format(tm, wt) )

            # 강수
            hourly_c_percent = soup.select("div.climate_box > div.icon_wrap > ul > li > em")
            hourly_c_mm      = soup.select("div.climate_box > div.graph_wrap > ul > li > div")

            try:
                rainPercent = hourly_c_percent[0].text
            except Exception as ex:
                _LOGGER.error(f"[{DOMAIN}] rainPercent Exception, %s", ex)

            try:
                Rainfall = hourly_c_mm[0].text
            except Exception as ex:
                _LOGGER.error(f"[{DOMAIN}] Rainfall Exception, %s", ex)

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
            
            oritime = datetime.utcnow() + timedelta(hours=9)
            timezone_kst = timezone(timedelta(hours=9))
            reftime = datetime(oritime.year, oritime.month, oritime.day, hour=0, minute=0, second=0, tzinfo=timezone_kst)
            reftimeday = datetime(oritime.year, oritime.month, oritime.day, oritime.hour, minute=0, second=0, tzinfo=timezone_kst)
            
            for di in date_info:
                data = {}

                # day
                day = di.select("span.date")

                dayInfo = ""

                for t in day:
                    dayInfo = t.text.strip()
                    # data['datetime'] = dayInfo

                data["datetime"] = reftime
                comptime = reftime.strftime("%m.%d.")
                if comptime[0] == "0":
                    comptime = comptime[1:]
                    
                try:
                    # temp
                    low  = re2num(di.select_one("span.lowest").text)
                    high = re2num(di.select_one("span.highest").text)
                    data["templow"]     = float(low)
                    data["temperature"] = float(high)

                    # condition
                    cell_w = di.select("div.cell_weather > span > i.wt_icon > span")

                    condition_am = di.select("div.cell_weather > span > i")[0]["class"][1].replace("ico_", "")
                    condition_pm = di.select("div.cell_weather > span > i")[1]["class"][1].replace("ico_", "")

                    data["condition"]    = CONDITIONS[condition_pm][0]
                    data["condition_am"] = condition_am
                    data["condition_pm"] = condition_pm

                    # rain_rate
                    rain_m = di.select("div.cell_weather > span > span.weather_left > span.rainfall")[0].text
                    data["rain_rate_am"] = int(re2num(rain_m))

                    rain_a = di.select("div.cell_weather > span > span.weather_left > span.rainfall")[1].text
                    data["rain_rate_pm"] = int(re2num(rain_a))

                    #if di.select_one("div > div.cell_date > span > span.date").text == comptime:
                    #    forecast.append(data)
                        
                    #내일 날씨
                    if di.select_one("div > div.cell_date > span > strong.day").text == "내일":
                        # 내일 오전온도
                        tomorrowMTemp = low

                        # 내일 오전상태
                        tomorrowMState = cell_w[0].text #CONDITIONS[condition_am][1]

                        # 내일 오후온도
                        tomorrowATemp = high

                        # 내일 오후상태
                        tomorrowAState = cell_w[1].text #CONDITIONS[condition_pm][1]

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
                
                forecast.append(daydata)
                
              except Exception as ex:
                eLog(ex)
            
            publicTime = soup.select_one("section.sc_new.cs_weather_new._cs_weather > div._tab_flicking > div.content_wrap > div.content_area > div.relate_info > dl > dd").text
            #eLog(publicTime)

            if FineDust == '-':
                FineDust = '0'

            if UltraFineDust == '-':
                UltraFineDust = '0'

            if Rainfall == '-':
                Rainfall = '0'

            if rainPercent == '-':
                rainPercent = '0'

            self.forecast = forecast
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
                UV[0]: TodayUV,
                UV_GRADE[0]: TodayUVGrade,
                NDUST[0]: FineDust,
                NDUST_GRADE[0]: FineDustGrade,
                UDUST[0]: UltraFineDust,
                UDUST_GRADE[0]: UltraFineDustGrade,
                OZON[0]: Ozon,
                OZON_GRADE[0]: OzonGrade,
                TOMORROW_AM[0]: tomorrowMState,
                TOMORROW_MIN[0]: tomorrowMTemp,
                TOMORROW_PM[0]: tomorrowAState,
                TOMORROW_MAX[0]: tomorrowATemp,
                RAINY_START[0]: rainyStart,
                RAINY_START_TMR[0]: rainyStartTmr,
                RAIN_PERCENT[0]: rainPercent,
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
