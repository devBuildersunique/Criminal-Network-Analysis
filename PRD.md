# PRD.md — Product Requirements Document
# SIH 26189: AI-Powered Criminal Network Analysis System
# Ministry of Home Affairs | NCRB, Women Safety Division
# Problem Statement ID: 26189 | Repository: SIH-189 | Theme: Blockchain & Cybersecurity

---

## 1. Product Overview

The **AI-Powered Criminal Network Analysis System** (SIH 26189) is an investigative intelligence-support tool designed for law enforcement agencies and intelligence analysts. It integrates unstructured investigative text (FIRs, surveillance reports) and structured records (CDRs, financial transactions) into a unified, queryable knowledge graph.

The system outputs:
- A unified entity and multi-predicate relationship graph.
- Multi-dimensional behavioral anomaly detection (CDR velocity + financial deviations).
- Historical cross-case connection discovery.
- An explainable investigation priority score for person-pairs.
- An interactive React + Cytoscape.js visual platform.

**Core Mission Invariant:** The system supports human investigators. **It does NOT make criminal determinations, legal verdicts, or probability-of-guilt statements.**

---

## 2. User Personas & Pain Points

### Primary Users
- **Case Investigators (Police / CBI / Crime Branch):** Officers investigating active cases who need to correlate multiple suspects, call logs, and money movements.
- **Supervisory Officers (SP / DIG / Intelligence Chiefs):** Senior personnel reviewing investigative leads, approving escalations, and assessing syndicate structures.

### Key Pain Points Solved
1. **Name Variation Disambiguation:** Resolves spelling variations ("Rahul Sharma", "R. Sharma", "Rahul S") without universal IDs.
2. **Data Silo Fragmentation:** Connects CDR data from telcos, transaction data from banks, and case records from police databases into a single interface.
3. **Cross-Case Blindness:** Automatically surfaces historical co-involvement across closed and open cases.
4. **Behavioral Pattern Blindness:** Isolates anomalous communication spikes and large fund transfers against individual historical baselines.
5. **Investigation Prioritization:** Ranks hundreds of potential entity connections by anomaly severity and network centrality.

---

## 3. Five-Zone Functional Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                   ZONE 1: SECURE MULTI-SOURCE INGESTION                     │
│   [FIRs / Scans · CDR Files · Bank Records · Surveillance · OSINT · History] │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│             ZONE 2: LOCAL AI / NLP & ENTITY RESOLUTION                      │
│   [spaCy Statistical NER · Regex · RapidFuzz Resolution · Alias Alignment]  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│               ZONE 3: HETEROGENEOUS KNOWLEDGE GRAPH                         │
│   [NetworkX Multi-Relational DiGraph · Attributed Edges · Historical Links] │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                 ZONE 4: INTELLIGENCE & ANALYTICS                            │
│   [Graph Centrality/Bridges · CDR Analytics · Financial · IsolationForest]   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│           ZONE 5: INVESTIGATOR INTELLIGENCE PLATFORM                        │
│   [Cytoscape.js UI · Anomaly Cards · XAI Explanations · Human-in-the-Loop]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Functional Requirements

### Zone 1: Ingestion
- **FR-01 (Implemented):** Accept free-form case text via `POST /analyze-case`.
- **FR-02 (Planned):** Accept batch CDR files (CSV), financial transaction logs (CSV), and FIR documents (PDF/Text) with Pydantic schema validation.
- **FR-03 (Planned):** Compute SHA-256 hash upon ingestion to anchor raw evidence in the audit ledger.

### Zone 2: NLP & Entity Resolution
- **FR-04 (Implemented):** Extract 7 entity types (`PERSON`, `LOCATION`, `PHONE`, `VEHICLE`, `MONEY`, `CASE`, `DATE`) using spaCy and high-precision regex.
- **FR-05 (Implemented):** Filter out temporal noise ("the day", "the night") using frozenset rejection.
- **FR-06 (Implemented):** Apply RapidFuzz `token_sort_ratio` against person/location databases; classify as `AUTO_MATCH` (≥90%), `POSSIBLE_MATCH` (70–89%), or `NEW_ENTITY` (<70%).
- **FR-07 (Implemented):** Extract 7 relationship predicates (`CALLED`, `TRANSFERRED_MONEY`, `MET`, `VISITED`, `USED_VEHICLE`, `INVOLVED_IN`, `USES_PHONE`).

### Zone 3: Knowledge Graph
- **FR-08 (Implemented):** Construct directed knowledge graph linking extracted entities and relational predicates with `record_source` metadata.
- **FR-09 (Implemented):** Auto-enrich active graph with historical cases, 60-day CDR call volumes, and bank transfers from SQLite.
- **FR-10 (Implemented):** Convert graph to Cytoscape.js JSON format for web rendering.

