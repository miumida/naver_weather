# 네이버 날씨 센서

![HAKC)][hakc-shield]
![HACS][hacs-shield]
![Version v1.4][version-shield]

네이버 날씨 Sensor for Home Assistant 입니다.<br>
네이버 날씨 웹페이지를 크롤링하여 센서로 추가해 줍니다.<br>
아무래도 크롤링을 해서 가져오는 부분이라 센서에서 호출하는 부분은 최소화할 수 있도록 했습니다.<br>
sensor.naver_weather(부모) - sensor.nw_*(자식) 센서라고 생각하시면 됩니다.<br>

부모 센서가 update 되는 시점에 자식 센서에 값을 함께 update 하도록 했습니다.<br>

![screenshot_1](https://github.com/miumida/naver_weather/blob/master/images/naver_weather.png?raw=true)<br>
![screenshot_2](https://github.com/miumida/naver_weather/blob/master/images/naver_weather_all.png?raw=true)<br>

<br>

## Version history
| Version | Date        | 내용              |
| :-----: | :---------: | ----------------------- |
| v1.0.0  | 2020.05.07  | First version  |
| v1.0.1  | 2020.05.08  | - 미세먼지/초미세먼지/오존/자외선 가져오기 수정<br>- 미세먼지등급/초미세먼지등급/오존등급 추가 |
| v1.0.2  | 2020.05.09  | - 자외선 가져오기 오류수정<br>- 시간당 강수량 가져오기 추가<br>- 오타수정 |
| v1.0.3  | 2020.05.10  | 시간당 강수량 가져오기 오류수정 |
| v1.0.4  | 2020.05.10  | 오타수정 |

<br>

## Installation
### Manual
- HA 설치 경로 아래 custom_components 에 파일을 넣어줍니다.<br>
  `<config directory>/custom_components/naver_weather/__init__.py`<br>
  `<config directory>/custom_components/naver_weather/manifest.json`<br>
  `<config directory>/custom_components/naver_weather/sensor.py`<br>
- configuration.yaml 파일에 설정을 추가합니다.<br>
- Home-Assistant 를 재시작합니다<br>

<br>

## Usage
### configuration
- HA 설정에 naver_weather sensor를 추가합니다.<br>
```yaml
sensor:
  - platform: naver_weather
    name: naver_weather
    area: '날씨'
```
<br><br>
### 기본 설정값

|옵션|내용|
|--|--|
|platform| (필수) naver_weather  |
|name| (옵션) default(naver_weather) |
|area| (옵션) 원하는 동네 / default(날씨) |
|scan_interval| (옵션) Sensor Update Term / default(900s) |

<br>

### area 설정값
area는 기본값으로 '날씨'로 들어갑니다.<br>
기본적으로 날씨로 지정되면 장비가 있는 위치를 기준으로 날씨가 나오는거 같았습니다.<br>
추가로 area에 원하시는 지역을 네이버에서 검색하셔서 입력해보시고 날씨가 조회되면 area에 입력하시면 됩니다.<br>
'<https://search.naver.com/search.naver?query=창원시+성산구+대방동+날씨>' 와 같은 형태로 확인이 됩니다.<br>
query= 뒷부분에 있는 부분을 arae로 입력하시면 됩니다.
띄워쓰기를 + 또는 %20으로 변경하시면 됩니다. 물론 네이버에 정상적으로 검색되는지 확인이 필요합니다.
![screenshot_3](https://github.com/miumida/naver_weather/blob/master/images/naver_weather_search.png?raw=true)<br>

<br>

## 참고사이트
[1] 네이버 HomeAssistant 카페 | af950833님의 [HA] 네이버 날씨 (<https://cafe.naver.com/stsmarthome/19337>)<br>

[version-shield]: https://img.shields.io/badge/version-v1.0.1-orange.svg
[hakc-shield]: https://img.shields.io/badge/HAKC-Enjoy-blue.svg
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-red.svg
