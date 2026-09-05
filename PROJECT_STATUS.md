# PROJECT_STATUS.md — SIH 26189
# AI-Powered Criminal Network Analysis System
# Problem Statement ID: 26189 | Repository: SIH-189

> All data in this project is fully synthetic.
> This is a Proof-of-Concept prototype for SIH Problem Statement 26189.
> It does not connect to any real government database.

---

## Current POC Status

| Component              | Status     | Notes                                               |
|------------------------|------------|-----------------------------------------------------|
| Backend (FastAPI)      | WORKING    | Uvicorn on localhost:8000                           |
| NLP Pipeline           | WORKING    | spaCy en_core_web_sm + regex                        |
| Entity Extractor       | WORKING    | PERSON, LOCATION, PHONE, VEHICLE, MONEY, CASE, DATE |
| Entity Resolver        | WORKING    | RapidFuzz fuzzy + exact match + alias matching      |
| Relationship Extractor | WORKING    | Rule-based: 7 relationship types                    |
| Graph Builder          | WORKING    | NetworkX DiGraph with historical enrichment         |
| Graph Analysis         | WORKING    | Centrality, betweenness, BFS, community, bridges    |
| Anomaly Detection      | WORKING    | IsolationForest, 11-feature vector, explanations    |
| Priority Scoring       | WORKING    | Rule-based, explainable, per person-pair            |
| SQLite Database        | WORKING    | 5 persons, 3 cases, 365 CDR rows, 138 transactions  |
| React Frontend         | WORKING    | Vite + Cytoscape.js interactive graph               |
| Automated Tests        | 6/6 PASS  | All tests pass as of 2026-09-01                     |

---

## Working Features (Verified by Code Inspection + Tests)

### Backend API Endpoints
- POST /analyze-case: Full 8-step pipeline (NLP, resolution, relationships, graph, anomaly, priority)
- GET /entity/{id}: Entity detail (person record, cases, CDR count, transaction count)
- GET /entity/{id}/history: Historical case involvement for an entity
- GET /entity/{id}/network: 1-hop CDR neighbor network
- POST /anomaly-detection: Standalone anomaly detection for a given entity_id
- GET /health: System health check (DB, NLP model, anomaly model)
- GET /demo-text: Returns pre-built demo case text

### NLP Entity Extraction
- PERSON via spaCy NER + DB name-scan fallback
- LOCATION via spaCy (GPE and LOC labels)
- PHONE via regex (Indian 10-digit mobile, 6-9 prefix)
- VEHICLE via regex (Indian plate: DL01AB1234)
- MONEY via regex (Rs / Rs. / rupee prefix)
- CASE via regex (C102, C10345)
- DATE via spaCy with noise filter (rejects "the day", "the night", etc.)
- ORG-to-PERSON reclassification when ORG text matches a DB person name
- Span overlap prevention: regex spans take priority over spaCy spans

### Entity Resolution
- Exact match: PHONE by number, VEHICLE by plate, CASE by ID
- Fuzzy match: RapidFuzz token_sort_ratio for PERSON and LOCATION
- Alias matching for all registered persons
- AUTO_MATCH (>=90%), POSSIBLE_MATCH (70-89%), NEW_ENTITY (<70%)
- Confidence score (0.0 to 1.0) per resolved entity

### Graph
- NetworkX DiGraph; node types: PERSON, LOCATION, VEHICLE, PHONE, CASE, ORGANIZATION
- Historical enrichment: CDR and financial transaction edges from DB
- Cytoscape.js-compatible node+edge export
- Degree centrality, betweenness centrality (undirected)
- BFS depth-1 and depth-2 neighbors for first 5 nodes
- Greedy modularity community detection (requires >=2 edges)
- Bridge entity identification (above-average betweenness)

### Anomaly Detection
- IsolationForest trained on 120 synthetic normal activity windows (seed=42)
- 11-feature vector: calls/day, calls_last_7_days, unique_contacts, new_contacts,
  night_calls, avg_call_duration, transaction_amount, transaction_frequency,
  avg_transaction_amount, new_recipients, amount_deviation
- CDR direction bug fixed: only outgoing calls (caller_id == entity_id) count
- Secondary threshold check catches extreme spikes the model might miss
- Human-readable reasons comparing current vs. baseline for each flagged feature
- Severity: HIGH, MEDIUM, LOW, NORMAL

