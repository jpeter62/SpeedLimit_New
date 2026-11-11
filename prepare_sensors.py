
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Load original Year N sensor readings.
readings = pd.read_csv(
    DATA_DIR / "Case_Study_Speed_Limit_SensorReadingsYearN_V100.csv",
    sep=";",
    decimal=",",
    encoding="utf-8-sig"
)

# Convert columns to numbers.
for column in ["Month", "Day", "Hour", "Sensor", "Value"]:
    readings[column] = pd.to_numeric(
        readings[column],
        errors="coerce"
    )

print("=== ORIGINAL SENSOR DATA ===")
print("Shape:", readings.shape)

# Sensor-ID choices based on inspected metadata and values.
sensor_groups = {
    "temperature_c": [15, 18, 19],
    "water_um": [1, 8, 11],
    "illuminance_lux": [2, 9, 12],
    "speed_limit": [-1]
}

# Aggregation policy for one row per hour.
aggregations = {
    "temperature_c": "min",
    "water_um": "max",
    "illuminance_lux": "min",
    "speed_limit": "first"
}

hourly_parts = []

for feature, sensor_ids in sensor_groups.items():
    subset = readings[
        readings["Sensor"].isin(sensor_ids)
    ].copy()

    hourly = (
        subset
        .groupby(["Month", "Day", "Hour"])["Value"]
        .agg(aggregations[feature])
        .reset_index(name=feature)
    )

    hourly_parts.append(hourly)

# Start with the complete January hourly timeline.
hourly_sensors = pd.MultiIndex.from_product(
    [[1], range(1, 32), range(24)],
    names=["Month", "Day", "Hour"]
).to_frame(index=False)

# Merge each feature onto the hourly timeline.
for hourly in hourly_parts:
    hourly_sensors = hourly_sensors.merge(
        hourly,
        on=["Month", "Day", "Hour"],
        how="left",
        validate="one_to_one"
    )

# Convert lux to millilux.
hourly_sensors["illuminance_mlx"] = (
    hourly_sensors["illuminance_lux"] * 1000
)

# Keep only the model inputs.
hourly_sensors = hourly_sensors[
    [
        "Month",
        "Day",
        "Hour",
        "temperature_c",
        "water_um",
        "illuminance_mlx",
        "speed_limit"
    ]
]

print("\n=== HOURLY SENSOR DATA ===")
print("Shape:", hourly_sensors.shape)

print("\nMissing values:")
print(hourly_sensors.isna().sum())

print("\nFirst 10 rows:")
print(hourly_sensors.head(10).to_string(index=False))

# Check expected sensor coverage.
assert len(hourly_sensors) == 744, (
    "Expected 744 hourly records for January."
)

# Save the prepared sensor dataset.
output_file = OUTPUT_DIR / "hourly_sensors.csv"
hourly_sensors.to_csv(output_file, index=False)

print("\nSaved to:", output_file)
