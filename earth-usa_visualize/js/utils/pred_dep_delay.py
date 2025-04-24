import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import joblib
from scipy import stats


# Define ResNet-style block
class ResidualBlock(nn.Module):
    def __init__(self, input_dim, hidden_dim=None):
        super(ResidualBlock, self).__init__()
        if hidden_dim is None:
            hidden_dim = input_dim

        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.bn1 = nn.BatchNorm1d(hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, input_dim)
        self.bn2 = nn.BatchNorm1d(input_dim)
        self.dropout = nn.Dropout(0.2)

    def forward(self, x):
        identity = x

        out = self.fc1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.dropout(out)

        out = self.fc2(out)
        out = self.bn2(out)

        out += identity  # Skip connection
        out = self.relu(out)

        return out


class BottleneckResidualBlock(nn.Module):
    def __init__(self, input_dim, bottleneck_dim):
        super(BottleneckResidualBlock, self).__init__()

        self.fc1 = nn.Linear(input_dim, bottleneck_dim)
        self.bn1 = nn.BatchNorm1d(bottleneck_dim)
        self.fc2 = nn.Linear(bottleneck_dim, bottleneck_dim)
        self.bn2 = nn.BatchNorm1d(bottleneck_dim)
        self.fc3 = nn.Linear(bottleneck_dim, input_dim)
        self.bn3 = nn.BatchNorm1d(input_dim)

        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)

    def forward(self, x):
        identity = x

        out = self.fc1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.fc2(out)
        out = self.bn2(out)
        out = self.relu(out)
        out = self.dropout(out)

        out = self.fc3(out)
        out = self.bn3(out)

        out += identity  # Skip connection
        out = self.relu(out)

        return out


