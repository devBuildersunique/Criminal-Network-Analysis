# AUTHORITATIVE PROJECT SPECIFICATION
# SIH 26189 — AI-Powered Criminal Network Analysis System
# Ministry of Home Affairs | National Crime Records Bureau (NCRB), Women Safety Division
# Problem Statement ID: 26189 | Repository: SIH-189 | Theme: Blockchain & Cybersecurity
# Last verified: 2026-09-01 | Tests: 6/6 PASS | API: ALL CHECKS PASSED

---

## 0. Terminology & Official Branding

| Term | Official Definition & Usage |
|------|-----------------------------|
| **SIH 26189** | The official Smart India Hackathon problem statement identifier. Must be used consistently across all presentations, documentation, and submissions. |
| **SIH-189** | The local repository folder name only. Used strictly when referencing local directory paths or scripts. |

> **Naming Rule:** Never refer to the project or problem statement as "SIH-189", "SIH189", or "189".

---

## 1. Executive Summary & Core Principle

**SIH 26189** is an investigative intelligence-support platform designed to assist law enforcement officers and intelligence analysts in identifying hidden connections across fragmented case data.

```text
The Core Story of SIH 26189:
"We have a working AI-assisted criminal network analysis Proof-of-Concept (POC) built on synthetic data.
It extracts and resolves entities, constructs and analyzes relationships, detects communication/financial
anomalies, links historical cases, and presents explainable investigative intelligence.
We are now extending it into a secure multi-source investigator platform with evidence-integrity controls.
Federated graph learning and advanced privacy-preserving technologies are future scalability directions."
```

### Ethical & Legal Guardrails (Non-Guilt Invariant)
1. **Investigative Signals Only:** The system produces *investigative signals*, *analytical leads*, and *prioritization metrics* to assist human review.
2. **No Guilt Determinations:** The system **never** makes criminal determinations, legal verdicts, or probability-of-guilt statements.
3. **100% Synthetic Data:** All current demonstration data is strictly synthetic and fictional. The system does not access or claim access to restricted NCRB or police databases. Future real-data deployment is designed as a *drop-in integration with authorized data sources*.

---

## 2. Three-Tier Maturity Framework

| System Layer | Current POC (Implemented Now) | Next Prototype (Phases 1–6 Roadmap) | Future Scalable Architecture (Phase 7+) |
|---|---|---|---|
| **Data Ingestion** | Case statement text input | Dedicated `/ingest` endpoints for FIR (PDF), CDR (CSV), Financial (CSV), Surveillance, OSINT | Distributed real-time stream ingestion (Kafka) |
| **NLP & NER** | spaCy (`en_core_web_sm`) + Regex + DB fallback + DATE filter | Double Metaphone phonetic matching (`jellyfish`) + FIR PDF OCR extraction | Local Llama via vLLM for degraded document comprehension |
| **Entity Resolution** | RapidFuzz 3-tier matching (`AUTO`, `POSSIBLE`, `NEW`) | Calibrated multi-attribute resolution & alias expansion | Distributed cross-jurisdiction entity disambiguation |
| **Knowledge Graph** | In-memory NetworkX `DiGraph` + historical DB enrichment | Persistent PostgreSQL relational graph storage | Neo4j / Memgraph distributed cluster with native Cypher |
| **Analytics & ML** | Centrality, bridges, BFS, communities, IsolationForest (11 features) | Dedicated network/temporal anomaly models, shortest path REST API | Temporal Heterogeneous Graph Transformers (T-HGT) / GNNs |
| **Investigator UI** | React 19 + Cytoscape.js graph, anomaly cards, priority list, modal | Interactive timeline view, Leaflet.js map view, XAI comparison charts | Multi-analyst collaborative workspace |
| **Investigator Workflow** | Explainable justifications & prominent non-guilt disclaimers | Human-in-the-loop decision controls (`Accept`, `Reject`, `Review`, `Escalate`, notes) | Case escalation workflow with supervisory sign-offs |
| **Security Layer** | Localhost execution, controlled synthetic data, basic API | JWT authentication, OTP, RBAC (`INVESTIGATOR`, `SUPERVISOR`, etc.), TLS, audit log | Zero-Trust Hardware Security Module (HSM) |
| **Evidence Integrity** | Conceptually verified SHA-256 hashing | Append-only SHA-256 hash chain + `/integrity/verify` endpoint | Permissioned consortium ledger (Hyperledger Fabric) |
| **Cross-Agency Learning**| Single-node centralized analytics | Multi-tenant case partitioning within one deployment | Privacy-Preserving Federated Learning (Flower + FedProx) |

