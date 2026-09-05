# TESTING.md — SIH 26189
# Testing Strategy and Test Cases
# Problem Statement ID: 26189 | Repository: SIH-189

---

## Current Testing Status

```
Checkpoint date:          2026-09-05
Implementation:           READY FOR TESTING
Automated tests (6/6):    PASS  — executed 2026-09-05 during push-readiness audit
API endpoint testing:     PENDING — requires running backend server
Frontend browser testing: PENDING — requires running frontend + backend
End-to-end testing:       PENDING
Manual demo verification: PENDING
Performance benchmarks:   PENDING (targets proposed only, not measured)
```

> **Note:** The automated test suite (`python backend/test_demo.py`) was executed
> during the 2026-09-05 audit and all 6 tests passed. API, frontend, and
> end-to-end tests were NOT performed during this audit and remain pending.
> Do not treat "automated tests pass" as full system verification.

---

## Current Automated Tests

Location: backend/test_demo.py
Test runner: Python (no external test framework; exits with code 0 on all pass, 1 on any fail)
Last run result: 6/6 TESTS PASSED (2026-09-05, push-readiness audit)

Run command:
    cd SIH-189
    python backend/test_demo.py

Optional debug output:
    python backend/test_demo.py --debug



Run command:
    cd SIH-189
    python backend/test_demo.py

Optional debug output:
    python backend/test_demo.py --debug

---

## How the Test Runner Works

Each test case:
1. Resets and reseeds the SQLite database (deterministic, seed=42)
2. Runs the full pipeline (entity extraction, resolution, relationship extraction, graph, anomaly detection)
3. Checks:
   - Expected entities are present in extracted output
   - Expected entities resolve to correct DB IDs with correct match status
   - Minimum relationship count is met
   - Anomaly detection produces correct severity for the target entity
   - Historical case connections are correctly found
   - New entities (not in DB) are correctly classified as NEW_ENTITY

---

## Test Case 1: Normal Case

Name: Normal Case
Purpose: Verify a routine, low-frequency interaction produces no major anomaly.

Input:
    "Priya Verma met Ravi Singh in Mumbai on 10 July.
    Priya called Ravi twice regarding a financial settlement."

Expected entities:
    Priya Verma (PERSON)
    Ravi Singh (PERSON)
    Mumbai (LOCATION)

Expected resolution:
    Priya Verma -> P005 (AUTO_MATCH)
    Ravi Singh  -> P003 (AUTO_MATCH)
    Mumbai      -> L002 (AUTO_MATCH)

Expected anomaly:
    P005 (Priya Verma): severity must NOT exceed MEDIUM

Expected relationships:
    At least 1 (MET or CALLED)

Result: PASS (verified 2026-09-01)

---

## Test Case 2: Communication Anomaly

Name: Communication Anomaly
Purpose: Verify that the injected 42-call spike for P001 is correctly detected.

Input:
    "Rahul Sharma met Amit Kumar in Delhi on 25 August.
    Rahul contacted Amit 42 times in two days using phone 9876543210.
    Rahul used vehicle DL01AB1234."

Expected entities:
    Rahul Sharma (PERSON)
    Amit Kumar (PERSON)
    Delhi (LOCATION)
    9876543210 (PHONE)
    DL01AB1234 (VEHICLE)

Expected resolution:
    Rahul Sharma -> P001 (AUTO_MATCH)
    Amit Kumar   -> P002 (AUTO_MATCH)
    Delhi        -> L001 (AUTO_MATCH)

Expected anomaly:
    P001 (Rahul Sharma): severity must be at least MEDIUM (expected HIGH)

Expected relationships:
    At least 2 (MET + CALLED or MET + USES_PHONE)

Result: PASS (verified 2026-09-01)

---

## Test Case 3: Financial Anomaly

Name: Financial Anomaly
Purpose: Verify that the injected Rs 850000 transaction (90x baseline) is flagged.

Input:
    "Rahul Sharma transferred Rs 850000 to Amit Kumar on 25 August.
    The transfer was made via RTGS from Delhi."

