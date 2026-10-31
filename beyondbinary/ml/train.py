"""Train a binary BENIGN/DDoS CIC-IDS2017 model. Usage: python -m beyondbinary.ml.train --csv data/...csv"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer

LABEL = " Label"

def clean_columns(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--out", default="artifacts/ddos_model.joblib")
    p.add_argument("--test-size", type=float, default=.2)
    args = p.parse_args()
    df = clean_columns(pd.read_csv(args.csv, low_memory=False))
    if "Label" not in df:
        raise SystemExit("Training CSV must contain a Label column.")
    y = df["Label"].astype(str).str.strip().str.upper()
    valid = y.isin(["BENIGN", "DDOS"])
    df, y = df.loc[valid].copy(), y.loc[valid].map({"BENIGN": 0, "DDOS": 1})
    X = df.drop(columns=["Label"]).apply(pd.to_numeric, errors="coerce")
    X = X.replace([np.inf, -np.inf], np.nan)
    # Remove columns that are entirely missing; persist the exact feature list.
    X = X.dropna(axis=1, how="all")
    if X.empty or y.nunique() != 2:
        raise SystemExit("Need numeric features and both BENIGN and DDoS labels.")
    x_train, x_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=42, stratify=y
    )
    model = make_pipeline(SimpleImputer(strategy="median"),
                          HistGradientBoostingClassifier(random_state=42))
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    print(classification_report(y_test, pred, target_names=["BENIGN", "DDoS"], digits=4))
    print("Confusion matrix [BENIGN, DDoS]:")
    print(confusion_matrix(y_test, pred))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": X.columns.tolist(),
                 "classes": {0: "BENIGN", 1: "DDoS"}}, out)
    print(f"Saved model: {out}")

if __name__ == "__main__":
    main()
