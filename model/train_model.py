from pathlib import Path

import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import (
    RandomForestRegressor,
    HistGradientBoostingRegressor
)

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ==========================================
# 1. PROJECT PATHS AND CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "raw" / "merged"
MODEL_DIR = BASE_DIR / "model"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

ZONES = [1, 2, 4]

HORIZON = pd.Timedelta(hours=24)

RANDOM_STATE = 42


# ==========================================
# 2. LOAD AND CLEAN ZONE DATA
# ==========================================

def load_zone(zone):

    file_path = DATA_DIR / f"dataset_zone_{zone}.csv"

    if not file_path.exists():
        print(f"Missing file: {file_path}")
        return None

    df = pd.read_csv(file_path)

    df["ts"] = pd.to_datetime(
        df["ts"],
        errors="coerce"
    )

    df = df.dropna(subset=["ts"])

    df = df.sort_values("ts")

    df = df.drop_duplicates(
        subset="ts",
        keep="last"
    )

    df["soil_moisture"] = pd.to_numeric(
        df["soil_moisture"],
        errors="coerce"
    )

    # Keep only physically plausible readings.
    # These are still relative probe readings,
    # not universal soil-water percentages.

    df.loc[
        ~df["soil_moisture"].between(0, 100),
        "soil_moisture"
    ] = np.nan

    df["zone_id"] = zone

    return df


# ==========================================
# 3. CREATE TIME-ALIGNED FEATURES
# ==========================================

def create_dataset(df):

    df = df.copy()

    # Future soil moisture exactly 24 hours later.
    future = df[["ts", "soil_moisture"]].copy()

    future["ts"] = future["ts"] - HORIZON

    future = future.rename(
        columns={
            "soil_moisture": "target_soil_moisture"
        }
    )

    df = df.merge(
        future,
        on="ts",
        how="left",
        validate="one_to_one"
    )

    # Historical soil moisture lags.
    lag_periods = {
        "moisture_1h": pd.Timedelta(hours=1),
        "moisture_4h": pd.Timedelta(hours=4),
        "moisture_24h": pd.Timedelta(hours=24)
    }

    for feature_name, lag in lag_periods.items():

        historical = df[["ts", "soil_moisture"]].copy()

        historical["ts"] = historical["ts"] + lag

        historical = historical.rename(
            columns={
                "soil_moisture": feature_name
            }
        )

        df = df.merge(
            historical,
            on="ts",
            how="left",
            validate="one_to_one"
        )

    # Past rainfall over six hours.
    df["rainfall_6h"] = (
        df["weather_rain"]
        .rolling(36, min_periods=36)
        .sum()
    )

    # Past irrigation duration over four hours.
    df["irrigation_past_4h"] = (
        df["irrigation_duration_minutes"]
        .rolling(24, min_periods=24)
        .sum()
    )

    # Calendar features.
    df["hour"] = df["ts"].dt.hour

    df["day_of_year"] = df["ts"].dt.dayofyear

    return df


# ==========================================
# 4. SELECT FEATURES
# ==========================================

FEATURES = [

    "zone_id",

    "soil_moisture",
    "moisture_1h",
    "moisture_4h",
    "moisture_24h",

    "weather_temp",
    "weather_humidity",
    "weather_rain",
    "weather_wind_speed",
    "weather_radiation",

    "rainfall_6h",
    "irrigation_past_4h",

    "hour",
    "day_of_year"
]

TARGET = "target_soil_moisture"


# ==========================================
# 5. PREPARE ALL ZONES
# ==========================================

all_data = []

for zone in ZONES:

    print(f"\nProcessing Zone {zone}...")

    df = load_zone(zone)

    if df is None:
        continue

    df = create_dataset(df)

    required_columns = FEATURES + [TARGET]

    df = df.dropna(
        subset=required_columns
    )

    df = df.sort_values("ts")

    print("Usable samples:", len(df))

    if len(df) == 0:
        continue

    all_data.append(df)

if not all_data:

    raise ValueError(
        "No usable training data found. "
        "Check dataset paths and missing values."
    )

data = pd.concat(
    all_data,
    ignore_index=True
)

print("\nTotal usable samples:", len(data))


# ==========================================
# 6. CHRONOLOGICAL TRAIN / VALIDATION / TEST
# ==========================================

data = data.sort_values(
    ["zone_id", "ts"]
)

data["split_rank"] = (
    data.groupby("zone_id")
    .cumcount()
    /
    data.groupby("zone_id")["ts"].transform("count")
)

train = data[data["split_rank"] < 0.70]

validation = data[
    (data["split_rank"] >= 0.70)
    & (data["split_rank"] < 0.85)
]

