import pandas as pd
import requests
from datetime import datetime
import os

def fetch_weather_data(station_id, start_date, end_date, data_types, units="metric"):
    """
    Fetch weather data from NCEI API.
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
        
        # Standardize column names and order
        if not df.empty:
            df = standardize_columns(df)
            
        return df
    except Exception as e:
        print(f"Failed to fetch data (Station {station_id}): {e}")
        return None

def standardize_columns(df):
    """
    Standardize column order and format.
    """
    priority_columns = [
        'STATION', 'NAME', 'DATE', 'LATITUDE', 'LONGITUDE', 'ELEVATION'
    ]
    existing_priority = [col for col in priority_columns if col in df.columns]
    other_columns = [col for col in df.columns if col not in existing_priority]
    sorted_other_columns = sorted(other_columns, key=lambda x: (
        0 if x.startswith('T') else
        1 if x.startswith('PRCP') or x.startswith('SNOW') else
        2 if x.startswith('AWND') or x.startswith('WSF') or x.startswith('GUST') else
        3 if x.startswith('RH') or x.startswith('VIS') else
        4 if x.startswith('WT') else
        5
    ))
    final_columns = existing_priority + sorted_other_columns
    df = df[final_columns]
    if 'DATE' in df.columns:
        df['DATE'] = pd.to_datetime(df['DATE']).dt.strftime('%Y-%m-%d')
    return df

def save_to_csv(df, station_name, start_date, end_date, output_dir="weather_data"):
    """
    Save data to a CSV file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    clean_name = "".join(c for c in station_name if c.isalnum() or c in (' ', '-', '_'))
    start_str = start_date.replace("-", "")
    end_str = end_date.replace("-", "")
    filename = f"{clean_name}-{start_str}-{end_str}.csv"
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False)
    print(f"Saved: {filepath}")

def main():
    cities = {
        "Chicago": "USW00094846",  # Chicago O'Hare
    }
    start_date = "2020-01-01"
    end_date = "2025-01-31"
    data_types = [
        "TMAX", "TMIN", "TAVG",
        "PRCP", "SNOW",
        "AWND", "WSF2", "WSF5",
        "RH", "VIS",
        "WT01", "WT03"
    ]
    print(f"\nStarting to fetch weather data from {start_date} to {end_date}...")
    for city_name, station_id in cities.items():
        print(f"\nProcessing: {city_name} ({station_id})")
        df = fetch_weather_data(station_id, start_date, end_date, data_types)
        if df is not None and not df.empty:
            station_name = df['NAME'].iloc[0] if 'NAME' in df.columns else city_name
            save_to_csv(df, station_name, start_date, end_date)
        else:
            print(f"No valid data fetched for {city_name}")
    print("\nAll city data processing completed!")

if __name__ == "__main__":
    main()