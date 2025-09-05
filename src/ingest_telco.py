# src/ingest_telco.py
import os
import pandas as pd
from pandas_gbq import to_gbq

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET = os.getenv("BQ_DATASET", "telco")
TABLE   = os.getenv("BQ_TABLE", "customers")
CSV_PATH = "data/raw/telco.csv"

assert PROJECT_ID, "Falta env GCP_PROJECT_ID"
assert os.path.exists(CSV_PATH), f"No existe {CSV_PATH}"

df = pd.read_csv(CSV_PATH)

# Normaliza nombres a snake_case
df.columns = (df.columns
              .str.strip().str.lower()
              .str.replace(" ", "_")
              .str.replace("-", "_"))

# Cast típicos del dataset
for col in ["totalcharges", "tenure"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Limpia strings
for c in df.select_dtypes(include="object").columns:
    df[c] = df[c].astype(str).str.strip()

# Carga en BigQuery
to_gbq(
    df,
    destination_table=f"{DATASET}.{TABLE}",
    project_id=PROJECT_ID,
    if_exists="replace"  # o 'append' si quieres acumular
)

print(f"OK -> {PROJECT_ID}.{DATASET}.{TABLE} ({len(df):,} filas)")