test = data[data["split_rank"] >= 0.85]

print("\nTrain samples:", len(train))
print("Validation samples:", len(validation))
print("Test samples:", len(test))

if min(len(train), len(validation), len(test)) == 0:
    raise ValueError("Insufficient data for chronological splitting.")


X_train = train[FEATURES]
y_train = train[TARGET]

X_val = validation[FEATURES]
y_val = validation[TARGET]

X_test = test[FEATURES]
y_test = test[TARGET]


# ==========================================
# 7. TRAIN CANDIDATE MODELS
# ==========================================

models = {

    "Random Forest": RandomForestRegressor(
        n_estimators=150,
        max_depth=12,
        min_samples_leaf=3,
        n_jobs=-1,
        random_state=RANDOM_STATE
    ),

    "Hist Gradient Boosting": HistGradientBoostingRegressor(
        max_iter=150,
        max_leaf_nodes=15,
        learning_rate=0.08,
        l2_regularization=1.0,
        random_state=RANDOM_STATE
    )

}

results = {}

best_model = None
best_model_name = None
best_validation_mae = float("inf")


for name, model in models.items():

    print(f"\nTraining {name}...")

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(X_val)

    mae = mean_absolute_error(
        y_val,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(y_val, predictions)
    )

    print("Validation MAE:", round(mae, 4))
    print("Validation RMSE:", round(rmse, 4))

    results[name] = {
        "MAE": mae,
        "RMSE": rmse
    }

    if mae < best_validation_mae:

        best_validation_mae = mae

        best_model = model

        best_model_name = name


# ==========================================
# 8. FINAL TEST EVALUATION
# ==========================================

test_predictions = best_model.predict(X_test)

test_mae = mean_absolute_error(
    y_test,
    test_predictions
)

test_rmse = np.sqrt(
    mean_squared_error(y_test, test_predictions)
)

test_r2 = r2_score(
    y_test,
    test_predictions
)


# Persistence baseline:
# Predict future moisture = current moisture.

baseline_predictions = X_test["soil_moisture"]

baseline_mae = mean_absolute_error(
    y_test,
    baseline_predictions
)
# ==========================================
# ZONE-WISE MODEL PERFORMANCE
# ==========================================

print("\n========== ZONE-WISE PERFORMANCE ==========")

test_results = test[
    ["zone_id", TARGET, "soil_moisture"]
].copy()

test_results["model_prediction"] = test_predictions

test_results["baseline_prediction"] = baseline_predictions

for zone in sorted(test_results["zone_id"].unique()):

    zone_data = test_results[
        test_results["zone_id"] == zone
    ]

    model_mae = mean_absolute_error(
        zone_data[TARGET],
        zone_data["model_prediction"]
    )

    baseline_mae = mean_absolute_error(
        zone_data[TARGET],
        zone_data["baseline_prediction"]
    )

    print(f"\nZone {zone}")
    print("Model MAE:", round(model_mae, 4))
    print("Baseline MAE:", round(baseline_mae, 4))

print("\n========== FINAL RESULTS ==========")

print("Selected Model:", best_model_name)

print("Test MAE:", round(test_mae, 4))

print("Test RMSE:", round(test_rmse, 4))

print("Test R2:", round(test_r2, 4))

print("Persistence Baseline MAE:", round(baseline_mae, 4))


# ==========================================
# 9. SAVE MODEL AND METADATA
# ==========================================

model_path = MODEL_DIR / "soil_moisture_model.pkl"

metadata_path = MODEL_DIR / "model_metadata.pkl"

joblib.dump(
    best_model,
    model_path
)

metadata = {

    "model_name": best_model_name,

    "features": FEATURES,

    "target": TARGET,

    "prediction_horizon": "24 hours",

    "test_MAE": test_mae,

    "test_RMSE": test_rmse,

    "test_R2": test_r2,

    "baseline_MAE": baseline_mae,

    "training_zones": ZONES

}

joblib.dump(
    metadata,
    metadata_path
)

print("\nModel saved:", model_path)

print("Metadata saved:", metadata_path)
print("\n========== MODEL ACCURACY REPORT ==========")

print(f"Model Name: {best_model_name}")
print(f"MAE: {test_mae:.4f}")
print(f"RMSE: {test_rmse:.4f}")
print(f"R2 Score: {test_r2:.4f}")
print(f"R2 Score (%): {test_r2 * 100:.2f}%")

if test_r2 >= 0:
    print(f"Explained Variance: {test_r2 * 100:.2f}%")
else:
    print("Model performance needs improvement.")

print("==========================================")
print("\nMODEL TRAINING COMPLETED!")