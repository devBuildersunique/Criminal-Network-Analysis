"""
isolation_forest.py
Trains IsolationForest on baseline behavioral features and scores
a given entity's current activity.

Output includes:
  - status: ANOMALY | NORMAL
  - severity: HIGH | MEDIUM | LOW | NORMAL
  - anomaly_score: raw IsolationForest score
  - reasons: human-readable explanations of what deviated
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, List, Tuple

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import backend.database as db
from backend.anomaly.feature_builder import (
    build_features_for_entity,
    build_training_dataset,
    features_to_vector,
    FEATURE_KEYS,
)

_model: IsolationForest | None = None
_training_features: List[Dict] | None = None


def _get_model() -> IsolationForest:
    global _model, _training_features
    if _model is None:
        _training_features = build_training_dataset()
        X = np.array([features_to_vector(f) for f in _training_features])
        _model = IsolationForest(
            n_estimators=100,
            contamination=0.03,
            random_state=42,
        )
        _model.fit(X)
    return _model


def _explain_anomaly(
    current: Dict, baseline: Dict | None, score: float
) -> Tuple[List[str], str]:
    """
    Generate human-readable reasons for why an entity was flagged.
    Returns (reasons_list, severity).
    """
    reasons = []

    def check(feature, label, multiplier=2.0, format_fn=lambda x: str(round(x, 1))):
        cur_val = current.get(feature, 0)
        base_val = (baseline or {}).get(feature, None)
        if base_val is not None and base_val > 0:
            if cur_val >= base_val * multiplier:
                reasons.append(
                    f"{label}: baseline avg {format_fn(base_val)}, "
                    f"current {format_fn(cur_val)} "
                    f"({round(cur_val/base_val, 1)}x higher than normal)"
                )
        elif cur_val > 0 and base_val is not None and base_val == 0:
            reasons.append(f"{label}: current {format_fn(cur_val)} (baseline: 0)")

    check("calls_per_day", "Calls per day", multiplier=2.5, format_fn=lambda x: f"{x:.1f}")
    check("night_calls", "Night-time calls", multiplier=2.5)
    check("new_contacts", "New contacts", multiplier=2.0)
    check("unique_contacts", "Unique contacts in window", multiplier=2.0)
    check("transaction_amount", "Total transaction amount",
          multiplier=4.0, format_fn=lambda x: f"Rs {x:,.0f}")
    check("amount_deviation", "Transaction amount deviation ratio", multiplier=3.0)
    check("new_recipients", "New money recipients", multiplier=2.0)

    # Severity determination based on IsolationForest anomaly score and reason count
    if score < -0.15 and len(reasons) >= 2:
        severity = "HIGH"
    elif score < 0.0 or len(reasons) >= 1:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    if not reasons and score < -0.05:
        reasons.append("Behavioral pattern differs significantly from historical baseline.")

    return reasons, severity


def run_anomaly_detection(entity_id: str) -> Dict:
    """
    Score a single entity using IsolationForest.
    Returns a structured anomaly result dict.
    """
    model = _get_model()
    person = db.get_person(entity_id)
    entity_name = person["name"] if person else entity_id
    baseline = db.get_baseline(entity_id)

    current_features = build_features_for_entity(entity_id, period_days=2)
    baseline_features = {k: (baseline.get(k, 0) if baseline else 0) for k in FEATURE_KEYS}

    X = np.array([features_to_vector(current_features)])
    raw_score = float(model.score_samples(X)[0])
    prediction = int(model.predict(X)[0])  # -1 = anomaly, 1 = normal

    is_anomaly = (prediction == -1)

    # Secondary check: if features deviate massively (4x+ baseline on calls or amount), ensure flagged
    if not is_anomaly and baseline:
        cpd_base = baseline.get("calls_per_day", 0)
        cpd_cur = current_features.get("calls_per_day", 0)
        amt_base = baseline.get("transaction_amount", 0)
        amt_cur = current_features.get("transaction_amount", 0)
        if (cpd_base > 0 and cpd_cur > cpd_base * 4) or (amt_base > 0 and amt_cur > amt_base * 5):
            is_anomaly = True

    if is_anomaly:
        reasons, severity = _explain_anomaly(current_features, baseline, raw_score)
    else:
        reasons = []
        severity = "NORMAL"

    return {
        "entity_id": entity_id,
        "entity_name": entity_name,
        "status": "ANOMALY" if is_anomaly else "NORMAL",
        "anomaly_score": round(raw_score, 4),
        "severity": severity,
        "reasons": reasons,
        "current_features": current_features,
        "baseline_features": baseline_features,
    }


def run_anomaly_detection_all(entity_ids: List[str]) -> List[Dict]:
    """Run anomaly detection for a list of entity IDs."""
    results = []
    for eid in entity_ids:
        try:
            results.append(run_anomaly_detection(eid))
        except Exception as e:
            results.append({
                "entity_id": eid,
                "entity_name": eid,
                "status": "UNKNOWN",
                "anomaly_score": 0.0,
                "severity": "UNKNOWN",
                "reasons": [f"Could not compute features: {e}"],
                "current_features": {},
                "baseline_features": {},
            })
    return results


if __name__ == "__main__":
    db.ensure_seeded()
    result = run_anomaly_detection("P001")
    print(f"Entity: {result['entity_name']}")
    print(f"Status: {result['status']} | Severity: {result['severity']}")
    print(f"Score:  {result['anomaly_score']}")
    print("Reasons:")
    for r in result["reasons"]:
        print(f"  - {r}")
