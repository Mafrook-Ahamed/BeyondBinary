# Architecture

## Logical pipeline

```text
Host CSV
  |
  v
Import Manager
  |-- File validation
  |-- Schema/profile detection
  |-- Chunked parsing
  v
Canonical Event Records
  |
  v
Feature Extraction
  |
  v
Inference Orchestrator
  |-- Benign vs suspicious
  |-- Attack-family predictions
  |-- Confidence and evidence
  v
Correlation Engine
  |-- Time-window relationships
  |-- Shared hosts / IPs / ports / protocols
  |-- Repeated or sequential behavior
  v
Incident Builder
  |
  v
Risk and Priority Engine
  |
  v
SOC Analyst Queue + Incident Detail
```

## Component responsibilities

### Import Manager

Owns file intake, schema checks, streaming/chunk processing, row-level validation errors, and import summaries. Avoid loading an entire large CSV into memory.

### Canonical Event Records

A normalized internal representation independent of the original CSV column names. Preserve source row references so the analyst can trace predictions back to input records.

### Feature Extraction

The training and inference pipelines must share the same versioned feature definitions. Feature order, units, missing-value policy, and categorical encoding must be explicit.

### Inference Orchestrator

Loads only compatible model versions. Returns predictions with model version, feature schema version, class probabilities where available, and timing information.

### Correlation Engine

Links events using configurable temporal and entity relationships. Correlation output should preserve its reasons and contributing event IDs. A shared IP or short time gap alone must not be treated as proof of a common attack.

### Risk and Priority Engine

Produces a transparent score and priority band. Keep model confidence separate from impact/severity. Show score contributions so analysts can understand why an incident appears near the top.

### Analyst Queue

Supports review state, analyst decision, notes, filters, sorting, and traceability. Do not silently discard benign events; retain import-level counts and provide search/audit access.

## Initial canonical event fields

The exact contract is pending host sample CSVs. Candidate fields include:

- Event identifier and source row number
- Timestamp
- Source and destination IP/address
- Source and destination port
- Protocol
- Source and destination host or asset identifiers
- Flow duration and packet/byte counters
- Event or traffic features used by the selected model
- Original source label when available (training/evaluation only)

Do not assume all event exports contain all fields. Schema profiles and mapping are required.

## Local-first boundary

CSV parsing, model inference, correlation, and persistence should run locally. Network access should not be required for core analysis. Any optional threat-intelligence enrichment must be separately configurable and clearly marked as external.
