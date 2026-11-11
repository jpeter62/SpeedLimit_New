# SpeedLimit — Project Progress Report
**Review snapshot:** 11 November 2026  
**Status:** Prototype in progress, not production-ready. Results below come from reported local terminal runs, not an independent audit.

## Project goal
- **REQ1:** Under darkness or black-ice conditions, reduce the speed limit to achieve **at most 1 near-accident per hour on average**.
- **REQ2:** When poor air quality is predicted, reduce the speed limit appropriately.
- **REQ3:** Otherwise the default is **80 km/h**.
- **SPEC1:** Dark if illuminance < 500 millilux.
- **SPEC2:** Black-ice danger if road water > 1,000 µm **and** temperature < 0°C.
- **SPEC3:** Learn associations between weather, historical speed limit and near-accidents using a neural network.
- **SPEC4:** Near accident = skidding or getting too close to another car or guardrail.

## What has been implemented
| Component | File(s) | Status |
|---|---|---|
| Inspect six CSV datasets | `data_preparation.py` | Executed |
| Diagnose sensor/accident data issues | `diagnose_data.py` | Executed |
| Aggregate near accidents by hour | `prepare_accidents.py` | Executed |
| Aggregate sensor measurements by hour | `prepare_sensors.py` | Executed |
| Merge hourly datasets | `combine_data.py` | Executed |
| Check missing values, ranges, duplicate hours | `validate_training_data.py` | Executed |
| Darkness and black-ice analysis | `analyze_conditions.py` | Executed |
| Weather-condition router | `router.py` | Four manual examples passed |
| Train and compare MLP architectures | `train.py` | Executed |
| Saved scikit-learn pipeline | `models/weather_model.joblib` | Generated |
| Weather inference + experimental candidate speeds | `inference.py` | Executed |
| REQ1 exploratory evaluation | `evaluate_req1.py` | Executed |
| UML, cleaning and deployment notes | `docs/` | Drafted |
| Air-quality API, LLM, working Streamlit interface | Pending | Not demonstrated |
| Automated pytest suite + five app demos | Pending | Not completed |

## Data preparation findings
- 18 sensor descriptions; 9 type descriptions; 12,648 readings per supplied sensor-reading year; 997 Year N and 844 Year N+1 accident records.
- Year N+1 sensor file had no header. Files used semicolon separators and decimal commas. Parsed Year N / Year N+1 sensor records were reported identical.
- `T` means both traffic and temperature. Sensor 19 had readings but no description, provisionally treated as temperature. Sensors 7, 10 and 17 had descriptions but no readings. ID `-1` represented the speed limit.
- Investigated professor's dated anomalies; many were not reproduced in the supplied Year N V100 file. Selected raw reading checks found no empty fields or exact/within-sensor-hour duplicates.
- Accident categories: 964 near-accident-only, 32 accident-only, 1 unclassified. Licence plates are not input features.
- **Unverified assumption:** Accident hour 1–24 was mapped to sensor hour 0–23 by subtracting one.
- Features: min temperature from sensors 15/18/19, max road water from 1/8/11, min illuminance from 2/9/12 (lux converted to millilux), speed from sensor -1. Wind, noise, humidity and traffic were not selected in the initial model.
- `output/training_data.csv`: **744 rows × 8 columns**, 964 near accidents, 206 zero-event hours, no missing values and no duplicate hours in the checked output.

## Dangerous condition analysis
| Condition | Hours | Historical near-accidents/hour |
|---|---:|---:|
| Darkness | 354 | 1.271 |
| Black ice danger | 63 | 1.413 |
| Both | 28 | — |
| Darkness OR black ice | **389** | **1.265** |
| Neither | 355 | 1.330 |

## Neural network experiments
- Inputs: `temperature_c`, `water_um`, `illuminance_mlx`, `speed_limit`. Target: `near_accident_count`.
- Previous two-way split: Jan 1–24 train (576 hours), Jan 25–31 test (168 hours).
  - `(32,16)` MLP: train MAE 0.827; test MAE **1.017**.
  - `(8,)` MLP: train MAE 0.926; test MAE **0.905**.
  - Mean baseline: test MAE **0.910**.
- Revised split: Jan 1–20 train (480), Jan 21–24 validate (96), Jan 25–31 test (168). Validation MAE: baseline **0.897**, `(32,16)` **0.898**, `(8,)` **0.913**. The code selected `(32,16)` among the two neural networks, refit on Jan 1–24, and obtained test MAE **1.017** versus baseline **0.910**.
- The held-out week was inspected during earlier experiments, so it is not a pristine unseen final test. The selected model produced two negative raw predictions on test data; inference clamps negative values to zero.

## REQ1 evaluation — current limitation
A representative case (temperature -5°C, water 1,500 µm, light 200 mlx) gave predictions at 80/70/60/50/40 km/h of **1.340 / 0.944 / 1.377 / 2.293 / 2.160** near-accidents/hour. The code selected 70 km/h experimentally for that **single** case; this does **not** establish REQ1 over time.

Fixed hypothetical speed limits across **389 dangerous historical hours** gave:

| Speed | Mean model prediction per hour | ≤ 1? |
|---|---:|---|
| 80 km/h | **1.049** | No |
| 70 km/h | 1.081 | No |
| 60 km/h | 1.249 | No |
| 50 km/h | 1.460 | No |
| 40 km/h | 1.713 | No |

The observed historical mean was **1.265**. Thus **REQ1 has NOT been demonstrated** by the tested model. The fixed-speed experiment includes training observations and cannot identify the causal effect of changing speed. In observed dangerous hours, counts by historical speeds were 40: 7, 50: 55, 60: 230, 70: 97; no recorded 80 km/h dangerous hours. A likely limitation is confounding: slower historical limits may have been chosen when conditions were more dangerous.

## Open tasks before submission
1. Confirm sensor 19 meaning, accident-hour mapping and sensor aggregation rationale.
2. Complete external air-quality API / LLM assessment and reliable failure handling (REQ2).
3. Implement and demonstrate combined weather + air decisions, Streamlit UI and five scenarios.
4. Add automated tests (router thresholds, model loading, decision behavior, external failures).
5. Revisit REQ1 evaluation design and get guidance on the averaging requirement; do not fabricate passing results.
6. Finish presentation, requirements documentation and README.

## Sharing and reproducibility
Recommended commands from the project root: `python data_preparation.py`, `python prepare_accidents.py`, `python prepare_sensors.py`, `python combine_data.py`, `python validate_training_data.py`, `python analyze_conditions.py`, `python router.py`, `python train.py`, `python inference.py`, `python evaluate_req1.py`.

**Warning:** Running `train.py` overwrites `models/weather_model.joblib`. Do not publicly publish accident files containing licence plates or any API credentials. Ask the data owner before sharing raw data, even in a private repository.

## Questions for a reviewer
- Is the intended target near-accident count or directly predicted speed limit?
- How should REQ1's **average** be defined and assessed?
- Is `accident_hour - 1` the right alignment?
- Is `review_required` the right response when no model-supported reduction meets the target?