---

## 3. Verified Runtime State (2026-09-01)

### Backend Environment (Verified)
- **Python:** 3.11.9
- **FastAPI:** 0.141.1
- **spaCy:** 3.7.5 (model: `en_core_web_sm` 3.7.1) — *Statistical NLP, NOT an LLM*
- **RapidFuzz:** 3.14.5
- **NetworkX:** 3.6.1 — *In-memory graph algorithms, NOT Graph ML*
- **scikit-learn:** 1.9.0 (`IsolationForest`) — *Unsupervised ML, NOT Deep Learning*
- **NumPy:** 1.26.4
- **Pydantic:** 2.13.4
- **Database:** SQLite 3 (embedded, auto-seeded)

### Frontend Environment (Verified)
- **Node.js:** v24.18.0
- **React:** ^19.2.8
- **Vite:** ^8.2.2
- **Cytoscape.js:** ^3.34.2
- **Axios:** ^1.20.0
- **Build Status:** `npm run build` completed in 636ms with 0 errors.

### Automated Test Results (Verified)
```
================================================
  SIH-189 DEMO TESTS
================================================
-> Database seeded deterministically.
  [PASS] Normal Case
  [PASS] Communication Anomaly
  [PASS] Financial Anomaly
  [PASS] Entity Resolution
  [PASS] Historical Connection
  [PASS] New Entity
================================================
  6/6 TESTS PASSED
================================================
```

### Live API Verification (Verified)
- `GET /health` → `status=ok`, `database=ok`, `nlp=ok`, `anomaly_model=ok`
- `POST /analyze-case` (comm anomaly) → P001 flagged `ANOMALY/HIGH`, 0 DATE noise, 7 nodes / 11 edges.
- `POST /analyze-case` (full demo) → 14 nodes, 22 edges, 11 relationships, 3 historical cases.

---

## 4. Current POC Architecture vs Target Prototype

### Current Working POC Pipeline
```text
                 CURRENT WORKING POC

              Case Statement Text
                     │
                     ▼
             NLP / Entity NER
      (spaCy + Regex + DB Fallback)
                     │
                     ▼
             Entity Resolution
      (RapidFuzz Token Sort Ratio)
                     │
                     ▼
          Relationship Extraction
        (7 Rule-Based Predicates)
                     │
                     ▼
              Knowledge Graph
    (NetworkX DiGraph + Historical DB)
                     │
          ┌──────────┼──────────┐
          │          │          │
         CDR      Financial   Graph
      Analytics   Analytics   Analytics
          │          │          │
          └──────────┼──────────┘
                     │
                     ▼
              IsolationForest
         (11-Feature Vector + Override)
                     │
                     ▼
           Anomaly Detection
         (Severity + Explanations)
                     │
                     ▼
        Priority Score & Explanations
                     │
                     ▼
          Investigator Dashboard
   (Cytoscape.js Network Visualization)
```

