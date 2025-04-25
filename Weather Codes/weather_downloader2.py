import pandas as pd
import requests
from datetime import datetime
import os
import time
from tqdm import tqdm  # show progress bar

def fetch_weather_data(station_id, start_date, end_date, data_types, units="metric"):
    """
    Get weather data from NCEI API
    """
    base_url = "https://www.ncei.noaa.gov/access/services/data/v1"
    
    params = {
        "dataset": "daily-summaries",
        "stations": station_id,
        "startDate": start_date,
        "endDate": end_date,
        "dataTypes": ",".join(data_types),
        "units": units,
        "format": "json",
        "includeStationName": "true",
        "includeStationLocation": "true"
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    url = f"{base_url}?{query_string}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        
        # 规范化列名和顺序
        if not df.empty:
            df = standardize_columns(df)
            
        return df
    except Exception as e:
        print(f"\nFailed to get data (site{station_id}): {e}")
        return None

def standardize_columns(df):
    """
    Standardize data column order and format
    """
    # define the priority columns
    priority_columns = [
        'STATION', 'NAME', 'DATE', 'LATITUDE', 'LONGITUDE', 'ELEVATION'
    ]
    
    # get existing priority columns
    existing_priority = [col for col in priority_columns if col in df.columns]
    
    # other columns
    other_columns = [col for col in df.columns if col not in existing_priority]
    
    # ranking other columns
    sorted_other_columns = sorted(other_columns, key=lambda x: (
        0 if x.startswith('T') else  # temperature
        1 if x.startswith('PRCP') or x.startswith('SNOW') else  # precipitation
        2 if x.startswith('AWND') or x.startswith('WSF') or x.startswith('GUST') else  # wind speed
        3 if x.startswith('RH') or x.startswith('VIS') else  # humidity and visibility
        4 if x.startswith('WT') else  # weather phenomena
        5  # others
    ))
    
    # combine the columns
    final_columns = existing_priority + sorted_other_columns
    df = df[final_columns]
    
    # standardize date format
    if 'DATE' in df.columns:
        df['DATE'] = pd.to_datetime(df['DATE']).dt.strftime('%Y-%m-%d')
    
    return df

def save_monthly_data(df, iata_code, year, month, output_dir="weather_data"):
    """
    Save monthly data as a CSV file according to the specified naming convention
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # filter out the monthly data
    df['DATE'] = pd.to_datetime(df['DATE'])
    monthly_df = df[(df['DATE'].dt.year == year) & (df['DATE'].dt.month == month)]
    
    if monthly_df.empty:
        return False
    
    # generate filename
    month_name = datetime(year, month, 1).strftime('%b')  # get the month's abbreviation
    filename = f"{iata_code}_{year}_{month_name}_1.csv"
    filepath = os.path.join(output_dir, filename)
    
    # multiple files check
    counter = 1
    while os.path.exists(filepath):
        counter += 1
        filename = f"{iata_code}_{year}_{month_name}_{counter}.csv"
        filepath = os.path.join(output_dir, filename)
    
    monthly_df.to_csv(filepath, index=False)
    return True

def main():

    station_df = pd.read_csv('station/final_station_id.csv')
    station_df = station_df.dropna(subset=['IATA_CODE'])

    data_types = [
        "TMAX", "TMIN", "TAVG",    # Temperature
        "PRCP", "SNOW",             # precipitation
        "AWND", "WSF2", "WSF5",     # wind speed
        "RH", "VIS",                # humidity and visibility
        "WT01", "WT03"              # weather phenomena (fog, thunderstorms)
    ]
    
    years = range(2021, 2025)  # 2021-2024
    months = [5, 6, 7, 8]      # 5-8 months
    
    print(f"\n Started acquiring weather data(2021-2024/5-8 months)...")
    
    # Iterate through each station
    for _, row in tqdm(station_df.iterrows(), total=len(station_df), desc="Processing stations"):
        station_id = row['station_id']
        iata_code = row['IATA_CODE']
        
        # Get the complete data for the station
        full_df = fetch_weather_data(
            station_id=station_id,
            start_date="2021-01-01",
            end_date="2024-12-31",
            data_types=data_types
        )
        
        if full_df is None or full_df.empty:
            continue
        
        # Save monthly data
        for year in years:
            for month in months:
                saved = save_monthly_data(full_df, iata_code, year, month)
                if not saved:
                    print(f"\nWarning: {iata_code} {year}-{month} no data")
        
        # Avoid excessive API requests
        time.sleep(1)
    
    print("\nAll data processing completed!")

if __name__ == "__main__":
    main()