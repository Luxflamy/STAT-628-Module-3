
| 变量名                | 含义解释（中文）                    | Explanation (English)                   | 单位/取值范围          |
|-----------------------|-------------------------------------|-----------------------------------------|------------------------|
| STATION               | 气象站ID                           | Station identification code            | 11字符编码             |
| DATE                  | 观测日期                          | Date of observation                    | YYYY-MM-DD             |
| TMAX                  | 日最高气温                        | Daily maximum temperature              | °C                     |
| TMIN                  | 日最低气温                        | Daily minimum temperature              | °C                     |
| TAVG                  | 日平均气温                        | Daily average temperature              | °C                     |
| PRCP                  | 日降水量                          | Daily precipitation amount             | mm                     |
| SNOW                  | 日降雪量                          | Daily snowfall amount                  | mm                     |
| AWND                  | 日平均风速                        | Average daily wind speed               | m/s                    |
| WSF2                  | 日最大2分钟风速                   | Peak 2-second wind speed               | m/s                    |
| WSF5                  | 日最大5秒风速                     | Peak 5-second wind speed               | m/s                    |
| WDF2                  | 日最大2分钟风向                   | Direction of peak 2-second wind        | 角度(0-360)            |
| WDF5                  | 日最大5秒风向                     | Direction of peak 5-second wind        | 角度(0-360)            |
| WT01                  | 雾天气现象                        | Fog occurrence flag                    | 1=存在，0=不存在       |
| WT03                  | 雷暴天气现象                      | Thunderstorm occurrence flag           | 1=存在，0=不存在       |
| WT04                  | 冰雹天气现象                      | Hail occurrence flag                   | 1=存在，0=不存在       |
| WT05                  | 冻雨/冻雾现象                     | Freezing rain/fog flag                 | 1=存在，0=不存在       |
| WT08                  | 烟雾天气现象                      | Smoke/haze occurrence flag             | 1=存在，0=不存在       |
| WT11                  | 高风速警报                        | High wind warning flag                 | 1=存在，0=不存在       |
| VIS                   | 水平能见度                        | Horizontal visibility                  | km                     |
| RH                    | 相对湿度                          | Relative humidity                      | %                      |
| WESD                  | 雪水当量                          | Snow water equivalent                  | mm                     |
| SNWD                  | 积雪深度                          | Snow depth                             | mm                     |
| PGTM                  | 日最大阵风时间                    | Time of peak wind gust                 | HHMM                   |
| PSUN                  | 日照时长                          | Daily sunshine duration                | 分钟                   |
| TSUN                  | 日照百分率                        | Percentage of possible sunshine        | %                      |
| PRES                  | 海平面气压                        | Sea level pressure                     | hPa                    |
| WDMV                  | 日最大风速风向                    | Wind direction at max speed            | 角度(0-360)            |
| TOBS                  | 观测时气温                        | Temperature at observation time        | °C                     |
| MDPR                  | 日平均露点温度                    | Mean daily dew point temperature       | °C                     |
| DAPR                  | 日露点温度范围                    | Dew point temperature range            | °C                     |
| EVAP                  | 蒸发量                            | Evaporation amount                     | mm                     |
| FMTM                  | 首场冻雨时间                      | First freezing rain occurrence time    | HHMM                   |
| FOG                   | 雾持续时间                        | Fog duration                           | 分钟                   |
| FRGB                  | 地面冻结时间                      | Ground frost duration                  | 分钟                   |
| FRGT                  | 空气冻结时间                      | Air frost duration                     | 分钟                   |
| THUNDER               | 雷暴持续时间                      | Thunderstorm duration                  | 分钟                   |
| SLP                   | 海平面气压                        | Sea level pressure                     | hPa                    |
| STP                   | 站点气压                          | Station pressure                       | hPa                    |

Supplementary notes:
1. **Weather phenomenon codes (WTxx)**: The complete list contains 28 weather phenomena, commonly used aviation-related codes include:
   - WT02: Heavy Fog
   - WT06: Dust Storm/Sand Storm
   - WT07: Flying Sand
   - WT09: Blowing Snow
   - WT18: Severe Thunderstorm

2. **Wind speed data classification**:
   - 10m wind speed (regular)
   - 20m wind speed (for runway area)
   - Gust data (3-second/5-second peaks)

3. **Visibility classification**:
   - VIS < 400m: low visibility program activated
   - VIS < 800m: CAT II/III Approach Criteria
   - VIS < 1600m: flight scheduling affected

4. **Temperature data accuracy**:
   - Airborne dedicated station data accuracy up to 0.1°C
   - Freezing rain detection sensitivity 0.01mm