# Define FlightDelayClassifier
class FlightDelayClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim=256):
        super(FlightDelayClassifier, self).__init__()

        # Initial embedding layer
        self.embedding = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3)
        )

        # Residual blocks
        self.res_block1 = ResidualBlock(hidden_dim)
        self.res_block2 = ResidualBlock(hidden_dim)
        self.res_block3 = ResidualBlock(hidden_dim)

        # Bottleneck residual block for dimensionality reduction
        self.bottleneck = BottleneckResidualBlock(hidden_dim, hidden_dim // 2)

        # Final prediction layers
        self.prediction = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        x = self.embedding(x)
        x = self.res_block1(x)
        x = self.res_block2(x)
        x = self.res_block3(x)
        x = self.bottleneck(x)
        x = self.prediction(x)
        return x


# Define FlightDelayRegressor
class FlightDelayRegressor(nn.Module):
    def __init__(self, input_dim, hidden_dim=256):
        super(FlightDelayRegressor, self).__init__()

        # Initial embedding layer
        self.embedding = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.LeakyReLU(0.1),
            nn.Dropout(0.3)
        )

        # Residual blocks
        self.res_block1 = ResidualBlock(hidden_dim)
        self.res_block2 = ResidualBlock(hidden_dim)
        self.res_block3 = ResidualBlock(hidden_dim)

        # Bottleneck residual block
        self.bottleneck = BottleneckResidualBlock(hidden_dim, hidden_dim // 2)

        # Final prediction layers
        self.prediction = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.BatchNorm1d(64),
            nn.LeakyReLU(0.1),
            nn.Dropout(0.2),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        x = self.embedding(x)
        x = self.res_block1(x)
        x = self.res_block2(x)
        x = self.res_block3(x)
        x = self.bottleneck(x)
        x = self.prediction(x)
        return x


# Load preprocessing pipeline and models
def load_artifacts(year):
    base_path = '/Users/lixiangyi/Documents/学习/网页设计/Web/earth-usa/models/dep_delay_nn'  

    preprocessor_path = f'{base_path}/year_2021/resnet_preprocessor_2021.joblib'
    classifier_path = f'{base_path}/year_{year}/models_{year}/resnet_classifier_{year}.pth'
    regressor_path = f'{base_path}/year_{year}/models_{year}/resnet_regressor_{year}.pth'
    
    # Load preprocessor
    preprocessor = joblib.load(preprocessor_path)

    # Preprocessed feature count is 139
    input_dim = 139

    # Load classifier
    classifier_state_dict = torch.load(classifier_path)
    classifier = FlightDelayClassifier(input_dim=input_dim)
    classifier.load_state_dict(classifier_state_dict)

    # Load regressor
    regressor_state_dict = torch.load(regressor_path)
    regressor = FlightDelayRegressor(input_dim=input_dim)
    regressor.load_state_dict(regressor_state_dict)

    return preprocessor, classifier, regressor


# Hardcoded RMSE values for each year
def get_rmse(year):
    """Return RMSE value for the given year"""
    rmse_values = {
        2021: 28.70781707763672,
        2022: 38.48480987548828,
        2023: 37.411659240722656,
        2024: 49.193267822265625
    }

    if year not in rmse_values:
        return 40.0

    return rmse_values[year]


def create_advanced_time_features(df):
    df['DEP_HOUR'] = df['SCH_DEP_TIME'] // 100
    df['DEP_MINUTE'] = df['SCH_DEP_TIME'] % 100
    df['TIME_MINS'] = df['DEP_HOUR'] * 60 + df['DEP_MINUTE']
    df['HOUR_SIN'] = np.sin(2 * np.pi * df['DEP_HOUR'] / 24)  # Cyclic encoding
    df['HOUR_COS'] = np.cos(2 * np.pi * df['DEP_HOUR'] / 24)

    # Add more advanced time features
    df['NORMALIZED_TIME'] = df['TIME_MINS'] / (24 * 60)

    # 12-hour cycle (AM/PM mode)
    df['HALFDAY_SIN'] = np.sin(2 * np.pi * df['DEP_HOUR'] / 12)
    df['HALFDAY_COS'] = np.cos(2 * np.pi * df['DEP_HOUR'] / 12)

    # 6-hour cycle (four parts of a day)
    df['QUARTER_DAY_SIN'] = np.sin(2 * np.pi * df['DEP_HOUR'] / 6)
    df['QUARTER_DAY_COS'] = np.cos(2 * np.pi * df['DEP_HOUR'] / 6)

    # Create peak hour indicators
    df['IS_MORNING_PEAK'] = ((df['DEP_HOUR'] >= 7) & (df['DEP_HOUR'] <= 9)).astype(int)
    df['IS_EVENING_PEAK'] = ((df['DEP_HOUR'] >= 16) & (df['DEP_HOUR'] <= 19)).astype(int)

    # Add TIME_BLOCK feature
    time_blocks = {
        0: 'Late Night (0-3)',
        1: 'Late Night (0-3)',
        2: 'Late Night (0-3)',
        3: 'Early Morning (3-6)',
        4: 'Early Morning (3-6)',
        5: 'Early Morning (3-6)',
        6: 'Morning (6-9)',
        7: 'Morning (6-9)',
        8: 'Morning (6-9)',
        9: 'Mid-Day (9-12)',
        10: 'Mid-Day (9-12)',
        11: 'Mid-Day (9-12)',
        12: 'Afternoon (12-15)',
        13: 'Afternoon (12-15)',
        14: 'Afternoon (12-15)',
        15: 'Evening (15-18)',
        16: 'Evening (15-18)',
        17: 'Evening (15-18)',
        18: 'Night (18-21)',
        19: 'Night (18-21)',
        20: 'Night (18-21)',
        21: 'Late Night (21-24)',
        22: 'Late Night (21-24)',
        23: 'Late Night (21-24)'
    }
    df['TIME_BLOCK'] = df['DEP_HOUR'].map(time_blocks)

    return df


# Airport features
def create_airport_features(df):
    hubs = ['ATL', 'DFW', 'ORD', 'LAX', 'DEN', 'CLT', 'LAS', 'PHX', 'MCO', 'SEA']
    df['IS_MAJOR_HUB_ORIGIN'] = df['ORIGIN_IATA'].isin(hubs).astype(int)
    df['IS_HUB_TO_HUB'] = 0  # Default value

    if 'DEST_IATA' in df.columns:
        df['IS_MAJOR_HUB_DEST'] = df['DEST_IATA'].isin(hubs).astype(int)
        df['IS_HUB_TO_HUB'] = (df['IS_MAJOR_HUB_ORIGIN'] & df['IS_MAJOR_HUB_DEST']).astype(int)

    # Regional indicators
    west_coast = ['LAX', 'SFO', 'SEA', 'PDX', 'SAN', 'LAS']
    east_coast = ['JFK', 'LGA', 'EWR', 'BOS', 'DCA', 'IAD', 'MIA', 'FLL', 'ATL', 'CLT']
    central = ['ORD', 'MDW', 'DFW', 'IAH', 'DEN', 'MSP', 'DTW', 'STL']

    df['IS_WEST_COAST_ORIGIN'] = df['ORIGIN_IATA'].isin(west_coast).astype(int)
    df['IS_EAST_COAST_ORIGIN'] = df['ORIGIN_IATA'].isin(east_coast).astype(int)
    df['IS_CENTRAL_ORIGIN'] = df['ORIGIN_IATA'].isin(central).astype(int)

    if 'DEST_IATA' in df.columns:
        df['IS_WEST_COAST_DEST'] = df['DEST_IATA'].isin(west_coast).astype(int)
        df['IS_EAST_COAST_DEST'] = df['DEST_IATA'].isin(east_coast).astype(int)
        df['IS_CENTRAL_DEST'] = df['DEST_IATA'].isin(central).astype(int)

        # Transcontinental flight indicator
        df['IS_TRANSCON'] = ((df['IS_WEST_COAST_ORIGIN'] & df['IS_EAST_COAST_DEST']) |
                             (df['IS_EAST_COAST_ORIGIN'] & df['IS_WEST_COAST_DEST'])).astype(int)

    # Create distance category feature
    if 'DISTANCE' in df.columns:
        df['DISTANCE_CAT'] = pd.cut(
            df['DISTANCE'],
            bins=[0, 500, 1000, 1500, 2000, float('inf')],
            labels=['Very Short', 'Short', 'Medium', 'Long', 'Very Long']
        )

        # Normalize distance
        max_dist = 3000  # Empirically set max distance
        df['NORMALIZED_DISTANCE'] = df['DISTANCE'] / max_dist

        # Create log distance feature
        df['LOG_DISTANCE'] = np.log1p(df['DISTANCE'])

    return df


# Add weather features
def create_weather_features(df):
    df = df.copy()

    if 'PRCP' in df.columns:
        df['RAIN_SEVERITY'] = pd.cut(
            df['PRCP'],
            bins=[-0.01, 0.0, 0.1, 0.5, 1.0, float('inf')],
            labels=[0, 1, 2, 3, 4]
        ).astype(int)
    else:
        df['RAIN_SEVERITY'] = 0
        df['PRCP'] = 0.0

    if 'EXTREME_WEATHER' not in df.columns:
        df['EXTREME_WEATHER'] = 0

    df['WEATHER_SCORE'] = df['RAIN_SEVERITY'] + df['EXTREME_WEATHER'] * 3

    if 'IS_MAJOR_HUB_ORIGIN' in df.columns and 'WEATHER_SCORE' in df.columns:
        df['HUB_WEATHER_IMPACT'] = df['IS_MAJOR_HUB_ORIGIN'] * df['WEATHER_SCORE']

    if 'IS_MORNING_PEAK' in df.columns and 'IS_EVENING_PEAK' in df.columns and 'WEATHER_SCORE' in df.columns:
        df['PEAK_WEATHER_IMPACT'] = (df['IS_MORNING_PEAK'] | df['IS_EVENING_PEAK']) * df['WEATHER_SCORE']

    return df


def create_advanced_day_features(df):
    """
    Create advanced date features, including cyclic encoding

    Args:
        df: DataFrame containing DAY, MONTH, YEAR columns

    Returns:
        DataFrame with added date features
    """
    # Create a copy to avoid modifying the original data
    df = df.copy()

    # Add DAY_NAME feature - corrected mapping, using standard date library (Mon-Sat as 1-6, Sun as 0)
    day_map = {
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday',
        0: 'Sunday'
    }

    # Add day of the week based on date information
    if all(col in df.columns for col in ['YEAR', 'MONTH', 'DAY']):
        try:
            # Create date object
            df['DATE'] = pd.to_datetime(df[['YEAR', 'MONTH', 'DAY']])

            # Extract day of the week (Python default Mon as 0, Sun as 6)
            python_weekday = df['DATE'].dt.weekday  # 0-6 (Mon-Sun)

            # Convert to desired format (Mon-Sat as 1-6, Sun as 0)
            df['DAY_OF_WEEK'] = (python_weekday + 1) % 7  # Convert to Mon=1,...,Sat=6,Sun=0

            # Add day name
            df['DAY_NAME'] = df['DAY_OF_WEEK'].map(day_map)

            # Create weekend indicator
            df['IS_WEEKEND'] = ((df['DAY_OF_WEEK'] == 6) | (df['DAY_OF_WEEK'] == 0)).astype(int)

            # Create cyclic encoding
            df['DAY_SIN'] = np.sin(2 * np.pi * df['DAY_OF_WEEK'] / 7)
            df['DAY_COS'] = np.cos(2 * np.pi * df['DAY_OF_WEEK'] / 7)

            # Weekend/weekday cycle
            df['WEEKDAY_SIN'] = np.sin(np.pi * df['IS_WEEKEND'])
            df['WEEKDAY_COS'] = np.cos(np.pi * df['IS_WEEKEND'])

            # Workweek feature (5-day cycle for weekdays)
            workday_map = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: np.nan, 0: np.nan}  # Map to 0-4
            df['WORKWEEK_DAY'] = df['DAY_OF_WEEK'].map(workday_map)

            # Fill weekends with mean workday value
            work_day_mean = 2  # Default to middle value
            df['WORKWEEK_DAY'] = df['WORKWEEK_DAY'].fillna(work_day_mean)

            # Workweek cycle
            df['WORKWEEK_SIN'] = np.sin(2 * np.pi * df['WORKWEEK_DAY'] / 5)
            df['WORKWEEK_COS'] = np.cos(2 * np.pi * df['WORKWEEK_DAY'] / 5)
        except Exception as e:
            # If unable to create date features, add default values
            df['DAY_OF_WEEK'] = 1  # Default to Monday
            df['DAY_NAME'] = 'Monday'  # Default to Monday
            df['IS_WEEKEND'] = 0
            df['DAY_SIN'] = np.sin(2 * np.pi * 1 / 7)  # Sin value for Monday
            df['DAY_COS'] = np.cos(2 * np.pi * 1 / 7)  # Cos value for Monday
            df['WEEKDAY_SIN'] = 0
            df['WEEKDAY_COS'] = 1
            df['WORKWEEK_SIN'] = np.sin(2 * np.pi * 0 / 5)  # Sin value for Monday workweek
            df['WORKWEEK_COS'] = np.cos(2 * np.pi * 0 / 5)  # Cos value for Monday workweek
    else:
        # If date columns are missing, use default values
        df['DAY_OF_WEEK'] = 1  # Default to Monday
        df['DAY_NAME'] = 'Monday'  # Default to Monday
        df['IS_WEEKEND'] = 0
        df['DAY_SIN'] = np.sin(2 * np.pi * 1 / 7)  # Sin value for Monday
        df['DAY_COS'] = np.cos(2 * np.pi * 1 / 7)  # Cos value for Monday
        df['WEEKDAY_SIN'] = 0
        df['WEEKDAY_COS'] = 1
        df['WORKWEEK_SIN'] = np.sin(2 * np.pi * 0 / 5)  # Sin value for Monday workweek
        df['WORKWEEK_COS'] = np.cos(2 * np.pi * 0 / 5)  # Cos value for Monday workweek

    return df


