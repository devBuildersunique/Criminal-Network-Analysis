"""
feature_builder.py
Converts CDR + transaction records into numerical feature vectors
suitable for IsolationForest anomaly detection.

Features per entity:
  - calls_per_day
  - calls_last_7_days
  - unique_contacts
  - new_contacts          (contacts not in baseline)
  - night_calls
  - avg_call_duration
  - transaction_amount    (total in current period)
  - transaction_frequency (count in current period)
  - avg_transaction_amount
  - new_recipients        (recipients not seen historically)
  - amount_deviation      (ratio of current max transaction to baseline avg)
"""

import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import backend.database as db

FEATURE_KEYS = [
    "calls_per_day",
    "calls_last_7_days",
    "unique_contacts",
    "new_contacts",
    "night_calls",
    "avg_call_duration",
    "transaction_amount",
    "transaction_frequency",
    "avg_transaction_amount",
    "new_recipients",
    "amount_deviation",
]


def _parse_datetime(ts_str: str) -> datetime:
    return datetime.fromisoformat(ts_str.replace("Z", ""))


def build_features_for_entity(entity_id: str, period_days: int = 2) -> Dict:
    """
    Build a numerical feature vector for a given entity from DB records.
    period_days = window for 'current' activity measurement (default 2 days).
    """
    cdr_records = db.get_cdr_for_entity(entity_id)
    txn_records = db.get_transactions_for_entity(entity_id)
    baseline = db.get_baseline(entity_id)

    # ── Reference Window ───────────────────────────────────────────────────────
    # Determine the timeline reference point (latest timestamp for this entity or globally)
    if cdr_records:
        latest_ts = max(_parse_datetime(r["timestamp"]) for r in cdr_records)
    else:
        latest_ts = datetime(2024, 8, 25, 23, 59, 59)

    window_start = latest_ts - timedelta(days=period_days)
    last_7_start = latest_ts - timedelta(days=7)

    # ── CDR Features ──────────────────────────────────────────────────────────
    current_calls = []
    pre_window_calls = []
    last_7_calls = []

    for r in cdr_records:
        ts = _parse_datetime(r["timestamp"])
        if ts >= window_start:
            current_calls.append(r)
        else:
            pre_window_calls.append(r)
        if ts >= last_7_start:
            last_7_calls.append(r)

    # Outgoing calls from this entity during current window
    current_outgoing = [r for r in current_calls if r["caller_id"] == entity_id]
    calls_per_day = len(current_outgoing) / max(period_days, 1)

    # Calls in last 7 days (outgoing)
    last_7_outgoing = [r for r in last_7_calls if r["caller_id"] == entity_id]
    calls_last_7_days = len(last_7_outgoing)

    # Contacts reached by outgoing calls (unique callees in window)
    current_contacts = {r["callee_id"] for r in current_outgoing}
    pre_outgoing = [r for r in pre_window_calls if r["caller_id"] == entity_id]
    pre_contacts = {r["callee_id"] for r in pre_outgoing}
    unique_contacts = len(current_contacts)
    new_contacts = len(current_contacts - pre_contacts)

    # Night calls: only count outgoing calls made during night hours.
    # Incoming calls are the caller's activity — do NOT attribute them here.
    night_calls = sum(1 for r in current_outgoing if r.get("is_night", 0))

    # Average call duration: only outgoing calls
    durations = [r.get("duration_sec", 0) for r in current_outgoing]
    avg_call_duration = (sum(durations) / len(durations)) if durations else 0.0

    # ── Transaction Features ───────────────────────────────────────────────────
    sent_txns = [t for t in txn_records if t["sender_id"] == entity_id]
    window_start_date_str = window_start.strftime("%Y-%m-%d")

    current_sent_txns = [t for t in sent_txns if t["timestamp"] >= window_start_date_str]
    pre_sent_txns = [t for t in sent_txns if t["timestamp"] < window_start_date_str]

    if current_sent_txns:
        amounts = [t["amount"] for t in current_sent_txns]
        total_amount = sum(amounts)
        txn_frequency = len(current_sent_txns)
        avg_txn_amount = total_amount / txn_frequency

        cur_recipients = {t["receiver_id"] for t in current_sent_txns}
        pre_recipients = {t["receiver_id"] for t in pre_sent_txns}
        new_recipients = len(cur_recipients - pre_recipients)

        # Baseline average transaction for comparison
        baseline_avg = baseline.get("avg_transaction_amount", 6000.0) if baseline else 6000.0
        baseline_avg = baseline_avg if baseline_avg > 0 else 6000.0
        amount_deviation = max(amounts) / baseline_avg
    else:
        total_amount = 0.0
        txn_frequency = 0
        avg_txn_amount = 0.0
        new_recipients = 0
        amount_deviation = 0.0

    return {
        "calls_per_day": round(calls_per_day, 2),
        "calls_last_7_days": round(calls_last_7_days, 2),
        "unique_contacts": unique_contacts,
        "new_contacts": new_contacts,
        "night_calls": night_calls,
        "avg_call_duration": round(avg_call_duration, 2),
        "transaction_amount": round(total_amount, 2),
        "transaction_frequency": txn_frequency,
        "avg_transaction_amount": round(avg_txn_amount, 2),
        "new_recipients": new_recipients,
        "amount_deviation": round(amount_deviation, 2),
    }


