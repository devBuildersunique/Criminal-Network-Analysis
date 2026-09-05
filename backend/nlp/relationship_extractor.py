"""
relationship_extractor.py
Rule-based relationship extraction from case statement text.

Identifies relationships such as:
  CALLED, TRANSFERRED_MONEY, MET, VISITED, USED_VEHICLE,
  INVOLVED_IN, USES_PHONE
"""

import re
from typing import List, Dict


# ─── Relationship Patterns ─────────────────────────────────────────────────────
# Each rule: (pattern, predicate, metadata_extractor_fn)
# We match against the full text (case-insensitive).

def _extract_call_frequency(text: str) -> dict:
    """Try to extract call count from surrounding context."""
    m = re.search(r"(\d+)\s*times?", text, re.IGNORECASE)
    freq = int(m.group(1)) if m else None
    m2 = re.search(r"in\s+(\w+)\s+days?", text, re.IGNORECASE)
    days = m2.group(1) if m2 else None
    return {"frequency": freq, "period_days": days}


def _extract_amount(text: str) -> dict:
    m = re.search(r"(?:Rs\.?\s*|₹\s*)([\d,]+)", text, re.IGNORECASE)
    if m:
        amount = int(m.group(1).replace(",", ""))
        return {"amount": amount, "currency": "INR"}
    return {}


