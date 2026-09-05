# TECH_STACK.md — SIH 26189
# Technology Stack: AI-Powered Criminal Network Analysis System
# Ministry of Home Affairs | NCRB, Women Safety Division
# Problem Statement ID: 26189 | Repository: SIH-189

---

## 1. Currently Used Stack (Verified POC — 2026-09-01)

| Layer | Technology | Verified Version | Purpose & Rationale | Current Status |
|---|---|---|---|---|
| **Backend Runtime** | Python | 3.11.9 | High-performance execution of scientific, NLP, and graph libraries | **ACTIVE** |
| **REST API Framework** | FastAPI | 0.141.1 | High-throughput asynchronous REST framework with auto-generated OpenAPI docs | **ACTIVE** |
| **ASGI Web Server** | Uvicorn (standard) | 0.34.0+ | Lightweight, production-capable ASGI server for FastAPI | **ACTIVE** |
| **Statistical NLP & NER** | spaCy (`en_core_web_sm`) | 3.7.5 (model 3.7.1) | Fast, local entity recognition (PERSON, GPE, LOC, ORG, DATE) without external API dependencies | **ACTIVE** |
| **Pattern Extraction** | Python `re` (Regex) | Built-in | Deterministic, high-precision regex extraction for Indian phones, vehicles, money, and case IDs | **ACTIVE** |
| **Fuzzy Entity Resolution** | RapidFuzz | 3.14.5 | High-speed C++ Levenshtein string distance (`token_sort_ratio`) for alias & name disambiguation | **ACTIVE** |
| **Knowledge Graph Engine** | NetworkX | 3.6.1 | In-memory directed graph construction, centrality metrics, BFS traversal, and community detection | **ACTIVE** |
| **Machine Learning** | scikit-learn (`IsolationForest`) | 1.9.0 | Unsupervised multivariate anomaly detection over 11-dimensional behavioral feature vectors | **ACTIVE** |
| **Numerical Arrays** | NumPy | 1.26.4 | Efficient matrix operations and feature vector transformation for ML pipelines | **ACTIVE** |
| **Data Validation** | Pydantic | 2.13.4 | Strict type checking, request payload validation, and response serialization | **ACTIVE** |
| **Embedded Database** | SQLite 3 | Built-in | Zero-configuration local relational storage for synthetic development and testing | **ACTIVE** |
| **Frontend Framework** | React | ^19.2.8 | Component-based interactive UI with React Hooks and strict state management | **ACTIVE** |
| **Frontend Bundler** | Vite | ^8.2.2 | Ultra-fast ES module build tool with instant Hot Module Replacement (HMR) | **ACTIVE** |
| **Network Visualization** | Cytoscape.js | ^3.34.2 | Browser-native, interactive force-directed (COSE) network graph rendering | **ACTIVE** |
| **HTTP Client** | Axios | ^1.20.0 | Promise-based HTTP client for frontend-to-backend communication | **ACTIVE** |
| **Frontend Runtime** | Node.js | v24.18.0 | JavaScript runtime for package management and client-side compilation | **ACTIVE** |

---

## 2. Planned for Prototype (Phases 1–6)

| Layer | Proposed Technology | Target Phase | Purpose & Rationale |
|---|---|---|---|
| **Phonetic Matching** | `jellyfish` (Double Metaphone) | Phase 1 | Phonetic name matching for Indian language transliteration variants |
| **Document OCR / Parsing** | PyMuPDF (`fitz`) / `pdfplumber` | Phase 2 | Local extraction of text from structured FIR and scanned police reports |
| **Geospatial Mapping** | Leaflet.js / OpenStreetMap | Phase 3 | Interactive web mapping for location coordinates and movement paths |
| **Event Timeline** | Vis-timeline / Chart.js | Phase 3 | Interactive time-series stream visualization for CDR calls and bank transfers |
| **Full-Text Search** | SQLite FTS5 | Phase 4 | High-speed keyword search across past case statement archives |
| **Authentication & AuthZ** | PyJWT + Passlib (`bcrypt`) | Phase 5 | Stateless JSON Web Token authentication and secure password hashing |
| **Evidence Hash Chain** | Python `hashlib` (SHA-256) | Phase 6 | Append-only cryptographic hash chain for evidence tamper detection |
| **Relational Database** | PostgreSQL 16 | Phase 5–7 | Scalable multi-user persistence with concurrent write handling and row-level security |

---

## 3. Future / Advanced Architecture (Phase 7 / Post-Hackathon)

| Layer | Technology | Purpose & Rationale |
|---|---|---|
| **Distributed Graph Database** | Neo4j / Memgraph | Native graph database with Cypher query language for multi-billion edge national graphs |
| **Graph Neural Networks (GNN)** | PyTorch Geometric / T-HGT | Deep learning for temporal link prediction and syndicate hidden association discovery |
| **Federated Learning** | Flower (`flwr`) + FedProx | Decentralized model training across state police agencies without sharing raw case data |
| **Encrypted Model Sharing** | Homomorphic Encryption (TenSEAL) | Privacy-preserving aggregation of gradient updates at the central NCRB node |
| **Local LLM Engine** | Llama-3-8B via vLLM / Ollama | Advanced local semantic document comprehension for degraded, ambiguous handwritten text |
| **Container Orchestration** | Docker + Kubernetes | Standardized deployment on secure, air-gapped government cloud datacenters |

---

## 4. Explicitly Excluded Technologies (Why We Do NOT Use Them in POC)

1. **Cloud-Based LLMs (OpenAI GPT, Claude API):** Unacceptable for law enforcement systems due to strict data sovereignty, air-gapped environment requirements, and risk of hallucinations.
2. **Public Blockchains (Ethereum, Polygon):** Unsuitable for criminal records due to public visibility of data, high transaction gas fees, and immutability conflicts with data privacy/retention laws.
3. **Graph Neural Networks (in current POC):** Overkill for small demonstration graphs and lacks the labeled training datasets required for supervised link prediction.
4. **Heavyweight Message Brokers (Kafka / RabbitMQ):** Unnecessary operational overhead for single-node prototype workloads.
