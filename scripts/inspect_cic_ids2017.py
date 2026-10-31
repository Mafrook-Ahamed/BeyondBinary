"""Inspect CIC-IDS2017 CSV labels and basic data quality without training models.

Usage:
  python scripts/inspect_cic_ids2017.py path/to/cic_csv_or_folder
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

LABEL_CANDIDATES = ("Label", "label", "Class", "class", "Attack", "attack")


def find_csvs(path: Path) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() != ".csv":
            raise ValueError(f"Expected a CSV file: {path}")
        return [path]
    if not path.is_dir():
        raise FileNotFoundError(path)
    return sorted(path.rglob("*.csv"))


def label_column(columns: list[str]) -> str | None:
    for candidate in LABEL_CANDIDATES:
        if candidate in columns:
            return candidate
    return None


def inspect_csv(path: Path, chunksize: int) -> tuple[int, dict[str, int], list[str]]:
    rows = 0
    counts: dict[str, int] = {}
    columns: list[str] = []
    for chunk in pd.read_csv(path, chunksize=chunksize, low_memory=False):
        if not columns:
            columns = [str(c) for c in chunk.columns]
            label = label_column(columns)
            if label is None:
                raise ValueError(
                    f"No recognized label column in {path.name}. "
                    f"Columns: {', '.join(columns[:30])}"
                )
        values = chunk[label].fillna("<MISSING>").astype(str).str.strip()
        for name, count in values.value_counts().items():
            counts[name] = counts.get(name, 0) + int(count)
        rows += len(chunk)
    return rows, counts, columns


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="CSV file or directory containing CIC-IDS2017 CSVs")
    parser.add_argument("--chunksize", type=int, default=100_000)
    args = parser.parse_args()
    if args.chunksize < 1:
        parser.error("--chunksize must be positive")

    try:
        files = find_csvs(args.path)
        if not files:
            print(f"No CSV files found under {args.path}", file=sys.stderr)
            return 2
        total_rows = 0
        combined: dict[str, int] = {}
        print(f"Found {len(files)} CSV file(s)")
        for file in files:
            rows, counts, columns = inspect_csv(file, args.chunksize)
            total_rows += rows
            for label, count in counts.items():
                combined[label] = combined.get(label, 0) + count
            print(f"\n{file}: {rows:,} rows, {len(columns)} columns")
            print("Labels:")
            for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
                print(f"  {label}: {count:,}")
        print(f"\nTOTAL rows: {total_rows:,}")
        print("COMBINED labels:")
        for label, count in sorted(combined.items(), key=lambda item: (-item[1], item[0])):
            print(f"  {label}: {count:,}")
        print(f"Distinct labels: {len(combined)}")
        print("This is a label inventory only; it does not define or train 24 models.")
        return 0
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        print(f"Inspection failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
