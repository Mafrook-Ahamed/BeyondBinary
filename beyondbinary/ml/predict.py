"""Score an unlabeled CIC-IDS2017-style CSV with a trained binary model."""
from __future__ import annotations
import argparse
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="artifacts/ddos_model.joblib")
    p.add_argument("--input", required=True, help="CSV without Label column")
    p.add_argument("--output", default="predictions.csv")
    args = p.parse_args()
    bundle = joblib.load(args.model)
    df = pd.read_csv(args.input, low_memory=False)
    df.columns = [str(c).strip() for c in df.columns]
    if "Label" in df.columns:
        df = df.drop(columns=["Label"])
    features = bundle["features"]
    X = df.reindex(columns=features).apply(pd.to_numeric, errors="coerce")
    X = X.replace([np.inf, -np.inf], np.nan)
    pred = bundle["model"].predict(X)
    result = df.copy()
    result["predicted_label"] = np.where(pred == 1, "DDoS", "BENIGN")
    if hasattr(bundle["model"], "predict_proba"):
        result["ddos_probability"] = bundle["model"].predict_proba(X)[:, 1]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    print(f"Scored {len(result)} rows -> {output}")

if __name__ == "__main__":
    main()