### Target Prototype Pipeline (Extended with Ingestion & Integrity)
```text
FIR / Scans · CDR CSV · Bank CSV · Surveillance · OSINT · History
                             │
                             ▼
                     Secure Ingestion
              (Pydantic Schema Validation)
                             │
                             ▼
                  SHA-256 Evidence Hashing
                (Append-Only Hash Chain)
                             │
                             ▼
                   Local AI / NLP & NER
              (spaCy + Metaphone Phonetics)
                             │
                             ▼
                Heterogeneous Knowledge Graph
                  (PostgreSQL / NetworkX)
                             │
                             ▼
                Multi-Modal Analytics & ML
            (IsolationForest + Temporal/Network)
                             │
                             ▼
                Investigator UI & Analytics
                (Timeline + Leaflet Map + XAI)
                             │
                             ▼
               Investigator HITL Decision Flow
             (Accept · Reject · Review · Notes)
                             │
                             ▼
              Enterprise Security & Audit Trail
               (JWT + RBAC + Immutable Logs)
```

---

## 5. Precise Clarifications on Key Areas

### A. Multi-Source Ingestion
- **Current POC:** Uses a synthetic database and accepts case-statement text.
- **Prototype Status:** The architecture is designed for multi-source ingestion. Dedicated ingestion endpoints for FIRs (`/ingest/fir`), CDRs (`/ingest/cdr`), financial records (`/ingest/financial`), surveillance, and OSINT are **prototype roadmap items (PLANNED)**.

### B. Human-in-the-Loop (HITL)
- **Current POC:** Provides an interactive investigator dashboard, entity inspection modals, explainable anomaly bullets, and non-guilt disclaimers.
- **Prototype Status:** Human-in-the-loop decision controls (`Accept`, `Reject`, `Review`, `Escalate`, and investigator notes) are **part of the prototype roadmap (PLANNED)**. The current POC provides investigator-facing analytical results but does not yet provide the complete decision workflow.

### C. Security Architecture
- **Current POC:** Runs locally on localhost with open CORS for development and controlled synthetic data.
- **Prototype Status:** Security architecture is defined, while production authentication (JWT + OTP), authorization (RBAC), transport encryption (TLS 1.3), storage encryption (SQLCipher), rate limiting, and security audit logging are **prototype roadmap items (PLANNED)**.

### D. Evidence Integrity & Blockchain
- **Current POC:** Cryptographic hashing concepts verified.
- **Prototype Status:** The prototype uses cryptographic evidence-integrity mechanisms (SHA-256 record hashing, append-only hash chains, chain-of-custody logs, and tamper verification) rather than placing sensitive case data on-chain (**PLANNED**). Cryptographic hashing provides tamper detection and chain-of-custody tracking, not automated legal admissibility. A permissioned blockchain (Hyperledger Fabric) is a **future scalability option (FUTURE)**.

### E. AI / ML Distinction
- **Statistical NLP (Active):** spaCy `en_core_web_sm` statistical NER and regex patterns (NOT an LLM).
- **Machine Learning (Active):** scikit-learn `IsolationForest` multivariate anomaly detection (NOT Deep Learning).
- **Graph Analytics (Active):** NetworkX centrality, bridges, BFS, community detection (Graph Analytics, NOT Graph ML).
- **Future AI/ML (Future):** Graph Neural Networks (GNN / T-HGT), Federated Learning (Flower / FedProx), Homomorphic Encryption, and Local Llama/vLLM document understanding are **future advanced research capabilities (FUTURE)**.

---

## 6. Future Privacy-Preserving Federated Architecture (Phase 7)

For future multi-agency intelligence collaboration where state-level raw graphs and suspect PII cannot legally leave local state boundaries:

```text
 STATE / AGENCY A (Local Node)          STATE / AGENCY B (Local Node)
┌────────────────────────────────┐     ┌────────────────────────────────┐
│  • Local PostgreSQL / Neo4j    │     │  • Local PostgreSQL / Neo4j    │
│  • Local Case Graph            │     │  • Local Case Graph            │
│  • Local Graph ML (T-HGT)      │     │  • Local Graph ML (T-HGT)      │
└───────────────┬────────────────┘     └────────────────┬───────────────┘
                │                                       │
      Encrypted Local Gradient                Encrypted Local Gradient
      (Homomorphic Encryption)                (Homomorphic Encryption)
                │                                       │
                └───────────────────┬───────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │       CENTRAL NCRB NODE       │
                    │  • Federated Orchestration    │
                    │    (Flower / FedProx)         │
                    │  • Secure Model Aggregation   │
                    │  • Zero Access to Raw Graphs  │
                    └───────────────┬───────────────┘
                                    │
                         Updated Global Model
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
             STATE A UPDATED                 STATE B UPDATED
```

