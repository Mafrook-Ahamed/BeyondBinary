# Project Plan

## Phase 0 — Scope and contracts

- [ ] Confirm the exact 24 attack labels and mapping from CIC-IDS2017 labels.
- [ ] Define the host-provided CSV schema and required/optional columns.
- [ ] Decide how to handle missing columns, malformed rows, duplicates, and timestamps.
- [ ] Define incident identity and correlation windows.
- [ ] Define severity and priority policy with analyst input.

## Phase 1 — Data foundation

- [ ] Build a streaming/chunked CSV reader.
- [ ] Add schema profiles and import validation reports.
- [ ] Normalize timestamps, addresses, ports, protocols, and numeric fields.
- [ ] Add deterministic feature extraction shared by training and inference.
- [ ] Add unit tests for malformed, empty, oversized, and inconsistent CSVs.

## Phase 2 — Detection models

- [ ] Download and document CIC-IDS2017 provenance and license/usage terms.
- [ ] Inspect actual labels and class distribution.
- [ ] Establish day-aware train/validation/test splits.
- [ ] Train a reproducible multi-class baseline.
- [ ] Evaluate class imbalance and leakage risks.
- [ ] Compare attack-specific models against the shared baseline.
- [ ] Version model artifacts, feature schema, label map, and metrics together.

## Phase 3 — Correlation and triage

- [ ] Build a normalized event representation.
- [ ] Correlate by time, hosts, IPs, ports, protocols, and shared indicators.
- [ ] Construct incidents and candidate attack chains.
- [ ] Calculate a transparent risk score with evidence breakdown.
- [ ] Add queue ordering, analyst status, and audit trail.

## Phase 4 — Application

- [ ] Implement local backend and persistent storage.
- [ ] Implement CSV import and processing status UI.
- [ ] Implement overview, attack queue, incident detail, correlation graph, and model performance screens.
- [ ] Add exportable analyst reports.
- [ ] Add cancellation, retries, and safe handling of large jobs.

## Phase 5 — Validation and release

- [ ] Test on large CSV files and resource-constrained machines.
- [ ] Benchmark end-to-end processing and inference latency.
- [ ] Perform security review of file uploads and local storage.
- [ ] Document installation, supported schemas, model limitations, and troubleshooting.
- [ ] Produce reproducible release builds.

## Exit criteria

A phase is complete only when its implementation, automated tests, documented evidence, and known limitations are recorded. UI mockups and illustrative sample values are not evidence of model performance.
