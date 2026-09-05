"""
seed_data.py — Seeds the SQLite database with fully deterministic synthetic records.
All data is fictional and for demonstration purposes only.

Usage:
    python -m backend.data.seed_data        # reset + reseed
    python backend/data/seed_data.py        # same
"""

import sqlite3
import os
import random
import json
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "criminal_network.db")
GROUND_TRUTH_PATH = os.path.join(os.path.dirname(__file__), "anomaly_ground_truth.json")

SEED = 42


def get_connection():
    db_path = os.path.abspath(DB_PATH)
    return sqlite3.connect(db_path)


def drop_tables(conn):
    """Drop all tables so we can start fresh."""
    cur = conn.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS people;
        DROP TABLE IF EXISTS vehicles;
        DROP TABLE IF EXISTS locations;
        DROP TABLE IF EXISTS phones;
        DROP TABLE IF EXISTS cases;
        DROP TABLE IF EXISTS case_entities;
        DROP TABLE IF EXISTS cdr;
        DROP TABLE IF EXISTS transactions;
        DROP TABLE IF EXISTS behavioral_baseline;
    """)
    conn.commit()


def create_tables(conn):
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS people (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            aliases TEXT,
            age INTEGER,
            address TEXT
        );

        CREATE TABLE IF NOT EXISTS vehicles (
            id TEXT PRIMARY KEY,
            plate TEXT NOT NULL,
            owner_id TEXT,
            make TEXT,
            color TEXT
        );

        CREATE TABLE IF NOT EXISTS locations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            state TEXT
        );

        CREATE TABLE IF NOT EXISTS phones (
            id TEXT PRIMARY KEY,
            number TEXT NOT NULL,
            owner_id TEXT
        );

        CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY,
            title TEXT,
            status TEXT,
            date TEXT
        );

        CREATE TABLE IF NOT EXISTS case_entities (
            case_id TEXT,
            entity_id TEXT,
            entity_type TEXT,
            role TEXT,
            PRIMARY KEY (case_id, entity_id)
        );

        CREATE TABLE IF NOT EXISTS cdr (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caller_id TEXT,
            callee_id TEXT,
            timestamp TEXT,
            duration_sec INTEGER,
            is_night INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id TEXT,
            receiver_id TEXT,
            amount REAL,
            timestamp TEXT,
            method TEXT
        );

        CREATE TABLE IF NOT EXISTS behavioral_baseline (
            entity_id TEXT PRIMARY KEY,
            calls_per_day REAL,
            calls_last_7_days REAL,
            unique_contacts REAL,
            new_contacts REAL,
            night_calls REAL,
            avg_call_duration REAL,
            transaction_amount REAL,
            transaction_frequency REAL,
            avg_transaction_amount REAL,
            new_recipients REAL,
            amount_deviation REAL
        );
    """)
    conn.commit()


# ─── Static reference data ────────────────────────────────────────────────────

def seed_people(conn):
    people = [
        ("P001", "Rahul Sharma",  "R. Sharma,Rahul S",    32, "Sector 15, Delhi"),
        ("P002", "Amit Kumar",    "A. Kumar",              28, "Lajpat Nagar, Delhi"),
        ("P003", "Ravi Singh",    "R. Singh",              45, "Andheri, Mumbai"),
        ("P004", "Sameer Khan",   "S. Khan,Sameer K",      35, "Bandra, Mumbai"),
        ("P005", "Priya Verma",   "P. Verma",              27, "Connaught Place, Delhi"),
    ]
    conn.executemany("INSERT OR IGNORE INTO people VALUES (?,?,?,?,?)", people)
    conn.commit()


def seed_vehicles(conn):
    vehicles = [
        ("V001", "DL01AB1234", "P001", "Honda City",   "White"),
        ("V002", "DL02XY5678", "P004", "Swift Dzire",  "Silver"),
    ]
    conn.executemany("INSERT OR IGNORE INTO vehicles VALUES (?,?,?,?,?)", vehicles)
    conn.commit()


