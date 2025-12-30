from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import joblib
import os

# Load the trained model
model_path = os.path.join(os.path.dirname(__file__), "fuel_model.pkl")
model = joblib.load(model_path)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict_fuel', methods=['POST'])
def predict_fuel():
    try:
        data = request.json

        # Handle one-hot encoding for ship_type
        ship_types = ["Cargo", "Container", "Tanker"]
        for stype in ship_types:
            data[f"ship_type_{stype}"] = 1 if data["ship_type"] == stype else 0

        # Remove original categorical field
        data.pop("ship_type", None)

        # Ensure features are in the exact same order as during model training
        feature_order = [
            "distance_km", "speed_knots", "wind_speed",
            "ocean_current", "wave_height", "load_percent",
            "ship_type_Cargo", "ship_type_Container", "ship_type_Tanker"
        ]

        # Create DataFrame with ordered features
        input_data = pd.DataFrame([[data[feature] for feature in feature_order]], columns=feature_order)

        # Predict using the model
        prediction = model.predict(input_data)[0]
        return jsonify({"predicted_fuel_liters": round(prediction, 2)})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
