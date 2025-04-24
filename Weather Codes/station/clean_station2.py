import pandas as pd
from pathlib import Path

def filter_us_stations(input_csv, output_csv=None):
    """
    Extract rows from the CSV file where station_id starts with 'US'
    
    Parameters:
        input_csv: Input CSV file path
        output_csv: Optional, output CSV file path. If None, only returns DataFrame without saving
    """
    # Read the CSV file
    df = pd.read_csv(input_csv)
    
    # Filter rows starting with 'US'
    us_stations = df[df['station_id'].str.startswith('USW')]
    
    count_usw_stations = us_stations.shape[0]
    print(f"Found {count_usw_stations} stations starting with 'USW'.")
    
    if output_csv:
        us_stations.to_csv(output_csv, index=False)
        print(f"Filtered data saved to {output_csv}")
    
    return us_stations

# Example usage
input_file = 'ghcnd-stations.csv'  # Your input CSV file
output_file = 'us_stations.csv'    # Output file (optional)

# Call the function
result = filter_us_stations(input_file, output_file)

# Display the first few rows
print("Filtered data sample:")
print(result.head())


# Read the CSV file
df = pd.read_csv("us_stations.csv")

# Filter rows where 'name' or 'additional_info' contains standalone " AP"
ap_stations = df[
    df["name"].str.contains(r'\bAP\b', case=False, regex=True, na=False) |
    df["additional_info"].str.contains(r'\bAP\b', case=False, regex=True, na=False)
]

# Output results
print("Stations containing 'AP':")
print(ap_stations)

# Save to a new CSV (optional)
ap_stations.to_csv("us_ap_stations.csv", index=False)
print("Saved to us_ap_stations.csv")