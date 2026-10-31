# Incident correlation data requirements

BeyondBinary can score flow records using the model feature columns, but it can only correlate those records into incidents when the input also contains trustworthy event context.

## Required correlation context

Each flow row must include:

- **Source IP**: the observed source address for the flow.
- **Timestamp**: the event time, consistently formatted and preferably normalized to UTC.

The correlator uses source identity and a time window to group related suspicious flows. It does not infer either field from model features.

## Current CIC-IDS2017 limitation

The supplied CIC-IDS2017 flow CSV used by the current pipeline contains model features and a label, but does not provide the source-IP and timestamp columns required by the correlator. In that case, the pipeline intentionally leaves suspicious rows unassigned and reports the missing context. A review flag is a model-generated lead, not a confirmed attack or incident.

Do not synthesize IP addresses or timestamps, and do not use row order as a substitute for event time. Doing so can create false incident relationships.

## Preparing an enriched flow export

For correlation-capable input, export flow records from the same capture using a source that preserves network metadata, such as Zeek connection logs or a flow exporter. Join metadata to model features only through a stable flow identifier or a documented, deterministic matching key. Validate that:

1. Source IP values are present and parse as IP addresses.
2. Timestamps are present, parseable, and use a consistent timezone.
3. Each enriched row maps to the intended original flow; ambiguous joins are rejected rather than guessed.
4. Model feature columns remain unchanged from the training/inference schema.
5. The export and any join procedure are documented for reproducibility.

## Validation before correlation

Run the pipeline on a small sample first. Confirm that missing or malformed metadata produces unassigned review rows, while valid metadata allows events from the same source within the configured time window to be grouped. Review the resulting incidents before treating them as actionable findings.

## Interpretation

- **Model score / review flag:** prioritizes a flow for analyst review.
- **Correlated incident:** a rule-based grouping of flows with available metadata; it is not proof of malicious activity.
- **Confirmed incident:** requires investigation and corroborating evidence outside this pipeline.