---

## 7. All 19 SIH Capability Areas Coverage

| # | SIH Capability Area | Current POC Status | Current POC Reality | Prototype Roadmap Target |
|---|---|---|---|---|
| 1 | Document AI / OCR / NLP / LLM | **PARTIAL** | Free-form text input; spaCy statistical NER; regex | Structured FIR PDF text extraction via PyMuPDF |
| 2 | Entity Extraction / NER | **IMPLEMENTED** | 7 types extracted (PERSON, LOC, PHONE, VEHICLE, MONEY, CASE, DATE) | Additional international phone/currency regex |
| 3 | Entity Resolution | **PARTIAL** | RapidFuzz token sort ratio (AUTO/POSSIBLE/NEW tiers) | Double Metaphone phonetic matching for Indian names |
| 4 | Semantic Search / IR | **PLANNED** | Not in current POC | Full-text cross-case search via SQLite FTS5 |
| 5 | Knowledge Graph | **PARTIAL** | NetworkX multi-relational DiGraph + historical enrichment | Persistent PostgreSQL / Neo4j schema expansion |
| 6 | Criminal Network Graph Analytics | **IMPLEMENTED** | Degree & betweenness centrality, BFS, bridge identification | Weighted centrality based on connection frequency |
| 7 | Influencer / Centrality Detection | **IMPLEMENTED** | Top-3 bridge identification, most connected entity detection | Temporal bridge emergence tracking |
| 8 | Community Detection | **PARTIAL** | Greedy modularity computed in backend | Color-coded community clusters in Cytoscape UI |
| 9 | Graph ML / GNN | **FUTURE** | Not in current POC | Temporal Heterogeneous Graph Transformers (T-HGT) |
| 10 | Anomaly / Suspicious Pattern Detection | **PARTIAL** | IsolationForest on 11 features with dual-threshold override | Dedicated network-structure and night-clustering models |
| 11 | CDR / Communication Analytics | **IMPLEMENTED** | Outgoing call velocity, unique contacts, night-time ratio | Batch CDR CSV file upload and processing |
| 12 | Financial Network / Fraud Analytics | **IMPLEMENTED** | Transaction sum, velocity, recipient expansion, deviation ratio | Batch banking CSV file upload and processing |
| 13 | Spatio-Temporal / Geospatial | **PLANNED** | Location names in graph; timestamps in database | Lat/Lon geocoding, Leaflet.js map, Vis-timeline |
| 14 | Cyber Intelligence | **PARTIAL** | Phone number extraction, owner resolution, USES_PHONE edges | Email, IP address, username, domain extraction |
| 15 | Multi-Source Integration | **PARTIAL** | Synthetic relational database + case text ingestion | Ingestion endpoints for CDR, Financial, FIR, OSINT |
| 16 | Security / Privacy / Access Control | **PLANNED** | Localhost execution, basic input validation | JWT auth, OTP, RBAC, TLS 1.3, audit logging |
| 17 | Blockchain / Evidence Integrity | **PLANNED** | Conceptually verified | SHA-256 record hashing, append-only hash chain |
| 18 | Dashboard / Visualization / XAI | **PARTIAL** | Cytoscape graph, anomaly cards, priority list, modal | Interactive timeline, map view, XAI comparison charts |
| 19 | Investigator Workflow / HITL | **PARTIAL** | Explainable outputs & prominent non-guilt disclaimers | Accept/Reject/Review lead decision buttons & notes |

---

## 8. Verified Bug Audit Register

