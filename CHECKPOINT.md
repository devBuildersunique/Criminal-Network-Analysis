# SIH 26189 — Development Checkpoint
# Problem Statement ID: 26189 | Repository: SIH-189
# Ministry of Home Affairs | NCRB, Women Safety Division

---

**Date:** 2026-09-05

**Status:**
- 🟢 Implementation checkpoint — POC complete
- 🟡 Testing pending — automated tests pass; API/browser/E2E not yet formally verified
- 🟢 Documentation prepared for team handoff

---

## Summary

The SIH 26189 POC is complete. The full analysis pipeline — from free-text case statement input through NLP, entity resolution, knowledge graph construction, anomaly detection, and interactive dashboard — is implemented and the automated test suite passes (6/6).

This checkpoint marks the transition from solo/small-group development to team handoff.

---

## Implemented

| Capability | Notes |
|---|---|
| Free-text case statement ingestion | POST /analyze-case |
| Entity extraction (7 types) | PERSON, LOCATION, PHONE, VEHICLE, MONEY, CASE, DATE |
| DB name-scan fallback | Catches persons missed by spaCy in context |
| DATE noise filter | Rejects vague phrases ("the day", "the night") |
| Multi-tier entity resolution | Exact + RapidFuzz fuzzy + alias matching |
| 7-predicate relationship extraction | Rule-based (MET, CALLED, TRANSFERRED_MONEY, USED_VEHICLE, INVOLVED_IN, USES_PHONE, VISITED) |
| Attributed knowledge graph (NetworkX) | Multi-type nodes, directed edges, record_source metadata |
| Historical DB enrichment | CDR and transaction edges added from DB |
| Graph analytics | Degree centrality, betweenness, bridge detection, community detection |
| 11-feature anomaly detection | IsolationForest + secondary threshold + human-readable reasons |
| CDR direction correctness | Only outgoing calls attributed to caller |
| Priority scoring | Rule-based, per entity pair, with explanation |
| Synthetic SQLite database | 5 persons, 3 cases, 365 CDRs, 138 transactions |
| Auto-seeding | DB auto-seeded on startup if missing |
| React + Cytoscape.js dashboard | Entity panel, graph, anomaly cards, priority ranking, historical cases |
| FastAPI REST backend | /analyze-case, /health, /entity/{id}, /entity/{id}/history, /entity/{id}/network, /anomaly-detection, /demo-text |
| Automated test suite | 6 tests covering normal, anomaly, resolution, historical, new-entity cases |

---

## Partial

| Capability | What Is Done | What Remains |
|---|---|---|
| Graph analytics | Backend computes communities | Community IDs not exposed as Cytoscape node colors |
| Shortest path | `shortest_path()` function exists in graph_analysis.py | GET /graph/path endpoint not implemented |
| Cyber identifier extraction | Phone number extraction only | Emails, IPs, usernames not extracted |
| Dashboard panels | Core panels implemented | Timeline, map, HITL decision controls not implemented |

---

## Planned (Not Implemented)

- FIR / CDR file / financial CSV ingestion endpoints
- Indian-name phonetic matching (Double Metaphone)
- Full-text cross-case search
- Human-in-the-loop Accept/Reject/Review/Escalate controls
- Interactive timeline for CDR and transaction events
- Geospatial map view (Leaflet.js)
- JWT authentication + RBAC (4 roles)
- Append-only audit logging
- SHA-256 evidence hashing and hash chain

---

## Future / Advanced (Deferred Post-Hackathon)

- Neo4j / Memgraph persistent graph store
- Graph Neural Network (T-HGT) for link prediction
- Federated Learning (Flower / FedProx)
- Homomorphic Encryption
- Hyperledger Fabric permissioned ledger
- Local LLM (vLLM) for enhanced NLP extraction

---

## Known Limitations

1. Small synthetic dataset (5 persons, 3 cases) — not representative of real investigation scale.
2. Rule-based relationship extraction — misses complex or passive-voice sentences.
3. spaCy en_core_web_sm — limited accuracy for Indian proper nouns and transliterations.
4. No authentication — API is fully open; no login system.
5. Community detection requires ≥2 edges — small inputs may show 0 communities.
6. No timeline UI — timestamps exist in DB but are not displayed as a timeline.
7. No geospatial analytics — location names are strings; no coordinates.

---

## Testing Status

```
Automated tests (6/6):    PASS  — executed 2026-09-05
API endpoint testing:     PENDING
Frontend browser testing: PENDING
End-to-end testing:       PENDING
Performance benchmarks:   PENDING
Formal evaluation metrics: PENDING
```

**Testing was not fully executed during this checkpoint audit.**
The automated pipeline tests pass. API, browser, and end-to-end tests remain pending.

---

## Known Bugs Fixed (Do Not Revert)

| Bug | File | Fix |
|---|---|---|
| CDR direction: incoming calls attributed to receiver as their outgoing activity | `backend/anomaly/feature_builder.py` | `current_outgoing = [r for r in current_calls if r["caller_id"] == entity_id]` |
| DATE noise: "the day", "the night" extracted as DATE entities | `backend/nlp/entity_extractor.py` | `_DATE_NOISE` frozenset filter |
| Graph `frequency=None` crash (TypeError on edge increment) | `backend/graph/graph_builder.py` | Strip None metadata before `**meta` spread; use `int(current_freq or 0)` |
| Ravi Singh not extracted by spaCy in context | `backend/nlp/entity_extractor.py` | DB name-scan fallback (Step 3) |

---

## Next Development Milestone

**Goal:** Formal testing + first prototype feature

**Tasks:**
1. Execute browser end-to-end demo verification (TESTING.md BT-1 to BT-5).
2. Implement `POST /ingest/cdr` CSV ingestion endpoint.
3. Add phonetic matching to entity_resolver.py for Indian name variants.
4. Expand synthetic dataset to 20+ persons and 1000+ CDR records.
5. Add HITL Accept/Reject controls to the frontend entity resolution table.

---

*All data is 100% synthetic and fictional. This is a POC for SIH Problem Statement 26189.*
*Last updated: 2026-09-05*
