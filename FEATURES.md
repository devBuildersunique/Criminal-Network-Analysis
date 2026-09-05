# FEATURES.md — SIH 26189
# AI-Powered Criminal Network Analysis System
# Feature Status Across 19 Capability Areas

This document maps the 19 capability areas from the SIH role sheet to the current implementation.

Status values:
- IMPLEMENTED: Working in the current POC codebase (verified by code inspection and test run)
- PARTIAL: Some aspects are implemented; others are missing or incomplete
- PLANNED: Designed and scoped for the next prototype phase; not yet coded
- FUTURE: Intended for a later phase beyond the immediate prototype

---

## AI / NLP

### 1. Document AI / OCR / NLP / LLM

| Capability           | Status   | POC Implementation                     | Prototype Plan                          | Technology            | Priority |
|----------------------|----------|----------------------------------------|-----------------------------------------|-----------------------|----------|
| Text input (free-form)| IMPLEMENTED | Case statement text via POST /analyze-case | Same; add structured document types | FastAPI, React    | DONE     |
| NLP preprocessing    | IMPLEMENTED | spaCy tokenization + regex             | Improve Indian name handling            | spaCy en_core_web_sm  | HIGH     |
| PDF / OCR ingestion  | PLANNED  | Not implemented                        | PDF text extraction for FIR documents   | PyMuPDF or pdfplumber | HIGH     |
| LLM / GPT            | FUTURE   | Not implemented                        | Not in scope for prototype              | Not decided           | LOW      |

Notes:
- The current system is NLP-based (spaCy), not LLM-based. No GPT or transformer is used.
- PDF parsing is needed for real FIR documents in the prototype phase.

---

### 2. Entity Extraction / NER

| Capability       | Status      | POC Implementation                                      | Prototype Plan                         | Technology       | Priority |
|------------------|-------------|--------------------------------------------------------|----------------------------------------|-----------------|----------|
| PERSON           | IMPLEMENTED | spaCy NER + DB name-scan fallback + confidence 0.85-0.9| Larger DB; Indian name corpus          | spaCy + regex   | DONE     |
| LOCATION         | IMPLEMENTED | spaCy GPE + LOC labels; fuzzy-matched to DB            | Add coordinates; more city names       | spaCy           | DONE     |
| PHONE            | IMPLEMENTED | Regex: Indian 10-digit mobile (6-9 prefix)             | Extend to landlines, ISD codes         | Regex           | DONE     |
| VEHICLE          | IMPLEMENTED | Regex: Indian plate format (DL01AB1234)                | No change needed                       | Regex           | DONE     |
| MONEY            | IMPLEMENTED | Regex: Rs / Rs. / rupee prefix                         | Add USD, EUR, crypto amounts           | Regex           | DONE     |
| CASE ID          | IMPLEMENTED | Regex: C102, C10345 format                             | Extend to FIR numbers, court case IDs  | Regex           | DONE     |
| DATE / TIME      | IMPLEMENTED | spaCy DATE/TIME with _DATE_NOISE filter applied        | Add relative date resolution           | spaCy + filter  | DONE     |
| ORGANIZATION     | PARTIAL     | Extracted by spaCy; re-classified to PERSON if DB match| Add ORG graph nodes (banks, companies) | spaCy           | MEDIUM   |
| EMAIL / IP / URL | FUTURE      | Not implemented                                        | OSINT / cyber intelligence phase       | Regex           | LOW      |

---

### 3. Entity Resolution

