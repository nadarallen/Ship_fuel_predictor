import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
import os

# Define the feature order exactly as expected by app.py
feature_order = [
    "distance_km", "speed_knots", "wind_speed",
    "ocean_current", "wave_height", "load_percent",
    "ship_type_Cargo", "ship_type_Container", "ship_type_Tanker"
]

# Create dummy training data
data = {
    "distance_km": [100, 500, 1000],
    "speed_knots": [10, 15, 20],
    "wind_speed": [5, 10, 15],
    "ocean_current": [1, 2, 3],
    "wave_height": [0.5, 1.5, 2.5],
    "load_percent": [50, 75, 100],
    "ship_type_Cargo": [1, 0, 0],
    "ship_type_Container": [0, 1, 0],
    "ship_type_Tanker": [0, 0, 1],
    "fuel_liters": [2000, 8000, 15000]  # Dummy target values
}

df = pd.DataFrame(data)
model = LinearRegression()
model.fit(df[feature_order], df["fuel_liters"])

# Save the model to the same directory as this script
output_path = os.path.join(os.path.dirname(__file__), "fuel_model.pkl")
joblib.dump(model, output_path)
print(f"Model saved to {output_path}")