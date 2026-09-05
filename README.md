# SIH 26189 — AI-Powered Criminal Network Analysis System
# Ministry of Home Affairs | National Crime Records Bureau (NCRB), Women Safety Division
# Problem Statement ID: 26189 | Repository: SIH-189 | Theme: Blockchain & Cybersecurity

> **DISCLAIMER:** This project is an investigative intelligence-support Proof-of-Concept (POC) built for Smart India Hackathon.
> **All data used for development and demonstration is 100% synthetic and fictional.**
> The system does NOT connect to any real government or NCRB database. It does NOT make determinations of guilt or criminal liability.

---

## What Is This?

SIH 26189 is an AI-assisted criminal network analysis system. The current POC accepts a case statement, extracts entities and relationships, combines them with synthetic historical records, builds a knowledge graph, detects unusual activity, and presents investigative leads through a dashboard.

The system is an **investigative intelligence tool** — it surfaces analytical signals for human investigators to review. It does not determine guilt. It does not access real records.

```text
  Case Statement
       ↓
  NLP / Entity Extraction (spaCy + Regex)
       ↓
  Entity Resolution (RapidFuzz)
       ↓
  Relationship Extraction (Rule-based)
       ↓
  Synthetic Database (SQLite)
       ↓
  Knowledge Graph (NetworkX)
       ↓
  CDR / Financial / Graph Analytics
       ↓
  Anomaly Detection (IsolationForest)
       ↓
  Priority + Explanation
       ↓
  Interactive Dashboard (React + Cytoscape.js)
```

---

## Current Checkpoint Status

```
Date:               2026-09-05
POC Implementation: COMPLETE
Automated Tests:    6/6 PASS (executed 2026-09-05)
API Testing:        PENDING
Frontend Testing:   PENDING
End-to-End:         PENDING
```

> Testing is **pending** at this checkpoint. The automated pipeline tests pass,
> but API endpoint testing, browser testing, and end-to-end verification have
> not been formally executed. See [TESTING.md](TESTING.md) for full details.

---

## 1. Executive Overview

Law enforcement investigations are often hindered by data fragmentation across paper FIRs, telecom Call Detail Records (CDRs), banking transactions, surveillance logs, and prior criminal histories.

**SIH 26189** solves this by ingesting unstructured case statements into a unified **Heterogeneous Knowledge Graph**, uncovering hidden operational connections, calculating behavioral anomaly signals, and prioritizing leads for human investigator review.

---

## 2. POC → Prototype → Production Roadmap

```text
CURRENT POC (implemented)
  ↓ Text case statement input
  ↓ NLP entity extraction + resolution
  ↓ Rule-based relationship extraction
  ↓ NetworkX knowledge graph
  ↓ IsolationForest anomaly detection
  ↓ React + Cytoscape.js dashboard

NEXT PROTOTYPE (planned)
  ↓ FIR / CDR file / financial CSV ingestion
  ↓ Human-in-the-loop Accept/Reject/Review
  ↓ Indian-name phonetic matching
  ↓ Timeline + Geospatial map view
  ↓ JWT authentication + RBAC

FUTURE ARCHITECTURE (deferred)
  ↓ Neo4j / Memgraph persistent graph store
  ↓ Graph Neural Network (T-HGT) link prediction
  ↓ Federated learning (Flower / FedProx)
  ↓ SHA-256 evidence hash chain
  ↓ Hyperledger Fabric permissioned ledger
  ↓ Local LLM (vLLM) for free-text analysis
```

---

## 3. Five-Zone System Architecture

> **Note:** The diagram below shows the **full intended architecture** across all
> development phases. Zones 1 (file ingestion), the Cross-Cutting Security layer
> (JWT, RBAC, audit logging, blockchain), and Zone 4 GNN components are **PLANNED**
> features, not currently implemented. See [FEATURE_MATRIX.md](FEATURE_MATRIX.md)
> for the exact implementation status of each capability.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                   ZONE 1: SECURE MULTI-SOURCE INGESTION   [PLANNED]         │
│   [FIRs / Scans · CDR Files · Bank Records · Surveillance · OSINT · History] │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│             ZONE 2: LOCAL AI / NLP & ENTITY RESOLUTION   [IMPLEMENTED]      │
│   [spaCy Statistical NER · Regex · RapidFuzz Resolution · Alias Alignment]  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│               ZONE 3: HETEROGENEOUS KNOWLEDGE GRAPH   [IMPLEMENTED]         │
│   [NetworkX Multi-Relational DiGraph · Attributed Edges · Historical Links] │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                 ZONE 4: INTELLIGENCE & ANALYTICS   [PARTIAL]                │
│   [Graph Centrality/Bridges · CDR Analytics · Financial · IsolationForest]   │
│   [GNN Link Prediction — FUTURE]                                             │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│           ZONE 5: INVESTIGATOR INTELLIGENCE PLATFORM   [PARTIAL]            │
│   [Cytoscape.js UI · Anomaly Cards · Explainable Signals]                   │
│   [HITL Accept/Reject · Timeline · Map — PLANNED]                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                       ▲
  ┌────────────────────────────────────┴────────────────────────────────────┐
  │         CROSS-CUTTING: SECURITY & EVIDENCE INTEGRITY   [PLANNED]        │
  │   • JWT / RBAC Access Control   • Append-Only Audit Logging             │
  │   • SHA-256 Record Hashing      • Immutable Evidence Hash Chain         │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Quick Start & Setup

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & npm
- **spaCy English Model** (`en_core_web_sm`) — installed in the step below

### 1. Backend Setup & Run

