"""Unit tests for the first-pass event correlator."""
import unittest

import pandas as pd

from beyondbinary.ml.correlate_events import correlate_events


class CorrelateEventsTests(unittest.TestCase):
    def test_groups_same_source_events_inside_window(self):
        frame = pd.DataFrame({
            "Source IP": ["10.0.0.1", "10.0.0.1", "10.0.0.2"],
            "Timestamp": [
                "2017-07-07 10:00:00",
                "2017-07-07 10:03:00",
                "2017-07-07 10:01:00",
            ],
            "predicted_label": ["PortScan", "DDoS", "PortScan"],
        })
        result = correlate_events(frame, window_minutes=5, min_events=2)
        self.assertEqual(result.loc[0, "incident_id"], result.loc[1, "incident_id"])
        self.assertTrue(result.loc[0, "incident_id"])
        self.assertEqual(result.loc[2, "incident_id"], "")

    def test_does_not_group_events_outside_window(self):
        frame = pd.DataFrame({
            "Source IP": ["10.0.0.1", "10.0.0.1"],
            "Timestamp": ["2020-01-01 10:00:00", "2020-01-01 10:08:00"],
            "predicted_label": ["PortScan", "PortScan"],
        })
        result = correlate_events(frame, window_minutes=5)
        self.assertTrue(result["incident_id"].eq("").all())

    def test_strips_whitespace_from_csv_headers(self):
        frame = pd.DataFrame({
            " Source IP ": ["10.0.0.1", "10.0.0.1"],
            " Timestamp ": ["2020-01-01 10:00:00", "2020-01-01 10:01:00"],
            " predicted_label ": ["DDoS", "DDoS"],
        })
        result = correlate_events(frame)
        self.assertEqual(result.loc[0, "incident_id"], result.loc[1, "incident_id"])

    def test_matches_metadata_headers_case_insensitively(self):
        frame = pd.DataFrame({
            "source ip": ["10.0.0.1", "10.0.0.1"],
            "TIMESTAMP": ["2020-01-01 10:00:00", "2020-01-01 10:01:00"],
            "PREDICTED_LABEL": ["DDoS", "DDoS"],
        })
        result = correlate_events(frame)
        self.assertEqual(result.loc[0, "incident_id"], result.loc[1, "incident_id"])
        self.assertTrue(result.loc[0, "incident_id"])

    def test_missing_context_keeps_suspicious_rows_unassigned(self):
        frame = pd.DataFrame({"predicted_label": ["DDoS"]})
        result = correlate_events(frame)
        self.assertEqual(result.loc[0, "incident_id"], "")
        self.assertIn("source IP", result.loc[0, "correlation_reason"])
        self.assertIn("timestamp", result.loc[0, "correlation_reason"])


if __name__ == "__main__":
    unittest.main()
