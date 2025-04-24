from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import pandas as pd
from pred_cancelled_prob import predict_flight_cancellation, get_airport_distance
from pred_dep_delay import predict_delay
from pred_arr_delay import predict_arrival_delay

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

@app.route('/run-python', methods=['POST'])
def run_python():
    try:
        data = request.json
        logging.debug(f"Received data: {data}")
        user_input = data.get('input', '')
        output = f"{user_input.replace(',', ' >> ')}"
        return jsonify({'output': output})
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/predict-cancellation', methods=['POST'])
def predict_cancellation():
    try:
        flight_data = request.json.get('flightData', {})
        
        distance = flight_data.get('distance', 0)
        if distance == 0:
            distance = get_airport_distance(flight_data.get('from', ''), flight_data.get('to', ''))
            logging.debug(f"Distance calculated from function: {distance}")
        else:
            logging.debug(f"Using distance provided by frontend: {distance}")
        
        airline_code = flight_data.get('airline', '')
        if not airline_code and flight_data.get('flightNumber', ''):
            airline_code = flight_data.get('flightNumber', '')[:2]
        if not airline_code:
            airline_code = "DL"
        
        extreme_weather = int(flight_data.get('extremeWeather', 0))
        rainfall = float(flight_data.get('rainfall', 0.0))
        
        year = int(flight_data.get('year', 2024))
        if year > 2024:
            year = 2024
        month = 1
        day = 1
        
        if flight_data.get('time'):
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(flight_data.get('time').replace('Z', '+00:00'))
                month = dt.month
                day = dt.day
            except Exception as e:
                logging.warning(f"无法从时间字符串解析月/日: {e}")
        
        prediction_data = {
            "YEAR": year,
            "WEEK": int(flight_data.get('week', 1)),
            "MKT_AIRLINE": airline_code,
            "ORIGIN_IATA": flight_data.get('from', ''),
            "DEST_IATA": flight_data.get('to', ''),
            "DISTANCE": distance,
            "DEP_TIME": float(flight_data.get('depTime', 0)),
            "EXTREME_WEATHER": extreme_weather,
            "PRCP": rainfall
        }
        
        logging.debug(f"预测输入数据: {prediction_data}")
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        available_years = [2021, 2022, 2023, 2024]
        
        if year in available_years:
            model_year = year
        else:
            available_years.sort()
            model_year = min(available_years, key=lambda x: abs(x - year))
            logging.debug(f"No model for year {year}, using closest available model from {model_year}")
        
        model_path = os.path.normpath(os.path.join(current_dir, f"../../models/cancelled_prob/May{model_year}_model.joblib"))
        
        result = predict_flight_cancellation(model_path, prediction_data)
        
        result['model_input'] = prediction_data
        
        dep_time = float(prediction_data.get('DEP_TIME', 0))
        is_redeye = 0
        if 0 <= dep_time < 600:
            is_redeye = 1
        result['model_input']['IS_REDEYE'] = is_redeye
        
        delay_data = pd.DataFrame({
            'SCH_DEP_TIME': [dep_time],
            'ORIGIN_IATA': [prediction_data["ORIGIN_IATA"]],
            'DEST_IATA': [prediction_data["DEST_IATA"]],
            'DISTANCE': [distance],
            'PRCP': [rainfall],
            'MONTH': [month],
            'DAY': [day],
            'YEAR': [year],
            'MKT_AIRLINE': [airline_code],
            'EXTREME_WEATHER': [extreme_weather]
        })
        
        try:
            delay_probs, delay_times, ci_lower, ci_upper = predict_delay(delay_data)
            
            result['delay_probability'] = float(delay_probs[0][0])
            result['predicted_delay_minutes'] = float(delay_times[0][0])
            result['delay_confidence_interval'] = {
                'lower': float(ci_lower[0][0]),
                'upper': float(ci_upper[0][0])
            }
            
            logging.debug(f"延误概率: {result['delay_probability']:.4f}")
            logging.debug(f"预测延误: {result['predicted_delay_minutes']:.1f} 分钟")
            logging.debug(f"延误置信区间: [{result['delay_confidence_interval']['lower']:.1f}, {result['delay_confidence_interval']['upper']:.1f}] 分钟")
            
            try:
                arr_delay_input = {
                    'SCH_DEP_TIME': float(prediction_data.get('DEP_TIME', 0)),
                    'ORIGIN_IATA': prediction_data['ORIGIN_IATA'],
                    'DEST_IATA': prediction_data['DEST_IATA'],
                    'DISTANCE': distance,
                    'PRCP': rainfall,
                    'MONTH': month,
                    'DAY': day,
                    'YEAR': year,
                    'MKT_AIRLINE': airline_code,
                    'EXTREME_WEATHER': extreme_weather,
                    'WEEK': prediction_data['WEEK'],
                    'DEP_DELAY': float(delay_times[0][0])
                }
                
                arr_delay_model_dir = os.path.normpath(os.path.join(current_dir, "../../models/arr_delay_rf_models"))
                
                arr_delay_result = predict_arrival_delay(arr_delay_model_dir, arr_delay_input, year=model_year)
                
                if "error" not in arr_delay_result:
                    result['arrival_delay'] = {
                        'predicted': arr_delay_result['delay_predicted'],
                        'probability': float(arr_delay_result['delay_probability']),
                        'minutes': float(arr_delay_result['delay_minutes']),
                        'confidence_interval': {
                            'lower': float(arr_delay_result['delay_lower_bound']),
                            'upper': float(arr_delay_result['delay_upper_bound'])
                        },
                        'is_weekend': arr_delay_result['is_weekend'],
                        'is_late_night_arrival': arr_delay_result['is_late_night_arrival'],
                        'is_morning_rush': arr_delay_result['is_morning_rush'],
                        'is_evening_rush': arr_delay_result['is_evening_rush']
                    }
                    logging.debug(f"到达延迟概率: {result['arrival_delay']['probability']:.4f}")
                    logging.debug(f"预测到达延迟: {result['arrival_delay']['minutes']:.1f} 分钟")
                    logging.debug(f"到达延迟置信区间: [{result['arrival_delay']['confidence_interval']['lower']:.1f}, {result['arrival_delay']['confidence_interval']['upper']:.1f}] 分钟")
                else:
                    logging.warning(f"到达延迟预测错误: {arr_delay_result['error']}")
                    result['arrival_delay_error'] = arr_delay_result['error']
                
            except Exception as e:
                logging.error(f"到达延迟预测错误: {e}")
                result['arrival_delay_error'] = str(e)
            
        except Exception as e:
            logging.error(f"延误预测错误: {e}")
            result['delay_error'] = str(e)
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"预测错误: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

