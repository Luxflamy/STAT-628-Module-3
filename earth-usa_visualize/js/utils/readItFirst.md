# Core logic
## 1. example.js
It uses `pred_arr_delay.py`, `pred_cancelled_prob.py`, and `pred_dep_delay.py` to predict the delay and cancellation probability of the flight.

## 2. pred_dep_delay.py
Defines machine learning models (e.g., ResNet-based) to predict departure delay probabilities and delay durations. Includes advanced feature engineering for time, weather, and airport data.

## 3. pred_arr_delay.py
Handles arrival delay predictions using similar logic to departure delay, focusing on arrival-specific features.

## 4. pred_cancelled_prob.py
Calculates the probability of flight cancellations based on factors like weather, airline, and airport conditions.


