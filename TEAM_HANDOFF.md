# SIH 26189 — Team Handoff Document
# Problem Statement ID: 26189 | Repository: SIH-189
# Ministry of Home Affairs | NCRB, Women Safety Division

> **All data in this project is 100% synthetic and fictional.**
> This is a working POC — it does not connect to any real government database.
> It does not make determinations of guilt or criminal liability.

---

## 1. What We Have

A working Proof-of-Concept (POC) for an AI-assisted criminal network analysis system.

**What it does:**
A team member types (or pastes) a case statement into the browser. The system extracts named entities (people, phones, vehicles, money amounts, case references), resolves them against a synthetic historical database, builds a knowledge graph, detects unusual communication/financial activity, and presents the results as an interactive dashboard with ranked investigative leads.

**What it does NOT do:**
- It does not access any real government, NCRB, or police database.
- It does not determine criminal guilt.
- It does not accept uploaded files (yet — that is Phase 2).
- It does not have login/authentication (yet — that is Phase 5).
- All analytical signals are investigative leads for human review, not conclusions.

---

## 2. What Works (Implemented & Code-Verified)

| Component | Status | Where |
|---|---|---|
| Text case statement → full analysis | WORKING | `backend/main.py` POST /analyze-case |
| Entity extraction (7 types) | WORKING | `backend/nlp/entity_extractor.py` |
| Fuzzy entity resolution | WORKING | `backend/nlp/entity_resolver.py` |
| Rule-based relationship extraction | WORKING | `backend/nlp/relationship_extractor.py` |
| Knowledge graph (NetworkX) | WORKING | `backend/graph/graph_builder.py` |
| Graph analytics (centrality, bridges) | WORKING | `backend/graph/graph_analysis.py` |
| Anomaly detection (IsolationForest) | WORKING | `backend/anomaly/isolation_forest.py` |
| CDR/financial feature vectorization | WORKING | `backend/anomaly/feature_builder.py` |
| Priority scoring with explanations | WORKING | `backend/main.py` |
| Synthetic SQLite database (auto-seed) | WORKING | `backend/data/seed_data.py` |
| React dashboard + Cytoscape.js graph | WORKING | `frontend/src/` |
| FastAPI REST backend | WORKING | `backend/main.py` |
| Automated test suite (6 tests) | 6/6 PASS | `backend/test_demo.py` |

---

## 3. What Is Remaining (Planned / Partial)

**High priority (Phase 1–2):**
- [ ] Multi-source file ingestion: FIR PDF, CDR CSV, financial CSV endpoints
- [ ] Indian-name phonetic matching (jellyfish / Double Metaphone)
- [ ] Expand dataset: 20+ persons, 1000+ CDR records, 10+ cases
- [ ] Additional automated test cases (TC-7 to TC-12)

**Medium priority (Phase 3–4):**
- [ ] Human-in-the-loop Accept/Reject/Review buttons for entity resolution
- [ ] Interactive timeline for CDR and transaction events
- [ ] Geospatial map view (Leaflet.js)
- [ ] Community coloring in Cytoscape graph
- [ ] Expose GET /graph/path endpoint

**Deferred (Phase 5–7 / Future):**
- [ ] JWT authentication + RBAC (4 user roles)
- [ ] Append-only audit logging
- [ ] SHA-256 evidence hash chain
- [ ] Neo4j / Memgraph persistent graph store
- [ ] Graph Neural Network (T-HGT) link prediction
- [ ] Federated learning (Flower / FedProx)
- [ ] Local LLM (vLLM) for enhanced extraction
- [ ] Hyperledger Fabric permissioned ledger

---

## 4. How To Run (Fresh Environment)

### Backend

```bash
cd SIH-189

# Create virtual environment
python -m venv .venv

# Activate — Windows:
.venv\Scripts\activate
# Activate — macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model (one-time)
python -m spacy download en_core_web_sm

# Seed the database (one-time; auto-seeded on startup too)
python -m backend.data.seed_data

# Start backend
uvicorn backend.main:app --reload --port 8000
```

Backend is live at: http://localhost:8000
Swagger UI (API explorer): http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend is live at: http://localhost:5173

### Run Automated Tests

```bash
cd SIH-189
python backend/test_demo.py
```

Expected output: `6/6 TESTS PASSED`

---

## 5. How The Pipeline Works

```text
User types a case statement in the browser
    ↓
POST /analyze-case (FastAPI backend receives text)
    ↓
Step 1 — Entity Extraction
  spaCy NER + Regex + DB name-scan fallback
  → PERSON, LOCATION, PHONE, VEHICLE, MONEY, CASE, DATE entities

Step 2 — Entity Resolution
  RapidFuzz fuzzy matching against SQLite DB
  → Each entity: matched to DB record (AUTO_MATCH) or flagged NEW_ENTITY

Step 3 — Relationship Extraction
  Rule-based regex + string matching
  → MET, CALLED, TRANSFERRED_MONEY, USED_VEHICLE, INVOLVED_IN, etc.

Step 4 — Graph Construction
  NetworkX DiGraph from resolved entities + relationships
  + historical enrichment from DB CDR and transaction records

Step 5 — Graph Analysis
  Degree centrality, betweenness, bridge detection, community detection

Step 6 — Anomaly Detection
  IsolationForest on 11-feature vector per resolved PERSON entity
  Secondary threshold check catches extreme spikes

Step 7 — Priority Scoring
  Rule-based scoring per entity pair
  Weighted by: direct connections, anomaly severity, historical cases shared

Step 8 — Response
  JSON returned to React frontend
  Frontend renders: entity chips, resolution table, Cytoscape.js graph,
  anomaly cards, historical cases panel, priority ranking
```

