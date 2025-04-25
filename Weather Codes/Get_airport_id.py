import os
import pandas as pd

def get_unique_airport_info():
    # Get all CSV files in the cleaned_data folder
    data_dir = "cleaned_data"
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    # Initialize a dictionary to store airport information
    airport_info = {}
    
    # Iterate through each CSV file
    for file in csv_files:
        file_path = os.path.join(data_dir, file)
        try:
            # Read the CSV file and load required columns
            df = pd.read_csv(file_path, usecols=[
                'ORIGIN_AIRPORT_ID', 'ORIGIN_CITY', 'ORIGIN_IATA',
                'DEST_AIRPORT_ID', 'DEST_CITY', 'DEST_IATA'
            ])
            
            # Process origin and destination airport information
            for _, row in df.iterrows():
                origin_id = row['ORIGIN_AIRPORT_ID']
                if origin_id not in airport_info:
                    city_state = row['ORIGIN_CITY'].split(', ')
                    if len(city_state) == 2:
                        city, state = city_state
                    else:
                        city, state = city_state[0], 'Unknown'
                    
                    airport_info[origin_id] = {
                        'state': state,
                        'city': city,
                        'iata': row['ORIGIN_IATA']
                    }
                
                dest_id = row['DEST_AIRPORT_ID']
                if dest_id not in airport_info:
                    city_state = row['DEST_CITY'].split(', ')
                    if len(city_state) == 2:
                        city, state = city_state
                    else:
                        city, state = city_state[0], 'Unknown'
                    
                    airport_info[dest_id] = {
                        'state': state,
                        'city': city,
                        'iata': row['DEST_IATA']
                    }
            
            print(f"Processed {file}, current unique airports: {len(airport_info)}")
        except Exception as e:
            print(f"Error processing {file}: {str(e)}")
    
    # Convert the dictionary to a DataFrame
    result_data = []
    for airport_id, info in airport_info.items():
        result_data.append([
            airport_id,
            info['state'],
            info['city'],
            info['iata']
        ])
    
    # Sort by airport ID
    result_df = pd.DataFrame(result_data, columns=['AIRPORT_ID', 'STATE', 'CITY', 'IATA_CODE'])
    result_df = result_df.sort_values('AIRPORT_ID').reset_index(drop=True)
    
    # Save the results to a CSV file
    result_df.to_csv('airport_id.csv', index=False)
    
    print(f"Total unique airports found: {len(result_df)}")
    print("Results saved to airport_id.csv")

if __name__ == "__main__":
    get_unique_airport_info()