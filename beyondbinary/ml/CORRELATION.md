# Event correlation (first pass)

The correlator groups **predicted suspicious flow events** by source IP when their
timestamps fall within a configured window. This is a transparent heuristic to
help an analyst triage related activity; it does not prove common attribution
or reconstruct an attack chain.

## Run

From the repository root, after producing a scored-events CSV:

```bash
python -m beyondbinary.ml.correlate_events scored_events.csv --output correlated_events.csv --window-minutes 5 --min-events 2
```

The input should contain a predicted label (or probability), a source IP field,
and a timestamp field. Supported names are listed in the script. If source IP or
timestamp is missing, suspicious rows remain unassigned and explain why.

## Output

Adds:
- `event_id`: preserved if supplied, otherwise generated for the input rows
- `incident_id`: stable within this output run for each multi-event cluster
- `correlation_reason`: short explanation of the grouping decision

Rows that do not form a multi-event cluster remain in the output for review.
The current implementation does not correlate across different source IPs,
does not infer causal links, and does not yet calculate incident severity.
