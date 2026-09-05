# ROADMAP.md — SIH 26189
# Development Roadmap: AI-Powered Criminal Network Analysis System
# Problem Statement ID: 26189 | Repository: SIH-189

---

## Roadmap Overview

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  Phase 0: Core Working POC               [COMPLETE — 6/6 Tests Passing]    │
│  Phase 1: Stabilization & Data Expansion [Weeks 1–2: Phonetics & Regressions│
│  Phase 2: Multi-Source Data Ingestion    [Weeks 2–3: Batch CSV/PDF Ingest]  │
│  Phase 3: Multi-Modal Intelligence       [Weeks 2–3: Map, Timeline, API]    │
│  Phase 4: Investigator Platform (HITL)   [Weeks 2–3: Accept/Reject UI & XAI]│
│  Phase 5: Enterprise Security Layer      [Weeks 1–2: JWT, RBAC, Audit Log]  │
│  Phase 6: Evidence Integrity Layer       [Weeks 1–2: SHA-256 Hash Chain]    │
│  Phase 7: Production & Federated Scale   [Post-Hackathon: Neo4j & FedProx]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 0 — Working POC (COMPLETE ✅)
* **Status:** Verified operational (2026-09-01)
* **Objective:** Establish an 8-step investigative intelligence pipeline processing free-form text into knowledge graphs, IsolationForest anomalies, and Cytoscape.js visualizations.
* **Delivered Components:**
  - `backend/nlp/entity_extractor.py`: 7-type NER + DB name-scan fallback + `_DATE_NOISE` filter.
  - `backend/nlp/entity_resolver.py`: 3-tier RapidFuzz fuzzy resolver (`AUTO`, `POSSIBLE`, `NEW`).
  - `backend/nlp/relationship_extractor.py`: 7-predicate sentence-level rule extractor.
  - `backend/graph/graph_builder.py` & `graph_analysis.py`: NetworkX graph with historical enrichment & centrality analytics.
  - `backend/anomaly/feature_builder.py` & `isolation_forest.py`: 11-feature ML anomaly engine with dual-threshold override.
  - `frontend/src/App.jsx`: Full React 19 + Cytoscape.js dashboard with live health monitor.
  - `backend/test_demo.py`: 6/6 automated test cases passing deterministically.

---

## Phase 1 — Stabilization & Data Expansion (Weeks 1–2)
* **Objective:** Harden the codebase against regressions, expand synthetic benchmarks, and improve Indian name resolution.
* **Key Tasks:**
  1. *Expand Synthetic Registry:* Scale `seed_data.py` to 20+ entities, 10+ cases, and 1,000+ CDR records.
  2. *Automated Regression Suite:* Implement TC-7 through TC-12 in `test_cases.py` (covering CDR direction, DATE noise, vehicle-location links, and multi-source inputs).
  3. *Indian Name Phonetic Resolution:* Integrate `jellyfish` Double Metaphone in `entity_resolver.py` to handle transliteration variants.
  4. *Passive-Voice NLP Rules:* Extend `relationship_extractor.py` to recognize passive sentence constructions.
* **Owner:** AI/NLP Engineer & Data/Backend Engineer
* **Completion Criteria:** 12/12 automated test cases pass; transliteration match accuracy exceeds 90%.

---

## Phase 2 — Multi-Source Data Ingestion (Weeks 2–3)
* **Objective:** Ingest structured and unstructured data from all 7 problem statement source channels (Zone 1).
* **Key Tasks:**
  1. *Structured CDR Ingestion:* Implement `POST /ingest/cdr` supporting standard telecom CSV headers.
  2. *Financial Log Ingestion:* Implement `POST /ingest/financial` for banking transaction CSVs.
  3. *FIR & Document Ingestion:* Implement `POST /ingest/fir` supporting multi-line text and PDF extraction via PyMuPDF.
  4. *Surveillance & Intelligence Ingestion:* Implement `POST /ingest/surveillance` and `POST /ingest/intelligence_report`.
  5. *Unified `source_records` Table:* Store ingested payload metadata with unique `record_hash` identifiers.
* **Owner:** Data/Backend Engineer
* **Completion Criteria:** All 7 data source formats successfully ingest and map to internal graph schemas.

---

## Phase 3 — Intelligence Upgrades (Weeks 2–3)
* **Objective:** Enhance Zone 4 intelligence with temporal, geospatial, and advanced pathfinding capabilities.
* **Key Tasks:**
  1. *Shortest Path REST API:* Expose `GET /graph/path?source={id}&target={id}` in `main.py`.
  2. *Community UI Visualization:* Map NetworkX greedy modularity community IDs to distinct Cytoscape node classes/colors.
  3. *Interactive Event Timeline:* Build a chronological event stream component in React for CDR calls and bank transfers.
  4. *Geospatial Map View:* Add latitude/longitude coordinates to location entities and render interactive Leaflet.js map markers.
  5. *Dedicated Temporal/Network Anomaly Detectors:* Split general IsolationForest into specialized sub-models for sudden degree changes and night-time clustering.
* **Owner:** Graph Intelligence Engineer & ML / Intelligence Analyst
* **Completion Criteria:** Timeline and map render accurately on multi-hop cases; shortest path API verified.

---

## Phase 4 — Investigator Platform & HITL (Weeks 2–3)
* **Objective:** Deliver full human-in-the-loop (HITL) oversight and comprehensive explainability (Zone 5).
* **Key Tasks:**
  1. *Lead Decision Controls:* Add `Accept`, `Reject`, `Review`, and `Escalate` buttons on entity resolution and priority panels.
  2. *Investigator Annotation Drawer:* Allow officers to add case notes and attach rationale to specific nodes/edges.
  3. *Dedicated XAI Panel:* Render side-by-side feature comparison charts (Baseline vs Current Activity) explaining anomaly scores.
  4. *Cross-Case Entity Search:* Implement full-text search across past case statements using SQLite FTS5.
  5. *Clean Technical Debt:* Connect `getEntityHistory()` to a dedicated historical drawer component in the UI.
* **Owner:** Frontend / UX Engineer
* **Completion Criteria:** Investigator decisions persist in database; all AI outputs provide full visual justifications.

---

## Phase 5 — Enterprise Security Layer (Weeks 1–2)
* **Objective:** Secure the system for controlled multi-user departmental access.
* **Key Tasks:**
  1. *JWT Authentication:* Implement token issuance (`/auth/login`, `/auth/refresh`) with bcrypt password hashing.
  2. *Multi-Factor OTP:* Support mock/SMS OTP verification for supervisor elevation.
  3. *Role-Based Access Control (RBAC):* Middleware enforcing permissions for `INVESTIGATOR`, `SUPERVISOR`, `ADMIN`, `ANALYST`.
  4. *Case-Level Authorization:* Partition graph and case access by assigned officer rosters.
  5. *Immutable Audit Log:* Create append-only `audit_log` recording user ID, timestamp, endpoint, query parameters, and export events.
  6. *Transport & Storage Security:* Enforce TLS 1.3 / HTTPS and integrate SQLCipher encryption at rest.
* **Owner:** Security & Integrity Engineer
* **Completion Criteria:** Unauthorized role access rejected with HTTP 403; all actions logged to audit trail.

---

## Phase 6 — Evidence Integrity Layer (Weeks 1–2)
* **Objective:** Deliver cryptographic chain-of-custody tracking for all ingested evidence documents.
* **Key Tasks:**
  1. *SHA-256 Ingestion Fingerprinting:* Compute raw cryptographic hash upon file receipt.
  2. *Append-Only Hash Chain:* Implement linked block table where $H_i = \text{SHA-256}(H_{i-1} \parallel \text{Record ID} \parallel \text{Timestamp} \parallel \text{Actor} \parallel H_0)$.
  3. *Integrity Verification Endpoint:* Build `GET /integrity/verify/{record_id}` to detect database tampering.
  4. *Chain-of-Custody Export:* Generate cryptographic verification reports for supervisory review.
* **Owner:** Security & Integrity Engineer
* **Completion Criteria:** Tamper detection test successfully flags modified database records.

---

## Phase 7 — Production Scaling & Federated Architecture (Post-Hackathon / Advanced)
* **Objective:** Scale to nationwide deployment with multi-agency federated privacy.
* **Key Tasks:**
  1. *Database Migrations:* Transition from SQLite to PostgreSQL with connection pooling.
  2. *Graph Database Migration:* Transition from NetworkX to Neo4j / Memgraph for billion-edge distributed graph querying.
  3. *Containerization:* Docker and Kubernetes manifests for on-premise air-gapped police datacenter deployment.
  4. *Federated Graph Learning:* Deploy Flower / FedProx framework allowing state police departments to train Temporal Heterogeneous Graph Transformers (T-HGT) on local subgraphs without exporting raw suspect PII.
* **Owner:** Full Engineering Team
* **Completion Criteria:** Multi-node cluster handles 100,000+ concurrent entities; federated aggregation completes across 3 simulated state nodes.
