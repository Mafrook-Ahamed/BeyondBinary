"""Correlate scored flow events into transparent, time-bounded incident groups.

This is a first-pass rule-based correlator, not a causal attribution engine.
It uses fields present in CIC-IDS-style flow CSVs when available and gracefully
falls back to uncorrelated event rows when required context is missing.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


TIME_COLUMNS = ("Timestamp", "timestamp", "Flow Start", "flow_start")
SRC_COLUMNS = ("Source IP", "Src IP", "src_ip", "source_ip")
DST_COLUMNS = ("Destination IP", "Dst IP", "dst_ip", "destination_ip")
LABEL_COLUMNS = ("predicted_label", "Label", "label")
PROB_COLUMNS = ("prediction_probability", "probability", "confidence")


def find_column(frame: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    return next((name for name in candidates if name in frame.columns), None)


def correlate_events(
    frame: pd.DataFrame,
    window_minutes: int = 5,
    min_events: int = 2,
) -> pd.DataFrame:
    """Assign related suspicious flows to incidents using source and time window."""
    if window_minutes < 1:
        raise ValueError("window_minutes must be >= 1")
    if min_events < 1:
        raise ValueError("min_events must be >= 1")

    data = frame.copy().reset_index(drop=True)
    # CICFlowMeter exports often include leading/trailing spaces in headers.
    data.columns = [str(column).strip() for column in data.columns]
    data["event_id"] = data.get("event_id", pd.Series(range(1, len(data) + 1))).astype(str)

    time_col = find_column(data, TIME_COLUMNS)
    src_col = find_column(data, SRC_COLUMNS)
    dst_col = find_column(data, DST_COLUMNS)
    label_col = find_column(data, LABEL_COLUMNS)
    prob_col = find_column(data, PROB_COLUMNS)

    if label_col:
        suspicious = data[label_col].astype(str).str.upper().ne("BENIGN")
    elif prob_col:
        suspicious = pd.to_numeric(data[prob_col], errors="coerce").fillna(0) >= 0.5
    else:
        suspicious = pd.Series(False, index=data.index)

    data["incident_id"] = ""
    data["correlation_reason"] = "insufficient fields for correlation"

    # Without both source and timestamp, avoid inventing relationships.
    if not src_col or not time_col:
        missing = []
        if not src_col:
            missing.append("source IP")
        if not time_col:
            missing.append("timestamp")
        data.loc[suspicious, "correlation_reason"] = (
            "suspicious event; correlation unavailable because "
            + " and ".join(missing)
            + " field(s) are missing from input"
        )
        return data

    data["_time"] = pd.to_datetime(data[time_col], errors="coerce")
    data["_source"] = data[src_col].astype(str)
    data["_destination"] = data[dst_col].astype(str) if dst_col else ""

    suspicious_rows = data.loc[suspicious & data["_time"].notna()].copy()
    window = pd.Timedelta(minutes=window_minutes)
    incident_number = 0

    for source, group in suspicious_rows.groupby("_source", sort=False):
        group = group.sort_values("_time")
        cluster: list[int] = []
        cluster_start = None
        previous_time = None

        def assign_cluster(indices: list[int], start_time: pd.Timestamp) -> None:
            nonlocal incident_number
            if len(indices) < min_events:
                return
            incident_number += 1
            incident_id = f"INC-{incident_number:06d}"
            data.loc[indices, "incident_id"] = incident_id
            data.loc[indices, "correlation_reason"] = (
                f"same source {source}; events within {window_minutes} minute window"
            )

        for idx, row in group.iterrows():
            current_time = row["_time"]
            if previous_time is None or current_time - cluster_start <= window:
                if not cluster:
                    cluster_start = current_time
                cluster.append(idx)
            else:
                assign_cluster(cluster, cluster_start)
                cluster = [idx]
                cluster_start = current_time
            previous_time = current_time
        if cluster:
            assign_cluster(cluster, cluster_start)

    # Keep suspicious singleton/unassigned rows visible for analyst review.
    still_unassigned = suspicious & data["incident_id"].eq("")
    data.loc[still_unassigned, "correlation_reason"] = (
        "suspicious event; no multi-event source/time cluster formed"
    )
    return data.drop(columns=["_time", "_source", "_destination"], errors="ignore")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path, help="Scored events CSV")
    parser.add_argument("--output", type=Path, default=Path("correlated_events.csv"))
    parser.add_argument("--window-minutes", type=int, default=5)
    parser.add_argument("--min-events", type=int, default=2)
    args = parser.parse_args()

    events = pd.read_csv(args.input_csv, low_memory=False)
    correlated = correlate_events(events, args.window_minutes, args.min_events)
    correlated.to_csv(args.output, index=False)
    incidents = correlated.loc[correlated["incident_id"].ne(""), "incident_id"].nunique()
    print(f"Saved {len(correlated):,} events and {incidents:,} correlated incidents to {args.output}")


if __name__ == "__main__":
    main()
