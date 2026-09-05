"""
database.py — SQLite connection + query helpers.
Auto-seeds the DB if empty on first import.
"""

import sqlite3
import os
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "criminal_network.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_seeded():
    """Seed the database if it has no people loaded yet."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM people")
        count = cur.fetchone()[0]
    except sqlite3.OperationalError:
        count = 0
    conn.close()
    if count == 0:
        from backend.data.seed_data import seed_all
        seed_all()


# ─── People ────────────────────────────────────────────────────────────────────

def get_all_people():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM people").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_person(person_id: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM people WHERE id=?", (person_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Vehicles ──────────────────────────────────────────────────────────────────

def get_all_vehicles():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM vehicles").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_vehicle_by_plate(plate: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM vehicles WHERE plate=?", (plate,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Locations ─────────────────────────────────────────────────────────────────

def get_all_locations():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM locations").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Phones ────────────────────────────────────────────────────────────────────

def get_all_phones():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM phones").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_phone_by_number(number: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM phones WHERE number=?", (number,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Cases ─────────────────────────────────────────────────────────────────────

def get_all_cases():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM cases").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_case(case_id: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_cases_for_entity(entity_id: str) -> list:
    conn = get_connection()
    rows = conn.execute(
        """SELECT c.*, ce.role FROM cases c
           JOIN case_entities ce ON c.id = ce.case_id
           WHERE ce.entity_id = ?""",
        (entity_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_entities_for_case(case_id: str) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM case_entities WHERE case_id=?", (case_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── CDR ───────────────────────────────────────────────────────────────────────

def get_cdr_for_entity(entity_id: str) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM cdr WHERE caller_id=? OR callee_id=?",
        (entity_id, entity_id),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_cdr(entity_id: str, days: int = 7) -> list:
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM cdr
           WHERE (caller_id=? OR callee_id=?)
             AND timestamp >= date('now', ?)""",
        (entity_id, entity_id, f"-{days} days"),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Transactions ──────────────────────────────────────────────────────────────

def get_transactions_for_entity(entity_id: str) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM transactions WHERE sender_id=? OR receiver_id=?",
        (entity_id, entity_id),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Behavioral Baseline ───────────────────────────────────────────────────────

def get_baseline(entity_id: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM behavioral_baseline WHERE entity_id=?", (entity_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_baselines() -> list:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM behavioral_baseline").fetchall()
    conn.close()
    return [dict(r) for r in rows]