Expected entities:
    Rahul Sharma (PERSON)
    Amit Kumar (PERSON)
    Rs 850000 (MONEY)
    Delhi (LOCATION)

Expected resolution:
    Rahul Sharma -> P001 (AUTO_MATCH)
    Amit Kumar   -> P002 (AUTO_MATCH)

Expected anomaly:
    P001 (Rahul Sharma): severity must be at least MEDIUM (expected HIGH due to amount_deviation)

Expected relationships:
    At least 1 (TRANSFERRED_MONEY)

Result: PASS (verified 2026-09-01)

---

## Test Case 4: Entity Resolution (Name Variations)

Name: Entity Resolution
Purpose: Verify that abbreviated names ("R. Sharma", "Rahul S.") resolve correctly using fuzzy matching.

Input:
    "R. Sharma was seen in Delhi on 15 August.
    Rahul S. contacted Amit Kumar using phone 9876543210."

Expected entities:
    9876543210 (PHONE)
    Delhi (LOCATION)

Expected resolution:
    9876543210 -> PH001 (AUTO_MATCH)
    Delhi      -> L001 (AUTO_MATCH)
    Any "Sharma" mention should resolve to P001 with confidence >= 70%

Expected anomaly:
    None required for this test

Result: PASS (verified 2026-09-01)

---

## Test Case 5: Historical Connection

Name: Historical Connection
Purpose: Verify that persons appearing in the same historical case are correctly linked.

Input:
    "Rahul Sharma was previously mentioned in Case C102 with Ravi Singh.
    Ravi Singh is currently located in Mumbai."

Expected entities:
    Rahul Sharma (PERSON)
    Ravi Singh (PERSON)
    C102 (CASE)
    Mumbai (LOCATION)

Expected resolution:
    Rahul Sharma -> P001 (AUTO_MATCH)
    Ravi Singh   -> P003 (AUTO_MATCH)
    C102         -> C102 (AUTO_MATCH)

Expected historical connections:
    Case C102 must involve both P001 and P003

Expected relationships:
    At least 1 (INVOLVED_IN or MET)

Result: PASS (verified 2026-09-01)

---

## Test Case 6: New Entity

Name: New Entity
Purpose: Verify that a person not in the database is NOT force-matched to any existing person.

Input:
    "Vikram Malhotra was seen near Delhi on 20 August.
    He was driving vehicle DL02XY5678 and contacted an unknown number."

Expected entities:
    Delhi (LOCATION)
    DL02XY5678 (VEHICLE)

Expected resolution:
    Delhi      -> L001 (AUTO_MATCH)
    DL02XY5678 -> V002 (AUTO_MATCH)
    Vikram Malhotra: must NOT resolve to P001-P005 (must be NEW_ENTITY or POSSIBLE_MATCH at most)

Expected anomaly:
    None required

Result: PASS (verified 2026-09-01)

---

## Ground Truth for Anomaly Evaluation

Location: backend/data/anomaly_ground_truth.json

Known injected anomalies:

GT001: Communication spike
  Entity: P001 (Rahul Sharma)
  Event: 42 calls in 2 days (normal avg: 5.5/day)
  Expected: DETECTED, severity HIGH

GT002: Financial anomaly
  Entity: P001 (Rahul Sharma)
  Event: Rs 850000 single transfer (normal avg: Rs ~9000)
  Expected: DETECTED, severity HIGH

GT003: Combined communication + financial
  Entity: P001 (Rahul Sharma)
  Event: Both GT001 and GT002 in same 48-hour window
  Expected: DETECTED, severity HIGH

Normal entities (expected NORMAL or LOW):
  P002, P003, P004, P005

---

## Planned Additional Test Cases

These are test cases to write in Phase 1 (not yet implemented):

### TC-7: Vehicle + Location
Input: "Sameer Khan drove vehicle DL02XY5678 from Mumbai to Delhi."
Expected:
  Entities: Sameer Khan (PERSON), DL02XY5678 (VEHICLE), Mumbai (LOCATION), Delhi (LOCATION)
  Resolution: P004 (Sameer Khan), V002, L002, L001
  Relationships: USED_VEHICLE, VISITED (both locations)

