"""Run the BeyondBinary CSV-to-prioritized-incident pipeline.

Example:
  python -m beyondbinary.ml.pipeline --input data/incoming.csv --output out/incident_queue.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from beyondbinary.ml.correlate_events import (
    SRC_COLUMNS,
    TIME_COLUMNS,
    correlate_events,
)
from beyondbinary.ml.score_events import score_events


def run_pipeline(
    input_csv: str,
    model_path: str,
    window_minutes: int = 5,
    min_events: int = 2,
) -> pd.DataFrame:
    """Score raw flows, correlate suspicious events, and rank the review queue."""
    scored = score_events(input_csv, model_path)
    correlated = correlate_events(
        scored,
        window_minutes=window_minutes,
        min_events=min_events,
    )

    # Keep the queue order from scoring; add an incident-level review hint.
    correlated["review_reason"] = correlated["correlation_reason"]
    correlated.loc[
        correlated["incident_id"].ne(""),
        "review_reason",
    ] = (
        correlated["correlation_reason"]
        + "; prioritize as a correlated incident"
    )
    return correlated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="artifacts/ddos_model.joblib")
    parser.add_argument("--input", required=True, help="Unlabeled flow CSV")
    parser.add_argument("--output", default="incident_queue.csv")
    parser.add_argument("--window-minutes", type=int, default=5)
    parser.add_argument("--min-events", type=int, default=2)
    args = parser.parse_args()

    # Inspect the source headers separately so the CLI can explain why
    # correlation is unavailable without changing the model feature schema.
    headers = pd.read_csv(args.input, nrows=0).columns
    normalized_headers = {str(column).strip().casefold() for column in headers}
    has_source = any(column.casefold() in normalized_headers for column in SRC_COLUMNS)
    has_time = any(column.casefold() in normalized_headers for column in TIME_COLUMNS)

    queue = run_pipeline(
        input_csv=args.input,
        model_path=args.model,
        window_minutes=args.window_minutes,
        min_events=args.min_events,
    )
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    queue.to_csv(target, index=False)

    suspicious = queue["human_review_required"].sum()
    incidents = queue.loc[queue["incident_id"].ne(""), "incident_id"].nunique()
    print(
        f"Processed {len(queue):,} flows; {int(suspicious):,} require review; "
        f"{incidents:,} correlated incidents."
    )
    if not has_source or not has_time:
        missing = []
        if not has_source:
            missing.append("source IP")
        if not has_time:
            missing.append("timestamp")
        print(
            "Correlation limitation: input is missing "
            + " and ".join(missing)
            + ". Provide a flow export with these fields to enable incident grouping."
        )
    print(f"Incident queue written to {target}")


if __name__ == "__main__":
    main()