def seed_locations(conn):
    locations = [
        ("L001", "Delhi",  "Delhi"),
        ("L002", "Mumbai", "Maharashtra"),
    ]
    conn.executemany("INSERT OR IGNORE INTO locations VALUES (?,?,?)", locations)
    conn.commit()


def seed_phones(conn):
    phones = [
        ("PH001", "9876543210", "P001"),
        ("PH002", "9123456780", "P002"),
    ]
    conn.executemany("INSERT OR IGNORE INTO phones VALUES (?,?,?)", phones)
    conn.commit()


def seed_cases(conn):
    cases = [
        ("C101", "Narcotics Supply Network",  "Closed", "2023-03-10"),
        ("C102", "Financial Fraud Ring",       "Active",  "2023-11-15"),
        ("C103", "Vehicle Theft Syndicate",   "Closed", "2024-01-20"),
    ]
    conn.executemany("INSERT OR IGNORE INTO cases VALUES (?,?,?,?)", cases)
    conn.commit()


def seed_case_entities(conn):
    links = [
        # C101 — Narcotics
        ("C101", "P001", "PERSON",   "suspect"),
        ("C101", "P004", "PERSON",   "associate"),
        ("C101", "L001", "LOCATION", "primary_location"),
        # C102 — Financial Fraud
        ("C102", "P001", "PERSON",   "suspect"),
        ("C102", "P002", "PERSON",   "associate"),
        ("C102", "P003", "PERSON",   "witness"),
        ("C102", "L001", "LOCATION", "primary_location"),
        # C103 — Vehicle Theft
        ("C103", "P003", "PERSON",   "suspect"),
        ("C103", "P004", "PERSON",   "associate"),
        ("C103", "V001", "VEHICLE",  "evidence"),
        ("C103", "V002", "VEHICLE",  "evidence"),
        ("C103", "L002", "LOCATION", "primary_location"),
    ]
    conn.executemany("INSERT OR IGNORE INTO case_entities VALUES (?,?,?,?)", links)
    conn.commit()


# ─── Deterministic synthetic CDR (300–500 records) ──────────────────────────