| Bug ID | Severity | Component | Issue Description | Verified Resolution |
|---|---|---|---|---|
| **BUG-001** | HIGH | `feature_builder.py` | Incoming calls were erroneously counted toward caller activity. | **FIXED:** Filtered to `caller_id == entity_id`. Protected by TC-2. |
| **BUG-002** | MEDIUM | `entity_extractor.py` | "the day", "the night" extracted as calendar DATE entities. | **FIXED:** Added `_DATE_NOISE` frozenset filter. Protected by API check. |
| **BUG-003** | LOW | `relationship_extractor.py` | Docstring stated `ASSOCIATED_WITH` while code used `USES_PHONE`. | **FIXED:** Aligned docstring and section comments to `USES_PHONE`. |
| **BUG-004** | LOW | `frontend/src/api.js` | `getEntityHistory()` exported in client but unused in UI. | **DOCUMENTED:** Retained for future historical drawer panel. |

---

## 9. 8-Phase Development Roadmap Summary

- **Phase 0 (Working POC):** ✅ Complete & verified (6/6 tests passing).
- **Phase 1 (Stabilization & Expansion):** Expand synthetic data, regression tests (TC-7 to TC-12), phonetic matching.
- **Phase 2 (Multi-Source Ingestion):** Ingest FIRs, CDR files, banking CSVs, and surveillance notes.
- **Phase 3 (Intelligence Upgrades):** Temporal/network anomaly detection, map view, timeline view, `/graph/path` API.
- **Phase 4 (Investigator Platform):** Full human-in-the-loop decision controls, lead escalation, and XAI panels.
- **Phase 5 (Security Layer):** JWT, RBAC, database encryption, and immutable audit logging.
- **Phase 6 (Evidence Integrity):** Append-only hash chain and chain-of-custody verification.
- **Phase 7 (Production & Scale):** PostgreSQL + Neo4j migration, Docker containerization, and federated graph learning.

---

## 10. Complete Documentation Index

| File | Purpose |
|---|---|
| [AUTHORITATIVE_PROJECT_SPEC.md](file:///c:/Users/ushir/OneDrive/Desktop/SIH-189/AUTHORITATIVE_PROJECT_SPEC.md) | Single Source of Truth for the entire project specification |
| [ARCHITECTURE.md](file:///c:/Users/ushir/OneDrive/Desktop/SIH-189/ARCHITECTURE.md) | In-depth technical architecture, 5 zones, security, and federated learning |
| [ARCHITECTURE_SIMPLE.md](file:///c:/Users/ushir/OneDrive/Desktop/SIH-189/ARCHITECTURE_SIMPLE.md) | 1-page clean architecture diagram for presentations |
| [FEATURE_MATRIX.md](file:///c:/Users/ushir/OneDrive/Desktop/SIH-189/FEATURE_MATRIX.md) | Complete 19-capability status and ownership matrix |
| [PRD.md](file:///c:/Users/ushir/OneDrive/Desktop/SIH-189/PRD.md) | Product requirements, personas, and success metrics |
| [README.md](file:///c:/Users/ushir/OneDrive/Desktop/SIH-189/README.md) | Quick start, verified status, and repository structure |
| [TECH_STACK.md](file:///c:/Users/ushir/OneDrive/Desktop/SIH-189/TECH_STACK.md) | 3-tier technology breakdown with technical justifications |
| [ROADMAP.md](file:///c:/Users/ushir/OneDrive/Desktop/SIH-189/ROADMAP.md) | 8-phase development roadmap from POC to production |
| [TESTING.md](file:///c:/Users/ushir/OneDrive/Desktop/SIH-189/TESTING.md) | Test cases, verification scripts, and quality assurance |
| [TEAM_ROLES.md](file:///c:/Users/ushir/OneDrive/Desktop/SIH-189/TEAM_ROLES.md) | 6 team roles mapped to 5 zones, capabilities, and handoffs |
| [PROJECT_STATUS.md](file:///c:/Users/ushir/OneDrive/Desktop/SIH-189/PROJECT_STATUS.md) | Current POC status, verified bugs, and immediate tasks |
