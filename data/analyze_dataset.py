import pandas as pd
from pathlib import Path

DATA_DIR = Path("C:/Users/User/Downloads/Soil Moisture, Irrigation Actuator and Weather Dat/Soil Moisture, Irrigation Actuator and Weather Dat/02_processed_data/preprocessed")

files = sorted(DATA_DIR.glob("dataset_zone_*_preprocessed.csv"))

print("\n========== AIML FARMER DATASET REPORT ==========\n")

if not files:
    print("No dataset files found. Check folder path.")
else:
    for file in files:
        df = pd.read_csv(file, parse_dates=["ts"])

        print(f"\n{'='*45}")
        print(f"FILE: {file.name}")
        print(f"{'='*45}")

        print("Rows:", len(df))
        print("Columns:", len(df.columns))

        print("\nMissing Values:")
        print(df.isna().sum().to_string())

        print("\nSoil Moisture:")
        print(df["soil_moisture"].describe().round(2))

        print("\nTimestamp Gaps:")
        gaps = df["ts"].diff().dropna().dt.total_seconds() / 60
        print(gaps.value_counts().head(5).to_string())

        print("\nDuplicate Timestamps:", df["ts"].duplicated().sum())

print("\n========== ANALYSIS COMPLETE ==========")