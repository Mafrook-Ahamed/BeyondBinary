"""Score unlabeled flow CSVs and produce a human-review queue.

Usage:
  python -m beyondbinary.ml.score_events --input data/incoming.csv --output out/attack_queue.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


def score_events(input_csv: str, model_path: str) -> pd.DataFrame:
    bundle = joblib.load(model_path)
    model = bundle["model"]
    features = bundle["features"]

    events = pd.read_csv(input_csv, low_memory=False)
    events.columns = [str(column).strip() for column in events.columns]
    # Never allow the ground-truth label to leak into prediction.
    events = events.drop(columns=["Label"], errors="ignore")
    matrix = events.reindex(columns=features).apply(pd.to_numeric, errors="coerce")
    matrix = matrix.replace([np.inf, -np.inf], np.nan)

    predictions = model.predict(matrix)
    probabilities = (
        model.predict_proba(matrix)[:, 1]
        if hasattr(model, "predict_proba")
        else np.where(predictions == 1, 1.0, 0.0)
    )

    output = events.copy()
    output.insert(0, "event_id", [f"flow-{i + 1:07d}" for i in range(len(output))])
    output["predicted_label"] = np.where(predictions == 1, "DDoS", "BENIGN")
    output["ddos_probability"] = probabilities.round(6)
    output["priority"] = np.select(
        [probabilities >= 0.90, probabilities >= 0.70, probabilities >= 0.50],
        ["P1", "P2", "P3"],
        default="P4",
    )
    output["human_review_required"] = probabilities >= 0.50
    # P1 first, then strongest model score. Stable ordering preserves input order on ties.
    priority_order = {"P1": 0, "P2": 1, "P3": 2, "P4": 3}
    output["_priority_order"] = output["priority"].map(priority_order)
    output = output.sort_values(
        ["_priority_order", "ddos_probability"],
        ascending=[True, False],
        kind="stable",
    ).drop(columns="_priority_order")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="artifacts/ddos_model.joblib")
    parser.add_argument("--input", required=True, help="Unlabeled flow CSV")
    parser.add_argument("--output", default="attack_queue.csv")
    args = parser.parse_args()

    queue = score_events(args.input, args.model)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    queue.to_csv(target, index=False)
    print(f"Scored {len(queue)} events; {int(queue['human_review_required'].sum())} queued for review.")
    print(f"Queue written to {target}")


if __name__ == "__main__":
    main()
