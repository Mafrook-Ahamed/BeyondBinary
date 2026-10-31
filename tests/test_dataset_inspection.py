from pathlib import Path

import pandas as pd

from scripts.inspect_cic_ids2017 import find_csvs, label_column


def test_label_column_recognizes_dataset_label():
    assert label_column(["Flow Duration", "Label"]) == "Label"


def test_find_csvs_returns_only_csv_files(tmp_path: Path):
    (tmp_path / "one.csv").write_text("Label\nBENIGN\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("not data", encoding="utf-8")
    assert [p.name for p in find_csvs(tmp_path)] == ["one.csv"]


def test_csv_can_be_read_in_chunks(tmp_path: Path):
    path = tmp_path / "sample.csv"
    pd.DataFrame({"Label": ["BENIGN", "DoS Hulk"]}).to_csv(path, index=False)
    frame = pd.read_csv(path, chunksize=1)
    assert sum(len(chunk) for chunk in frame) == 2
