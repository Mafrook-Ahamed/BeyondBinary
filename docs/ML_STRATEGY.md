# Machine-Learning Strategy

## Dataset

Primary training source: CIC-IDS2017.

Before implementation, verify the downloaded dataset files, label spellings, duplicates, class counts, missing values, and collection-day distribution. Preserve provenance and checksums for source files.

## The 24-model target

The product requirement is to build 24 attack-specific models. Treat this as a target architecture to validate, not a reason to train 24 isolated models without comparison.

Required first step: create a version-controlled label taxonomy with exactly 24 intended attack classes and a mapping from every source label to one of:

- Benign
- One of the 24 attack classes
- Explicitly excluded / unresolved

No source label should be silently dropped or remapped.

## Compare two designs

### A. Shared multi-class classifier

One classifier predicts benign plus all supported attack classes. This gives a consistent probability distribution and a simple inference path.

### B. Specialized attack classifiers

A benign/attack gate or shared model routes traffic to specialized binary or family classifiers. This may help classes with distinct feature patterns but can increase compute cost, calibration complexity, and false positives.

Evaluate both using the same fixed data splits and feature contract. Retain specialized models only when they improve the required class-level metrics and operational outcomes.

## Data splitting and leakage control

- Keep related flows and duplicate records from leaking across train and test partitions.
- Prefer day-aware or chronological evaluation where appropriate.
- Fit scaling, encoding, feature selection, and resampling on training data only.
- Do not use test data for threshold selection or tuning.
- Record dataset versions, random seeds, preprocessing version, and label map.

## Metrics

Report at minimum:

- Per-class precision, recall, F1, and support
- Macro and weighted F1
- Confusion matrix
- False-positive rate and false-negative rate
- Precision-recall curves for imbalanced classes
- Probability calibration and threshold behavior
- Inference throughput, latency, and memory use

Accuracy alone is not sufficient, especially when benign records dominate.

## Inference output contract

Each prediction should include:

- Event reference / source row
- Predicted class
- Confidence or calibrated probability
- Model name and version
- Feature-schema version
- Inference timestamp and duration
- Supporting feature evidence, where explainable

## Operational caveat

CIC-IDS2017 is a benchmark dataset, not a guarantee of performance on a host's real network. Validate against representative host data before production use. Distribution shift, capture differences, encrypted traffic, and different feature availability can materially change results.
