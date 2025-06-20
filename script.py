import requests

url = "http://127.0.0.1:5000/predict_fuel"

data = {
    "distance_km": 500,
    "speed_knots": 16,
    "wind_speed": 5,
    "ocean_current": 1.2,
    "wave_height": 1.5,
    "load_percent": 75,
    "ship_type": "Cargo"
}

response = requests.post(url, json=data)
print(response.json())
