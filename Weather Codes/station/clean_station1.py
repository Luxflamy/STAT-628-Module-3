import pandas as pd

def convert_stations_to_csv(input_file, output_file):
    # Define fixed-width format - adjust these values based on sample data
    col_specs = [
        (0, 11),    # Station ID
        (12, 20),   # Latitude
        (21, 30),   # Longitude
        (31, 37),   # Elevation
        (38, 40),   # State/Province
        (41, 71),   # Station Name
        (72, 75)    # Additional Info (if any)
    ]
    
    # Define column names
    column_names = ['station_id', 'latitude', 'longitude', 'elevation', 'state', 'name', 'additional_info']
    
    # Read fixed-width file
    df = pd.read_fwf(input_file, colspecs=col_specs, header=None, names=column_names)
    
    # Clean data - strip whitespace from string fields
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()
    
    # Save as CSV
    df.to_csv(output_file, index=False)
    print(f"File successfully converted to {output_file}")

# Example usage
input_file = 'ghcnd-stations.txt'
output_file = 'ghcnd-stations.csv'
convert_stations_to_csv(input_file, output_file)