# ARCHITECTURE.md — SIH 26189
# System Architecture: AI-Powered Criminal Network Analysis System
# Ministry of Home Affairs | NCRB, Women Safety Division
# Problem Statement ID: 26189 | Repository: SIH-189

---

## 1. Executive System Overview

The **SIH 26189 AI-Powered Criminal Network Analysis System** is an investigative intelligence-support platform designed to assist law enforcement officers and intelligence analysts in identifying hidden connections across disparate, fragmented case data.

The architecture is organized around **Five Distinct Conceptual Zones** coupled with cross-cutting **Security** and **Evidence Integrity** layers:

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
                                       ▲
  ┌────────────────────────────────────┴────────────────────────────────────┐
  │         CROSS-CUTTING: SECURITY & EVIDENCE INTEGRITY                    │
  │   • JWT / RBAC Access Control   • Append-Only Audit Logging             │
  │   • SHA-256 Record Hashing      • Immutable Evidence Hash Chain         │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Five-Zone Architectural Breakdown

### ZONE 1 — Secure Multi-Source Ingestion
* **Objective:** Collect and validate unstructured text and structured tabular data from fragmented investigative channels without storing raw sensitive records on public ledgers.
* **Supported Source Streams:**
  1. *FIRs & Police Reports:* Text statements and scanned PDFs (processed locally).
  2. *Call Detail Records (CDRs):* CSV/tabular files with caller, callee, timestamp, duration, and tower IDs.
  3. *Financial Transactions:* Bank records, UPI/NEFT/RTGS transaction logs.
  4. *Surveillance Reports:* Field intelligence notes and officer observations.
  5. *OSINT & Digital Identifiers:* Safe synthetic social handles, usernames, and associations.
  6. *Criminal History:* Prior case registry records, conviction statuses, and role tags.
  7. *Intelligence Agency Notes:* Cross-jurisdictional intelligence summaries.
* **Ingestion Invariant:** Every ingested file/record is validated against Pydantic schemas, assigned a timestamp, and cryptographically fingerprinted using **SHA-256** to establish a tamper-evident audit record.

```text
                 RAW DATA SOURCES
                        │
         ┌──────────────┼──────────────┐
        FIR            CDR         Financial
         │              │              │
    Surveillance      OSINT        Past Cases
         │              │              │
         └──────────────┬──────────────┘
                        │
                        ▼
               SOURCE VALIDATION
                        │
                        ▼
                 SHA-256 HASH
                        │
                        ▼
             TAMPER-EVIDENT RECORD
                        │
                        ▼
             CORE PROCESSING PIPELINE
```

---

### ZONE 2 — Local AI / NLP + Entity Resolution
* **Objective:** Convert unstructured investigative text into structured, standardized entities and relational triples.
* **Current POC Technology:**
  - **spaCy** (`en_core_web_sm`): Fast, lightweight statistical named entity recognition (NOT an LLM).
  - **Deterministic Regex:** Custom regular expressions for high-precision extraction of structured identifiers (`PHONE`, `VEHICLE`, `MONEY`, `CASE`).
  - **DATE Noise Filter:** Frozenset rejection of non-calendar temporal noise ("the day", "the night").
  - **Database Name-Scan Fallback:** Secondary scan against existing database aliases to recover proper names missed by generic statistical models.
  - **RapidFuzz (`token_sort_ratio`):** Normalized fuzzy string matching to reconcile spelling variations, initials, and aliases against the master registry.
* **Resolution Outcomes:**
  - `AUTO_MATCH` (Confidence ≥ 0.90): Automatically linked to existing database profile.
  - `POSSIBLE_MATCH` (0.70 ≤ Confidence < 0.90): Flagged for mandatory investigator review.
  - `NEW_ENTITY` (Confidence < 0.70): Isolated as a new node (`NEW_{type}_{id}`) to avoid premature false-positive merging.

```text
             Case Text / FIR Statement
                         │
                         ▼
               Regex Pre-Extraction
      (PHONE: \b[6-9]\d{9}\b, VEHICLE: [A-Z]{2}..., MONEY, CASE)
                         │
                         ▼
                 spaCy Statistical NER
               (PERSON, LOCATION, DATE, ORG)
                         │
                         ▼
               DATE Noise Filter
                         │
                         ▼
             DB Name-Scan Fallback
                         │
                         ▼
               Normalized Entities
                         │
                         ▼
            RapidFuzz Entity Resolution
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
  AUTO_MATCH       POSSIBLE_MATCH      NEW_ENTITY
(Conf ≥ 0.90)     (0.70 ≤ Conf < 0.90)  (Conf < 0.70)
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
             Relationship Extraction
 (CALLED, TRANSFERRED_MONEY, MET, VISITED, USED_VEHICLE, INVOLVED_IN, USES_PHONE)
```

---

