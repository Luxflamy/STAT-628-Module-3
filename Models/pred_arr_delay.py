import pandas as pd
import numpy as np
import os
import joblib
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from scipy import stats
import warnings

warnings.filterwarnings('ignore')


def predict_arrival_delay(model_dir, flight_data, year=2024, confidence=0.95):
    if isinstance(flight_data, dict):
        df = pd.DataFrame([flight_data])
    else:
        df = flight_data.copy()

    # Get model paths
    year_model_dir = os.path.join(model_dir, f'year_{year}')
    class_model_path = os.path.join(year_model_dir, f"arr_delay_class_model_{year}.joblib")
    reg_model_path = os.path.join(year_model_dir, f"arr_delay_reg_model_{year}.joblib")

    if not (os.path.exists(class_model_path) and os.path.exists(reg_model_path)):
        return {"error": f"Models for year {year} not found in {year_model_dir}"}

    # Load the models
    try:
        class_model = joblib.load(class_model_path)
        reg_model = joblib.load(reg_model_path)
    except Exception as e:
        return {"error": f"Failed to load models: {str(e)}"}

    df = create_features_for_prediction(df)
    cat_features = ['DAY_NAME', 'ARR_TIME_BLOCK', 'MKT_AIRLINE',
                    'ORIGIN_IATA', 'DEST_IATA', 'FLIGHT_DISTANCE_CAT',
                    'IS_LATE_NIGHT_ARR', 'IS_WEEKEND', 'IS_MORNING_RUSH_ARR', 'IS_EVENING_RUSH_ARR',
                    'EXTREME_WEATHER', 'DEST_EXTREME_WEATHER']
    num_features = [
        'DISTANCE',
        'PRCP', 'DEST_PRCP',
        'DEP_DELAY'
    ]

    for col in cat_features:
        if col not in df.columns:
            if col == 'EXTREME_WEATHER' or col == 'DEST_EXTREME_WEATHER':
                df[col] = 0
            else:
                df[col] = 'unknown'
        elif df[col].isnull().sum() > 0:
            df[col] = df[col].fillna('unknown')

    for col in num_features:
        if col not in df.columns:
            df[col] = 0
        elif df[col].isnull().sum() > 0:
            if df[col].notna().any():
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(0)

    X_pred = df[cat_features + num_features]

    # Make predictions
    try:
        delay_prob = class_model.predict_proba(X_pred)[:, 1]
        delay_predicted = class_model.predict(X_pred)

        delay_minutes = reg_model.predict(X_pred)

        rmse_values = {
            2021: 26.00,
            2022: 28.22,
            2023: 27.06,
            2024: 37.22
        }

        rmse = rmse_values.get(year, 40.0)
        z_score = stats.norm.ppf(1 - (1 - confidence) / 2)

        margin_of_error = z_score * rmse

        # Calculate confidence interval bounds
        lower_bounds = delay_minutes - margin_of_error
        upper_bounds = delay_minutes + margin_of_error

        lower_bounds = np.maximum(lower_bounds, 0)

        result = {
            "delay_predicted": bool(delay_predicted[0]),
            "delay_probability": float(delay_prob[0]),
            "delay_minutes": float(delay_minutes[0]),
            "delay_lower_bound": float(lower_bounds[0]),
            "delay_upper_bound": float(upper_bounds[0]),
            "is_weekend": bool(df['IS_WEEKEND'].iloc[0]),
            "is_late_night_arrival": bool(df['IS_LATE_NIGHT_ARR'].iloc[0]),
            "is_morning_rush": bool(df['IS_MORNING_RUSH_ARR'].iloc[0]),
            "is_evening_rush": bool(df['IS_EVENING_RUSH_ARR'].iloc[0])
        }

        if len(df) > 1 and isinstance(flight_data, pd.DataFrame):
            results = []
            for i in range(len(df)):
                flight_result = {
                    "delay_predicted": bool(delay_predicted[i]),
                    "delay_probability": float(delay_prob[i]),
                    "delay_minutes": float(delay_minutes[i]),
                    "delay_lower_bound": float(lower_bounds[i]),
                    "delay_upper_bound": float(upper_bounds[i]),
                    "is_weekend": bool(df['IS_WEEKEND'].iloc[i]),
                    "is_late_night_arrival": bool(df['IS_LATE_NIGHT_ARR'].iloc[i]),
                    "is_morning_rush": bool(df['IS_MORNING_RUSH_ARR'].iloc[i]),
                    "is_evening_rush": bool(df['IS_EVENING_RUSH_ARR'].iloc[i])
                }
                results.append(flight_result)
            return results

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Prediction failed: {str(e)}"}


