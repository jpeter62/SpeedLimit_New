
from pathlib import Path

import joblib
import pandas as pd

from router import weather_router

MODEL_PATH = Path("models/weather_model.joblib")

FEATURES = [
    "temperature_c",
    "water_um",
    "illuminance_mlx",
    "speed_limit"
]


def predict_near_accidents(
    temperature_c: float,
    water_um: float,
    illuminance_mlx: float,
    speed_limit: float
) -> float:
    """
    Predict near-accidents per hour using our trained neural network.
    """

    # Load the trained model and scaler
    model = joblib.load(MODEL_PATH)

    # Prepare input with the same feature names as training
    input_data = pd.DataFrame(
        [[temperature_c, water_um, illuminance_mlx, speed_limit]],
        columns=FEATURES
    )

    # Make prediction
    prediction = model.predict(input_data)[0]

    # Negative near-accident counts are impossible
    return max(0.0, float(prediction))


def choose_weather_speed(
    temperature_c: float,
    water_um: float,
    illuminance_mlx: float
):
    """
    Compare candidate speed limits using the neural network.

    Returns the highest candidate meeting the model target,
    or None if no candidate meets it.
    """

    candidate_speeds = [80, 70, 60, 50, 40]

    predictions = {}

    for speed in candidate_speeds:
        predicted_count = predict_near_accidents(
            temperature_c,
            water_um,
            illuminance_mlx,
            speed
        )

        predictions[speed] = predicted_count

    for speed in candidate_speeds:
        if predictions[speed] <= 1.0:
            return speed, predictions

    return None, predictions


def recommend_weather_speed(
    temperature_c: float,
    water_um: float,
    illuminance_mlx: float
):
    """
    Decide whether a weather-related speed reduction is needed.

    Returns a decision with a status, speed and message.
    """

    needs_nn = weather_router(
        illuminance_mlx,
        water_um,
        temperature_c
    )

    # REQ3: Normal conditions -> default 80 km/h
    # Air quality will be checked separately.
    if not needs_nn:
        return {
            "status": "normal",
            "speed": 80,
            "message": "No weather-related reduction required."
        }

    # REQ1: Dangerous conditions -> evaluate the NN
    selected_speed, predictions = choose_weather_speed(
        temperature_c,
        water_um,
        illuminance_mlx
    )

    # No candidate satisfies the model threshold
    if selected_speed is None:
        return {
            "status": "review_required",
            "speed": None,
            "predictions": predictions,
            "message": (
                "No candidate meets the predicted target. "
                "Human review is required."
            )
        }

    # A candidate satisfies the model threshold
    return {
        "status": "candidate_found",
        "speed": selected_speed,
        "predictions": predictions,
        "message": (
            "Candidate found by the experimental model. "
            "Safety is not guaranteed."
        )
    }


if __name__ == "__main__":

 

    print("=== SPEEDLIMIT INFERENCE TEST ===")

    temperature = -5.0
    water = 1500.0
    illuminance = 200.0
    speed = 60.0

    # Check if neural network should be activated
    needs_nn = weather_router(
        illuminance,
        water,
        temperature
    )

    print("Weather NN needed:", needs_nn)

    if needs_nn:
        prediction = predict_near_accidents(
            temperature,
            water,
            illuminance,
            speed
        )

        print(
            "Predicted near-accidents/hour:",
            round(prediction, 3)
        )
    else:
        print("Normal conditions: Weather NN not required.")

    print("\n=== SPEED COMPARISON ===")

    selected_speed, speed_predictions = choose_weather_speed(
        temperature,
        water,
        illuminance
    )

    for speed, predicted in speed_predictions.items():
        print(
            f"{speed} km/h: "
            f"{predicted:.3f} predicted near-accidents/hour"
        )

    if selected_speed is not None:
        print("Selected speed:", selected_speed, "km/h")
    else:
        print("No candidate speed meets the model target.")

    print("\n=== FINAL WEATHER DECISION TEST ===")

    decision = recommend_weather_speed(
        temperature,
        water,
        illuminance
    )

    print("Status:", decision["status"])
    print("Speed:", decision["speed"])
    print("Message:", decision["message"])
        