### Zone 4: Intelligence & Analytics
- **FR-11 (Implemented):** Compute degree and betweenness centrality on the undirected graph projection.
- **FR-12 (Implemented):** Identify top-3 bridge entities and greedy modularity communities.
- **FR-13 (Implemented):** Profile outgoing CDR patterns and sent financial transactions across an 11-dimensional feature vector.
- **FR-14 (Implemented):** Execute scikit-learn `IsolationForest` anomaly scoring with dual-threshold override for extreme volume spikes.
- **FR-15 (Implemented):** Compute normalized investigation priority score $[0.0, 1.0]$ with plain-language reason lists.

### Zone 5: Investigator Platform
- **FR-16 (Implemented):** Render interactive force-directed (COSE) network graph with color-coded nodes and edge labels.
- **FR-17 (Implemented):** Display entity resolution confidence progress bars, anomaly severity badges, and historical case drawer.
- **FR-18 (Implemented):** Provide click-to-inspect entity detail modal for deep profile analysis.
- **FR-19 (Planned):** Provide `Accept`, `Reject`, `Review`, and `Escalate` decision controls for every AI lead.
- **FR-20 (Planned):** Render interactive event timeline (CDR/transactions) and geospatial map (Leaflet.js).

---

## 5. Security & Evidence Integrity Requirements

- **SR-01 (Planned):** JWT token authentication with optional OTP verification.
- **SR-02 (Planned):** Role-Based Access Control (`INVESTIGATOR`, `SUPERVISOR`, `ADMIN`, `ANALYST`).
- **SR-03 (Planned):** Case-level tenant isolation restricting access to assigned officer rosters.
- **SR-04 (Planned):** Append-only audit logging recording all reads, queries, and lead status updates.
- **SR-05 (Planned):** TLS 1.3 in-transit encryption and SQLCipher at-rest encryption.
- **BC-01 (Planned):** SHA-256 cryptographic fingerprinting of all raw evidence payloads.
- **BC-02 (Planned):** Append-only hash chain linking previous block hash, record hash, timestamp, and actor ID.
- **BC-03 (Planned):** `/integrity/verify/{record_id}` endpoint to detect any unauthorized database tampering.
- **BC-04 (Future):** Permissioned consortium ledger (Hyperledger Fabric) for cross-agency evidence sharing.

---

## 6. Future Federated Intelligence Requirements (Phase 7)

- **FR-FED-01:** Support local training of Temporal Heterogeneous Graph Transformers (T-HGT) on state-level case subgraphs.
- **FR-FED-02:** Central NCRB aggregation using Flower / FedProx frameworks without centralizing raw graph or PII data.
- **FR-FED-03:** Homomorphic encryption of model weight updates in transit.

---

## 7. Success Metrics & Verification

| Metric | Target | Status | Verification Source |
|---|---|---|---|
| **Automated Tests** | 100% Pass | **VERIFIED** | 6/6 tests pass in `backend/test_demo.py` |
| **Live API Health** | 100% Ok | **VERIFIED** | `GET /health` reports backend, DB, NLP, anomaly OK |
| **Pipeline Latency** | < 3.0s (5-entity case) | **VERIFIED** | Benchmark average ~1.2s locally |
| **Anomaly Ground-Truth Recall** | 100% (3/3 injected) | **VERIFIED** | GT001, GT002, GT003 correctly detected |
| **DATE Noise False-Positive Rate** | 0% on benchmark | **VERIFIED** | Filter verified by `verify_api.py` |
| **Synthetic Dataset Coverage** | 100% synthetic | **VERIFIED** | Zero real government PII used |

---

## 8. Risk Register & Mitigations

| Risk | Impact | Likelihood | Mitigation Strategy | Status |
|---|---|---|---|---|
| Indian Name Transliteration Misses | HIGH | HIGH | DB name-scan fallback active; Double Metaphone phonetic matching planned Phase 1 | PARTIALLY MITIGATED |
| False-Positive Entity Merging | HIGH | MEDIUM | High threshold (90%) for `AUTO_MATCH`; `POSSIBLE_MATCH` requires human review | MITIGATED |
| CDR Attribution Error | HIGH | LOW | Filtered strictly to `caller_id == entity_id`; regression tested in TC-2 | MITIGATED |
| Misinterpretation as Guilt | HIGH | MEDIUM | Prominent non-guilt disclaimers across all UI panels and documentation | MITIGATED |
| Local API Vulnerability | HIGH | LOW (Local) | Development on localhost; JWT, RBAC, and TLS planned Phase 5 | OPEN (Phase 5) |
| Evidence Tampering | HIGH | LOW (POC) | SHA-256 append-only hash chain planned Phase 6 | OPEN (Phase 6) |