def seed_cdr(conn):
    """
    Generate ~400 deterministic CDR records:
      - 60 days of historical normal activity (≈350 rows, across all 5 persons)
      - Normal current activity for P002..P005 (≈10 rows)
      - Injected anomaly window for P001: 42 calls in 2 days (2024-08-24/25)
    """
    rng = random.Random(SEED)
    records = []
    PEOPLE = ["P001", "P002", "P003", "P004", "P005"]
    DURATIONS = {"P001": 120, "P002": 140, "P003": 100, "P004": 130, "P005": 90}

    # 1. Historical normal activity: 60 days (2024-06-25 to 2024-08-23)
    start_date = datetime(2024, 6, 25)
    for day_offset in range(60):
        current_day = start_date + timedelta(days=day_offset)
        for caller in PEOPLE:
            n_calls = rng.choices([0, 1, 2], weights=[0.25, 0.50, 0.25])[0]
            for _ in range(n_calls):
                callee = rng.choice([p for p in PEOPLE if p != caller])
                hour = rng.randint(8, 21)
                minute = rng.randint(0, 59)
                is_night = 1 if (hour >= 22 or hour < 6) else 0
                dur = max(20, int(rng.gauss(DURATIONS[caller], 20)))
                ts = (current_day + timedelta(hours=hour, minutes=minute)).strftime("%Y-%m-%d %H:%M:%S")
                records.append((caller, callee, ts, dur, is_night))

    # 2. Current normal activity (2024-08-24 & 2024-08-25) for P002, P003, P004, P005
    for day_offset in [60, 61]:
        current_day = start_date + timedelta(days=day_offset)
        for caller in ["P002", "P003", "P004", "P005"]:
            n_calls = rng.choices([0, 1, 2], weights=[0.25, 0.55, 0.20])[0]
            for _ in range(n_calls):
                callee = rng.choice([p for p in PEOPLE if p != caller])
                hour = rng.randint(9, 19)
                minute = rng.randint(0, 59)
                dur = max(20, int(rng.gauss(DURATIONS[caller], 20)))
                ts = (current_day + timedelta(hours=hour, minutes=minute)).strftime("%Y-%m-%d %H:%M:%S")
                records.append((caller, callee, ts, dur, 0))

    # 3. INJECTED ANOMALY — P001 makes 42 calls to P002 in 2 days (2024-08-24 & 2024-08-25)
    day1 = datetime(2024, 8, 24)
    day2 = datetime(2024, 8, 25)
    anomaly_hours_day1 = [1, 1, 2, 2, 3, 3, 4, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    anomaly_hours_day2 = [0, 1, 2, 6, 8, 10, 12, 14, 16, 18, 20, 22, 23, 0, 1]

    for h in anomaly_hours_day1:
        ts = (day1 + timedelta(hours=h, minutes=rng.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S")
        is_night = 1 if (h >= 22 or h < 6) else 0
        records.append(("P001", "P002", ts, rng.randint(15, 45), is_night))

    for h in anomaly_hours_day2:
        ts = (day2 + timedelta(hours=h, minutes=rng.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S")
        is_night = 1 if (h >= 22 or h < 6) else 0
        records.append(("P001", "P002", ts, rng.randint(15, 45), is_night))

    # Sort chronologically
    records.sort(key=lambda r: r[2])

    conn.executemany(
        "INSERT INTO cdr (caller_id, callee_id, timestamp, duration_sec, is_night) VALUES (?,?,?,?,?)",
        records,
    )
    conn.commit()
    print(f"[seed_data] Inserted {len(records)} CDR records.")
    return len(records)


# ─── Deterministic synthetic transactions (100–200 records) ──────────────────

def seed_transactions(conn):
    """
    Generate ~130 deterministic transactions:
      - 60 days of normal small/medium transactions across network
      - 1 injected large transaction (P001 → P002, Rs 850000 on 2024-08-25)
    """
    rng = random.Random(SEED + 1)
    records = []
    PEOPLE = ["P001", "P002", "P003", "P004", "P005"]
    METHODS = ["UPI", "NEFT", "IMPS", "RTGS"]
    AMOUNT_PARAMS = {
        "P001": (7000, 2000), "P002": (6500, 1800), "P003": (5000, 1500),
        "P004": (7000, 2000), "P005": (4500, 1200),
    }

    start_date = datetime(2024, 6, 25)
    for day_offset in range(60):
        current_day = start_date + timedelta(days=day_offset)
        # ~2 transactions per day across all 5 persons
        for sender in PEOPLE:
            if rng.random() < 0.45:
                receiver = rng.choice([p for p in PEOPLE if p != sender])
                mean_amt, sigma_amt = AMOUNT_PARAMS[sender]
                amount = round(max(500, rng.gauss(mean_amt, sigma_amt)), 2)
                method = rng.choice(METHODS[:3])
                day_str = current_day.strftime("%Y-%m-%d")
                records.append((sender, receiver, amount, day_str, method))

    # Normal activity on 2024-08-24 & 2024-08-25 for other persons
    records.append(("P002", "P003", 6000.0, "2024-08-24", "UPI"))
    records.append(("P004", "P005", 5500.0, "2024-08-24", "NEFT"))

    # INJECTED FINANCIAL ANOMALY: P001 → P002 Rs 850000 on 2024-08-25
    records.append(("P001", "P002", 850000.0, "2024-08-25", "RTGS"))

    records.sort(key=lambda r: (r[3], r[0]))

    conn.executemany(
        "INSERT INTO transactions (sender_id, receiver_id, amount, timestamp, method) VALUES (?,?,?,?,?)",
        records,
    )
    conn.commit()
    print(f"[seed_data] Inserted {len(records)} transaction records.")
    return len(records)


# ─── Behavioral baseline ──────────────────────────────────────────────────────

def seed_behavioral_baseline(conn):
    baselines = [
        # entity_id, calls/day, calls_7d, unique_contacts, new_contacts,
        # night_calls, avg_call_duration, txn_amount, txn_freq, avg_txn, new_recipients, amount_deviation
        ("P001", 5.5,  38.0, 4.0, 1.0, 1.0, 120.0,  9000.0, 1.5,  9000.0, 0.3, 1.2),
        ("P002", 7.0,  49.0, 5.0, 1.5, 2.0, 140.0,  7500.0, 1.0,  7500.0, 0.5, 1.1),
        ("P003", 4.0,  28.0, 3.0, 0.5, 0.5, 100.0,  6000.0, 0.5,  6000.0, 0.3, 1.0),
        ("P004", 6.0,  42.0, 4.5, 1.0, 1.5, 130.0,  8000.0, 1.0,  8000.0, 0.5, 1.1),
        ("P005", 3.5,  24.0, 3.0, 0.5, 0.3,  90.0,  5000.0, 0.8,  5000.0, 0.3, 1.0),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO behavioral_baseline VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        baselines,
    )
    conn.commit()


# ─── Ground truth storage ─────────────────────────────────────────────────────

def save_ground_truth():
    ground_truth = {
        "description": (
            "Known injected anomalies in the synthetic dataset. "
            "Used for demo evaluation only. Not used during IsolationForest training."
        ),
        "anomalies": [
            {
                "id": "GT001",
                "type": "communication_spike",
                "entity_id": "P001",
                "entity_name": "Rahul Sharma",
                "description": "42 calls in 2 days (normal avg: 5.5/day)",
                "period": {"start": "2024-08-24", "end": "2024-08-25"},
                "expected_detection": True,
                "expected_severity": "HIGH",
                "details": {
                    "anomalous_calls_per_day": 21.0,
                    "normal_avg_calls_per_day": 5.5,
                    "night_calls_injected": 15,
                    "normal_avg_night_calls": 1.0,
                },
            },
            {
                "id": "GT002",
                "type": "financial_anomaly",
                "entity_id": "P001",
                "entity_name": "Rahul Sharma",
                "description": "Rs 850000 single transfer (normal avg: Rs ~9000)",
                "period": {"date": "2024-08-25"},
                "expected_detection": True,
                "expected_severity": "HIGH",
                "details": {
                    "anomalous_transaction": 850000,
                    "normal_avg_transaction": 9000,
                    "recipient": "P002",
                    "method": "RTGS",
                },
            },
            {
                "id": "GT003",
                "type": "communication_combined",
                "entity_id": "P001",
                "entity_name": "Rahul Sharma",
                "description": "Combined comm + financial anomaly within same 48-hour window",
                "period": {"start": "2024-08-24", "end": "2024-08-25"},
                "expected_detection": True,
                "expected_severity": "HIGH",
                "details": {
                    "note": "Combination of GT001 and GT002 in same window amplifies anomaly signal"
                },
            },
        ],
        "normal_entities": ["P002", "P003", "P004", "P005"],
        "generated_with_seed": SEED,
        "generation_timestamp": "2024-08-28T00:00:00",
    }
    gt_path = os.path.abspath(GROUND_TRUTH_PATH)
    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2)
    print(f"[seed_data] Ground truth saved to {gt_path}")


def seed_all(conn=None):
    close = False
    if conn is None:
        conn = get_connection()
        close = True
    create_tables(conn)
    seed_people(conn)
    seed_vehicles(conn)
    seed_locations(conn)
    seed_phones(conn)
    seed_cases(conn)
    seed_case_entities(conn)
    seed_cdr(conn)
    seed_transactions(conn)
    seed_behavioral_baseline(conn)
    save_ground_truth()
    if close:
        conn.close()
    print("[seed_data] Database seeded successfully.")


def reset_all():
    random.seed(SEED)
    conn = get_connection()
    print("[seed_data] Dropping all tables...")
    drop_tables(conn)
    print("[seed_data] Recreating and seeding...")
    seed_all(conn)
    conn.close()
    print("[seed_data] Reset complete. Database is deterministic.")


if __name__ == "__main__":
    reset_all()
