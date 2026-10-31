## Binary DDoS baseline

Install dependencies with `pip install -r requirements-dev.txt scikit-learn joblib`.

Train only with a labeled CSV:
```bash
python -m beyondbinary.ml.train --csv data/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
```

Score an unlabeled CSV (same CICFlowMeter feature schema):
```bash
python -m beyondbinary.ml.predict --input data/incoming.csv --output predictions.csv
```

The training script filters to BENIGN and DDoS, uses Label only as the target, and saves feature names with the model. Inference drops any Label column and aligns incoming features to the saved schema. Missing feature values are imputed. This is a development baseline, not a production detector; evaluate on a separate capture/day before deployment. Keep model artifacts and datasets out of Git.
