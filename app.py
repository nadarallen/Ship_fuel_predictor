from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import joblib
import os

import numpy as np

# Load the trained model and feature columns
model_path = os.path.join(os.path.dirname(__file__), "fuel_model.pkl")
model = joblib.load(model_path)
features_path = os.path.join(os.path.dirname(__file__), "model_features.pkl")
model_features = joblib.load(features_path)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict_fuel', methods=['POST'])
def predict_fuel():
    try:
        data = request.json

        # Prepare input dictionary with default 0s
        input_data = {feature: 0 for feature in model_features}

        # map frontend inputs to model features
        input_data['engine_power_kw'] = float(data.get('engine_power_kw', 0))
        input_data['sfoc'] = float(data.get('sfoc', 0))
        input_data['cargo_load_pct'] = float(data.get('cargo_load_pct', 0))
        input_data['avg_speed_knots'] = float(data.get('avg_speed_knots', 0))
        input_data['distance_nm'] = float(data.get('distance_nm', 0))
        input_data['wave_height_m'] = float(data.get('wave_height_m', 0))
        input_data['wind_speed_mps'] = float(data.get('wind_speed_mps', 0))
        input_data['current_speed_mps'] = float(data.get('current_speed_mps', 0))
        input_data['monsoon_season'] = int(data.get('monsoon_season', 0)) # 0 or 1

        # Handle ship_type one-hot encoding
        ship_type = data.get('ship_type', '')
        ship_type_feature = f"ship_type_{ship_type}"
        if ship_type_feature in input_data:
            input_data[ship_type_feature] = 1

        # Create DataFrame with ordered features
        input_df = pd.DataFrame([input_data])
        
        # Predict using the model (Output is Log(Tons))
        prediction_log = model.predict(input_df)[0]
        # Inverse transform: exp(x) - 1
        prediction_tons = np.expm1(prediction_log)
        
        return jsonify({"predicted_fuel_tons": round(prediction_tons, 2)})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