| Capability           | Status      | POC Implementation                                 | Prototype Plan                             | Technology       | Priority |
|----------------------|-------------|----------------------------------------------------|--------------------------------------------|-----------------|----------|
| Exact match          | IMPLEMENTED | PHONE by number, VEHICLE by plate, CASE by ID      | Same                                       | SQLite query    | DONE     |
| Normalized match     | IMPLEMENTED | Lowercase + punctuation strip before fuzzy compare | Improve: remove prefixes (Shri, Dr, etc.)  | Python string ops| MEDIUM  |
| Fuzzy match          | IMPLEMENTED | RapidFuzz token_sort_ratio >= 90 -> AUTO_MATCH     | Tune thresholds on larger dataset          | RapidFuzz       | DONE     |
| Alias matching       | IMPLEMENTED | DB aliases field split by comma                    | Add more aliases per person                | Python          | DONE     |
| Phonetic match       | PLANNED     | Not implemented                                    | Add Metaphone/Soundex for Indian names     | jellyfish       | HIGH     |
| Confidence score     | IMPLEMENTED | score/100 (0.0 to 1.0) per entity                  | Calibrate on ground-truth dataset          | RapidFuzz score | DONE     |
| NEW_ENTITY handling  | IMPLEMENTED | Entities with score < 70 marked NEW_ENTITY + added as unresolved graph nodes | Same | Python | DONE |
| Human review trigger | PLANNED     | Not in UI                                          | Add Accept/Reject/Review buttons in UI     | React           | HIGH     |

---

### 4. Semantic Search / Information Retrieval

| Capability              | Status | POC Implementation | Prototype Plan                                  | Technology                        | Priority |
|-------------------------|--------|--------------------|-------------------------------------------------|-----------------------------------|----------|
| Keyword search          | PLANNED| Not implemented    | Search entities by name across all cases        | SQLite FTS or Postgres full-text  | MEDIUM   |
| Semantic similarity     | FUTURE | Not implemented    | Document similarity for OSINT/intelligence match| sentence-transformers             | LOW      |
| Information retrieval   | FUTURE | Not implemented    | Cross-case entity search at scale               | Elasticsearch or Postgres         | LOW      |

---

## Graph Intelligence

### 5. Knowledge Graph

| Capability              | Status      | POC Implementation                                  | Prototype Plan                           | Technology   | Priority |
|-------------------------|-------------|-----------------------------------------------------|------------------------------------------|--------------|----------|
| Graph construction      | IMPLEMENTED | NetworkX DiGraph from resolved entities + relationships | Add ORG nodes, financial nodes      | NetworkX     | DONE     |
| Node types              | IMPLEMENTED | PERSON, LOCATION, VEHICLE, PHONE, CASE, ORGANIZATION | Add BANK_ACCOUNT, ORGANIZATION          | NetworkX     | MEDIUM   |
| Edge types              | IMPLEMENTED | CALLED, TRANSFERRED_MONEY, MET, VISITED, USED_VEHICLE, INVOLVED_IN, USES_PHONE | Add ASSOCIATED_WITH, EMPLOYED_BY | NetworkX | MEDIUM |
| Historical enrichment   | IMPLEMENTED | CDR edges + transaction edges from DB added to graph | Same pattern extended to new sources   | SQLite + NetworkX | DONE |
| Evidence / source tag   | IMPLEMENTED | record_source field on each edge (CDR, financial_record, case_statement, CDR_db, transaction_db) | Extend to all ingestion sources | Python | DONE |
| Persistent graph store  | FUTURE      | Not implemented (in-memory only)                    | Neo4j for persistent, queryable graph   | Neo4j        | FUTURE   |

---

### 6. Criminal Network Graph Analytics

| Capability              | Status      | POC Implementation                            | Prototype Plan                     | Technology              | Priority |
|-------------------------|-------------|-----------------------------------------------|------------------------------------|-------------------------|----------|
| Degree analysis         | IMPLEMENTED | in-degree, out-degree, total per node         | No change needed                   | NetworkX                | DONE     |
| Relationship frequency  | IMPLEMENTED | Frequency count on CALLED edges; shown in UI  | Extend to all edge types           | NetworkX edge attributes| DONE     |
| Relationship strength   | IMPLEMENTED | Priority score uses edge count as signal       | Explicit edge weight field         | Python                  | DONE     |
| Shortest path           | IMPLEMENTED | shortest_path() function in graph_analysis.py (not exposed via API yet) | Add GET /graph/path endpoint | NetworkX | MEDIUM |
| Multi-hop analysis      | IMPLEMENTED | BFS depth 1 and 2 for first 5 nodes           | Extend depth; expose full BFS API  | NetworkX                | MEDIUM   |

---

### 7. Influencer / Centrality Detection

