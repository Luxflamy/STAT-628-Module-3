<<<<<<< HEAD
# STAT-628-Module-3

Airline performance analysis

[Variables Explanation (Chinese and English)](preprocessing/variables_explanation.md)
=======
# Airline Performance Analysis with Weather Impact Evaluation(STAT-628-Module-3)

Airline performance analysis with weather impact evaluation
[Project requirements](stat628_sp25_airline.pdf)

## 🌦️ Meteorological Data Processing

### 1. Data Preparation
- Source files:
  - `Weather Codes/station/ghcnd-stations.txt` (NOAA raw station data)
  - `Weather Codes/station/airport_id.csv` (Airport IATA codes)

### 2. Station-Airport Matching
```bash
cd Weather Codes/station/
python merge_station_id.py
```
Generates: `final_station_id.csv` (station_id, airport_id, IATA_CODE pairs)

### 3. Download Weather Data
```bash
cd ..
python weather_downloader2.py
```
Outputs: Airport-specific CSV files (e.g., `ORD_2021_May_1.csv`)

[Airport Variables Explanation (Chinese and English)](preprocessing/variables_explanation.md) | [Weather Variables Explanation (Chinese and English)](Weather%20Codes/variables_exp.md)



>>>>>>> 4f47b349fe7d11fb3f7837fc762a3898289ce313
