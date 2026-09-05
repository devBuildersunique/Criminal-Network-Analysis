"""
entity_resolver.py
Matches extracted entities against the database using fuzzy name matching.

Thresholds (configurable):
  >= AUTO_MATCH_THRESHOLD  → AUTO_MATCH
  >= POSSIBLE_MATCH_THRESHOLD → POSSIBLE_MATCH
  <  POSSIBLE_MATCH_THRESHOLD → NEW_ENTITY
"""

import re
from typing import List, Dict, Optional
from rapidfuzz import fuzz

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import backend.database as db

# ─── Configurable Thresholds ───────────────────────────────────────────────────

AUTO_MATCH_THRESHOLD = 90.0       # >= auto-match
POSSIBLE_MATCH_THRESHOLD = 70.0   # 70–90 → possible match


def _normalize(text: str) -> str:
    """Lowercase, remove punctuation, collapse whitespace."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _best_person_match(name: str, people: List[Dict]) -> Optional[Dict]:
    """Return the best matching person and the similarity score."""
    norm_input = _normalize(name)
    best_score = 0.0
    best_person = None

    for person in people:
        db_name = person["name"]
        norm_db = _normalize(db_name)

        # Check main name
        score = fuzz.token_sort_ratio(norm_input, norm_db)

        # Also check aliases
        if person.get("aliases"):
            for alias in person["aliases"].split(","):
                alias_score = fuzz.token_sort_ratio(norm_input, _normalize(alias.strip()))
                score = max(score, alias_score)

        if score > best_score:
            best_score = score
            best_person = person

    return best_person, best_score


def _match_status(score: float) -> str:
    if score >= AUTO_MATCH_THRESHOLD:
        return "AUTO_MATCH"
    elif score >= POSSIBLE_MATCH_THRESHOLD:
        return "POSSIBLE_MATCH"
    else:
        return "NEW_ENTITY"


def resolve_entities(extracted: List[Dict]) -> List[Dict]:
    """
    For each extracted entity, resolve against the database.
    Returns a list of resolution results.
    """
    people = db.get_all_people()
    vehicles = db.get_all_vehicles()
    locations = db.get_all_locations()
    phones = db.get_all_phones()
    cases = db.get_all_cases()

    results = []

    for ent in extracted:
        text = ent["text"]
        etype = ent["type"]
        result = {
            "input_text": text,
            "input_type": etype,
            "db_id": None,
            "db_name": None,
            "confidence": 0.0,
            "match_status": "NEW_ENTITY",
            "db_record": None,
        }

        if etype in ("PERSON", "ORGANIZATION"):
            best, score = _best_person_match(text, people)
            conf = round(score / 100.0, 3)
            status = _match_status(score)
            if status != "NEW_ENTITY" and best:
                result.update(
                    input_type="PERSON",
                    db_id=best["id"],
                    db_name=best["name"],
                    confidence=conf,
                    match_status=status,
                    db_record=best,
                )
            else:
                result["confidence"] = conf

        elif etype == "PHONE":
            # Exact number match
            phone = db.get_phone_by_number(text)
            if phone:
                owner = db.get_person(phone["owner_id"]) if phone.get("owner_id") else None
                result.update(
                    db_id=phone["id"],
                    db_name=f"Phone {phone['number']}" + (f" (owner: {owner['name']})" if owner else ""),
                    confidence=1.0,
                    match_status="AUTO_MATCH",
                    db_record={**phone, "owner": owner},
                )

        elif etype == "VEHICLE":
            plate = text.upper()
            vehicle = db.get_vehicle_by_plate(plate)
            if vehicle:
                owner = db.get_person(vehicle["owner_id"]) if vehicle.get("owner_id") else None
                result.update(
                    db_id=vehicle["id"],
                    db_name=f"Vehicle {vehicle['plate']}",
                    confidence=1.0,
                    match_status="AUTO_MATCH",
                    db_record={**vehicle, "owner": owner},
                )

        elif etype == "LOCATION":
            norm_input = _normalize(text)
            best_score = 0.0
            best_loc = None
            for loc in locations:
                score = fuzz.token_sort_ratio(norm_input, _normalize(loc["name"]))
                if score > best_score:
                    best_score = score
                    best_loc = loc
            conf = round(best_score / 100.0, 3)
            status = _match_status(best_score)
            if status != "NEW_ENTITY" and best_loc:
                result.update(
                    db_id=best_loc["id"],
                    db_name=best_loc["name"],
                    confidence=conf,
                    match_status=status,
                    db_record=best_loc,
                )

        elif etype == "CASE":
            case_id = text.upper()
            case = db.get_case(case_id)
            if case:
                result.update(
                    db_id=case["id"],
                    db_name=f"Case {case['id']}: {case['title']}",
                    confidence=1.0,
                    match_status="AUTO_MATCH",
                    db_record=case,
                )

        results.append(result)

    return results


if __name__ == "__main__":
    db.ensure_seeded()
    test_entities = [
        {"text": "Rahul Sharma", "type": "PERSON"},
        {"text": "R. Sharma", "type": "PERSON"},
        {"text": "Amit Kumar", "type": "PERSON"},
        {"text": "9876543210", "type": "PHONE"},
        {"text": "DL01AB1234", "type": "VEHICLE"},
        {"text": "Delhi", "type": "LOCATION"},
        {"text": "C102", "type": "CASE"},
    ]
    for r in resolve_entities(test_entities):
        print(f"  {r['input_text']:20s} → {r.get('db_id','?'):6s} | {r['match_status']:15s} | conf={r['confidence']:.2f}")