| Capability              | Status      | POC Implementation                             | Prototype Plan              | Technology  | Priority |
|-------------------------|-------------|------------------------------------------------|-----------------------------|-------------|----------|
| Degree centrality       | IMPLEMENTED | nx.degree_centrality on undirected graph       | No change needed            | NetworkX    | DONE     |
| Betweenness centrality  | IMPLEMENTED | nx.betweenness_centrality on undirected graph  | No change needed            | NetworkX    | DONE     |
| Bridge detection        | IMPLEMENTED | Nodes with above-average betweenness, top 3    | Expose as separate alert    | NetworkX    | DONE     |
| Most connected entity   | IMPLEMENTED | Max degree centrality node returned in response| Shown in graph analysis panel| NetworkX   | DONE     |
| PageRank / eigenvector  | FUTURE      | Not implemented                                | If larger graph justifies it| NetworkX   | FUTURE   |

---

### 8. Community Detection

| Capability              | Status  | POC Implementation                              | Prototype Plan                        | Technology       | Priority |
|-------------------------|---------|--------------------------------------------------|---------------------------------------|------------------|----------|
| Community detection     | PARTIAL | Greedy modularity communities (NetworkX), requires >=2 edges | Works for demo graph; add Louvain for larger graphs | NetworkX community | MEDIUM |
| Community visualization | PARTIAL | Community count shown in graph panel; no coloring | Color nodes by community in Cytoscape.js | Cytoscape.js | MEDIUM |
| Community change alerts | FUTURE  | Not implemented                                  | Alert when entity switches community  | Python           | FUTURE   |

---

### 9. Graph ML / GNN

| Capability | Status | POC Implementation | Prototype Plan | Technology | Priority |
|------------|--------|--------------------|----|----|----|
| GNN        | FUTURE | Not implemented    | Not in prototype scope; requires labeled graph training data | PyTorch Geometric | FUTURE |

---

## Intelligence Analytics

### 10. Anomaly / Suspicious Pattern Detection

| Capability              | Status      | POC Implementation                                    | Prototype Plan                        | Technology              | Priority |
|-------------------------|-------------|-------------------------------------------------------|---------------------------------------|-------------------------|----------|
| Communication anomaly   | IMPLEMENTED | IsolationForest on CDR features (calls/day, night_calls, new_contacts, etc.) | No change for prototype | scikit-learn | DONE |
| Financial anomaly       | IMPLEMENTED | IsolationForest on transaction features (amount, frequency, amount_deviation) | No change for prototype | scikit-learn | DONE |
| Combined anomaly        | IMPLEMENTED | Single 11-feature vector covers both CDR + financial  | Separate anomaly types in output      | scikit-learn            | DONE     |
| Network anomaly         | PLANNED     | Not implemented as a separate detector                | Detect sudden degree increase, new bridge formation | Python/NetworkX | HIGH |
| Temporal anomaly        | PLANNED     | Timestamps available in DB but no separate temporal detector | Spike detection on time-binned CDR | Python        | HIGH     |
| Explainability          | IMPLEMENTED | Human-readable reasons per flagged feature            | Extend to all anomaly types           | Python                  | DONE     |

Notes:
- Isolation Forest is not described as detecting all anomaly types separately.
  The current 11-feature vector captures communication + financial signals jointly.
- Network anomaly and temporal anomaly require separate feature engineering (planned).
- Feature engineering for each anomaly type:
  Communication: calls/day, unique_contacts, new_contacts, night_calls, avg_call_duration
  Financial: transaction_amount, transaction_frequency, avg_transaction_amount, new_recipients, amount_deviation
  Network (planned): sudden_degree_increase, new_community_bridges, unusual_new_connections
  Temporal (planned): activity_spike_ratio, unusual_hour_distribution, deviation_from_weekly_baseline

---

### 11. CDR / Communication Analytics