---

## 6. Where Things Are

| Feature | File / Folder |
|---|---|
| Main API orchestrator | `backend/main.py` |
| Entity extraction | `backend/nlp/entity_extractor.py` |
| Entity resolution | `backend/nlp/entity_resolver.py` |
| Relationship extraction | `backend/nlp/relationship_extractor.py` |
| Graph builder + historical enrichment | `backend/graph/graph_builder.py` |
| Graph analytics (centrality, bridges) | `backend/graph/graph_analysis.py` |
| Anomaly detection engine | `backend/anomaly/isolation_forest.py` |
| CDR/financial feature vectorizer | `backend/anomaly/feature_builder.py` |
| Database helpers / queries | `backend/database.py` |
| Pydantic API schemas | `backend/models.py` |
| Synthetic DB seeder | `backend/data/seed_data.py` |
| Test cases definitions | `backend/data/test_cases.py` |
| Automated test runner | `backend/test_demo.py` |
| API verification script | `verify_api.py` |
| React main app | `frontend/src/App.jsx` |
| API client (Axios) | `frontend/src/api.js` |
| Cytoscape.js graph component | `frontend/src/components/NetworkGraph.jsx` |
| Anomaly panel | `frontend/src/components/AnomalyPanel.jsx` |
| Entity panels | `frontend/src/components/EntitiesPanel.jsx` |
| Case input + demo loader | `frontend/src/components/CaseInput.jsx` |
| Historical cases panel | `frontend/src/components/HistoryCasesPanel.jsx` |
| Entity detail modal | `frontend/src/components/EntityDetailModal.jsx` |
| Python dependencies | `requirements.txt` |
| Frontend dependencies | `frontend/package.json` |

---

## 7. Team Ownership

| Role | Owns | Key Files |
|---|---|---|
| AI/NLP Engineer | Entity extraction, resolution, relationship extraction, cyber identifiers | `backend/nlp/` |
| Graph Intelligence Engineer | Knowledge graph, graph analytics, community detection, GNN (future) | `backend/graph/` |
| ML / Intelligence Analyst | Anomaly detection, CDR analytics, financial analytics, geospatial (future) | `backend/anomaly/` |
| Security & Integrity Engineer | Auth/RBAC, audit logging, evidence hash chain, blockchain (future) | Not yet implemented |
| Frontend / UX Engineer | Dashboard, Cytoscape.js, HITL controls (future), timeline (future) | `frontend/src/` |
| Data / Backend Engineer | Database, API endpoints, data ingestion, test automation | `backend/main.py`, `backend/database.py`, `backend/data/` |

See [TEAM_ROLES.md](TEAM_ROLES.md) for detailed task assignments and file ownership.

---

## 8. Testing

```
Automated tests:       6/6 PASS (executed 2026-09-05)
API testing:           PENDING
Browser testing:       PENDING
End-to-end testing:    PENDING
Performance testing:   PENDING
```

**Testing is pending at this checkpoint.** The 6 automated pipeline tests pass, which verifies entity extraction, resolution, relationship extraction, anomaly detection, historical case lookup, and new-entity classification. API, browser, and end-to-end tests have not been formally executed.

To run automated tests:
```bash
python backend/test_demo.py
```

See [TESTING.md](TESTING.md) for all planned test cases, browser test cases, and evaluation metrics.

---

## 9. Important Rules

1. **Synthetic data only.** All persons, cases, CDR records, and transactions in the database are fictional. Never use real case data in development.
2. **AI provides investigative signals — not conclusions.** The system surfaces anomalies and priority leads for human investigators to evaluate. It does not determine guilt.
3. **Do not claim planned features are implemented.** The FEATURE_MATRIX.md tracks exactly what is IMPLEMENTED vs PLANNED vs FUTURE.
4. **Do not commit the SQLite database or node_modules.** The `.gitignore` excludes these; they are generated at runtime.
5. **Run tests before pushing.** `python backend/test_demo.py` should always exit 0.
6. **Read PROJECT_STATUS.md** for known bugs, fixed bugs, and limitations before making changes to core pipeline files.

---

## 10. Recommended Next 5 Tasks After This Checkpoint

1. **(HIGH)** Formally test the browser demo end-to-end: start both servers, load the demo case, verify all 12 dashboard panels render correctly.
2. **(HIGH)** Implement the first multi-source ingestion endpoint: `POST /ingest/cdr` accepting a CSV file.
3. **(HIGH)** Add phonetic matching to `entity_resolver.py` using `jellyfish` Double Metaphone for Indian name transliteration variants.
4. **(MEDIUM)** Expand the synthetic dataset in `seed_data.py` to 20+ persons, 10+ cases, and 1000+ CDR records for more realistic graph testing.
5. **(MEDIUM)** Add Human-in-the-Loop Accept/Reject controls to the entity resolution table in the frontend.

---

*Last updated: 2026-09-05 | All data is synthetic | POC checkpoint*
