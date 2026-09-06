import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

# Load historical weather data
df = pd.read_csv("data/weather.csv")

# Features
features = [
    "temperature",
    "humidity",
    "wind_speed"
]

X = df[features]
y = df["rainfall"]

# Create model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

# Train model
model.fit(X, y)

# Save trained model
joblib.dump(model, "rainfall_model.pkl")

print("✅ Rainfall model trained and saved successfully!")