| Capability               | Status      | POC Implementation                              | Prototype Plan                       | Technology | Priority |
|--------------------------|-------------|------------------------------------------------|--------------------------------------|------------|----------|
| CDR ingestion            | PARTIAL     | CDR records in SQLite; no CSV/file ingestion    | POST /ingest/cdr endpoint for CSV    | Python     | HIGH     |
| Call frequency analysis  | IMPLEMENTED | calls_per_day, calls_last_7_days per entity    | No change                            | Python     | DONE     |
| Night call detection     | IMPLEMENTED | is_night flag per CDR record; counted per entity| Extend to hourly distribution        | Python     | DONE     |
| Contact network          | IMPLEMENTED | GET /entity/{id}/network returns 1-hop contacts | Add 2-hop; add contact timeline      | SQLite     | MEDIUM   |
| CDR direction bug        | FIXED       | Outgoing-only attribution (caller_id == entity_id) | Verified fixed                    | Python     | DONE     |
| Call duration analysis   | IMPLEMENTED | avg_call_duration in feature vector             | No change                            | Python     | DONE     |

---

### 12. Financial Network / Fraud Analytics

| Capability               | Status      | POC Implementation                              | Prototype Plan                       | Technology | Priority |
|--------------------------|-------------|------------------------------------------------|--------------------------------------|------------|----------|
| Transaction records      | IMPLEMENTED | Transactions in SQLite (sender, receiver, amount, method, timestamp) | Add structured CSV ingestion | Python | HIGH |
| Financial anomaly        | IMPLEMENTED | Transaction amount, frequency, amount_deviation in IsolationForest | No change | scikit-learn | DONE |
| Large transfer detection | IMPLEMENTED | Amount deviation = max_amount / baseline_avg; flagged if high | Add explicit threshold alert | Python | DONE |
| New recipient detection  | IMPLEMENTED | new_recipients counted per window               | No change                            | Python     | DONE     |
| Money network graph      | PARTIAL     | TRANSFERRED_MONEY edges in graph; no dedicated financial node | Add BANK_ACCOUNT nodes | NetworkX | MEDIUM |

---

### 13. Spatio-Temporal / Geospatial Analytics

| Capability               | Status  | POC Implementation                          | Prototype Plan                                 | Technology      | Priority |
|--------------------------|---------|---------------------------------------------|------------------------------------------------|-----------------|----------|
| Location extraction      | IMPLEMENTED | spaCy GPE/LOC + fuzzy match to locations DB | Add more location records                      | spaCy + SQLite  | DONE     |
| Location graph nodes     | IMPLEMENTED | LOCATION nodes in graph; VISITED edges      | No change                                      | NetworkX        | DONE     |
| Coordinates / map view   | PLANNED | Locations stored as name strings only        | Add lat/lon to locations table; map view in UI | GeoPandas, Leaflet.js | HIGH |
| Movement timeline        | PLANNED | Timestamps exist in CDR but not displayed    | Timeline view per entity                       | React           | HIGH     |
| Location clustering      | FUTURE  | Not implemented                              | DBSCAN on location coordinates                 | scikit-learn    | FUTURE   |

---

### 14. Cyber Intelligence

| Capability               | Status  | POC Implementation          | Prototype Plan                                       | Technology | Priority |
|--------------------------|---------|-----------------------------|------------------------------------------------------|------------|----------|
| Phone number extraction  | IMPLEMENTED | Regex extraction + DB resolution | No change for POC                              | Regex      | DONE     |
| Suspicious phone detection| PARTIAL | Phones associated with flagged persons visible in entity modal | Dedicated alert for flagged phones | Python | MEDIUM |
| Digital identifiers      | PLANNED | Not implemented              | Add email, username fields to person record          | Regex      | LOW      |
| IP / domain analysis     | FUTURE  | Not implemented              | OSINT phase only; safe synthetic data                | Not decided| FUTURE   |
| OSINT integration        | FUTURE  | Not implemented              | Safe mock OSINT data ingestion                       | Not decided| FUTURE   |

Note: No offensive cyber capabilities are implemented or planned.

---

## Platform / Engineering

### 15. Data Engineering / Multi-source Integration

