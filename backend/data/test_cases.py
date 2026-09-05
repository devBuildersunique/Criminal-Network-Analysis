"""
test_cases.py — Six structured test cases for the SIH-189 demo pipeline.

Each test case contains:
  - name: human-readable label
  - input_text: case statement to feed into the pipeline
  - expected_entities: list of (text, type) pairs that MUST appear
  - expected_min_relationships: minimum number of relationships expected
  - expected_resolution: list of (input_text, db_id_or_None, match_status)
  - expected_anomaly: dict with entity_id, min_severity_level (0=NORMAL, 1=LOW, 2=MEDIUM, 3=HIGH)
  - description: what this test is verifying

DISCLAIMER: All data is synthetic. These tests use fictional records only.
"""

# Severity ordering for comparison
SEVERITY_ORDER = {"NORMAL": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "UNKNOWN": -1}

TEST_CASES = [
    # ──────────────────────────────────────────────────────────────────────────
    # TEST 1 — Normal Case
    # A routine interaction; no anomalies expected.
    # ──────────────────────────────────────────────────────────────────────────
    {
        "name": "Normal Case",
        "description": (
            "A routine, low-frequency contact between known entities. "
            "Expects entities extracted, some relationships formed, NO major anomaly."
        ),
        "input_text": (
            "Priya Verma met Ravi Singh in Mumbai on 10 July. "
            "Priya called Ravi twice regarding a financial settlement."
        ),
        "expected_entities": [
            ("Priya Verma", "PERSON"),
            ("Ravi Singh",  "PERSON"),
            ("Mumbai",      "LOCATION"),
        ],
        "expected_min_relationships": 1,
        "expected_resolution": [
            # (input_text, expected_db_id, expected_match_status)
            ("Priya Verma", "P005", "AUTO_MATCH"),
            ("Ravi Singh",  "P003", "AUTO_MATCH"),
            ("Mumbai",      "L002", "AUTO_MATCH"),
        ],
        "expected_anomaly": {
            # P005 is a quiet entity; should NOT flag as HIGH anomaly
            "entity_id": "P005",
            "max_allowed_severity": "MEDIUM",
        },
        "check_no_anomaly_for": ["P003", "P005"],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 2 — Communication Anomaly
    # Very high call volume from P001 (Rahul Sharma) — matches injected data.
    # ──────────────────────────────────────────────────────────────────────────
    {
        "name": "Communication Anomaly",
        "description": (
            "Rahul Sharma contacted Amit Kumar 42 times in 2 days — far above baseline. "
            "Expects communication anomaly to be detected for P001."
        ),
        "input_text": (
            "Rahul Sharma met Amit Kumar in Delhi on 25 August. "
            "Rahul contacted Amit 42 times in two days using phone 9876543210. "
            "Rahul used vehicle DL01AB1234."
        ),
        "expected_entities": [
            ("Rahul Sharma", "PERSON"),
            ("Amit Kumar",   "PERSON"),
            ("Delhi",        "LOCATION"),
            ("9876543210",   "PHONE"),
            ("DL01AB1234",   "VEHICLE"),
        ],
        "expected_min_relationships": 2,
        "expected_resolution": [
            ("Rahul Sharma", "P001", "AUTO_MATCH"),
            ("Amit Kumar",   "P002", "AUTO_MATCH"),
            ("Delhi",        "L001", "AUTO_MATCH"),
        ],
        "expected_anomaly": {
            "entity_id": "P001",
            "min_severity": "MEDIUM",   # Must be at least MEDIUM; ideally HIGH
        },
        "check_no_anomaly_for": [],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 3 — Financial Anomaly
    # Large single transaction from P001 to P002 (Rs 850000 vs ~9000 baseline).
    # ──────────────────────────────────────────────────────────────────────────
    {
        "name": "Financial Anomaly",
        "description": (
            "Rahul Sharma transferred Rs 850000 to Amit Kumar — 90× normal average. "
            "Expects financial anomaly to be detectable for P001."
        ),
        "input_text": (
            "Rahul Sharma transferred Rs 850000 to Amit Kumar on 25 August. "
            "The transfer was made via RTGS from Delhi."
        ),
        "expected_entities": [
            ("Rahul Sharma", "PERSON"),
            ("Amit Kumar",   "PERSON"),
            ("Rs 850000",    "MONEY"),
            ("Delhi",        "LOCATION"),
        ],
        "expected_min_relationships": 1,
        "expected_resolution": [
            ("Rahul Sharma", "P001", "AUTO_MATCH"),
            ("Amit Kumar",   "P002", "AUTO_MATCH"),
        ],
        "expected_anomaly": {
            "entity_id": "P001",
            "min_severity": "MEDIUM",
        },
        "check_no_anomaly_for": [],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 4 — Entity Resolution (name variations)
    # Tests that abbreviated and partial names resolve correctly to P001.
    # ──────────────────────────────────────────────────────────────────────────
    {
        "name": "Entity Resolution",
        "description": (
            "Uses name variations 'R. Sharma' and 'Rahul S.' to verify fuzzy matching "
            "resolves to P001 with appropriate confidence."
        ),
        "input_text": (
            "R. Sharma was seen in Delhi on 15 August. "
            "Rahul S. contacted Amit Kumar using phone 9876543210."
        ),
        "expected_entities": [
            ("9876543210", "PHONE"),
            ("Delhi",      "LOCATION"),
        ],
        "expected_min_relationships": 0,
        "expected_resolution": [
            # At least one of these variations must resolve to P001
            # The NLP may extract them as "R. Sharma" or "Rahul S."
            ("9876543210", "PH001", "AUTO_MATCH"),
            ("Delhi",      "L001",  "AUTO_MATCH"),
        ],
        "expected_resolution_fuzzy": [
            # (input_text_fragment_in_name, target_db_id, min_confidence)
            ("Sharma", "P001", 0.70),   # At least 70% confidence for any "Sharma" match
        ],
        "expected_anomaly": None,
        "check_no_anomaly_for": [],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 5 — Historical Connection
    # Rahul + Ravi Singh co-mentioned; C102 links them.
    # ──────────────────────────────────────────────────────────────────────────
    {
        "name": "Historical Connection",
        "description": (
            "Rahul Sharma and Ravi Singh are both mentioned. Both appear in C102. "
            "Expects cross-case connection to be shown in historical_cases."
        ),
        "input_text": (
            "Rahul Sharma was previously mentioned in Case C102 with Ravi Singh. "
            "Ravi Singh is currently located in Mumbai."
        ),
        "expected_entities": [
            ("Rahul Sharma", "PERSON"),
            ("Ravi Singh",   "PERSON"),
            ("C102",         "CASE"),
            ("Mumbai",       "LOCATION"),
        ],
        "expected_min_relationships": 1,
        "expected_resolution": [
            ("Rahul Sharma", "P001", "AUTO_MATCH"),
            ("Ravi Singh",   "P003", "AUTO_MATCH"),
            ("C102",         "C102", "AUTO_MATCH"),
        ],
        "expected_historical": {
            "case_id": "C102",
            "must_involve": ["P001", "P003"],
        },
        "expected_anomaly": None,
        "check_no_anomaly_for": [],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # TEST 6 — New Entity (not in database)
    # A person not in the DB must NOT be incorrectly force-matched.
    # ──────────────────────────────────────────────────────────────────────────
    {
        "name": "New Entity",
        "description": (
            "Introduces 'Vikram Malhotra' who is NOT in the database. "
            "Expects the resolver to mark this as NEW_ENTITY, not force-match to any existing person."
        ),
        "input_text": (
            "Vikram Malhotra was seen near Delhi on 20 August. "
            "He was driving vehicle DL02XY5678 and contacted an unknown number."
        ),
        "expected_entities": [
            ("Delhi",      "LOCATION"),
            ("DL02XY5678", "VEHICLE"),
        ],
        "expected_min_relationships": 0,
        "expected_resolution": [
            ("Delhi",      "L001",  "AUTO_MATCH"),
            ("DL02XY5678", "V002",  "AUTO_MATCH"),
        ],
        "expected_new_entity": {
            "name_fragment": "Vikram",
            "must_NOT_match_db_id": ["P001", "P002", "P003", "P004", "P005"],
            "allowed_statuses": ["NEW_ENTITY", "POSSIBLE_MATCH"],
        },
        "expected_anomaly": None,
        "check_no_anomaly_for": [],
    },
]
