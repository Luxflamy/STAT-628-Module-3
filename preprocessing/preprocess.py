import pandas as pd
import numpy as np
from datetime import datetime
import pytz


def clean_flight_data(main_csv, airport_info_csv, airport_tz_csv, output_csv):
    # Load data
    main_data = pd.read_csv(main_csv)
    our_airports = pd.read_csv(airport_info_csv)
    airport_tz = pd.read_csv(airport_tz_csv)[['iata_code', 'iana_tz']]
    our_airports = our_airports[our_airports['iata_code'].notna()]

    # Recode variables
    day_map = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu",
               5: "Fri", 6: "Sat", 7: "Sun", 9: np.nan}
    cancel_map = {"A": "Carrier", "B": "Weather", "C": "NAS", "D": "Security"}

    main_data['DAY_OF_WEEK'] = main_data['DAY_OF_WEEK'].map(day_map)
    main_data = main_data[main_data['DAY_OF_WEEK'].notna()]
    main_data['CANCELLATION_CODE'] = main_data['CANCELLATION_CODE'].map(
        cancel_map)

    main_data = main_data.rename(columns={
        "DAY_OF_MONTH": "DAY", "DAY_OF_WEEK": "WEEK", "FL_DATE": "DATE",
        "ORIGIN": "ORIGIN_IATA", "ORIGIN_CITY_NAME": "ORIGIN_CITY",
        "DEST": "DEST_IATA", "DEST_CITY_NAME": "DEST_CITY",
        "MKT_UNIQUE_CARRIER": "MKT_AIRLINE", "MKT_CARRIER_FL_NUM": "MKT_FL_NUM",
        "CRS_DEP_TIME": "SCH_DEP_TIME", "DEP_TIME": "ACT_DEP_TIME",
        "CRS_ARR_TIME": "SCH_ARR_TIME", "ARR_TIME": "ACT_ARR_TIME",
        "CRS_ELAPSED_TIME": "SCH_DURATION", "ACTUAL_ELAPSED_TIME": "ACT_DURATION"
    })

    # Merge airport info
    main_data = main_data.merge(
        our_airports.rename(columns={
                            "iata_code": "ORIGIN_IATA", "type": "ORIGIN_TYPE", "elevation_ft": "ORIGIN_ELEV"}),
        on="ORIGIN_IATA", how="left"
    ).merge(
        airport_tz.rename(
            columns={"iata_code": "ORIGIN_IATA", "iana_tz": "ORIGIN_TZ"}),
        on="ORIGIN_IATA", how="left"
    ).merge(
        our_airports.rename(columns={
                            "iata_code": "DEST_IATA", "type": "DEST_TYPE", "elevation_ft": "DEST_ELEV"}),
        on="DEST_IATA", how="left"
    ).merge(
        airport_tz.rename(
            columns={"iata_code": "DEST_IATA", "iana_tz": "DEST_TZ"}),
        on="DEST_IATA", how="left"
    )

    # Time conversion
    def to_utc(row, time_col, tz_col):
        try:
            time_val = row[time_col]
            if pd.isnull(time_val) or pd.isnull(row[tz_col]):
                return pd.NaT
            time_str = f"{int(time_val):04d}"
            hour, minute = int(time_str[:2]), int(time_str[2:])
            local_tz = pytz.timezone(row[tz_col])
            naive = datetime(int(row['YEAR']), int(
                row['MONTH']), int(row['DAY']), hour, minute)
            localized = local_tz.localize(naive)
            return localized.astimezone(pytz.utc)
        except:
            return pd.NaT

    # Add UTC times
    main_data['SCH_DEP_TIME_UTC'] = main_data.apply(
        lambda r: to_utc(r, 'SCH_DEP_TIME', 'ORIGIN_TZ'), axis=1)
    main_data['ACT_DEP_TIME_UTC'] = main_data['SCH_DEP_TIME_UTC'] + \
        pd.to_timedelta(main_data['DEP_DELAY'].fillna(0), unit='m')
    main_data['SCH_ARR_TIME_UTC'] = main_data['SCH_DEP_TIME_UTC'] + \
        pd.to_timedelta(main_data['SCH_DURATION'].fillna(0), unit='m')
    main_data['ACT_ARR_TIME_UTC'] = main_data['SCH_ARR_TIME_UTC'] + \
        pd.to_timedelta(main_data['ARR_DELAY'].fillna(0), unit='m')

    # Save
    main_data.to_csv(output_csv, index=False)
