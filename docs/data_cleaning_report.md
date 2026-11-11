# SpeedLimit — Data Preparation and Cleaning Report

## 1. Dataset Overview

The SpeedLimit project uses historical sensor measurements and accident records to investigate the relationship between road conditions, speed limits and near-accidents.

The original datasets contain:

| Dataset | Records |
|---|---:|
| Sensor descriptions | 18 |
| Sensor types | 9 |
| Sensor readings, Year N | 12,648 |
| Sensor readings, Year N+1 | 12,648 |
| Accident records, Year N | 997 |
| Accident records, Year N+1 | 844 |

## 2. Identified Data Issues and Decisions

| Issue | Finding | Decision |
|---|---|---|
| Ambiguous sensor code `T` | Code describes temperature and traffic | Resolve provisionally using sensor IDs and observed ranges |
| Undocumented sensor 19 | 744 readings but no description | Provisionally classify as temperature; document uncertainty |
| Sensors 7, 10 and 17 | Described but no Year N readings | Exclude from feature extraction; retain original metadata |
| Missing Year N+1 header | No column headings | Supply the seven expected column names when reading |
| Decimal commas | Values use commas as decimal separators | Read using `decimal=","` |
| Near-accident classification | 964 near-accident-only records, 32 accident-only records and one unclassified record | Use near-accident-only records for the target; exclude other categories provisionally |
| Different hour conventions | Sensors use 0–23 and accidents use 1–24 | Provisionally map accident hour to sensor hour using `Hour - 1` |
| Multiple sensors of one type | Several sensors record temperature, water and light | Aggregate by hour using documented rules |

The selected Year N diagnostic checks found no empty fields, exact duplicate records or duplicate sensor-hour records. The specific date-related errors described on slide 17 of the case-study presentation were not reproduced in these checks. This does not establish that every reading is accurate.

## 3. Feature Engineering

Each training observation represents one hour.

The following input features are used:

| Feature | Sensor IDs | Aggregation |
|---|---|---|
| Temperature (°C) | 15, 18, 19 | Minimum |
| Road water (µm) | 1, 8, 11 | Maximum |
| Illuminance (millilux) | 2, 9, 12 | Minimum, then convert lux to millilux |
| Speed limit (km/h) | −1 | Recorded value |

The minimum/maximum choices represent a conservative aggregation approach, but they may emphasize localized extremes rather than typical highway conditions.

Sensor 19 is treated as a temperature sensor based on its observed values, pending metadata confirmation.

## 4. Prediction Target

The neural network will predict:

**`near_accident_count` — the number of recorded near-accidents per hour.**

A record is provisionally classified as a near-accident if it contains at least one of these indicators:

- `CloseCarCm`
- `CloseGuardrailCm`
- `SkidAngle`

and contains neither `Damage` nor `Injured`.

Actual accidents are kept separate. One unclassified event requires further investigation.

Hours without recorded near-accidents receive a target value of zero.

## 5. Prepared Dataset

The two hourly datasets were merged using month, day and hour.

The resulting `output/training_data.csv` contains:

- 744 hourly observations
- Four neural-network input features
- One prediction target
- Three timestamp columns

Basic validation found no missing values, duplicate hours or out-of-range values in the selected weather features.

There were 964 recorded near-accidents in total, with 206 hours containing zero recorded near-accidents.

## 6. Darkness and Black-Ice Analysis

According to the requirements specification:

- Darkness: illuminance below 500 millilux
- Black-ice danger: water greater than 1,000 µm and temperature below 0°C

The prepared data contain:

| Condition | Hours | Average near-accidents/hour |
|---|---:|---:|
| Darkness | 354 | 1.271 |
| Black-ice danger | 63 | 1.413 |
| Darkness or black ice | 389 | 1.265 |
| Neither condition | 355 | 1.330 |

The categories overlap. Twenty-eight hours satisfy both darkness and black-ice conditions.

These values describe historical observations and cannot establish the causal effect of changing the speed limit.

## 7. Year N+1 and Retraining

The parsed sensor readings for Year N and Year N+1 were found to be identical, including record order and values.

The Year N+1 accident dataset contains 844 records, compared with 997 in Year N.

Identical sensor inputs do not automatically mean retraining is unnecessary. A retraining decision also requires comparison of accident outcomes, model prediction errors and possible changes in the relationship between inputs and outputs.

## 8. Limitations and Assumptions

1. The data cover January only, limiting seasonal generalization.
2. Sensor 19 has no official sensor description.
3. The accident-hour alignment is provisional and unverified.
4. Extreme-value aggregation may not reflect typical road conditions.
5. Near-accident categories are inferred from the presence of recorded indicators.
6. The data are observational and cannot prove that a particular speed limit will achieve the required near-accident rate.
7. The prepared dataset passes basic structural checks, but those checks do not prove the absence of all data-quality problems.

These assumptions must be reviewed when interpreting model predictions and evaluating the system.