### Synthetic Database
- 5 persons: Rahul Sharma (P001), Amit Kumar (P002), Ravi Singh (P003),
             Sameer Khan (P004), Priya Verma (P005)
- 2 vehicles: DL01AB1234 (P001 owner), DL02XY5678 (P004 owner)
- 2 locations: Delhi (L001), Mumbai (L002)
- 2 phones: 9876543210 (P001), 9123456780 (P002)
- 3 cases: C101 Narcotics (Closed), C102 Financial Fraud (Active), C103 Vehicle Theft (Closed)
- 365 CDR records (60 days normal + injected anomaly: P001 makes 42 calls in 2 days)
- 138 transactions (60 days normal + injected Rs 850000 P001->P002)
- Behavioral baselines for P001-P005
- anomaly_ground_truth.json: 3 known injected anomalies for evaluation

### Frontend
- Case input panel with demo text loader
- System health status bar (polls every 15 seconds)
- Extracted entities panel with type icons and badges
- Entity resolution table with confidence progress bars
- Cytoscape.js interactive network graph: zoom, pan, node click
- Anomaly panel with current vs baseline feature comparison
- Historical cases panel with shared-entity indicator
- Relationships panel with frequency and amount metadata
- Graph analysis panel: centrality, bridge entities, communities
- Investigation priority panel: score, level (HIGH/MEDIUM/LOW), reasons
- Entity detail modal: person profile, cases, CDR count, transaction count

---

## Known Bugs Fixed (Do Not Revert)

1. CDR Direction Bug
   File: backend/anomaly/feature_builder.py
   Problem: Incoming calls were attributed to the receiver as their outgoing activity.
   Fix: current_outgoing = [r for r in current_calls if r["caller_id"] == entity_id]

2. DATE False Positives
   File: backend/nlp/entity_extractor.py
   Problem: "the day", "the night", "morning", etc. tagged as DATE entities.
   Fix: _DATE_NOISE frozenset filter rejects vague time-of-day phrases.

---

## Current Limitations

1. Small synthetic dataset: 5 persons, 2 locations, 3 cases.
2. Rule-based relationship extraction: misses complex sentences.
3. No authentication: API is fully open; no login system.
4. Single data source type: no separate FIR/CDR file/financial/OSINT ingestion.
5. No geospatial analytics: locations are name strings only, no coordinates.
6. No timeline UI: CDR/transaction timestamps exist but not displayed as a timeline.
7. Community detection: requires >=2 graph edges; small inputs show 0 communities.
8. No blockchain/evidence integrity: not implemented.
9. No human-in-the-loop UI: no Accept/Reject/Review buttons.
10. spaCy en_core_web_sm: limited accuracy for Indian proper nouns.

---

## Next 5 Implementation Tasks

1. (HIGH) Expand synthetic dataset: 20+ persons, 10+ cases, 1000+ CDR records.
2. (HIGH) Multi-source ingestion: POST /ingest/fir, /ingest/cdr, /ingest/financial endpoints.
3. (MEDIUM) Human-in-the-loop UI: Accept/Reject/Review on resolution table and anomaly cards.
4. (MEDIUM) Timeline view: chronological CDR and transaction events per entity.
5. (MEDIUM) Evidence hash chain: SHA-256 hash of each case record + audit log.

---

## Prototype Completion Estimate

Layer               | Status                         | Completion
--------------------|--------------------------------|----------
Data ingestion      | Text input only                | ~20%
NLP / NER           | 7 entity types working         | ~55%
Entity resolution   | Fuzzy + exact + aliases        | ~50%
Graph               | Core + historical enrichment   | ~60%
Graph analytics     | Centrality, BFS, community     | ~65%
Anomaly detection   | Comm + financial combined      | ~40%
Dashboard           | Core panels working            | ~45%
Security            | None implemented               | ~0%
Blockchain/integrity| None implemented               | ~0%
Testing             | 6 automated tests              | ~30%

Overall POC to Prototype: approximately 40% complete.

---

Last verified: 2026-09-05 (push-readiness audit) | Automated tests: 6/6 PASS | All data is synthetic.

---

## Team Handoff Documents

- [TEAM_HANDOFF.md](TEAM_HANDOFF.md) — Start here if you are new to the project.
- [CHECKPOINT.md](CHECKPOINT.md) — Formal checkpoint record: implemented, partial, planned, future.
- [TESTING.md](TESTING.md) — Current testing status and all test cases.