| Capability               | Status  | POC Implementation                               | Prototype Plan                                    | Technology | Priority |
|--------------------------|---------|--------------------------------------------------|---------------------------------------------------|------------|----------|
| Single-source ingestion  | IMPLEMENTED | Free-form text via POST /analyze-case          | No change for text                                | FastAPI    | DONE     |
| Synthetic database       | IMPLEMENTED | seed_data.py creates deterministic SQLite DB   | Expand to 20+ persons, 10+ cases                  | SQLite     | HIGH     |
| Multi-source ingestion   | PLANNED | Not implemented                                  | FIR, CDR, financial, surveillance, OSINT pipelines| FastAPI    | HIGH     |
| Unified data schema      | PARTIAL | All data in same SQLite schema; no per-source tags except record_source on edges | Add source_type field to records | Python | HIGH |
| Data validation          | IMPLEMENTED | Pydantic models on all API inputs               | Extend to file ingestion endpoints                | Pydantic   | DONE     |

---

### 16. Security / Privacy / Access Control

| Capability               | Status  | POC Implementation          | Prototype Plan                                        | Technology   | Priority |
|--------------------------|---------|-----------------------------|-------------------------------------------------------|--------------|----------|
| Authentication           | PLANNED | Not implemented (localhost) | JWT-based login with username + OTP                   | FastAPI OAuth2| HIGH    |
| RBAC                     | PLANNED | Not implemented             | Roles: INVESTIGATOR, SUPERVISOR, ADMIN, ANALYST        | FastAPI       | HIGH    |
| Session management       | PLANNED | Not implemented             | Token expiry, refresh tokens                          | JWT           | HIGH    |
| Encryption in transit    | PLANNED | HTTP only (localhost)       | HTTPS via Nginx + Let's Encrypt or internal CA         | Nginx + TLS   | HIGH    |
| Encryption at rest       | PLANNED | SQLite plain text           | SQLCipher (SQLite) or PostgreSQL TDE                   | SQLCipher     | HIGH    |
| Audit logging            | PLANNED | Not implemented             | Append-only audit log for every sensitive access       | Python        | HIGH    |
| Input validation         | PARTIAL | Pydantic validates API input| CORS restriction; rate limiting; input sanitization    | FastAPI       | MEDIUM   |
| Data minimization        | PLANNED | Not implemented             | Return only fields needed per role                     | FastAPI       | MEDIUM   |

---

### 17. Blockchain / Evidence Integrity

| Capability               | Status  | POC Implementation | Prototype Plan                                          | Technology                  | Priority |
|--------------------------|---------|--------------------|----------------------------------------------------------|-----------------------------|----------|
| Evidence hashing         | PLANNED | Not implemented    | SHA-256 hash of each submitted case record               | Python hashlib              | HIGH     |
| Hash chain               | PLANNED | Not implemented    | Linked list of record hashes (prev_hash included)        | Python                      | HIGH     |
| Chain-of-custody log     | PLANNED | Not implemented    | Append-only log: actor, action, record hash, timestamp   | SQLite append-only table    | HIGH     |
| Integrity verification   | PLANNED | Not implemented    | Recompute + compare hash to detect tampering             | Python                      | HIGH     |
| Permissioned ledger      | FUTURE  | Not implemented    | Hyperledger Fabric for multi-party endorsement           | Hyperledger Fabric          | FUTURE   |

What goes on-chain (planned):
  - SHA-256 hash of each evidence record (NOT the raw record)
  - Actor ID, timestamp, action type
  - Previous record hash (chain linkage)

What does NOT go on-chain:
  - Raw criminal records
  - Personal data
  - Case file contents

---

### 18. Dashboard / Visualization / XAI

