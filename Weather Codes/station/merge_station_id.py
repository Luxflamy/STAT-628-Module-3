import pandas as pd
from pathlib import Path
import re

# Set file paths
station_dir = Path("station")
airport_path = station_dir / "airport_id.csv"
usap_path = station_dir / "us_ap_stations.csv"
output_path = station_dir / "final_station_id.csv"

# Read data
airport_df = pd.read_csv(airport_path)
usap_df = pd.read_csv(usap_path)

# Preprocessing function
def clean_city_name(name):
    """Extract the core part of the city name from the airport name"""
    # Remove airport type identifiers
    name = re.sub(
        r'\b(AP|MUNI|RGNL|CO|FLD|MEMORIAL|INTL|EXEC|COUNTY|AIRPORT|FAA|WSO)\b', 
        '', 
        name, 
        flags=re.IGNORECASE
    )
    # Keep the main city name part
    city = name.split()[0] if len(name.split()) > 0 else name
    return city.strip().lower().replace(" ", "").replace("-", "")

# Preprocess city names
airport_df['city_clean'] = airport_df['CITY'].apply(clean_city_name)
usap_df['city_clean'] = usap_df['name'].apply(clean_city_name)

# Merge datasets (inner join)
merged = pd.merge(
    usap_df,
    airport_df,
    how='inner',
    left_on=['state', 'city_clean'],
    right_on=['STATE', 'city_clean']
)

# Select required columns and rename
result = merged[[
    'station_id', 'AIRPORT_ID', 'state', 'CITY', 'IATA_CODE',
    'longitude', 'latitude', 'elevation'
]].drop_duplicates().reset_index(drop=True)

result.columns = [
    'station_id', 'airport_id', 'state', 'city', 'IATA_CODE',
    'longitude', 'latitude', 'elevation'
]

# Save results
result.to_csv(output_path, index=False)
print(f"Merge completed, {len(result)} records matched")
print(f"Results saved to {output_path}")