def extract_relationships(
    case_text: str, resolved_entities: List[Dict]
) -> List[Dict]:
    """
    Given the case text and a list of resolved entities,
    extract relationships between them.

    Returns list of:
    {
      subject_id, subject_label,
      predicate,
      object_id, object_label,
      metadata
    }
    """
    relationships = []

    # Build quick lookups from resolved entities
    people = {
        r["db_id"]: r["db_name"]
        for r in resolved_entities
        if r["input_type"] == "PERSON" and r["db_id"]
    }
    locations = {
        r["db_id"]: r["db_name"]
        for r in resolved_entities
        if r["input_type"] == "LOCATION" and r["db_id"]
    }
    vehicles = {
        r["db_id"]: r["db_name"]
        for r in resolved_entities
        if r["input_type"] == "VEHICLE" and r["db_id"]
    }
    phones = {
        r["db_id"]: r["db_name"]
        for r in resolved_entities
        if r["input_type"] == "PHONE" and r["db_id"]
    }
    cases = {
        r["db_id"]: r["db_name"]
        for r in resolved_entities
        if r["input_type"] == "CASE" and r["db_id"]
    }

    text_lower = case_text.lower()
    person_ids = list(people.keys())

    def _name_pos(name: str, sentence: str) -> int:
        for token in name.lower().split():
            pos = sentence.find(token)
            if pos != -1:
                return pos
        return 999999

    # ── Rule 1: CALLED / CONTACTED ────────────────────────────────────────────
    call_patterns = [
        r"contacted", r"called", r"phone\s+calls?", r"times\s+in\s+\w+\s+days?"
    ]
    if any(re.search(p, text_lower) for p in call_patterns):
        if len(person_ids) >= 2:
            sentences = re.split(r"[.!?]", text_lower)
            for sent in sentences:
                if re.search(r"\bcontact|\bcall", sent):
                    for subj in person_ids:
                        for obj in person_ids:
                            if subj != obj:
                                sn = people[subj].lower()
                                on = people[obj].lower()
                                if (any(w in sent for w in sn.split()) and
                                        any(w in sent for w in on.split())):
                                    # Direction: caller appears before callee in sentence
                                    if _name_pos(people[subj], sent) < _name_pos(people[obj], sent):
                                        meta = _extract_call_frequency(sent)
                                        if not any(
                                            r["subject_id"] == subj and r["object_id"] == obj
                                            and r["predicate"] == "CALLED"
                                            for r in relationships
                                        ):
                                            relationships.append({
                                                "subject_id": subj,
                                                "subject_label": people[subj],
                                                "predicate": "CALLED",
                                                "object_id": obj,
                                                "object_label": people[obj],
                                                "metadata": {"record_source": "CDR", **meta},
                                            })

    # ── Rule 2: TRANSFERRED_MONEY ─────────────────────────────────────────────
    transfer_patterns = [r"transfer", r"paid", r"sent\s+(?:rs|₹|money)", r"deposited"]
    if any(re.search(p, text_lower) for p in transfer_patterns):
        sentences = re.split(r"[.!?]", text_lower)
        for sent in sentences:
            if re.search(r"transfer|paid|deposited", sent):
                for subj in person_ids:
                    for obj in person_ids:
                        if subj != obj:
                            sn = people[subj].lower()
                            on = people[obj].lower()
                            if (any(w in sent for w in sn.split()) and
                                    any(w in sent for w in on.split())):
                                # Direction: sender appears before receiver in sentence
                                if _name_pos(people[subj], sent) < _name_pos(people[obj], sent):
                                    meta = _extract_amount(case_text)
                                    if not any(
                                        r["subject_id"] == subj and r["object_id"] == obj
                                        and r["predicate"] == "TRANSFERRED_MONEY"
                                        for r in relationships
                                    ):
                                        relationships.append({
                                            "subject_id": subj,
                                            "subject_label": people[subj],
                                            "predicate": "TRANSFERRED_MONEY",
                                            "object_id": obj,
                                            "object_label": people[obj],
                                            "metadata": {"record_source": "financial_record", **meta},
                                        })

    # ── Rule 3: MET ───────────────────────────────────────────────────────────
    met_patterns = [r"\bmet\b", r"\bmeeting\b", r"\bencountered\b"]
    if any(re.search(p, text_lower) for p in met_patterns):
        sentences = re.split(r"[.!?]", text_lower)
        for sent in sentences:
            if re.search(r"\bmet\b|\bmeeting\b", sent):
                for subj in person_ids:
                    for obj in person_ids:
                        if subj != obj:
                            sn = people[subj].lower()
                            on = people[obj].lower()
                            if (any(w in sent for w in sn.split()) and
                                    any(w in sent for w in on.split())):
                                # Extract location from same sentence
                                loc_meta = {}
                                for loc_id, loc_name in locations.items():
                                    if loc_name.lower() in sent:
                                        loc_meta = {"location": loc_id, "location_name": loc_name}
                                if not any(
                                    r["subject_id"] == subj and r["object_id"] == obj
                                    and r["predicate"] == "MET"
                                    for r in relationships
                                ):
                                    relationships.append({
                                        "subject_id": subj,
                                        "subject_label": people[subj],
                                        "predicate": "MET",
                                        "object_id": obj,
                                        "object_label": people[obj],
                                        "metadata": {"record_source": "case_statement", **loc_meta},
                                    })

    # ── Rule 4: VISITED (person → location) ───────────────────────────────────
    for subj in person_ids:
        sn = people[subj].lower()
        for loc_id, loc_name in locations.items():
            ln = loc_name.lower()
            sentences = re.split(r"[.!?]", text_lower)
            for sent in sentences:
                if any(w in sent for w in sn.split()) and ln in sent:
                    if not any(
                        r["subject_id"] == subj and r["object_id"] == loc_id
                        and r["predicate"] == "VISITED"
                        for r in relationships
                    ):
                        relationships.append({
                            "subject_id": subj,
                            "subject_label": people[subj],
                            "predicate": "VISITED",
                            "object_id": loc_id,
                            "object_label": loc_name,
                            "metadata": {"record_source": "case_statement"},
                        })

    # ── Rule 5: USED_VEHICLE (person → vehicle) ────────────────────────────────
    used_patterns = [r"\bused\b", r"\bdrove\b", r"\bvehicle\b", r"\bcar\b"]
    if any(re.search(p, text_lower) for p in used_patterns):
        for subj in person_ids:
            sn = people[subj].lower()
            for veh_id, veh_name in vehicles.items():
                # veh_name e.g. "Vehicle DL01AB1234"
                plate = veh_name.replace("Vehicle ", "").lower()
                sentences = re.split(r"[.!?]", text_lower)
                for sent in sentences:
                    if any(w in sent for w in sn.split()) and plate in sent:
                        if not any(
                            r["subject_id"] == subj and r["object_id"] == veh_id
                            and r["predicate"] == "USED_VEHICLE"
                            for r in relationships
                        ):
                            relationships.append({
                                "subject_id": subj,
                                "subject_label": people[subj],
                                "predicate": "USED_VEHICLE",
                                "object_id": veh_id,
                                "object_label": veh_name,
                                "metadata": {"record_source": "case_statement"},
                            })

    # ── Rule 6: INVOLVED_IN / MENTIONED_IN (person → case) ───────────────────
    involved_patterns = [r"\bmentioned in\b", r"\binvolved in\b", r"\bcase\b"]
    if any(re.search(p, text_lower) for p in involved_patterns):
        for subj in person_ids:
            sn = people[subj].lower()
            for case_id, case_name in cases.items():
                cid = case_id.lower()
                sentences = re.split(r"[.!?]", text_lower)
                for sent in sentences:
                    if any(w in sent for w in sn.split()) and cid in sent:
                        if not any(
                            r["subject_id"] == subj and r["object_id"] == case_id
                            and r["predicate"] == "INVOLVED_IN"
                            for r in relationships
                        ):
                            relationships.append({
                                "subject_id": subj,
                                "subject_label": people[subj],
                                "predicate": "INVOLVED_IN",
                                "object_id": case_id,
                                "object_label": case_name,
                                "metadata": {"record_source": "case_statement"},
                            })

    # ── Rule 7: USES_PHONE (person → phone) ───────────────────────────────────
    for phone_id, phone_name in phones.items():
        phone_number = phone_name.split("Phone ")[-1].split(" ")[0]
        if phone_number in case_text:
            for subj in person_ids:
                sn = people[subj].lower()
                sentences = re.split(r"[.!?]", text_lower)
                for sent in sentences:
                    if (any(w in sent for w in sn.split()) and phone_number in sent):
                        if not any(
                            r["subject_id"] == subj and r["object_id"] == phone_id
                            and r["predicate"] == "USES_PHONE"
                            for r in relationships
                        ):
                            relationships.append({
                                "subject_id": subj,
                                "subject_label": people[subj],
                                "predicate": "USES_PHONE",
                                "object_id": phone_id,
                                "object_label": phone_name,
                                "metadata": {"record_source": "CDR"},
                            })

    return relationships


