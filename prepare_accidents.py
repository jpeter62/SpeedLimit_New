
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")

OUTPUT_DIR.mkdir(exist_ok=True)

# Read the original accident records.
accidents = pd.read_csv(
    DATA_DIR / "Case_Study_Speed_Limit_AccidentsYearN_V100.csv",
    sep=";",
    encoding="utf-8-sig"
)

# Identify near-accidents using SPEC4-related fields.
near_columns = [
    "CloseCarCm",
    "CloseGuardrailCm",
    "SkidAngle"
]

actual_columns = ["Damage", "Injured"]

has_near = accidents[near_columns].notna().any(axis=1)
has_actual = accidents[actual_columns].notna().any(axis=1)

# Keep records identified only as near-accidents.
near_accidents = accidents.loc[has_near & ~has_actual].copy()

print("Near-accident records:", len(near_accidents))

# Working assumption:
# Accident hours 1-24 correspond to sensor hours 0-23.
near_accidents["SensorHour"] = near_accidents["Hour"] - 1

# Count near-accidents for each day and hour.
hourly_counts = (
    near_accidents
    .groupby(["Month", "Day", "SensorHour"])
    .size()
    .reset_index(name="near_accident_count")
)

# Create a complete January hourly timeline.
all_hours = pd.MultiIndex.from_product(
    [[1], range(1, 32), range(24)],
    names=["Month", "Day", "SensorHour"]
).to_frame(index=False)

# Join counts onto the complete timeline.
hourly_data = all_hours.merge(
    hourly_counts,
    on=["Month", "Day", "SensorHour"],
    how="left",
    validate="one_to_one"
)

# No recorded event means zero recorded near-accidents.
hourly_data["near_accident_count"] = (
    hourly_data["near_accident_count"]
    .fillna(0)
    .astype(int)
)

# Save the result.
output_file = OUTPUT_DIR / "hourly_near_accidents.csv"
hourly_data.to_csv(output_file, index=False)

print("\n=== HOURLY NEAR-ACCIDENT DATA ===")
print("Shape:", hourly_data.shape)
print("Total near-accidents:", hourly_data["near_accident_count"].sum())
print("Hours with zero near-accidents:",
      (hourly_data["near_accident_count"] == 0).sum())

print("\nFirst 10 rows:")
print(hourly_data.head(10).to_string(index=False))

print("\nSaved to:", output_file)
