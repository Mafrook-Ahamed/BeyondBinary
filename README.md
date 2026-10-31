# BeyondBinary

**AI-powered SOC event triage, attack detection, correlation, and human-decision prioritization.**

BeyondBinary is a local-first application for security operations teams. A host imports a large CSV export of security events. The application validates and normalizes the records, detects suspicious activity, correlates related events into incidents, and ranks the incidents that need analyst attention first.

> **Project status:** Early foundation. The dashboard design and architecture are being established. No production detection models are claimed to exist yet.

## Product goals

- Process large host-provided CSV event exports.
- Separate benign activity from suspicious and malicious activity.
- Classify detected attack types using models trained on CIC-IDS2017.
- Correlate related events across time, source/destination addresses, ports, protocols, and hosts.
- Build an attack queue ranked by risk and operational impact.
- Explain why an incident is prioritized and show supporting evidence.
- Recommend which events require human review first.
- Run locally and keep imported event data under the host's control.

## Core workflow

`CSV import → validation and normalization → feature extraction → ML inference → event correlation → risk prioritization → analyst review`

## Planned capabilities

| Area | Responsibility |
| --- | --- |
| CSV ingestion | Upload, schema validation, parsing, batch processing, and import reporting |
| Detection | Benign/attack classification and attack-family identification |
| Correlation | Group events into related incidents and potential attack chains |
| Prioritization | Rank incidents using severity, impact, asset criticality, spread, recency, and confidence |
| Analyst queue | Show the highest-value human decisions first |
| Explainability | Surface detection evidence, model confidence, and correlation reasons |
| Local runtime | Local processing, storage, and model inference |

## Machine-learning plan

CIC-IDS2017 is the planned primary training dataset. The initial target is **24 attack-specific model artifacts**, subject to verification of the source labels and the intended taxonomy.

Before training, the team must publish a label-mapping specification that identifies the exact 24 classes, benign label handling, and any merged or excluded labels. Do not assume that the raw dataset's label count equals the model count.

The model design will be evaluated against a shared multi-class baseline. Attack-specific classifiers should only be retained when they show measurable value over the baseline. Evaluation must use leakage-resistant, time/day-aware splits and report per-class precision, recall, F1, confusion matrices, false-positive rate, calibration, and inference latency.

## Prioritization principles

Model confidence alone is not incident severity. The queue should combine detection evidence with operational context:

- Potential impact and attack severity
- Number and criticality of affected hosts or users
- Event volume and propagation across assets
- Correlation strength and progression over time
- Detection confidence and evidence quality
- Recency and whether activity appears ongoing

Priorities are recommendations for analysts, not autonomous containment decisions.

## Design

The editable Figma dashboard design is available here:

[BeyondBinary — SOC Operations Dashboard](https://www.figma.com/design/vc80nQ5oJS4vOMVpNLwXV6)

## Proposed development sequence

1. Confirm the 24-class attack taxonomy and host CSV contract.
2. Build ingestion, validation, normalization, and a reproducible dataset pipeline.
3. Train and evaluate a multi-class baseline on CIC-IDS2017.
4. Compare specialized attack classifiers with the baseline.
5. Build event correlation and incident construction.
6. Implement explainable risk scoring and analyst queue ordering.
7. Connect the UI to the local backend and inference pipeline.
8. Validate performance on large CSV files and unseen traffic.

## Security and data handling

- Keep host event data local by default.
- Never commit customer event CSVs, credentials, secrets, or trained model files containing sensitive data.
- Treat CSV fields as untrusted input.
- Record import metadata and processing errors without exposing sensitive payloads unnecessarily.
- Document model limitations and avoid presenting predictions as confirmed incidents.

## Development status

See [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), and [docs/ML_STRATEGY.md](docs/ML_STRATEGY.md) for the current foundation.
