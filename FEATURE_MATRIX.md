# FEATURE MATRIX — SIH 26189
# AI-Powered Criminal Network Analysis System
# Ministry of Home Affairs | NCRB, Women Safety Division

---

## Capability Status Definitions
- **IMPLEMENTED**: Code exists in the repository, verified operational, tested, and actively executing.
- **PARTIAL**: Basic or internal functionality exists, but critical interface, file ingestion, or visualization elements remain to be built.
- **PLANNED**: Explicitly designed and scoped for the immediate prototype phases (Phases 1–6).
- **FUTURE**: Intentionally deferred to advanced/production scaling (Phase 7 / Post-Hackathon).

---

## Complete 19-Capability Matrix

| ID | SIH Capability Area | Feature Name | Current Status | Current Implementation | Prototype Target | Technology | Primary Owner | Dependencies | Test Strategy | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| **F-01** | 1. Document AI / OCR / NLP | Free-form Case Statement Ingestion | **IMPLEMENTED** | `POST /analyze-case` endpoint processes raw text | Add structured PDF & multi-line text input | FastAPI, Pydantic | AI/NLP Engineer | None | `test_demo.py` TC-1 | DONE |
| **F-02** | 1. Document AI / OCR / NLP | Structured Document / FIR OCR | **PLANNED** | Not implemented | Extract text from scanned/PDF FIR reports | PyMuPDF, Tesseract | AI/NLP Engineer | Ingestion | Unit test on sample FIR PDF | HIGH |
| **F-03** | 2. Entity Extraction / NER | Core 7-Type Entity Extractor | **IMPLEMENTED** | Extracts PERSON, LOCATION, PHONE, VEHICLE, MONEY, CASE, DATE | Expand regex patterns for foreign phones/currencies | spaCy, Regex | AI/NLP Engineer | F-01 | `test_demo.py` TC-1 to TC-6 | DONE |
| **F-04** | 2. Entity Extraction / NER | DB Name-Scan Fallback | **IMPLEMENTED** | Regex scan of DB names/aliases to catch missed entities | Add phonetic indexing | Python Regex | AI/NLP Engineer | SQLite DB | `test_demo.py` TC-5 | DONE |
| **F-05** | 2. Entity Extraction / NER | Contextual DATE Noise Filter | **IMPLEMENTED** | Frozenset filter rejects vague time-of-day phrases | Maintain filter list | Python frozenset | AI/NLP Engineer | F-03 | `verify_api.py` noise check | DONE |
| **F-06** | 3. Entity Resolution | Multi-Tier Entity Resolver | **IMPLEMENTED** | Exact match (phone/vehicle/case), RapidFuzz (person/loc) | Calibrate confidence weights | RapidFuzz, SQLite | AI/NLP Engineer | F-03, Database | `test_demo.py` TC-4, TC-6 | DONE |
| **F-07** | 3. Entity Resolution | Indian Name Phonetic Matching | **PLANNED** | Not implemented | Double Metaphone / Soundex for Indian transliterations | jellyfish | AI/NLP Engineer | F-06 | Unit test on spelling variants | HIGH |
| **F-08** | 4. Semantic Search / IR | Cross-Case Full-Text Search | **PLANNED** | Not implemented | Full-text keyword search across past case statements | SQLite FTS5 | AI/NLP Engineer | Database | Query latency & precision test | MEDIUM |
| **F-09** | 5. Knowledge Graph | Attributed Multi-Source Graph | **IMPLEMENTED** | NetworkX DiGraph with node types & `record_source` metadata | Add ORG and BANK_ACCOUNT node types | NetworkX | Graph Engineer | F-06 | Cytoscape graph render verification | DONE |
| **F-10** | 5. Knowledge Graph | Historical Evidence Linking | **IMPLEMENTED** | Auto-enriches graph with past cases, CDRs, and txns | Multi-case cross-linking expansion | NetworkX, SQLite | Graph Engineer | F-09, Database | `test_demo.py` TC-5 | DONE |
| **F-11** | 5. Knowledge Graph | Persistent Graph Store | **FUTURE** | In-memory NetworkX only | Neo4j / Memgraph deployment with Cypher query API | Neo4j, Cypher | Graph Engineer | F-09 | Distributed graph query benchmark | FUTURE |
| **F-12** | 6. Criminal Network Graph Analytics | Degree & Betweenness Centrality | **IMPLEMENTED** | Computes degree and betweenness centrality on undirected projection | Weighted centrality based on edge frequency | NetworkX | Graph Engineer | F-09 | Centrality calculation unit tests | DONE |
| **F-13** | 6. Criminal Network Graph Analytics | Shortest Path Analysis | **PARTIAL** | `shortest_path()` function in `graph_analysis.py` | Expose dedicated `GET /graph/path` REST endpoint | NetworkX, FastAPI | Graph Engineer | F-09 | API endpoint response test | MEDIUM |
| **F-14** | 7. Influencer / Centrality Detection | Bridge Entity Detection | **IMPLEMENTED** | Identifies top-3 nodes bridging disconnected clusters | Add bridge evolution tracking over time | NetworkX | Graph Engineer | F-12 | Output validation on synthetic ring | DONE |
| **F-15** | 8. Community Detection | Modularity-Based Clustering | **PARTIAL** | Greedy modularity computed in backend; not colored in UI | Map community IDs to Cytoscape node colors/classes | NetworkX, Cytoscape | Graph Engineer | F-09, Frontend | Visual clustering verification | MEDIUM |
| **F-16** | 9. Graph ML / GNN | Link Prediction & Temporal GNN | **FUTURE** | Not implemented | T-HGT / GNN for hidden link prediction | PyTorch Geometric | Graph Engineer | Labeled Dataset | Precision/Recall on test graph | FUTURE |
| **F-17** | 10. Anomaly Detection | IsolationForest Behavioral Engine | **IMPLEMENTED** | 11-feature vector with secondary threshold override | Separate network and temporal anomaly sub-models | scikit-learn | ML Analyst | Ingestion/DB | `test_demo.py` TC-2, TC-3 | DONE |
| **F-18** | 10. Anomaly Detection | Plain-Language Anomaly Explanation | **IMPLEMENTED** | `_explain_anomaly()` generates structured multiplier reasons | Add baseline vs current comparative chart | Python | ML Analyst | F-17 | Reason string verification | DONE |
| **F-19** | 11. CDR / Communication Analytics | Outgoing Call Profiling & Spike Detection | **IMPLEMENTED** | 6 CDR features (calls/day, 7d, contacts, night calls, duration) | CDR CSV batch ingestion endpoint | Python, SQLite | ML Analyst | F-17, Database | `test_demo.py` TC-2 | DONE |
| **F-20** | 12. Financial Network / Fraud Analytics | Transaction Deviation Analytics | **IMPLEMENTED** | 5 financial features (amount, freq, new recipients, deviation) | Banking CSV batch ingestion endpoint | Python, SQLite | ML Analyst | F-17, Database | `test_demo.py` TC-3 | DONE |
| **F-21** | 13. Geospatial Analytics | Location Coordinate Mapping | **PLANNED** | Location name extraction only | Lat/Lon fields, Leaflet.js interactive map view | Leaflet.js, OpenStreetMap | ML Analyst | Frontend | Map marker render test | MEDIUM |
| **F-22** | 13. Temporal Analytics | Event Sequence Timeline | **PLANNED** | Timestamps in DB; no UI timeline component | Interactive timeline component for CDR/txn events | React, vis-timeline | Frontend Engineer | F-19, F-20 | Chronological event sorting test | MEDIUM |
| **F-23** | 14. Cyber Intelligence | Digital Identifier Extraction | **PARTIAL** | Phone number extraction and owner mapping | Extract emails, IP addresses, usernames, and domains | Python Regex | AI/NLP Engineer | F-03 | Regex test suite on OSINT logs | LOW |
| **F-24** | 15. Data Engineering | Deterministic Synthetic Data Layer | **IMPLEMENTED** | SQLite auto-seeding with 5 people, 365 CDRs, 138 txns | Expand to 20+ entities, 1,000+ CDRs, multi-source tables | SQLite, Python | Backend Engineer | None | Seed generation script test | DONE |
| **F-25** | 15. Data Engineering | Multi-Source Ingestion Pipeline | **PLANNED** | Text input only | Dedicated `/ingest/cdr`, `/ingest/financial`, `/ingest/fir` | FastAPI, Pandas | Backend Engineer | F-24 | CSV/JSON ingestion upload test | HIGH |
| **F-26** | 16. Security & Privacy | Authentication & RBAC | **PLANNED** | Open CORS (`*`), HTTP localhost only | JWT token auth, OTP verification, 4 user roles | FastAPI Security, PyJWT | Security Engineer | Backend | Auth token & role access test | HIGH |
| **F-27** | 16. Security & Privacy | Append-Only Audit Logging | **PLANNED** | Not implemented | Middleware logging all user actions, queries, and exports | SQLite / PostgreSQL | Security Engineer | F-26 | Audit log write & tamper test | HIGH |
| **F-28** | 17. Blockchain / Evidence Integrity | SHA-256 Record Hashing & Hash Chain | **PLANNED** | Not implemented | SHA-256 evidence hashing + linked append-only chain | Python `hashlib` | Security Engineer | F-25 | Tamper-detection verification test | HIGH |
| **F-29** | 17. Blockchain / Evidence Integrity | Permissioned Ledger Sharing | **FUTURE** | Not implemented | Hyperledger Fabric for inter-agency audit sharing | Hyperledger Fabric | Security Engineer | F-28 | Consortium node endorsement test | FUTURE |
| **F-30** | 18. Dashboard & Visualization | Interactive Graph & Intelligence UI | **IMPLEMENTED** | React 19 + Cytoscape.js with live health bar, modal, cards | Add timeline, map, and evidence source breakdown panels | React, Cytoscape.js | Frontend Engineer | Backend API | Frontend build & Cypress/Manual | DONE |
| **F-31** | 19. Investigator Workflow | Non-Guilt Disclaimers & Priority Scoring | **IMPLEMENTED** | Disclaimers on all UI anomaly and priority panels | Structured lead review drawer | React, CSS | Frontend Engineer | F-30 | UI text audit | DONE |
| **F-32** | 19. Investigator Workflow | Human-in-the-Loop Decision Controls | **PLANNED** | Not implemented | Accept/Reject/Review buttons for entity matches & leads | React, FastAPI | Frontend Engineer | F-06, F-30 | User decision state persistence test | HIGH |
