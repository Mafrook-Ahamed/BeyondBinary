## Event scoring and review queue

After training a model, score a CSV with no ground-truth label:

```bash
python -m beyondbinary.ml.score_events --input data/incoming.csv --output out/attack_queue.csv
```

The output includes a generated event ID, predicted class, DDoS probability, and review priority:
- P1: probability >= 0.90
- P2: >= 0.70
- P3: >= 0.50
- P4: below 0.50

These thresholds are initial demo defaults, not calibrated operational severity. The queue is ranked by model confidence; it does not yet correlate events across time or hosts. Validate thresholds against a separate capture before operational use.