def build_training_dataset() -> List[Dict]:
    """
    Build a realistic, deterministic normal training dataset for IsolationForest.
    Generates 120 synthetic normal 2-day activity windows across the baseline population.
    """
    rng = random.Random(42)
    dataset = []

    # Normal 2-day window distribution params
    # (cpd, c7d, uc, nc, night, dur, has_txn_prob, txn_amt, txn_freq, dev)
    normal_profiles = [
        {"cpd": (2.5, 1.0), "c7d": (15.0, 4.0), "uc": (2, 1), "dur": (120, 20), "amt": (7000, 2000)},
        {"cpd": (3.0, 1.2), "c7d": (18.0, 5.0), "uc": (3, 1), "dur": (140, 25), "amt": (6500, 1800)},
        {"cpd": (1.5, 0.8), "c7d": (10.0, 3.0), "uc": (2, 1), "dur": (100, 15), "amt": (5000, 1500)},
        {"cpd": (2.5, 1.0), "c7d": (16.0, 4.0), "uc": (2, 1), "dur": (130, 20), "amt": (7000, 2000)},
        {"cpd": (1.2, 0.6), "c7d": (8.0, 2.5),  "uc": (2, 1), "dur": (90, 15),  "amt": (4500, 1200)},
    ]

    for _ in range(24):
        for profile in normal_profiles:
            cpd = max(0.5, rng.gauss(*profile["cpd"]))
            c7d = max(3.0, rng.gauss(*profile["c7d"]))
            uc = max(1, int(rng.gauss(*profile["uc"])))
            nc = 0 if rng.random() > 0.15 else 1
            night = 0 if rng.random() > 0.10 else 1
            dur = max(30.0, rng.gauss(*profile["dur"]))

            has_txn = rng.random() > 0.45
            if has_txn:
                amt = max(500.0, rng.gauss(*profile["amt"]))
                freq = rng.choice([1, 1, 2])
                avg_amt = amt / freq
                new_rec = 0 if rng.random() > 0.15 else 1
                dev = max(0.8, rng.gauss(1.1, 0.2))
            else:
                amt = 0.0
                freq = 0
                avg_amt = 0.0
                new_rec = 0
                dev = 0.0

            dataset.append({
                "calls_per_day": round(cpd, 2),
                "calls_last_7_days": round(c7d, 2),
                "unique_contacts": uc,
                "new_contacts": nc,
                "night_calls": night,
                "avg_call_duration": round(dur, 2),
                "transaction_amount": round(amt, 2),
                "transaction_frequency": freq,
                "avg_transaction_amount": round(avg_amt, 2),
                "new_recipients": new_rec,
                "amount_deviation": round(dev, 2),
            })

    return dataset


def features_to_vector(features: Dict) -> List[float]:
    """Convert feature dict to ordered list of floats for sklearn."""
    return [float(features.get(k, 0)) for k in FEATURE_KEYS]
