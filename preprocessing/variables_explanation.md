
| 变量名                | 含义解释（中文）                    | Explanation (English)                   |Label                   |
| --------------------- | ----------------------------------- | --------------------------------------- | -------------------- |
| YEAR                  | 航班年份                            | Year of the flight                      |X                      |
| MONTH                 | 航班月份（1–12）                   | Month of the flight (1–12)             |X                         |
| DAY                   | 航班当月中的日期（1–31）           | Day of the month                        |X                        |
| WEEK                  | 星期几（Mon–Sun）                  | Day of the week                         |X                       |
| MKT_AIRLINE           | 航空公司代码                      | Airline Code                               |X (select top)        |
| MKT_FL_NUM            | 航班号（营销航司使用的编号）        | Marketing flight number                 |X                       |
| ORIGIN_AIRPORT_ID     | 起飞机场内部编号（非IATA代码）      | Unique ID for origin airport            |rm (depend on IATA)     |
| ORIGIN_AIRPORT_SEQ_ID | 起飞机场顺序编号                    | Sequence ID for origin airport          |rm (depend on IATA)     |
| ORIGIN_CITY_MARKET_ID | 起飞机场所属城市市场编号            | City market ID for origin               |rm (depend on IATA)     |
| ORIGIN_IATA           | 起飞机场的IATA三字码                | Origin airport IATA code                |X (select top)           |
| ORIGIN_CITY           | 起飞机场所在城市名                  | City name of origin airport             |rm (depend on IATA)     |
| DEST_AIRPORT_ID       | 目的地机场内部编号（非IATA代码）    | Unique ID for destination airport       |rm (depend on IATA)     |
| DEST_AIRPORT_SEQ_ID   | 目的地机场顺序编号                  | Sequence ID for destination airport     |rm (depend on IATA)     |
| DEST_CITY_MARKET_ID   | 目的地机场所属城市市场编号          | City market ID for destination          |rm (depend on IATA)     |
| DEST_IATA             | 目的地机场的IATA三字码              | Destination airport IATA code           |X (select top)           |
| DEST_CITY             | 目的地机场所在城市名                | City name of destination airport        |rm (depend on IATA)     |
| SCH_DEP_TIME          | 计划起飞时间（本地时间，HHMM）      | Scheduled departure time (local, HHMM)  |rm (transformed to UTC)   |
| ACT_DEP_TIME          | 实际起飞时间（本地时间，HHMM）      | Actual departure time (local, HHMM)     |rm (transformed to UTC)   |
| DEP_DELAY             | 起飞延误时间（分钟）                | Departure delay in minutes              |Y1                       |
| DEP_DELAY_NEW         | 正向起飞延误（分钟，若无延误则为0） | Positive departure delay only           |rm (depend on DEP_DELAY)   |
| TAXI_OUT              | 滑出时间（从登机口到起飞，分钟）    | Taxi-out time in minutes                |rm (unabable to know)      |
| WHEELS_OFF            | 轮离地时间（本地时间HHMM）          | Wheels-off time (local, HHMM)           |rm (depend on ACT_DEP_TIME_UTC and TAXI_OUT) |
| WHEELS_ON             | 轮着地时间（本地时间HHMM）          | Wheels-on time (local, HHMM)            |rm (depend on ACT_ARR_TIME_UTC and TAXI_IN) |
| TAXI_IN               | 滑入时间（落地到登机口，分钟）      | Taxi-in time in minutes                 |rm (unabable to know)      |
| SCH_ARR_TIME          | 计划到达时间（本地时间）            | Scheduled arrival time (local)          |rm (transformed to UTC)   |
| ACT_ARR_TIME          | 实际到达时间（本地时间）            | Actual arrival time (local)             |rm (transformed to UTC)   |
| ARR_DELAY             | 到达延误时间（分钟）                | Arrival delay in minutes                |Y2                        |
| ARR_DELAY_NEW         | 正向到达延误（分钟，若无延误则为0）  | Positive arrival delay only             |rm (depend on ARR_DELAY)   |
| CANCELLED             | 是否取消（1=取消, 0=未取消）        | Flight cancelled (1=yes, 0=no)          |rm (depend on CANCELLATION_CODE) |
| CANCELLATION_CODE     | 取消原因（如 Carrier, Weather）     | Reason for cancellation                 |Y1 (select for model 2)         |
| SCH_DURATION          | 计划飞行时长（分钟）                | Scheduled elapsed flight time           |X (better for model 2)     |
| ACT_DURATION          | 实际飞行时长（分钟）                | Actual elapsed flight time              |rm (ACT_DURATION = ACT_ARR_TIME_UTC - ACT_DEP_TIME_UTC)|
| AIR_TIME              | 空中飞行时间（分钟）                | Air time in minutes                     |rm (AIR_TIME = ACT_DURATION - TAXI_OUT - TAXI_IN) |
| DISTANCE              | 飞行距离（英里）                    | Flight distance in miles                |X                         |
| CARRIER_DELAY         | 航司自身原因延误（分钟）            | Carrier-related delay (minutes)         |rm (unabable to know)      |
| WEATHER_DELAY         | 天气原因延误（分钟）                | Weather-related delay (minutes)         |rm (unabable to know)      |
| NAS_DELAY             | NAS系统延误（分钟）                 | National Aviation System delay          |rm (unabable to know)      |
| SECURITY_DELAY        | 安检相关延误（分钟）                | Security-related delay                  |rm (unabable to know)      |
| LATE_AIRCRAFT_DELAY   | 前序航班晚到延误（分钟）            | Delay due to late incoming aircraft     |rm (unabable to know)      |
| TOTAL_ADD_GTIME       | 额外地面运行时间（分钟）            | Total Ground Time Away from Gate for Gate Return or Cancelled Flight |rm (unabable to know)      |
| ORIGIN_TYPE           | 起飞机场类型                        | Type of origin airport                  |X                         |
| ORIGIN_ELEV           | 起飞机场海拔（英尺）                | Elevation of origin airport (feet)       |X                         |
| ORIGIN_TZ             | 起飞机场城市                       | origin city                              |rm (depend on IATA)         |
| DEST_TYPE             | 目的地机场类型                      | Type of destination airport             |X (better for model 2)     |
| DEST_ELEV             | 目的地机场海拔（英尺）              | Elevation of destination airport (feet) |X (better for model 2)     |
| DEST_TZ               | 目的地机场城市                     | destination city                         |rm (depend on IATA)          |
| SCH_DEP_TIME_UTC      | 计划起飞时间（UTC）                 | Scheduled departure time (UTC)          |X                       |
| ACT_DEP_TIME_UTC      | 实际起飞时间（UTC）                 | Actual departure time (UTC)             |rm (depend on DEP_DELAY) |
| SCH_ARR_TIME_UTC      | 计划到达时间（UTC）                 | Scheduled arrival time (UTC)            |X (better for model 2)     |
| ACT_ARR_TIME_UTC      | 实际到达时间（UTC）                 | Actual arrival time (UTC)               |rm (depend on ARR_DELAY) |