# Red-eye flight indicator
def create_redeye_indicator(df):
    """
    Create red-eye flight indicator (flights departing or arriving between 0-6 AM)

    Args:
        df: DataFrame containing SCH_DEP_TIME and SCH_ARR_TIME

    Returns:
        DataFrame with IS_REDEYE column added
    """
    # Create a copy to avoid modifying the original data
    df = df.copy()

    # Initialize IS_REDEYE to 0 (non-red-eye flight)
    df['IS_REDEYE'] = 0

    # Identify red-eye flights based on departure time (0-6 AM)
    if 'SCH_DEP_TIME' in df.columns:
        # Time format is HHMM (e.g., 130 = 1:30 AM, 545 = 5:45 AM)
        redeye_departure = (df['SCH_DEP_TIME'] >= 0) & (df['SCH_DEP_TIME'] < 600)
        df.loc[redeye_departure, 'IS_REDEYE'] = 1

    # Identify red-eye flights based on arrival time (0-6 AM)
    if 'SCH_ARR_TIME' in df.columns:
        redeye_arrival = (df['SCH_ARR_TIME'] >= 0) & (df['SCH_ARR_TIME'] < 600)
        df.loc[redeye_arrival, 'IS_REDEYE'] = 1

    return df


# Generate predictions (including confidence intervals) - using hardcoded RMSE values
def predict_delay(new_data, confidence=0.95):
    """
    Predict flight delay, including uncertainty estimates based on yearly RMSE

    Args:
        new_data: Input DataFrame
        confidence: Confidence level (default 0.95 for 95% CI)

    Returns:
        tuple: (delay probability, delay time, lower bound of delay time CI, upper bound of delay time CI)
    """
    # Load preprocessing and models
    year = new_data['YEAR'][0]

    preprocessor, classifier, regressor = load_artifacts(year)

    # Ensure input data contains all necessary features
    required_features = [
        'SCH_DEP_TIME', 'ORIGIN_IATA', 'DEST_IATA', 'DISTANCE', 'PRCP',
        'MONTH', 'DAY', 'YEAR', 'MKT_AIRLINE', 'EXTREME_WEATHER'
    ]
    assert all(feat in new_data.columns for feat in required_features), "Missing required features"

    # Apply the same feature engineering
    processed_data = create_redeye_indicator(new_data)
    processed_data = create_advanced_time_features(processed_data)
    processed_data = create_advanced_day_features(processed_data)
    processed_data = create_airport_features(processed_data)
    processed_data = create_weather_features(processed_data)

    # Preprocess data
    X_processed = preprocessor.transform(processed_data)
    X_tensor = torch.FloatTensor(X_processed)

    # Set models to evaluation mode
    classifier.eval()
    regressor.eval()

    # Make predictions
    with torch.no_grad():
        delay_prob = classifier(X_tensor).numpy()  # Delay probability
        delay_time = regressor(X_tensor).numpy()  # Predicted delay time in minutes

    # Get RMSE value for the year
    rmse = get_rmse(year)

    # Calculate Z value for the confidence interval
    z_value = stats.norm.ppf(1 - (1 - confidence) / 2)

    # Calculate confidence interval
    ci_lower = delay_time - z_value * rmse
    ci_upper = delay_time + z_value * rmse

    # Ensure lower bound is not negative
    ci_lower = np.maximum(ci_lower, 0)

    return delay_prob, delay_time, ci_lower, ci_upper