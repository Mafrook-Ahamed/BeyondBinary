# Host CSV Contract — Draft

The production contract cannot be finalized until a representative host CSV sample is reviewed.

## Required design decisions

- Timestamp format and timezone
- Event/flow identifier availability
- Source and destination address field names
- Port and protocol representation
- Numeric feature names, units, and valid ranges
- Whether rows represent packets, flows, alerts, or aggregated events
- Whether duplicate records are possible
- Maximum file size and expected row count
- Whether multiple CSV schema profiles must be supported

## Import behavior

The importer should:

1. Validate file encoding, delimiter, headers, and row shape.
2. Identify a supported schema profile or request explicit field mapping.
3. Parse in chunks to bound memory use.
4. Preserve source row numbers and original field references.
5. Reject or quarantine malformed rows with actionable errors.
6. Produce a summary: total rows, accepted rows, rejected rows, duplicate rows, and processing duration.
7. Never interpret a missing value as zero unless the feature contract explicitly says so.

## Privacy

Host CSVs may contain sensitive operational metadata. Keep them out of Git and use local storage with access controls.
