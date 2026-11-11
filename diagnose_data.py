
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")

FILE = DATA_DIR / "Case_Study_Speed_Limit_SensorReadingsYearN_V100.csv"

# Read everything as text to preserve unusual entries.
df = pd.read_csv(
    FILE,
    sep=";",
    dtype=str,
    encoding="utf-8-sig",
    keep_default_na=False
)

# Remove accidental spaces around values.
for column in df.columns:
    df[column] = df[column].str.strip()

print("=== 1. BASIC INFORMATION ===")
print("Rows:", len(df))
print("Columns:", df.columns.tolist())

print("\n=== 2. EMPTY AND NULL VALUES ===")

for column in df.columns:
    invalid = df[column].str.lower().isin(
        ["", "null", "nan", "none"]
    )
    print(column, ":", invalid.sum())

print("\n=== 3. UNUSUAL MONTH VALUES ===")

print(df["Month"].value_counts(dropna=False))

print("\n=== 4. SENSOR IDS ===")

print(df["Sensor"].value_counts(dropna=False).sort_index())

print("\n=== 5. EXACT DUPLICATE ROWS ===")

print("Duplicate rows:", df.duplicated().sum())

print("\n=== 6. DUPLICATE SENSOR-HOUR RECORDS ===")

# Identifies multiple records for one sensor in one hour.
hour_columns = ["Month", "Day", "Hour", "Sensor"]

duplicates = df.duplicated(
    subset=hour_columns,
    keep=False
)

print("Rows involved:", duplicates.sum())
print(df.loc[duplicates].head(10).to_string(index=False))

print("\n=== 7. KNOWN PROBLEM LOCATIONS ===")

checks = [
    ("Sensor 18, Jan 26, hours 0-4", "18", "26", ["0", "1", "2", "3", "4"]),
    ("Sensor 15, Jan 24, hours 22-23", "15", "24", ["22", "23"]),
    ("Sensor 15, Jan 10", "15", "10", None),
    ("Sensor 4, Jan 12", "4", "12", None),
    ("Sensor 11, Jan 17, hour 9", "11", "17", ["9"]),
    ("Sensor 13, Jan 1, hours 12-14", "13", "1", ["12", "13", "14"]),
    ("Speed limit, Jan 6, hour 20", "-1", "6", ["20"]),
]

for title, sensor, day, hours in checks:
    selected = (
        (df["Sensor"] == sensor) &
        (df["Day"] == day)
    )

    if hours is not None:
        selected &= df["Hour"].isin(hours)

    result = df.loc[selected]

    print("\n", title)
    print("Matching rows:", len(result))
    print(result.head(8).to_string(index=False))


print("\n=== 8. NUMERICAL VALUE CHECK ===")

# Convert decimal commas to decimal points.
df["Value_numeric"] = pd.to_numeric(
    df["Value"].str.replace(",", ".", regex=False),
    errors="coerce"
)

# Check values that cannot be converted.
invalid_numbers = df["Value_numeric"].isna()

print("Non-numeric values:", invalid_numbers.sum())

if invalid_numbers.any():
    print(df.loc[invalid_numbers].head(10).to_string(index=False))

# Inspect numerical ranges for each sensor.
print("\n=== 9. SENSOR VALUE RANGES ===")

ranges = df.groupby("Sensor")["Value_numeric"].agg(
    ["count", "min", "max", "mean"]
)

print(ranges.to_string())

# Load Year N+1 without assuming it has a header.
year_n_plus1 = pd.read_csv(
    DATA_DIR / "Case_Study_Speed_Limit_SensorReadingsYearNPlus1_V100.csv",
    sep=";",
    header=None,
    names=["Month", "Day", "Hour", "Minute", "Second", "Sensor", "Value"],
    dtype=str,
    encoding="utf-8-sig",
    keep_default_na=False
)

for column in year_n_plus1.columns:
    year_n_plus1[column] = year_n_plus1[column].str.strip()

print("\n=== 10. YEAR N+1 BASIC CHECK ===")
print("Rows:", len(year_n_plus1))
print("Exact duplicates:", year_n_plus1.duplicated().sum())

year_n_plus1["Value_numeric"] = pd.to_numeric(
    year_n_plus1["Value"].str.replace(",", ".", regex=False),
    errors="coerce"
)

print("Non-numeric values:",
      year_n_plus1["Value_numeric"].isna().sum())

print("\n=== 11. YEAR N vs YEAR N+1 ===")

# Compare records in the original order.
same_data = df.drop(columns="Value_numeric").reset_index(drop=True).equals(
    year_n_plus1.drop(columns="Value_numeric").reset_index(drop=True)
)

print("All records identical in original order:", same_data)


print("\n=== 12. ACCIDENT DATA INVESTIGATION ===")

accidents = pd.read_csv(
    DATA_DIR / "Case_Study_Speed_Limit_AccidentsYearN_V100.csv",
    sep=";",
    encoding="utf-8-sig"
)

print("Shape:", accidents.shape)
print("Columns:", accidents.columns.tolist())

# Identify the columns describing accidents and near-accidents.
actual_columns = ["Damage", "Injured"]
near_columns = ["CloseCarCm", "CloseGuardrailCm", "SkidAngle"]

has_actual = accidents[actual_columns].notna().any(axis=1)
has_near = accidents[near_columns].notna().any(axis=1)

print("\n=== 13. EVENT CATEGORIES ===")

print("Near-accident indicators only:",
      (has_near & ~has_actual).sum())

print("Actual-accident indicators only:",
      (has_actual & ~has_near).sum())

print("Both kinds of indicators:",
      (has_actual & has_near).sum())

print("Neither kind of indicator:",
      (~has_actual & ~has_near).sum())

print("\n=== 14. ACCIDENT TIMESTAMP CHECK ===")

print("Month values:")
print(accidents["Month"].value_counts(dropna=False))

print("\nHour range:")
print("Minimum:", accidents["Hour"].min())
print("Maximum:", accidents["Hour"].max())

print("\nHours and number of records:")
print(
    accidents["Hour"]
    .value_counts(dropna=False)
    .sort_index()
    .to_string()
)

print("\n=== 15. NEAR-ACCIDENT TYPES ===")

for column in near_columns:
    print(column, ":", accidents[column].notna().sum())

print("\n=== 16. NEAR-ACCIDENTS PER DAY ===")

near_accidents = accidents.loc[has_near & ~has_actual].copy()

print(
    near_accidents.groupby("Day")
    .size()
    .to_string()
)

print("\n=== 17. DUPLICATE ACCIDENT RECORDS ===")

print("Exact duplicate records:", accidents.duplicated().sum())