if __name__ == "__main__":
    # Quick self-test
    demo_text = (
        "Rahul Sharma met Amit Kumar in Delhi on 25 August. "
        "Rahul contacted Amit 42 times in two days using phone 9876543210. "
        "Rahul transferred Rs 850000 to Amit. "
        "Rahul used vehicle DL01AB1234. "
        "Rahul was previously mentioned in Case C102 with Ravi Singh."
    )
    demo_resolved = [
        {"input_type": "PERSON", "db_id": "P001", "db_name": "Rahul Sharma"},
        {"input_type": "PERSON", "db_id": "P002", "db_name": "Amit Kumar"},
        {"input_type": "PERSON", "db_id": "P003", "db_name": "Ravi Singh"},
        {"input_type": "LOCATION", "db_id": "L001", "db_name": "Delhi"},
        {"input_type": "VEHICLE", "db_id": "V001", "db_name": "Vehicle DL01AB1234"},
        {"input_type": "PHONE", "db_id": "PH001", "db_name": "Phone 9876543210"},
        {"input_type": "CASE", "db_id": "C102", "db_name": "Case C102: Financial Fraud Ring"},
    ]
    rels = extract_relationships(demo_text, demo_resolved)
    for r in rels:
        print(f"  {r['subject_label']:20s} —[{r['predicate']:20s}]→ {r['object_label']}")
