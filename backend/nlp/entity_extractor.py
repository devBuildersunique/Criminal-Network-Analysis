"""
entity_extractor.py
Extracts named entities from a case statement using:
  - spaCy en_core_web_sm for PERSON, LOC, ORG, DATE
  - Regex rules for PHONE, VEHICLE, MONEY, CASE IDs
  - DB name-scan fallback for known persons that spaCy missed
  - DATE noise filter: removes vague time-of-day phrases with no calendar value
"""

import re
import spacy
from typing import List, Dict

# Load spaCy model once at module level
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError(
        "spaCy model not found. Run: python -m spacy download en_core_web_sm"
    )

# ─── Regex Patterns ────────────────────────────────────────────────────────────

PHONE_RE = re.compile(r"\b[6-9]\d{9}\b")               # Indian 10-digit mobile
VEHICLE_RE = re.compile(r"\b[A-Z]{2}\d{2}[A-Z]{1,3}\d{4}\b")  # DL01AB1234
MONEY_RE = re.compile(r"(?:Rs\.?\s*|₹\s*)[\d,]+", re.IGNORECASE)
CASE_RE = re.compile(r"\bC\d{3,5}\b")                  # C102, C10345 etc.

# ─── DATE Noise Filter ─────────────────────────────────────────────────────────
# spaCy's small model tags generic time-of-day phrases as DATE/TIME.
# These have no investigative calendar value and should be excluded.
_DATE_NOISE = frozenset([
    "the day", "the night", "the morning", "the evening", "the afternoon",
    "during the day", "during the night", "during the morning", "during the evening",
    "day", "night", "morning", "evening", "afternoon", "midnight", "midday",
    "today", "tomorrow", "yesterday",
    "daytime", "nighttime", "nowadays",
])


def _is_date_noise(text: str) -> bool:
    """Return True if the text is a vague time-of-day phrase with no calendar specificity."""
    return text.strip().lower() in _DATE_NOISE


def _overlaps_any(start: int, end: int, spans: list) -> bool:
    """Return True if [start,end) overlaps any span in spans list."""
    for (s, e) in spans:
        if not (end <= s or start >= e):
            return True
    return False


def extract_entities(text: str) -> List[Dict]:
    """
    Returns a list of entity dicts:
    { text, type, start, end, confidence }

    Steps:
      1. Regex: PHONE, VEHICLE, MONEY, CASE (highest priority)
      2. spaCy NER: PERSON, LOCATION, ORGANIZATION, DATE (skip regex overlaps)
      3. DB name-scan fallback: catch known persons missed by spaCy
    """
    found: List[Dict] = []
    seen_spans = set()   # (start, end) exact dedup

    def add(text_val, etype, start, end, conf=1.0):
        span_key = (start, end)
        if span_key not in seen_spans:
            seen_spans.add(span_key)
            found.append(
                {"text": text_val, "type": etype, "start": start, "end": end, "confidence": conf}
            )

    # ── Step 1: Regex-based extractions (high confidence, take priority) ─────
    for m in PHONE_RE.finditer(text):
        add(m.group(), "PHONE", m.start(), m.end())

    for m in VEHICLE_RE.finditer(text):
        add(m.group(), "VEHICLE", m.start(), m.end())

    for m in MONEY_RE.finditer(text):
        add(m.group().strip(), "MONEY", m.start(), m.end())

    for m in CASE_RE.finditer(text):
        add(m.group(), "CASE", m.start(), m.end())

    # ── Step 2: spaCy NER (PERSON, LOC, ORG, DATE) ──────────────────────────
    doc = nlp(text)
    regex_spans = [(e["start"], e["end"]) for e in found]  # snapshot before spaCy adds

    etype_map = {
        "PERSON": "PERSON",
        "GPE": "LOCATION",
        "LOC": "LOCATION",
        "ORG": "ORGANIZATION",
        "DATE": "DATE",
        "TIME": "DATE",
    }

    for ent in doc.ents:
        # Skip if this spaCy span overlaps with a regex-extracted span
        if _overlaps_any(ent.start_char, ent.end_char, regex_spans):
            continue

        mapped = etype_map.get(ent.label_)
        if mapped is None:
            continue

        # Filter out DATE/TIME entities that are vague time-of-day phrases
        # (e.g. "the day", "the night") — no investigative calendar value.
        if mapped == "DATE" and _is_date_noise(ent.text):
            continue

        # Re-classify ORG as PERSON if the name is in the DB
        if mapped == "ORGANIZATION":
            try:
                import backend.database as db
                people = db.get_all_people()
                norm_inp = set(ent.text.strip().lower().split())
                for p in people:
                    # Match if any DB name token appears in the entity text
                    db_tokens = set(p["name"].lower().split())
                    if db_tokens & norm_inp:
                        mapped = "PERSON"
                        break
                    for alias in (p.get("aliases") or "").split(","):
                        alias_tokens = set(alias.strip().lower().split())
                        if alias_tokens and alias_tokens & norm_inp:
                            mapped = "PERSON"
                            break
            except Exception:
                pass

        add(ent.text.strip(), mapped, ent.start_char, ent.end_char, 0.9)

    # ── Step 3: DB name-scan fallback ────────────────────────────────────────
    # After spaCy, scan for any known person names / aliases that were missed.
    # Adds any non-overlapping match as PERSON with confidence 0.85.
    try:
        import backend.database as db
        people = db.get_all_people()

        # Build list of (search_name, canonical_name) for full names + aliases
        candidates = []
        for p in people:
            candidates.append(p["name"])
            for alias in (p.get("aliases") or "").split(","):
                alias = alias.strip()
                if alias:
                    candidates.append(alias)

        # Current spans (including what spaCy added)
        current_spans = [(e["start"], e["end"]) for e in found]

        for name in candidates:
            pattern = re.compile(r"\b" + re.escape(name) + r"\b", re.IGNORECASE)
            for m in pattern.finditer(text):
                ms, me = m.start(), m.end()
                if not _overlaps_any(ms, me, current_spans):
                    add(m.group(), "PERSON", ms, me, 0.85)
                    current_spans.append((ms, me))  # prevent future overlaps
    except Exception:
        pass  # DB unavailable — gracefully degrade

    # Sort by position in text
    found.sort(key=lambda e: e["start"])
    return found


if __name__ == "__main__":
    demo = (
        "Rahul Sharma met Amit Kumar in Delhi on 25 August. "
        "Rahul contacted Amit 42 times in two days using phone 9876543210. "
        "Rahul transferred Rs 850000 to Amit. "
        "Rahul used vehicle DL01AB1234. "
        "Rahul was previously mentioned in Case C102 with Ravi Singh."
    )
    entities = extract_entities(demo)
    for e in entities:
        print(f"  [{e['type']:12s}] {e['text']}")