def create_features_for_prediction(df):
    #df = create_late_night_arrival_indicator(df)
    #df = create_arrival_time_block_features(df)
    df = create_day_features(df)

    # Create flight distance categories if not present
    if 'FLIGHT_DISTANCE_CAT' not in df.columns and 'DISTANCE' in df.columns:
        if df['DISTANCE'].isnull().any():
            valid_distance = ~df['DISTANCE'].isnull()
            df['FLIGHT_DISTANCE_CAT'] = pd.Series(dtype='object')

            if valid_distance.any():
                df.loc[valid_distance, 'FLIGHT_DISTANCE_CAT'] = pd.cut(
                    df.loc[valid_distance, 'DISTANCE'],
                    bins=[0, 300, 600, 1000, 1500, float('inf')],
                    labels=['Very Short (<300 mi)', 'Short (300-600 mi)', 'Medium (600-1000 mi)',
                            'Long (1000-1500 mi)', 'Very Long (>1500 mi)']
                )
            df['FLIGHT_DISTANCE_CAT'] = df['FLIGHT_DISTANCE_CAT'].fillna('Medium (600-1000 mi)')
        else:
            df['FLIGHT_DISTANCE_CAT'] = pd.cut(
                df['DISTANCE'],
                bins=[0, 300, 600, 1000, 1500, float('inf')],
                labels=['Very Short (<300 mi)', 'Short (300-600 mi)', 'Medium (600-1000 mi)',
                        'Long (1000-1500 mi)', 'Very Long (>1500 mi)']
            )

    return df


def create_day_features(df):
    """
    Creates day type features from text day names (Sun, Mon, etc.)
    """
    # Make a copy to avoid modifying the original
    df = df.copy()

    # Check if we have the WEEK column with text day names
    if 'WEEK' in df.columns:
        if isinstance(df['WEEK'].iloc[0], str):
            # Create a mapping from abbreviated day names to full day names
            day_name_map = {
                'Sun': 'Sunday',
                'Mon': 'Monday',
                'Tue': 'Tuesday',
                'Wed': 'Wednesday',
                'Thu': 'Thursday',
                'Fri': 'Friday',
                'Sat': 'Saturday'
            }

            # Map abbreviated names to full names
            df['DAY_NAME'] = df['WEEK'].map(day_name_map)

            # Handle any values not in the mapping
            if df['DAY_NAME'].isnull().any():
                df['DAY_NAME'] = df['DAY_NAME'].fillna('Monday')  # Default to Monday for unrecognized values

            # Create weekend indicator
            df['IS_WEEKEND'] = df['WEEK'].isin(['Sat', 'Sun']).astype(int)

        elif pd.api.types.is_numeric_dtype(df['WEEK']):
            # If WEEK is numeric, assume it follows 0=Sunday, 1=Monday, etc. format
            # Create IS_WEEKEND
            df['IS_WEEKEND'] = df['WEEK'].isin([0, 6]).astype(int)

            # Map day numbers to names for better interpretability
            day_names = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday',
                         4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
            df['DAY_NAME'] = df['WEEK'].map(day_names)

            # Handle any values not in the mapping
            if df['DAY_NAME'].isnull().any():
                df['DAY_NAME'] = df['DAY_NAME'].fillna('Monday')
    else:
        # Default values
        df['DAY_NAME'] = 'Monday'
        df['IS_WEEKEND'] = 0

    return df


# Example usage:
if __name__ == "__main__":
    # Example flight data
    flight = {
        "WEEK": "Thu",  # Day of week
        "MKT_AIRLINE": "DL",
        "ORIGIN_IATA": "ORD",
        "DEST_IATA": "ATL",
        "DISTANCE": 606.0,
        "SCH_DEP_TIME": 800,  # 8:00 AM
        "DEP_DELAY": 15,  # 15 minutes departure delay
        "PRCP": 0.0,  # No precipitation at origin
        "DEST_PRCP": 0.0,  # No precipitation at destination
        "EXTREME_WEATHER": 0,  # No extreme weather at origin
        "DEST_EXTREME_WEATHER": 0  # No extreme weather at destination
    }

    # Path to the models directory
    model_dir = "./arr_delay_rf_models/"

    # Make prediction
    result = predict_arrival_delay(model_dir, flight)

    # Print results
    if "error" not in result:
        print("\nPrediction Results:")
        print(f"Delay Probability: {result['delay_probability']:.2%}")
        print(f"Predicted Delay: {result['delay_minutes']:.1f} minutes")
        print(
            f"95% Confidence Interval: [{result['delay_lower_bound']:.1f}, {result['delay_upper_bound']:.1f}] minutes")
        print("\nFlight Characteristics:")
        print(f"Weekend Flight: {'Yes' if result['is_weekend'] else 'No'}")
        print(f"Late Night Arrival: {'Yes' if result['is_late_night_arrival'] else 'No'}")
        print(f"Morning Rush Hour: {'Yes' if result['is_morning_rush'] else 'No'}")
        print(f"Evening Rush Hour: {'Yes' if result['is_evening_rush'] else 'No'}")
    else:
        print(f"Error: {result['error']}")
