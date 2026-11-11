
def weather_router(
    illuminance_mlx: float,
    water_um: float,
    temperature_c: float
) -> bool:
    """
    Return True when the weather neural network is needed.

    SPEC1: Darkness below 500 millilux.
    SPEC2: Black ice danger when water exceeds 1000 um
           and temperature is below 0 degrees Celsius.
    """

    is_dark = illuminance_mlx < 500

    black_ice_danger = (
        water_um > 1000
        and temperature_c < 0
    )

    return is_dark or black_ice_danger


if __name__ == "__main__":

    print("=== WEATHER ROUTER TEST ===")

    print("Darkness:",
          weather_router(400, 0, 10))

    print("Normal conditions:",
          weather_router(10000, 0, 10))

    print("Black ice:",
          weather_router(10000, 1500, -5))

    print("Threshold conditions:",
          weather_router(500, 1000, 0))
