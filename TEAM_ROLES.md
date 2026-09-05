# TEAM_ROLES.md — SIH 26189
# Team Roles and Responsibilities
# Problem Statement ID: 26189 | Repository: SIH-189

---

## Team Structure & Ownership Overview

The 19 SIH capability areas and 5 architectural zones are assigned across six logical roles with zero overlapping ownership.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  AI/NLP Engineer:         Zone 2 (Capabilities 1, 2, 3, 4, 14)             │
│  Graph Intelligence:      Zone 3 & Zone 4A (Capabilities 5, 6, 7, 8, 9)     │
│  ML / Analytics Analyst:  Zone 4B, 4C, 4D, 4E (Capabilities 10, 11, 12, 13)│
│  Security & Integrity:    Cross-Cutting Layers (Capabilities 16, 17)        │
│  Frontend / UX Engineer:  Zone 5 (Capabilities 18, 19)                      │
│  Data / Backend Engineer: Zone 1 & Core Infra (Capability 15)               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Role 1: AI/NLP Engineer
* **Primary Zone:** Zone 2 (Local AI/NLP & Entity Resolution)
* **Owned Capabilities:**
  - 1. Document AI / OCR / NLP
  - 2. Entity Extraction / NER
  - 3. Entity Resolution
  - 4. Semantic Search / Information Retrieval
  - 14. Cyber Intelligence Identifiers
* **Current Active Files:**
  - `backend/nlp/entity_extractor.py`
  - `backend/nlp/entity_resolver.py`
  - `backend/nlp/relationship_extractor.py`
* **Immediate Tasks (Phases 1–2):**
  - Integrate `jellyfish` Double Metaphone in `entity_resolver.py` for Indian transliteration matching.
  - Implement passive-voice extraction rules in `relationship_extractor.py`.
  - Build PDF text parser using PyMuPDF for FIR statement ingestion.

---

## Role 2: Graph Intelligence Engineer
* **Primary Zone:** Zone 3 (Knowledge Graph) & Zone 4A (Graph Analytics)
* **Owned Capabilities:**
  - 5. Knowledge Graph
  - 6. Criminal Network Graph Analytics
  - 7. Influencer / Centrality Detection
  - 8. Community Detection
  - 9. Graph ML / GNN (Future Phase 7)
* **Current Active Files:**
  - `backend/graph/graph_builder.py`
  - `backend/graph/graph_analysis.py`
* **Immediate Tasks (Phases 1–3):**
  - Expose `GET /graph/path?source={id}&target={id}` in `main.py`.
  - Pass greedy modularity community IDs to node classes for frontend visual clustering.
  - Design graph schema expansion for `ORGANIZATION` and `BANK_ACCOUNT` node types.

---

## Role 3: ML / Intelligence Analyst
* **Primary Zone:** Zone 4B, 4C, 4D, 4E (Intelligence & Analytics)
* **Owned Capabilities:**
  - 10. Anomaly / Suspicious Pattern Detection
  - 11. CDR / Communication Analytics
  - 12. Financial Network / Fraud Analytics
  - 13. Spatio-Temporal & Geospatial Analytics
* **Current Active Files:**
  - `backend/anomaly/feature_builder.py`
  - `backend/anomaly/isolation_forest.py`
  - `backend/data/anomaly_ground_truth.json`
* **Immediate Tasks (Phases 1–3):**
  - Split general IsolationForest into specialized sub-models for network degree spikes and night clustering.
  - Add latitude and longitude coordinate support to the `locations` table.
  - Build baseline feature vector builders for structured banking CSVs.

---

## Role 4: Security & Integrity Engineer
* **Primary Zone:** Cross-Cutting Security & Evidence Integrity
* **Owned Capabilities:**
  - 16. Security / Privacy / Access Control
  - 17. Blockchain / Evidence Integrity
* **Current Active Files:**
  - Scoped for implementation in Phases 5 & 6
* **Immediate Tasks (Phases 5–6):**
  - Implement JWT authentication endpoints (`/auth/login`, `/auth/refresh`) and RBAC middleware.
  - Build append-only `audit_log` middleware recording all investigator queries and lead reviews.
  - Build SHA-256 evidence hashing and the append-only `hash_chain` verification endpoint.

---

## Role 5: Frontend / UX Engineer
* **Primary Zone:** Zone 5 (Investigator Intelligence Platform)
* **Owned Capabilities:**
  - 18. Dashboard / Visualization / XAI
  - 19. Investigator Workflow / Human-in-the-Loop
* **Current Active Files:**
  - `frontend/src/App.jsx`
  - `frontend/src/api.js`
  - `frontend/src/components/*.jsx`
* **Immediate Tasks (Phases 3–4):**
  - Implement `Accept`, `Reject`, `Review`, and `Escalate` decision controls in the entity table.
  - Build interactive time-series timeline component for CDR calls and bank transfers.
  - Integrate Leaflet.js interactive map for suspect location movement tracking.

---

## Role 6: Data / Backend Engineer
* **Primary Zone:** Zone 1 (Multi-Source Ingestion) & Core Infrastructure
* **Owned Capabilities:**
  - 15. Data Engineering / Multi-Source Integration
  - Core API & Database Operations
* **Current Active Files:**
  - `backend/main.py`
  - `backend/database.py`
  - `backend/models.py`
  - `backend/data/seed_data.py`
  - `backend/data/test_cases.py`
  - `backend/test_demo.py`
  - `verify_api.py`
* **Immediate Tasks (Phases 1–2):**
  - Implement dedicated `/ingest/cdr` and `/ingest/financial` CSV ingestion endpoints.
  - Expand synthetic database in `seed_data.py` to 20+ entities and 1,000+ CDR records.
  - Add automated test cases TC-7 to TC-12 in `test_cases.py`.
