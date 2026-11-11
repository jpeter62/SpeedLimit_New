
from pathlib import Path

import joblib
import pandas as pd

from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# ----------------------------------
# 1. Load the prepared data
# ----------------------------------

df = pd.read_csv("output/training_data.csv")

FEATURES = [
    "temperature_c",
    "water_um",
    "illuminance_mlx",
    "speed_limit"
]

TARGET = "near_accident_count"

# ----------------------------------
# 2. Chronological data split
# ----------------------------------

train_data = df[df["Day"] <= 20]
val_data = df[(df["Day"] >= 21) & (df["Day"] <= 24)]
test_data = df[df["Day"] >= 25]

X_train = train_data[FEATURES]
y_train = train_data[TARGET]

X_val = val_data[FEATURES]
y_val = val_data[TARGET]

X_test = test_data[FEATURES]
y_test = test_data[TARGET]

print("=== DATA SPLIT ===")
print("Training:", len(X_train))
print("Validation:", len(X_val))
print("Testing:", len(X_test))

# ----------------------------------
# 3. Baseline
# ----------------------------------

baseline = DummyRegressor(strategy="mean")
baseline.fit(X_train, y_train)

baseline_val_mae = mean_absolute_error(
    y_val,
    baseline.predict(X_val)
)

print("\n=== BASELINE ===")
print("Validation MAE:", round(baseline_val_mae, 3))

# ----------------------------------
# 4. Compare two neural networks
# ----------------------------------

architectures = [
    (32, 16),
    (8,)
]

best_model = None
best_architecture = None
best_val_mae = float("inf")

print("\n=== NEURAL NETWORK COMPARISON ===")

for architecture in architectures:

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("neural_network", MLPRegressor(
            hidden_layer_sizes=architecture,
            activation="relu",
            solver="adam",
            max_iter=2000,
            random_state=42
        ))
    ])

    model.fit(X_train, y_train)

    val_predictions = model.predict(X_val)

    val_mae = mean_absolute_error(
        y_val,
        val_predictions
    )

    print(
        f"Architecture {architecture}: "
        f"Validation MAE = {val_mae:.3f}"
    )

    if val_mae < best_val_mae:
        best_val_mae = val_mae
        best_model = model
        best_architecture = architecture

print("\n=== SELECTED MODEL ===")
print("Architecture:", best_architecture)
print("Validation MAE:", round(best_val_mae, 3))

# ----------------------------------
# 5. Refit using training + validation
# ----------------------------------

X_train_final = pd.concat([X_train, X_val])
y_train_final = pd.concat([y_train, y_val])

final_model = Pipeline([
    ("scaler", StandardScaler()),
    ("neural_network", MLPRegressor(
        hidden_layer_sizes=best_architecture,
        activation="relu",
        solver="adam",
        max_iter=2000,
        random_state=42
    ))
])

final_model.fit(X_train_final, y_train_final)

# ----------------------------------
# 6. Evaluate on the testing period
# ----------------------------------

test_predictions = final_model.predict(X_test)

test_mae = mean_absolute_error(
    y_test,
    test_predictions
)

baseline_final = DummyRegressor(strategy="mean")
baseline_final.fit(X_train_final, y_train_final)

baseline_test_mae = mean_absolute_error(
    y_test,
    baseline_final.predict(X_test)
)

print("\n=== TEST EVALUATION ===")
print("Baseline test MAE:", round(baseline_test_mae, 3))
print("Neural network test MAE:", round(test_mae, 3))

print(
    "Negative NN predictions:",
    (test_predictions < 0).sum()
)

# ----------------------------------
# 7. Save the selected model
# ----------------------------------

Path("models").mkdir(exist_ok=True)

joblib.dump(
    final_model,
    "models/weather_model.joblib"
)

print("\nSaved: models/weather_model.joblib")
