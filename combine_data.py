
from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path("output")

# 1. Load the two prepared datasets
sensors = pd.read_csv(
    OUTPUT_DIR / "hourly_sensors.csv"
)

accidents = pd.read_csv(
    OUTPUT_DIR / "hourly_near_accidents.csv"
)

print("=== INPUT DATASETS ===")
print("Hourly sensors:", sensors.shape)
print("Hourly near-accidents:", accidents.shape)

# 2. Rename accident hour to match sensor hour
accidents = accidents.rename(
    columns={"SensorHour": "Hour"}
)

# 3. Columns used to match the records
join_columns = ["Month", "Day", "Hour"]

# Check that each hour occurs only once
assert not sensors.duplicated(join_columns).any()
assert not accidents.duplicated(join_columns).any()

# 4. Merge sensors with accident counts
training_data = sensors.merge(
    accidents,
    on=join_columns,
    how="left",
    validate="one_to_one",
    indicator=True
)

# 5. Check that every hour was matched
print("\n=== MERGE CHECK ===")
print(training_data["_merge"].value_counts())

assert (training_data["_merge"] == "both").all(), (
    "Some sensor hours have no matching accident record."
)

training_data = training_data.drop(columns=["_merge"])

# 6. Select the final columns
training_data = training_data[
    [
        "Month",
        "Day",
        "Hour",
        "temperature_c",
        "water_um",
        "illuminance_mlx",
        "speed_limit",
        "near_accident_count"
    ]
]

# 7. Validate the result
print("\n=== VALIDATION ===")

print("Shape:", training_data.shape)

print("\nMissing values:")
print(training_data.isna().sum())

print("\nTotal near-accidents:",
      training_data["near_accident_count"].sum())

print("Hours with zero near-accidents:",
      (training_data["near_accident_count"] == 0).sum())

assert len(training_data) == 744
assert not training_data.isna().any().any()
assert training_data["near_accident_count"].sum() == 964
assert (training_data["near_accident_count"] >= 0).all()

# 8. Save the combined dataset
file_path = OUTPUT_DIR / "training_data.csv"

training_data.to_csv(file_path, index=False)

print("\n=== FIRST 10 ROWS ===")
print(training_data.head(10).to_string(index=False))

print("\nSaved to:", file_path)
