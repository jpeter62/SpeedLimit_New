
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")

# 1. Load sensor descriptions
sensors = pd.read_csv(
    DATA_DIR / "Case_Study_Speed_Limit_Sensors_V100.csv",
    sep=";",
    encoding="utf-8-sig"
)

# 2. Load sensor types
sensor_types = pd.read_csv(
    DATA_DIR / "Case_Study_Speed_Limit_SensorTypes_V100.csv",
    sep=";",
    encoding="utf-8-sig"
)

# 3. Load Year N readings
year_n = pd.read_csv(
    DATA_DIR / "Case_Study_Speed_Limit_SensorReadingsYearN_V100.csv",
    sep=";",
    decimal=",",
    encoding="utf-8-sig"
)

# 4. Load Year N+1 readings (no header)
year_n_plus1 = pd.read_csv(
    DATA_DIR / "Case_Study_Speed_Limit_SensorReadingsYearNPlus1_V100.csv",
    sep=";",
    decimal=",",
    header=None,
    names=["Month", "Day", "Hour", "Minute", "Second", "Sensor", "Value"],
    encoding="utf-8-sig"
)

# 5. Load accident records
accidents_n = pd.read_csv(
    DATA_DIR / "Case_Study_Speed_Limit_AccidentsYearN_V100.csv",
    sep=";",
    encoding="utf-8-sig"
)

accidents_n_plus1 = pd.read_csv(
    DATA_DIR / "AccidentsYearNPlus1_V100.csv",
    sep=";",
    encoding="utf-8-sig"
)

# 6. Print the shapes
print("\n=== DATASET SHAPES ===")

datasets = {
    "Sensors": sensors,
    "Sensor Types": sensor_types,
    "Sensor Readings Year N": year_n,
    "Sensor Readings Year N+1": year_n_plus1,
    "Accidents Year N": accidents_n,
    "Accidents Year N+1": accidents_n_plus1
}

for name, df in datasets.items():
    print(f"{name}: {df.shape}")

# 7. Inspect sensor IDs
print("\n=== SENSOR DESCRIPTIONS ===")
print(sensors.to_string(index=False))

# 8. Inspect sensor types
print("\n=== SENSOR TYPES ===")
print(sensor_types.to_string(index=False))

# 9. Inspect which sensor IDs have readings
print("\n=== SENSOR READING COUNTS (YEAR N) ===")
print(year_n["Sensor"].value_counts(dropna=False).sort_index())

# 10. Check missing sensor IDs
described_ids = set(sensors["SensorID"])
reading_ids = set(year_n["Sensor"].dropna())

print("\n=== MISSING SENSOR INFORMATION ===")
print("Described but no readings:",
      sorted(described_ids - reading_ids))

print("Readings but no description:",
      sorted(reading_ids - described_ids - {-1}))

print("\nSpecial speed-limit sensor (-1):",
      (year_n["Sensor"] == -1).sum(), "readings")
