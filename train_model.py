import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
import numpy as np

# Load the dataset
# Load the dataset
# Check if augmented data exists, else generate it
augmented_csv = os.path.join(os.path.dirname(__file__), "augmented_fuel_data.csv")
original_csv = os.path.join(os.path.dirname(__file__), "synthetic_ship_fuel_indian_ocean.csv")

if not os.path.exists(augmented_csv):
    print("Augmented data not found. Generating from original + synthetic short trips...")
    if not os.path.exists(original_csv):
        print(f"Error: Original data {original_csv} not found.")
        exit(1)
        
    df_orig = pd.read_csv(original_csv)
    
    # --- Augmentation Logic Start ---
    # Generate Physics-Based Short Trips (10-300 NM)
    # See augment_data.py (now merged)
    N_NEW = 2000
    new_data = []
    ship_types = ['Bulk Carrier', 'Container', 'Tanker']
    
    for _ in range(N_NEW):
        distance = np.random.uniform(10, 300)
        speed = np.random.uniform(8, 20)
        power = np.random.uniform(5000, 30000)
        sfoc = np.random.uniform(160, 190)
        
        # Physics Calculation
        time_h = distance / speed
        base_fuel = (power * sfoc * time_h) / 1_000_000
        
        # Add realistic variability (1.05x to 1.25x penalty)
        penalty = np.random.uniform(1.05, 1.25)
        final_fuel = base_fuel * penalty
        
        row = {
            'ship_type': np.random.choice(ship_types),
            'engine_power_kw': round(power, 2),
            'sfoc': round(sfoc, 2),
            'cargo_load_pct': round(np.random.uniform(50, 100), 2),
            'avg_speed_knots': round(speed, 2),
            'distance_nm': round(distance, 2),
            'wave_height_m': round(np.random.uniform(0.5, 3), 2),
            'wind_speed_mps': round(np.random.uniform(2, 10), 2),
            'current_speed_mps': round(np.random.uniform(0, 1.5), 2),
            'monsoon_season': np.random.choice([0, 1], p=[0.7, 0.3]),
            'fuel_consumption_tons': round(final_fuel, 4)
        }
        new_data.append(row)
        
    df_new = pd.DataFrame(new_data)
    df = pd.concat([df_orig, df_new], ignore_index=True)
    
    # Shuffle and Save
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df.to_csv(augmented_csv, index=False)
    print(f"✅ Generated and saved {augmented_csv} ({len(df)} rows)")
    
else:
    print(f"Loading existing augmented data: {augmented_csv}")
    df = pd.read_csv(augmented_csv)

# Separate features and target
X = df.drop("fuel_consumption_tons", axis=1)
y = np.log1p(df["fuel_consumption_tons"]) # Log-transform target to prevent negative predictions

# One-hot encode ship_type (categorical)
X = pd.get_dummies(X, columns=["ship_type"])

# Save the feature columns order for the app to use protection against drift
feature_columns = X.columns.tolist()
joblib.dump(feature_columns, "model_features.pkl")

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the model (Using best parameters found from previous Grid Search to save time, or we can keep the search)
# To be robust for future data updates, we'll keep the Grid Search but maybe reduce scope if it's too slow.
# For now, let's keep the full search as it ensures best quality.
gb_model = GradientBoostingRegressor(random_state=42)

param_grid = {
    'n_estimators': [100, 200, 300],
    'learning_rate': [0.01, 0.05, 0.1],
    'max_depth': [3, 4, 5],
    'min_samples_split': [2, 5],
    'subsample': [0.8, 1.0]
}

print(f"Starting Training & Grid Search...")
grid_search = GridSearchCV(estimator=gb_model, param_grid=param_grid, 
                           cv=3, n_jobs=-1, verbose=1, scoring='neg_mean_absolute_error')

grid_search.fit(X_train, y_train)

# Get best model
best_model = grid_search.best_estimator_
print(f"Best Parameters: {grid_search.best_params_}")

# Evaluate
y_pred_log = best_model.predict(X_test)
predictions = np.expm1(y_pred_log) # Inverse transform
y_test_orig = np.expm1(y_test)

mae = mean_absolute_error(y_test_orig, predictions)
r2 = r2_score(y_test_orig, predictions)
mape = np.mean(np.abs((y_test_orig - predictions) / y_test_orig)) * 100

print("-" * 30)
print("Model Performance")
print("-" * 30)
print(f"MAE: {mae:.2f} Tons")
print(f"MAPE: {mape:.2f}%")
print(f"R2 Score: {r2:.5f}")
print("-" * 30)

# Save the model
output_path = os.path.join(os.path.dirname(__file__), "fuel_model.pkl")
joblib.dump(best_model, output_path)
print(f"✅ Model saved as 'fuel_model.pkl'")