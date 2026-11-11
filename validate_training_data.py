
from pathlib import Path
import pandas as pd

FILE = Path("output/training_data.csv")

df = pd.read_csv(FILE)

print("=== 1. DATASET SHAPE ===")
print(df.shape)

print("\n=== 2. MISSING VALUES ===")
print(df.isna().sum().to_string())

print("\n=== 3. DUPLICATE HOURS ===")
duplicate_hours = df.duplicated(
    subset=["Month", "Day", "Hour"]
)
print("Duplicate hours:", duplicate_hours.sum())

print("\n=== 4. VALID DATE AND HOUR VALUES ===")
print("Months:", sorted(df["Month"].unique()))
print("Days:", df["Day"].min(), "to", df["Day"].max())
print("Hours:", df["Hour"].min(), "to", df["Hour"].max())

print("\n=== 5. SENSOR FEATURE RANGES ===")

feature_columns = [
    "temperature_c",
    "water_um",
    "illuminance_mlx",
    "speed_limit"
]

print(
    df[feature_columns]
    .agg(["min", "max", "mean"])
    .to_string()
)

print("\n=== 6. PHYSICAL RANGE CHECKS ===")

checks = {
    "temperature_c": (-30, 70),
    "water_um": (0, 10000),
    "illuminance_mlx": (0, 1000000000),
}

for column, (minimum, maximum) in checks.items():
    invalid = (
        (df[column] < minimum)
        | (df[column] > maximum)
    )

    print(column, "outside range:", invalid.sum())

print("\n=== 7. SPEED LIMIT VALUES ===")
print(df["speed_limit"].value_counts().sort_index())

print("\n=== 8. NEAR-ACCIDENT COUNTS ===")

print("Minimum:", df["near_accident_count"].min())
print("Maximum:", df["near_accident_count"].max())
print("Total:", df["near_accident_count"].sum())

print("\nCount distribution:")
print(
    df["near_accident_count"]
    .value_counts()
    .sort_index()
)

print("\n=== 9. DATA ORDER ===")

sorted_df = df.sort_values(
    ["Month", "Day", "Hour"]
).reset_index(drop=True)

print("Already chronological:", df.equals(sorted_df))

print("\n=== 10. FINAL BASIC CHECKS ===")

assert len(df) == 744
assert not df.isna().any().any()
assert not duplicate_hours.any()
assert df["near_accident_count"].sum() == 964
assert (df["near_accident_count"] >= 0).all()

print("Basic checks passed!")