| Capability               | Status      | POC Implementation                              | Prototype Plan                           | Technology       | Priority |
|--------------------------|-------------|------------------------------------------------|------------------------------------------|------------------|----------|
| Case input               | IMPLEMENTED | CaseInput.jsx with text area and demo loader   | Add file upload for FIR PDFs             | React            | DONE     |
| Entity display           | IMPLEMENTED | EntitiesPanel.jsx with type icons and badges   | No major change                          | React            | DONE     |
| Entity resolution table  | IMPLEMENTED | Shows input, DB match, status, confidence bar  | Add human review buttons                 | React            | DONE     |
| Network graph            | IMPLEMENTED | Cytoscape.js COSE layout, color-coded by type  | Community coloring, edge weight display  | Cytoscape.js     | DONE     |
| Node click detail modal  | IMPLEMENTED | EntityDetailModal.jsx with person profile      | Extend to VEHICLE, LOCATION, PHONE nodes | React            | MEDIUM   |
| Anomaly panel            | IMPLEMENTED | AnomalyPanel.jsx with severity, reasons, baseline comparison | Add Review button | React     | DONE     |
| Historical cases panel   | IMPLEMENTED | HistoryCasesPanel.jsx with shared-entity indicator | No major change                     | React            | DONE     |
| Relationship panel       | IMPLEMENTED | Shows subject, predicate, object, frequency, amount | Add source evidence link          | React            | DONE     |
| Graph analysis panel     | IMPLEMENTED | Centrality, bridge entities, community count   | Add full centrality table                | React            | DONE     |
| Priority scoring panel   | IMPLEMENTED | Per person-pair score, reasons, priority level | No major change                          | React            | DONE     |
| System health bar        | IMPLEMENTED | Polls /health every 15 seconds                 | No change                                | React            | DONE     |
| Timeline view            | PLANNED     | Not implemented                                | CDR + transaction timeline per entity    | React            | HIGH     |
| Map view                 | PLANNED     | Not implemented                                | Leaflet.js map with location markers     | Leaflet.js       | HIGH     |
| XAI / Explanation panel  | PARTIAL     | Anomaly reasons + priority reasons shown       | Dedicated XAI panel explaining every AI output | React     | MEDIUM   |
| Evidence source panel    | PLANNED     | record_source in edge metadata                 | UI panel showing which source produced each connection | React | MEDIUM |

---

### 19. Investigator Workflow / Human-in-the-loop

| Capability               | Status  | POC Implementation                        | Prototype Plan                                         | Technology | Priority |
|--------------------------|---------|-------------------------------------------|--------------------------------------------------------|------------|----------|
| Investigator review      | PLANNED | No Accept/Reject/Review controls in UI    | Add review buttons to entity resolution and anomaly panels | React  | HIGH     |
| Approval workflow        | PLANNED | Not implemented                           | Two-level review: investigator submits, supervisor approves | React | MEDIUM  |
| AI recommendation display| IMPLEMENTED | Priority score and anomaly results shown | Add explicit "AI suggests / investigator decides" framing | React | DONE  |
| Human decision audit     | PLANNED | Not implemented                           | Every Accept/Reject decision logged in audit trail     | Python     | HIGH     |
| Investigator notes       | FUTURE  | Not implemented                           | Freeform notes per entity/connection                   | React + DB | FUTURE  |

---

## Summary Table

| # | Capability Area                      | Status      |
|---|--------------------------------------|-------------|
| 1 | Document AI / OCR / NLP / LLM        | PARTIAL     |
| 2 | Entity Extraction / NER              | IMPLEMENTED |
| 3 | Entity Resolution                    | PARTIAL     |
| 4 | Semantic Search / IR                 | PLANNED     |
| 5 | Knowledge Graph                      | PARTIAL     |
| 6 | Criminal Network Graph Analytics     | IMPLEMENTED |
| 7 | Influencer / Centrality Detection    | IMPLEMENTED |
| 8 | Community Detection                  | PARTIAL     |
| 9 | Graph ML / GNN                       | FUTURE      |
|10 | Anomaly / Suspicious Pattern Detection| PARTIAL    |
|11 | CDR / Communication Analytics        | IMPLEMENTED |
|12 | Financial Network / Fraud Analytics  | IMPLEMENTED |
|13 | Spatio-Temporal / Geospatial         | PLANNED     |
|14 | Cyber Intelligence                   | PARTIAL     |
|15 | Data Engineering / Multi-source      | PARTIAL     |
|16 | Security / Privacy / Access Control  | PLANNED     |
|17 | Blockchain / Evidence Integrity      | PLANNED     |
|18 | Dashboard / Visualization / XAI      | PARTIAL     |
|19 | Investigator Workflow / HITL         | PARTIAL     |
