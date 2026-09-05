# SIH 26189 — One-Page Architecture Overview
# AI-Powered Criminal Network Analysis System
# Ministry of Home Affairs | NCRB, Women Safety Division

---

## 1. End-to-End System Pipeline

```text
                     DATA SOURCES
     [FIR / Reports · CDR · Financial · Surveillance · OSINT · History]
                          ↓
             ZONE 1: SECURE INGESTION
     [Validation · Ingestion Parsers · SHA-256 Record Hashing]
                          ↓
             ZONE 2: LOCAL AI / NLP
     [spaCy Statistical NER · Regex Extraction · DB Name-Scan Fallback]
                          ↓
             ZONE 2: ENTITY RESOLUTION
     [RapidFuzz Fuzzy Matching · Alias Reconciliation · New Entity Isolation]
                          ↓
             ZONE 3: HETEROGENEOUS KNOWLEDGE GRAPH
     [NetworkX DiGraph · Multi-Source Attributed Edges · Historical Enrichment]
                          ↓
┌───────────────────────┬───────────────────────┬───────────────────────┐
│   GRAPH ANALYTICS     │     CDR ANALYTICS     │  FINANCIAL ANALYTICS  │
│  Centrality · Bridges │   Calls/Day · Spikes  │  Amount · Freq · Dev  │
│  BFS · Communities    │  Night Calls · Rels   │  New Recipient Rels   │
└───────────────────────┴───────────────────────┴───────────────────────┘
                          ↓
             ZONE 4: ANOMALY DETECTION
     [scikit-learn IsolationForest · 11 Behavioral Features · Dual-Threshold]
                          ↓
             ZONE 4: PRIORITY & EXPLANATION
     [Composite Investigation Priority Score · Plain-Language Justifications]
                          ↓
             ZONE 5: INVESTIGATOR PLATFORM
     [Interactive Cytoscape.js Graph · Entity Modal · Anomaly Cards · Timeline]
                          ↓
             INVESTIGATOR DECISION & WORKFLOW
     [Human-in-the-Loop: Accept Match · Flag for Review · Reject Lead · Notes]
                          ↓
             EVIDENCE INTEGRITY & AUDIT
     [Append-Only SHA-256 Hash Chain · Tamper Detection · Immutable Audit Log]
```

---

## 2. Security Across All Layers (Cross-Cutting)

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                      ENTERPRISE SECURITY LAYER                          │
│  • Authentication: JWT Tokens + Multi-Factor OTP                       │
│  • Authorization: Role-Based Access Control (Investigator/Supervisor/Admin) │
│  • Data Protection: Case-Level Isolation · TLS In-Transit · SQLite/SQLCipher At-Rest │
│  • Auditability: Append-Only Immutable Audit Log of All User Actions    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Current vs Prototype vs Future Progression

```text
┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
│     CURRENT POC         │    NEXT PROTOTYPE       │    FUTURE SCALABLE      │
│     (WORKING NOW)       │    (BUILDING NEXT)      │    (POST-HACKATHON)     │
├─────────────────────────┼─────────────────────────┼─────────────────────────┤
│ • Free-form Text Input  │ • Multi-Source CSV/PDF  │ • Neo4j Distributed DB  │
│ • spaCy 7-Type NER      │ • Leaflet Geospatial Map│ • Local Llama/vLLM      │
│ • RapidFuzz Resolution  │ • Time-Series Timeline  │ • Temporal GNN / T-HGT  │
│ • NetworkX DiGraph      │ • SHA-256 Hash Chain    │ • Federated Learning    │
│ • IsolationForest ML    │ • JWT + RBAC Security   │   (Flower + FedProx)    │
│ • Priority Scoring      │ • HITL Accept/Reject UI │ • Homomorphic Encryption│
│ • React + Cytoscape UI  │ • PostgreSQL Migration  │ • Multi-Agency Sharing  │
└─────────────────────────┴─────────────────────────┴─────────────────────────┘
```

---

## 4. Key Guarantees

1. **Investigative Signal, NOT Guilt:** The system scores anomalous patterns and connection strength to prioritize human review. It never determines legal guilt or labels individuals as offenders.
2. **100% Synthetic Data in POC:** Demonstrations use strictly synthetic and fictional data. No real NCRB, police, or classified records are processed.
3. **Deterministic & Verified:** The 8-step pipeline runs in < 3 seconds with deterministic automated test suites (6/6 passing).