### TC-8: Multi-source Investigation
Simulate case where same person appears in both CDR and financial records:
  Input: Text mentioning a person + phone + money transfer
  Expected: Connections from both CDR and financial edges appear in graph

### TC-9: Free-form Complex Case
Input: Long paragraph with multiple persons, locations, phones, vehicles, cases.
Expected: All entity types correctly extracted; no duplicate edges.

### TC-10: Conflicting Information
Input: Two sentences giving conflicting information (e.g., same vehicle attributed to two people).
Expected: Both attributions captured; investigator can see the conflict.

---

## Manual Browser Test Cases

Run these after starting frontend + backend:

### BT-1: Demo Case Flow
  Action: Click "Load Demo" -> Click "Analyze"
  Expected:
    - Entities panel shows Rahul Sharma, Amit Kumar, Delhi, 9876543210, DL01AB1234
    - Resolution table shows all AUTO_MATCH with >= 90% confidence
    - Graph shows P001, P002, L001, PH001, V001 nodes connected
    - Anomaly panel shows P001 with HIGH severity
    - Priority panel shows P001 <-> P002 as HIGH priority
    - Historical cases panel shows C101 and C102

### BT-2: Node Click Detail
  Action: Click the "Rahul Sharma" node in the graph
  Expected:
    - Entity detail modal opens
    - Shows: name, age, address, aliases
    - Shows case history (C101 suspect, C102 suspect)
    - Shows CDR count and transaction count

### BT-3: Health Status
  Action: Load the page; check top status bar
  Expected: Backend, Database, NLP, Anomaly Model all show "Ready" (green)

### BT-4: New Entity (not in DB)
  Action: Type "Vikram Malhotra was seen in Delhi."
  Expected:
    - Vikram Malhotra appears in entity resolution with NEW_ENTITY badge
    - Confidence < 70%
    - No incorrect force-match to P001-P005

### BT-5: Normal Case (no anomaly)
  Action: Type "Priya Verma met Ravi Singh in Mumbai."
  Expected:
    - P005 and P003 resolved
    - Anomaly panel shows P005 as NORMAL
    - Priority panel shows LOW or MEDIUM priority

---

## Performance Targets (Proposed — Not Yet Measured)

| Metric                              | Target       | Notes                        |
|-------------------------------------|--------------|------------------------------|
| Entity extraction (5-entity text)   | < 200ms      | spaCy on CPU                 |
| Full pipeline (8 steps)             | < 3 seconds  | Including DB queries         |
| Graph analysis (< 20 nodes)         | < 500ms      | NetworkX in-memory           |
| Anomaly detection (1 entity)        | < 100ms      | IsolationForest predict      |
| Frontend render (graph < 20 nodes)  | < 1 second   | Cytoscape.js COSE layout     |

---

## Evaluation Metrics (Proposed Targets — Based on Prototype Dataset)

These targets are proposed and should be measured on the Phase 1 expanded dataset.
They are not measured values; they are goals.

Entity extraction:
  PERSON recall >= 85%
  PERSON precision >= 80%
  PHONE/VEHICLE/CASE/MONEY recall >= 95% (regex-based; should be near-perfect)

Entity resolution:
  AUTO_MATCH accuracy >= 95% (correctly matched AND not incorrectly matched)
  NEW_ENTITY false match rate < 5% (new persons incorrectly matched to existing)

Relationship extraction:
  Precision >= 70%
  Recall >= 60%
  (Rule-based; expected lower than ML-based; sufficient for POC)

Anomaly detection (on ground-truth dataset):
  Detection rate for injected anomalies: 100% (3/3 known anomalies)
  False positive rate for normal entities: < 20%

---

## Known Test Limitations

1. Ground truth only covers P001's anomalies (by design, as P001 has injected data).
2. No F1 measurement yet for entity extraction (requires annotated ground-truth text).
3. Relationship extraction precision/recall not formally measured (rule-based heuristic).
4. All tests use the same synthetic database; more varied datasets are needed in Phase 1.
