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

    # Select features
    cat_features = ['DAY_NAME', 'MKT_AIRLINE',
                   'ORIGIN_IATA', 'DEST_IATA', 'FLIGHT_DISTANCE_CAT',
                   'IS_WEEKEND', 'EXTREME_WEATHER', 'DEST_EXTREME_WEATHER']

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
            2021: 27.22,
            2022: 28.18,
            2023: 29.37,
            2024: 38.35
        }

        rmse = rmse_values.get(year, 40.0)
        z_score = stats.norm.ppf(1 - (1 - confidence) / 2)

        margin_of_error = z_score * rmse

        lower_bounds = delay_minutes - margin_of_error
        upper_bounds = delay_minutes + margin_of_error

        lower_bounds = np.maximum(lower_bounds, 0)

        result = {
            "delay_predicted": bool(delay_predicted[0]),
            "delay_probability": float(delay_prob[0]),
            "delay_minutes": float(delay_minutes[0]),
            "delay_lower_bound": float(lower_bounds[0]),
            "delay_upper_bound": float(upper_bounds[0]),
            "is_weekend": bool(df['IS_WEEKEND'].iloc[0])
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
                    "is_weekend": bool(df['IS_WEEKEND'].iloc[i])
                }
                results.append(flight_result)
            return results

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Prediction failed: {str(e)}"}


def create_features_for_prediction(df):
    df = create_day_features(df)

    if 'FLIGHT_DISTANCE_CAT' not in df.columns and 'DISTANCE' in df.columns:
        if df['DISTANCE'].isnull().any():
            valid_distance = ~df['DISTANCE'].isnull()
            df['FLIGHT_DISTANCE_CAT'] = pd.Series(dtype='object')  # Initialize as empty

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
    df = df.copy()

    if 'WEEK' in df.columns:
        if isinstance(df['WEEK'].iloc[0], str):
            day_name_map = {
                'Sun': 'Sunday',
                'Mon': 'Monday',
                'Tue': 'Tuesday',
                'Wed': 'Wednesday',
                'Thu': 'Thursday',
                'Fri': 'Friday',
                'Sat': 'Saturday'
            }

            df['DAY_NAME'] = df['WEEK'].map(day_name_map)

            if df['DAY_NAME'].isnull().any():
                df['DAY_NAME'] = df['DAY_NAME'].fillna('Monday')  # Default to Monday for unrecognized values

            df['IS_WEEKEND'] = df['WEEK'].isin(['Sat', 'Sun']).astype(int)

        elif pd.api.types.is_numeric_dtype(df['WEEK']):
            df['IS_WEEKEND'] = df['WEEK'].isin([0, 6]).astype(int)

            day_names = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday',
                         4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
            df['DAY_NAME'] = df['WEEK'].map(day_names)

            if df['DAY_NAME'].isnull().any():
                df['DAY_NAME'] = df['DAY_NAME'].fillna('Monday')
    else:
        df['DAY_NAME'] = 'Monday'
        df['IS_WEEKEND'] = 0

    return df


# Example usage:
if __name__ == "__main__":
    # Example flight data
    flight = {
        "WEEK": "Thu",
        "MKT_AIRLINE": "DL",
        "ORIGIN_IATA": "ATL",
        "DEST_IATA": "LAX",
        "DISTANCE": 1950.0,
        "DEP_DELAY": 50,
        "PRCP": 0.0,
        "DEST_PRCP": 0.0,
        "EXTREME_WEATHER": 0,
        "DEST_EXTREME_WEATHER": 0
    }

    model_dir = "./arr_delay_rf_models/"

    result = predict_arrival_delay(model_dir, flight)

    if "error" not in result:
        print("\nPrediction Results:")
        print(f"Delay Probability: {result['delay_probability']:.2%}")
        print(f"Predicted Delay: {result['delay_minutes']:.1f} minutes")
        print(
            f"95% Confidence Interval: [{result['delay_lower_bound']:.1f}, {result['delay_upper_bound']:.1f}] minutes")
        print("\nFlight Characteristics:")
        print(f"Weekend Flight: {'Yes' if result['is_weekend'] else 'No'}")
    else:
        print(f"Error: {result['error']}")
