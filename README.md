Custom from [miumi](https://github.com/miumida/naver_weather)

v2.5.1-0.1

# 네이버 날씨 for HA

![HAKC)][hakc-shield]
![HACS][hacs-shield]
![Version v2.5.1][version-shield]

<a href="https://www.buymeacoffee.com/miumida" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/white_img.png" alt="Buy Me A Coffee"></a>

네이버 날씨 for Home Assistant 입니다.<br>
네이버 날씨 웹페이지를 크롤링하여 센서로 추가해 줍니다.<br>
아무래도 크롤링을 해서 가져오는 부분이라 센서에서 호출하는 부분은 최소화할 수 있도록 했습니다.<br>

통합구성요소를 지원하며, 통합구성요소를 통해 추가시 기기 1개와 구성요소 25개가 추가됩니다.<br>
여러지역의 네이버 날씨를 지원합니다. 한군데 이상의 지역으로 등록 가능하지만 너무 많은 지역으로 등록은 삼가해주세요.<br>
10분 간격으로 네이버 날씨정보를 갱신합니다. 10분이면 충분하니 간격을 더 줄이는건 참아주세요!<br>

- senseor
![screenshot_1](https://github.com/miumida/naver_weather/blob/master/images/naver_weather.png?raw=true)<br>
![screenshot_2](https://github.com/miumida/naver_weather/blob/master/images/naver_weather_all.png?raw=true)<br>
- weather
![screenshot_3](https://github.com/miumida/naver_weather/blob/master/images/weather.naverweather.png?raw=true)<br>

<br>

## Version history
| Version | Date        | 내용              |
| :-----: | :---------: | --------------------------------------------------------------------------------------- |
| v1.0.0  | 2020.05.07  | First version  |
| v1.0.1  | 2020.05.08  | - 미세먼지/초미세먼지/오존/자외선 가져오기 수정<br>- 미세먼지등급/초미세먼지등급/오존등급 추가 |
| v1.0.2  | 2020.05.09  | - 자외선 가져오기 오류수정<br>- 시간당 강수량 가져오기 추가<br>- 오타수정 |
| v1.0.3  | 2020.05.10  | 시간당 강수량 가져오기 오류수정 |
| v1.0.4  | 2020.05.10  | 오타수정 |
| v1.0.5  | 2020.05.12  | - 풍속/풍향 추가<br>- 속성순서 수정 |
| v1.0.6  | 2020.05.12  | 현재습도 수정 |
| v1.1.0  | 2020.05.13  | weather.py 추가 |
| v1.1.1  | 2020.05.14  | 내일오전날씨/내일오후날씨 수정 |
| v1.1.2  | 2020.05.25  | SUB 지역(area_sub) 추가 |
| v1.1.3  | 2020.05.25  | 오류 수정 |
| v1.2.0  | 2020.06.18  | weathe에 sensor 통합 |
| v1.2.1  | 2020.10.14  | weathe, sensor 현재습도, 현재풍속 가져오기 수정 |
| v2.0.0  | 2021.04.12  | Renewal - 통합구성요소 적용 |
| v2.0.2  | 2021.04.13  | bug Fix |
| v2.0.3  | 2021.04.14  | bug Fix |
| v2.0.4  | 2021.04.15  | bug Fix |
| v2.0.5  | 2021.04.19  | bug Fix + 자외선등급 추가 |
| v2.0.6  | 2021.04.20  | bug Fix |
| v2.0.7  | 2021.04.26  | api_nweather.py 예외처리 |
| v2.0.8  | 2021.07.09  | api_nweather.py 예외처리 |
| v2.0.9  | 2021.07.10  | bug Fix(자외선등급 처리) |
| v2.1.0  | 2021.09.19  | 웹페이지 개편에 따른 api 수정 |
| v2.1.1  | 2021.09.19  | 로그출력 삭제 |
| v2.1.2  | 2021.09.24  | bs4 select 수정  |
| v2.1.4  | 2021.10.01  | 미세먼지 관련 오류   |
| v2.1.6  | 2021.12.15  | Fixed bug |
| v2.1.8  | 2022.05.04  | Fixed bug |
| v2.1.11  | 2022.06.22  | Fixed bug |
| v2.1.12  | 2022.06.28  | 강수확률, 시간당강수량 api 로직 수정 |
| v2.2.0 | 2022.07.07  | 현재날씨, 현재날씨정보 정리 + 현재날씨정보 출력형태 변경  |
| v2.2.1 | 2022.07.08  | Fixed bug  |
| v2.2.2 | 2022.07.18  | Fixed bug  |
| v2.2.3 | 2022.09.06  | - 자외선 등급 추가<br> - 내일오전날씨, 내일오후날씨 api 로직 수정<br> - 오늘비시작시간, 오늘내일비시작시간 api 로직 수정  |
| v2.2.4 | 2022.09.23  | 미세먼지, 초미세먼지 device_class(pm25) 추가  |
| v2.2.5 | 2022.12.29  | 주간예보에 오늘날씨 포함 옵션   |
| v2.2.6 | 2023.04.14  | 풍속 정규식 처리 |
| v2.2.7 | 2023.07.28  | DeviceEntryType -> entry_type   |
| v2.2.8 | 2023.07.29  | DeviceEntryType 원복  |
| v2.3.0 | 2023.10.12  | WeatherEntity 업데이트 대응  |
| v2.3.3 | 2024.02.27  | DeprecatedConstant 업데이트 대응, FORECAST_TWICE_DAILY 적용 |
| v2.4.1 | 2024.03.25  | FORECAST_DAILY 지원 |
| v2.5.1 | 2024.11.06  | api_nweather.py 수정 |
<br>

## Installation
### _My Home Assistant_ HACS로 설치
- 아래 링크를 클릭해서 이동 후 다운로드 버튼을 눌러 설치하세요.<br>
- 다운로드 후 Home Assistant를 재시작합니다.<br>
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ninthsword&repository=naver_weather&category=integration)
### Manual
- HA 설치 경로 아래 custom_components에 naver_weather폴더 안의 전체 파일을 복사해줍니다.<br>
  `<config directory>/custom_components/naver_weather/`<br>
- configuration.yaml 파일에 설정을 추가합니다.<br>
- Home-Assistant 를 재시작합니다<br>
### HACS
- HACS > Integretions > 우측상단 메뉴 > Custom repositories 선택
- 'https://github.com/ninthsword/naver_weather' 주소 입력, Category에 'integration' 선택 후, 저장
- HACS > Integretions 메뉴 선택 후, naver_weather 검색하여 설치

<br>

## Usage
### Custom Integration
- 구성 > 통합구성요소 > 통합구성요소 추가하기 > 네이버 날씨 선택 > 지역(area) 입력후, 확인.

<br>

### 기본 설정값

|옵션|내용|sensor|weather|
|--|--|--|--|
|platform| (필수) naver_weather  |O|O|
|area| (옵션) 원하는 동네 / default(날씨) |O|O|
|today| (옵션) 주간예보에 오늘날씨를 포함||O|
<br>

### area 설정값
area는 기본값으로 '날씨'로 들어갑니다.<br>
기본적으로 날씨로 지정되면 장비가 있는 위치를 기준으로 날씨가 나오는거 같았습니다.<br>
추가로 area에 원하시는 지역을 네이버에서 검색하셔서 입력해보시고 날씨가 조회되면 area에 입력하시면 됩니다.<br>
물론 네이버에 정상적으로 검색되는지 확인이 필요합니다.<br>
창원시 대방동 날씨로 검색했을 때, 정상적으로 날씨정보가 조회된다면 '창원시 대방동'으로 area를 입력하시면 됩니다.<br>
![screenshot_3](https://github.com/miumida/naver_weather/blob/master/images/naver_weather_search.png?raw=true)<br>

<br>

### 네이버 날씨 제공정보
|정보| 비고 |
|-------|-------|
|위치| |
|체감온도       | |
|현재온도       | |
|현재습도       | |
|현재풍속       | |
|현재풍향       | |
|최고온도       | |
|최저온도       | |
|내일최고온도     | |
|내일최저온도     | |
|~~자외선지수~~      | |
|자외선등급      | |
|강수확률 | 기상청에서 제공되는 강수확률에 문제가 있는 것으로 보임.<br> 현재시간 기준의 강수확률은 거의 표시되지 않음. |
|시간당강수량     | |
|오늘비시작시간   | |
|오늘내일비시작시간 | |
|현재날씨       | |
|현재날씨정보    | |
|내일오전날씨     | |
|내일오후날씨     | |


### 네이버 대기질 제공정보
|정보| 비고 |
|-------|-------|
|미세먼지       | |
|미세먼지등급     | |
|초미세먼지      | |
|초미세먼지등급   | |


### 네이버 오염물질 제공정보
|정보| 비고 |
|-------|-------|
|오존       ||
|오존등급       | |
|일산화탄소       ||
|아황산가스       ||
|이산화질소       ||
|통합대기       ||
<br>

#### thanks to.
- 네이버 HomeAssistant 카페 | 랜이님
- 네이버 HomeAssistant 카페 | 초후님
- 네이버 HomeAssistant 카페 | mahlernim님
- 네이버 HomeAssistant 카페 | 트루월드님

<br>

## 참고사이트
[1] 네이버 HomeAssistant 카페 | af950833님의 [HA] 네이버 날씨 (<https://cafe.naver.com/stsmarthome/19337>)<br>

[version-shield]: https://img.shields.io/badge/version-v2.5.1-orange.svg
[hakc-shield]: https://img.shields.io/badge/HAKC-Enjoy-blue.svg
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-red.svg
