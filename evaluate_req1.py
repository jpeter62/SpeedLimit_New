
import pandas as pd
import joblib

from router import weather_router

# Load our trained neural network
model = joblib.load("models/weather_model.joblib")

# Load the prepared hourly dataset
df = pd.read_csv("output/training_data.csv")

FEATURES = [
    "temperature_c",
    "water_um",
    "illuminance_mlx",
    "speed_limit"
]

# Identify dangerous hours using SPEC1 and SPEC2
dangerous = df[
    (df["illuminance_mlx"] < 500)
    |
    (
        (df["water_um"] > 1000)
        & (df["temperature_c"] < 0)
    )
].copy()

print("=== REQ1 EVALUATION ===")
print("Dangerous hours:", len(dangerous))

print("\n=== CANDIDATE SPEED COMPARISON ===")

for speed in [80, 70, 60, 50, 40]:

    conditions = dangerous[FEATURES].copy()

    # Evaluate the same historical weather conditions
    # with a hypothetical fixed speed limit
    conditions["speed_limit"] = speed

    predictions = model.predict(conditions)

    # Accident counts cannot be negative
    predictions = predictions.clip(min=0)

    average = predictions.mean()

    print(
        f"{speed} km/h: "
        f"{average:.3f} predicted near-accidents/hour"
    )

    if average <= 1:
        print("  Model average meets REQ1 threshold")
    else:
        print("  Model average exceeds REQ1 threshold")

print("\nHistorical dangerous-condition average:")
print(round(dangerous["near_accident_count"].mean(), 3))

print("\n=== HISTORICAL SPEED ANALYSIS ===")

historical = dangerous.groupby("speed_limit")[
    "near_accident_count"
].agg(["count", "mean", "min", "max"])

print(historical.to_string())

print("\n=== TRAINING AND TESTING PERIODS ===")

for name, subset in [
    ("Training period", dangerous[dangerous["Day"] <= 24]),
    ("Testing period", dangerous[dangerous["Day"] >= 25])
]:
    print("\n" + name)
    print("Dangerous hours:", len(subset))
    print(
        "Historical average near-accidents:",
        round(subset["near_accident_count"].mean(), 3)    )