### ZONE 3 — Heterogeneous Knowledge Graph
* **Objective:** Link disparate entity instances, communication records, financial movements, and historical criminal cases into a unified multi-relational graph.
* **Graph Schema:**
  - **Node Types (6):** `PERSON` (#6366f1), `VEHICLE` (#f59e0b), `LOCATION` (#10b981), `PHONE` (#3b82f6), `CASE` (#ef4444), `ORGANIZATION` (#8b5cf6).
  - **Edge Predicates (7):** `CALLED`, `TRANSFERRED_MONEY`, `MET`, `VISITED`, `USED_VEHICLE`, `INVOLVED_IN`, `USES_PHONE`.
  - **Edge Metadata:** `record_source` (`case_statement`, `CDR`, `financial_record`, `historical_db`), `timestamp`, `frequency`, `amount`, `currency`.
* **Historical Graph Enrichment:**
  When a case is analyzed, the graph automatically queries SQLite for the resolved entities' prior case co-appearances, 60-day CDR call volumes, and historical fund transfers, layering them onto the active case graph.
* **Storage Engine:**
  - *Current POC:* In-memory **NetworkX** `DiGraph` converted to Cytoscape.js JSON.
  - *Prototype / Future Target:* **PostgreSQL** relational persistence transitioning to **Neo4j / Memgraph** for native Cypher graph querying at scale.

---

### ZONE 4 — Intelligence & Analytics
This zone executes multi-modal analytics across structural, behavioral, and statistical vectors:

#### A. Graph Structural Analytics (NetworkX)
- **Degree Centrality:** Measures direct connectivity to highlight major operational hubs.
- **Betweenness Centrality:** Identifies bridge entities controlling communication channels between disconnected syndicates.
- **Top-3 Bridge Detection:** Filters nodes where betweenness exceeds the network average.
- **BFS Neighborhood Exploration:** Traverses 1-hop and 2-hop entity perimeters.
- **Community Detection:** Applies Greedy Modularity to detect cohesive sub-clusters.
- **Shortest Path Analysis:** Calculates shortest multi-hop paths between suspect entities.

#### B. CDR & Communication Analytics
- Profiles outgoing call volume (`calls_per_day`), 7-day communication velocity, unique contact expansion, night-time call frequencies (22:00–06:00), and average conversation durations.

#### C. Financial Network & Fraud Analytics
- Detects velocity spikes in fund transfers, large one-off RTGS/NEFT movements, recipient diversity expansion, and deviation ratio against historical baseline averages.

#### D. Behavioral Anomaly Detection (IsolationForest)
- **Engine:** scikit-learn `IsolationForest` (`n_estimators=100`, `contamination=0.03`, `random_state=42`) evaluated over an **11-dimensional numerical feature vector**.
- **Dual-Threshold Safeguard:** A deterministic fallback flags extreme behavioral spikes (>4× call baseline or >5× transaction baseline) even if the statistical tree isolates the point near normal boundaries.
- **Explainable Anomaly Reasons:** Generates explicit textual justifications (e.g., *"Calls per day: baseline avg 5.5, current 21.0 (3.8x higher than normal)"*).

#### E. Temporal & Geospatial Analytics (Current vs Planned)
- *Temporal (Current):* Timestamps stored in CDR and transaction tables. *Planned:* Vis-timeline interactive sequence view to observe chronological event chains.
- *Geospatial (Current):* Named location string matching. *Planned:* Geocoding with Lat/Lon coordinates, movement path plotting, and Leaflet.js interactive maps.

#### F. Investigation Priority Scoring
Combines multi-modal signals into a normalized composite score $[0.0, 1.0]$:
$$\text{Priority Score} = \min(1.0, S_{\text{direct}} + S_{\text{call\_freq}} + S_{\text{finance}} + S_{\text{shared\_cases}} + S_{\text{anomaly}} + S_{\text{centrality}})$$

---

### ZONE 5 — Investigator Intelligence Platform
* **Objective:** Present complex network intelligence in an intuitive, actionable dashboard with complete explainability and human oversight.
* **Core Views:**
  1. *Case Input & Demo Loader:* Free-form statement input with live backend status.
  2. *Entity Intelligence Panel:* Extracted chips and resolution confidence progress bars.
  3. *Cytoscape.js Network Graph:* Force-directed (COSE) layout, click-to-inspect nodes, edge labels.
  4. *Anomaly Alert Center:* Severity badges (`HIGH`, `MEDIUM`, `LOW`, `NORMAL`) with plain-language bullet points.
  5. *Historical Case Drawer:* Linked past cases with co-accused rosters.
  6. *Priority Connections Panel:* Top investigative leads ranked with explicit justification lists.
  7. *Entity Detail Modal:* Full profile drilldown (active cases, CDR counts, transaction totals).
* **Human-in-the-Loop (HITL) Invariant:**
  - AI outputs are strictly **Investigative Signals**, never legal proof or guilt declarations.
  - Investigators can review, confirm (`Accept`), dispute (`Reject`), annotate, or escalate leads.

---

## 3. Cross-Cutting Layers

### Enterprise Security Layer (Phase 5)
```text
┌────────────────────────────────────────────────────────────────────────┐
│                        SECURITY ARCHITECTURE                           │
├────────────────────────┬───────────────────────────────────────────────┤
│ Authentication         │ JWT Access & Refresh Tokens + OTP Multi-Factor│
│ Authorization (RBAC)   │ Roles: Investigator, Supervisor, Admin, Analyst│
│ Case-Level Isolation   │ Strict tenant/case-level data partitioning   │
│ Transport Security     │ HTTPS / TLS 1.3 encryption for all endpoints  │
│ Storage Encryption     │ SQLCipher / PostgreSQL Transparent Data Enc   │
│ API Hardening          │ Rate Limiting, Input Validation, Secure CORS  │
│ Audit Logging          │ Immutable log of every read, query, and edit  │
└────────────────────────┴───────────────────────────────────────────────┘
```

### Evidence Integrity Layer (Phase 6)
To provide cryptographic chain-of-custody support without storing sensitive personal data on public chains:
1. **Ingestion Hashing:** When an evidence document (FIR, CDR, Bank CSV) is received, calculate its `SHA-256` digest:
   $$H_0 = \text{SHA-256}(\text{Raw Evidence Payload})$$
2. **Append-Only Hash Chain:** Each ledger entry binds the record metadata, timestamp, user ID, current hash, and previous block hash:
   $$H_i = \text{SHA-256}(H_{i-1} \parallel \text{Record ID} \parallel \text{Timestamp} \parallel \text{Actor ID} \parallel H_0)$$
3. **Integrity Verification:** A dedicated `/integrity/verify/{record_id}` endpoint recomputes the chain from genesis to immediately detect any database tampering or unauthorized record alterations.

```text
[ Evidence Record 1 ] ──► Hash H1 ──► [ Block 1: H1 | Genesis ]
                                             │
[ Evidence Record 2 ] ──► Hash H2 ──► [ Block 2: H2 | Prev: Block 1 ]
                                             │
[ Evidence Record 3 ] ──► Hash H3 ──► [ Block 3: H3 | Prev: Block 2 ]
                                             │
                                   Verification Endpoint
                                (Recomputes chain in O(N))
```

---

## 4. Future Federated Intelligence Architecture (Phase 7 / Advanced)

In future multi-state or inter-agency deployments (e.g., sharing intelligence across State Police Crime Branches and central agencies like NCRB/CBI) where raw graph data and personal identifying information (PII) **cannot legally leave local state jurisdictions**:

```text
 STATE / AGENCY A (State Police A)      STATE / AGENCY B (State Police B)
┌────────────────────────────────┐     ┌────────────────────────────────┐
│  • Local PostgreSQL / Neo4j    │     │  • Local PostgreSQL / Neo4j    │
│  • Local Case Graph            │     │  • Local Case Graph            │
│  • Local GNN / T-HGT Model     │     │  • Local GNN / T-HGT Model     │
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

* **Federated Graph ML:** Local nodes train Temporal Heterogeneous Graph Transformers (T-HGT) on local subgraphs.
* **Privacy Guarantee:** Only encrypted weight matrices and gradient updates are transmitted to the central NCRB node via Flower/FedProx. Raw suspect PII and case texts remain entirely on local state air-gapped infrastructure.

---

## 5. Architectural Progression Matrix

| Architecture Component | Current Working POC | Next Prototype (Phases 1–6) | Future Scalable (Phase 7+) |
|---|---|---|---|
| **Data Ingestion** | Free-form case text | Multi-source CSV & PDF parsers | Distributed streaming (Kafka) |
| **NLP & NER** | spaCy + Regex + DB Fallback | Indian Name Phonetic Matching | Local Llama via vLLM for complex OCR |
| **Entity Resolution** | RapidFuzz token sort ratio | Calibrated multi-attribute resolution | Distributed entity disambiguation |
| **Graph Engine** | In-memory NetworkX DiGraph | Persistent SQLite / PostgreSQL | Neo4j / Memgraph Distributed Cluster |
| **Graph Analytics** | Centrality, BFS, Communities | Shortest Path REST API, UI Coloring | Temporal Heterogeneous Graph ML |
| **Anomaly Detection** | IsolationForest (11 features) | Multi-model Network + Temporal | Self-supervised temporal link anomaly |
| **Evidence Integrity** | SHA-256 file hashing | Append-only SQLite Hash Chain | Permissioned Ledger (Hyperledger) |
| **Security Layer** | Open localhost CORS | JWT + OTP + RBAC + Audit Log | Zero-Trust Hardware Security Module |
| **Deployment** | Python / Node Localhost | Docker-Compose & Nginx TLS | Kubernetes & Air-gapped Gov Deployment |
