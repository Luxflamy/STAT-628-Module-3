
| 变量名                | 含义解释（中文）                    | Explanation (English)                   |
| --------------------- | ----------------------------------- | --------------------------------------- |
| YEAR                  | 航班年份                            | Year of the flight                      |
| MONTH                 | 航班月份（1–12）                   | Month of the flight (1–12)             |
| DAY                   | 航班当月中的日期（1–31）           | Day of the month                        |
| WEEK                  | 星期几（Mon–Sun）                  | Day of the week                         |
| DATE                  | 航班的完整日期（YYYY-MM-DD）        | Flight date                             |
| MKT_AIRLINE           | 航空公司营销承运人代码              | Marketing carrier code                  |
| MKT_FL_NUM            | 航班号（营销航司使用的编号）        | Marketing flight number                 |
| ORIGIN_AIRPORT_ID     | 起飞机场内部编号（非IATA代码）      | Unique ID for origin airport            |
| ORIGIN_AIRPORT_SEQ_ID | 起飞机场顺序编号                    | Sequence ID for origin airport          |
| ORIGIN_CITY_MARKET_ID | 起飞机场所属城市市场编号            | City market ID for origin               |
| ORIGIN_IATA           | 起飞机场的IATA三字码                | Origin airport IATA code                |
| ORIGIN_CITY           | 起飞机场所在城市名                  | City name of origin airport             |
| DEST_AIRPORT_ID       | 目的地机场内部编号（非IATA代码）    | Unique ID for destination airport       |
| DEST_AIRPORT_SEQ_ID   | 目的地机场顺序编号                  | Sequence ID for destination airport     |
| DEST_CITY_MARKET_ID   | 目的地机场所属城市市场编号          | City market ID for destination          |
| DEST_IATA             | 目的地机场的IATA三字码              | Destination airport IATA code           |
| DEST_CITY             | 目的地机场所在城市名                | City name of destination airport        |
| SCH_DEP_TIME          | 计划起飞时间（本地时间，HHMM）      | Scheduled departure time (local, HHMM)  |
| ACT_DEP_TIME          | 实际起飞时间（本地时间，HHMM）      | Actual departure time (local, HHMM)     |
| DEP_DELAY             | 起飞延误时间（分钟）                | Departure delay in minutes              |
| DEP_DELAY_NEW         | 正向起飞延误（分钟，若无延误则为0） | Positive departure delay only           |
| TAXI_OUT              | 滑出时间（从登机口到起飞，分钟）    | Taxi-out time in minutes                |
| WHEELS_OFF            | 轮离地时间（本地时间HHMM）          | Wheels-off time (local, HHMM)           |
| WHEELS_ON             | 轮着地时间（本地时间HHMM）          | Wheels-on time (local, HHMM)            |
| TAXI_IN               | 滑入时间（落地到登机口，分钟）      | Taxi-in time in minutes                 |
| SCH_ARR_TIME          | 计划到达时间（本地时间）            | Scheduled arrival time (local)          |
| ACT_ARR_TIME          | 实际到达时间（本地时间）            | Actual arrival time (local)             |
| ARR_DELAY             | 到达延误时间（分钟）                | Arrival delay in minutes                |
| CANCELLED             | 是否取消（1=取消, 0=未取消）        | Flight cancelled (1=yes, 0=no)          |
| CANCELLATION_CODE     | 取消原因（如 Carrier, Weather）     | Reason for cancellation                 |
| SCH_DURATION          | 计划飞行时长（分钟）                | Scheduled elapsed flight time           |
| ACT_DURATION          | 实际飞行时长（分钟）                | Actual elapsed flight time              |
| AIR_TIME              | 空中飞行时间（分钟）                | Air time in minutes                     |
| DISTANCE              | 飞行距离（英里）                    | Flight distance in miles                |
| CARRIER_DELAY         | 航司自身原因延误（分钟）            | Carrier-related delay (minutes)         |
| WEATHER_DELAY         | 天气原因延误（分钟）                | Weather-related delay (minutes)         |
| NAS_DELAY             | NAS系统延误（分钟）                 | National Aviation System delay          |
| SECURITY_DELAY        | 安检相关延误（分钟）                | Security-related delay                  |
| LATE_AIRCRAFT_DELAY   | 前序航班晚到延误（分钟）            | Delay due to late incoming aircraft     |
| TOTAL_ADD_GTIME       | 额外地面运行时间（分钟）            | Total additional ground time            |
| ORIGIN_TYPE           | 起飞机场类型                        | Type of origin airport                  |
| ORIGIN_ELEV           | 起飞机场海拔（英尺）                | Elevation of origin airport (feet)      |
| ORIGIN_TZ             | 起飞机场时区（IANA格式）            | IANA timezone of origin                 |
| DEST_TYPE             | 目的地机场类型                      | Type of destination airport             |
| DEST_ELEV             | 目的地机场海拔（英尺）              | Elevation of destination airport (feet) |
| DEST_TZ               | 目的地机场时区（IANA格式）          | IANA timezone of destination            |
| SCH_DEP_TIME_UTC      | 计划起飞时间（UTC）                 | Scheduled departure time (UTC)          |
| ACT_DEP_TIME_UTC      | 实际起飞时间（UTC）                 | Actual departure time (UTC)             |
| SCH_ARR_TIME_UTC      | 计划到达时间（UTC）                 | Scheduled arrival time (UTC)            |
| ACT_ARR_TIME_UTC      | 实际到达时间（UTC）                 | Actual arrival time (UTC)               |