```bash
# Enter repository root
cd SIH-189

# Create and activate a virtual environment (recommended)
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Download spaCy English model (required — one-time)
python -m spacy download en_core_web_sm

# Seed the synthetic database (one-time; run from repo root)
# This creates backend/criminal_network.db with 5 persons, 365 CDRs, 138 transactions
python -m backend.data.seed_data

# Start FastAPI backend
# The database is also auto-seeded on startup if the DB file is missing.
uvicorn backend.main:app --reload --port 8000
```
Backend API will be live at: `http://localhost:8000` (Swagger UI at `/docs`).

### 2. Frontend Setup & Run

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies and start Vite dev server
npm install
npm run dev
```
Frontend dashboard will be live at: `http://localhost:5173`.

---

## 5. Running Automated Verification

To run the automated 6-test verification suite:
```bash
python backend/test_demo.py
```

To run the live REST API verification script:
```bash
python verify_api.py
```

---

## 6. Repository Directory Structure

```text
SIH-189/
├── backend/
│   ├── anomaly/
│   │   ├── feature_builder.py     # 11-feature CDR/financial numerical vectorizer
│   │   └── isolation_forest.py    # scikit-learn IsolationForest anomaly engine
│   ├── data/
│   │   ├── anomaly_ground_truth.json # Ground truth for injected test anomalies
│   │   ├── seed_data.py           # Deterministic SQLite database seeder
│   │   └── test_cases.py          # Structured pipeline test definitions
│   ├── graph/
│   │   ├── graph_analysis.py      # Degree, betweenness, bridge & community algorithms
│   │   └── graph_builder.py       # NetworkX DiGraph builder & historical enrichment
│   ├── nlp/
│   │   ├── entity_extractor.py    # spaCy NER + regex + DATE noise filter + DB fallback
│   │   ├── entity_resolver.py     # RapidFuzz 3-tier fuzzy entity matcher
│   │   └── relationship_extractor.py # Rule-based 7-predicate relation extractor
│   ├── database.py                # SQLite database helpers & query wrappers
│   ├── main.py                    # FastAPI application & pipeline orchestrator
│   ├── models.py                  # Pydantic request/response data schemas
│   └── test_demo.py               # Automated demo test runner (6/6 tests)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AnomalyPanel.jsx   # Severity cards & baseline comparison
│   │   │   ├── CaseInput.jsx      # Textarea, demo loader & error banners
│   │   │   ├── EntitiesPanel.jsx  # Extracted chips & resolution table
│   │   │   ├── EntityDetailModal.jsx # Profile drilldown modal
│   │   │   ├── HistoryCasesPanel.jsx # Historical cases & priority ranking
│   │   │   └── NetworkGraph.jsx   # Cytoscape.js interactive network graph
│   │   ├── api.js                 # Axios backend API client
│   │   ├── App.jsx                # Main layout & health monitor polling
│   │   └── main.jsx               # React entry point
│   ├── package.json
│   └── vite.config.js
├── verify_api.py                  # Live API endpoint verification script
├── requirements.txt               # Backend Python dependencies
└── [Documentation Files]          # Comprehensive architectural documentation
```

---

## 7. Development Roadmap

- **Phase 0 (Current POC):** Implementation complete — automated tests pass (6/6). API/browser testing pending.
- **Phase 1 (Stabilization & Expansion):** Expand synthetic data, regression tests (TC-7 to TC-12), phonetic matching.
- **Phase 2 (Multi-Source Ingestion):** Ingest FIRs, CDR files, banking CSVs, and surveillance notes.
- **Phase 3 (Intelligence Upgrades):** Temporal/network anomaly detection, map view, and timeline view.
- **Phase 4 (Investigator Platform):** Full human-in-the-loop decision controls, lead escalation, and XAI panels.
- **Phase 5 (Security Layer):** JWT, RBAC, database encryption, and audit logging.
- **Phase 6 (Evidence Integrity):** Append-only hash chain and chain-of-custody verification.
- **Phase 7 (Production & Scale):** PostgreSQL + Neo4j migration and containerized on-premise deployment.

---

## 8. Complete Documentation Index

| Document | Primary Focus & Purpose |
|---|---|
| **[TEAM_HANDOFF.md](TEAM_HANDOFF.md)** | **Start here if you are new — what works, how to run, where things are** |
| **[CHECKPOINT.md](CHECKPOINT.md)** | **Formal checkpoint: implemented / partial / planned / future** |
| [AUTHORITATIVE_PROJECT_SPEC.md](AUTHORITATIVE_PROJECT_SPEC.md) | Single Source of Truth for the entire project |
| [ARCHITECTURE.md](ARCHITECTURE.md) | In-depth 5-zone technical architecture & data flow |
| [ARCHITECTURE_SIMPLE.md](ARCHITECTURE_SIMPLE.md) | 1-page clean architecture diagram for presentations |
| [FEATURE_MATRIX.md](FEATURE_MATRIX.md) | Full capability status matrix (IMPLEMENTED / PARTIAL / PLANNED / FUTURE) |
| [PRD.md](PRD.md) | Product requirements, personas, and success metrics |
| [TECH_STACK.md](TECH_STACK.md) | 3-tier technology breakdown with technical justifications |
| [ROADMAP.md](ROADMAP.md) | 8-phase development roadmap from POC to production |
| [TESTING.md](TESTING.md) | Current testing status, test cases, and verification scripts |
| [TEAM_ROLES.md](TEAM_ROLES.md) | 6 team roles mapped to capabilities and handoffs |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Current POC status, fixed bugs, limitations, and immediate tasks |
