
import pandas as pd

# Load prepared training data
df = pd.read_csv("output/training_data.csv")

# Professor's SPEC1: Darkness
dark = df["illuminance_mlx"] < 500

# Professor's SPEC2: Black ice danger
black_ice = (
    (df["water_um"] > 1000) &
    (df["temperature_c"] < 0)
)

# REQ1: Neural network needed
dangerous = dark | black_ice

print("=== WEATHER CONDITIONS ===")
print("Total hours:", len(df))
print("Dark hours:", dark.sum())
print("Black ice danger hours:", black_ice.sum())
print("Hours with both conditions:", (dark & black_ice).sum())
print("Hours requiring NN:", dangerous.sum())
print("Hours not requiring NN:", (~dangerous).sum())

print("\n=== NEAR-ACCIDENT ANALYSIS ===")

for name, condition in [
    ("Darkness", dark),
    ("Black ice danger", black_ice),
    ("Dangerous conditions", dangerous),
    ("Normal conditions", ~dangerous)
]:
    subset = df.loc[condition]

    print("\n" + name)
    print("Number of hours:", len(subset))
    print("Total near-accidents:",
          subset["near_accident_count"].sum())

    if len(subset) > 0:
        average = subset["near_accident_count"].mean()
        print("Average near-accidents/hour:", round(average, 3))
    else:
        print("Average: N/A (no observations)")
