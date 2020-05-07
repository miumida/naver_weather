# 네이버 날씨 센서

![HAKC)][hakc-shield]
![HACS][hacs-shield]
![Version v1.4][version-shield]

네이버 날씨 Sensor for Home Assistant 입니다.<br>
네이버 날씨를 크롤링하여 센서로 추가해 줍니다.<br>

<br>

## Version history
| Version | Date        | 내용              |
| :-----: | :---------: | ----------------------- |
| v1.0.0  | 2020.05.06  | First version  |

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
area는 기본값으로 '날씨'로 들어갑니다.
기본적으로 날씨로 지정되면 장비가 있는 위치를 기준으로 날씨가 나오는거 같았습니다.
추가로 area에 원하시는 지역을 네이버에서 검색하셔서 입력해보시고 날씨가 조회되면 area에 입력하시면 됩니다.

<br>

## 참고사이트
[1] 네이버 HomeAssistant 카페 | af950833님의 [HA] 네이버 날씨 (<https://cafe.naver.com/stsmarthome/19337>)<br>

[version-shield]: https://img.shields.io/badge/version-v1.0.0-orange.svg
[hakc-shield]: https://img.shields.io/badge/HAKC-Enjoy-blue.svg
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-red.svg
