# Airline Performance Analysis with Weather Impact Evaluation(STAT-628-Module-3)

Airline performance analysis with weather impact evaluation

[Variables Explanation (Chinese and English)](preprocessing/variables_explanation.md)


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

## 🚀 Quick Start
1. Install requirements:
```bash
pip install pandas requests tqdm fuzzywuzzy python-Levenshtein
```

2. Run processing pipeline:
```bash
# Match stations to airports
python Weather Codes/station/merge_station_id.py

# Download weather data (2021-2024 May-Aug)
python Weather Codes/weather_downloader2.py
```
[Project requirements](stat628_sp25_airline.pdf)