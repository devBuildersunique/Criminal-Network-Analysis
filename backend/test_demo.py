"""
test_demo.py — Automated demo test suite for SIH-189.

Runs all 6 test cases through the full pipeline (no frontend, no HTTP).
Prints PASS/FAIL per test and exits with code 0 (all pass) or 1 (any fail).

Usage:
    python backend/test_demo.py
    python backend/test_demo.py --debug
    python -m backend.test_demo

DISCLAIMER: All data is synthetic. This test uses fictional records only.
"""

import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEBUG = "--debug" in sys.argv or os.environ.get("DEBUG", "").lower() in ("1", "true")


def bootstrap():
    """Reset and reseed the database before running tests."""
    from backend.data.seed_data import reset_all
    reset_all()
    import backend.anomaly.isolation_forest as _if
    _if._model = None
    _if._training_features = None


def run_pipeline(text: str) -> dict:
    """Run the full analysis pipeline and return the result dict."""
    import backend.database as db
    from backend.nlp.entity_extractor import extract_entities
    from backend.nlp.entity_resolver import resolve_entities
    from backend.nlp.relationship_extractor import extract_relationships
    from backend.graph.graph_builder import build_graph, graph_to_cytoscape
    from backend.graph.graph_analysis import analyze_graph
    from backend.anomaly.isolation_forest import run_anomaly_detection_all

    entities = extract_entities(text)
    resolved = resolve_entities(entities)
    relationships = extract_relationships(text, resolved)
    G = build_graph(resolved, relationships)
    nodes, edges = graph_to_cytoscape(G)
    graph_analysis = analyze_graph(G)

    # Historical cases
    person_ids = [e["db_id"] for e in resolved if e["input_type"] == "PERSON" and e["db_id"]]
    seen_cases = {}
    for pid in person_ids:
        for case in db.get_cases_for_entity(pid):
            cid = case["id"]
            if cid not in seen_cases:
                seen_cases[cid] = {
                    "case_id": cid,
                    "case_title": case.get("title", ""),
                    "entities_involved": [],
                }
            seen_cases[cid]["entities_involved"].append(pid)
    historical_cases = list(seen_cases.values())

    person_ids_unique = list({
        e["db_id"] for e in resolved if e["input_type"] == "PERSON" and e["db_id"]
    })
    anomalies = run_anomaly_detection_all(person_ids_unique)

    return {
        "entities": entities,
        "resolved_entities": resolved,
        "relationships": relationships,
        "historical_cases": historical_cases,
        "anomalies": anomalies,
        "graph_nodes": nodes,
        "graph_edges": edges,
    }


SEVERITY_ORDER = {"NORMAL": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "UNKNOWN": -1}


def check_expected_entities(result, expected_entities, errors):
    extracted_texts = [e["text"].lower() for e in result["entities"]]
    for (text, etype) in expected_entities:
        text_l = text.lower()
        found = any(text_l in et or et in text_l for et in extracted_texts)
        if not found:
            errors.append(f"Expected entity '{text}' ({etype}) not found in extracted entities")


def check_expected_resolution(result, expected_resolution, errors):
    resolved_map = {
        r["input_text"].lower(): r for r in result["resolved_entities"]
    }
    for (input_text, expected_db_id, expected_status) in expected_resolution:
        text_l = input_text.lower()
        match = None
        for key, r in resolved_map.items():
            if text_l in key or key in text_l:
                match = r
                break
        if match is None:
            errors.append(f"Resolution: '{input_text}' not found in resolved entities")
            continue
        if expected_db_id and match["db_id"] != expected_db_id:
            errors.append(
                f"Resolution: '{input_text}' -> got db_id={match['db_id']!r}, "
                f"expected {expected_db_id!r}"
            )
        if expected_status and match["match_status"] != expected_status:
            if not (expected_status == "POSSIBLE_MATCH" and match["match_status"] == "AUTO_MATCH"):
                errors.append(
                    f"Resolution: '{input_text}' status={match['match_status']!r}, "
                    f"expected {expected_status!r}"
                )


def check_min_relationships(result, min_count, errors):
    actual = len(result["relationships"])
    if actual < min_count:
        errors.append(
            f"Expected at least {min_count} relationship(s), got {actual}"
        )


def check_anomaly(result, anomaly_spec, errors):
    if anomaly_spec is None:
        return
    entity_id = anomaly_spec.get("entity_id")
    min_sev = anomaly_spec.get("min_severity")
    max_sev = anomaly_spec.get("max_allowed_severity")

    entity_anomaly = next(
        (a for a in result["anomalies"] if a["entity_id"] == entity_id), None
    )
    if entity_anomaly is None:
        errors.append(f"Anomaly check: entity {entity_id} not in anomaly results")
        return

    severity = entity_anomaly.get("severity", "UNKNOWN")
    sev_val = SEVERITY_ORDER.get(severity, -1)

    if min_sev:
        min_val = SEVERITY_ORDER.get(min_sev, 0)
        if sev_val < min_val:
            errors.append(
                f"Anomaly check: {entity_id} severity={severity!r}, "
                f"expected at least {min_sev!r}"
            )
    if max_sev:
        max_val = SEVERITY_ORDER.get(max_sev, 3)
        if sev_val > max_val:
            errors.append(
                f"Anomaly check: {entity_id} severity={severity!r}, "
                f"expected at most {max_sev!r}"
            )


def check_historical(result, historical_spec, errors):
    if historical_spec is None:
        return
    case_id = historical_spec["case_id"]
    must_involve = set(historical_spec.get("must_involve", []))
    found_case = next(
        (hc for hc in result["historical_cases"] if hc["case_id"] == case_id), None
    )
    if found_case is None:
        errors.append(f"Historical check: case {case_id} not found in historical_cases")
        return
    involved = set(found_case.get("entities_involved", []))
    missing = must_involve - involved
    if missing:
        errors.append(
            f"Historical check: case {case_id} missing entities: {missing}"
        )


def check_new_entity(result, new_entity_spec, errors):
    if new_entity_spec is None:
        return
    fragment = new_entity_spec["name_fragment"].lower()
    must_not_match = new_entity_spec["must_NOT_match_db_id"]
    allowed_statuses = new_entity_spec["allowed_statuses"]

    for r in result["resolved_entities"]:
        if r["input_type"] != "PERSON":
            continue
        if fragment in r["input_text"].lower():
            if r["db_id"] in must_not_match:
                errors.append(
                    f"New-entity check: '{r['input_text']}' incorrectly matched to "
                    f"db_id={r['db_id']!r} - should be NEW_ENTITY"
                )
            if r["match_status"] not in allowed_statuses and r["match_status"] == "AUTO_MATCH":
                errors.append(
                    f"New-entity check: '{r['input_text']}' got AUTO_MATCH to "
                    f"{r['db_id']!r} - should be NEW_ENTITY or POSSIBLE_MATCH"
                )


def check_graph(result, errors):
    nodes = result.get("graph_nodes", [])
    edges = result.get("graph_edges", [])
    node_ids = set()
    for n in nodes:
        nid = n.get("data", {}).get("id")
        if not nid:
            errors.append("Graph: node missing 'id' in data")
        node_ids.add(nid)
    for e in edges:
        data = e.get("data", {})
        if "source" not in data:
            errors.append(f"Graph edge missing 'source': {data}")
        if "target" not in data:
            errors.append(f"Graph edge missing 'target': {data}")
        if "source" in data and "target" in data:
            if data["source"] not in node_ids:
                errors.append(f"Graph edge source {data['source']!r} not in node_ids")
            if data["target"] not in node_ids:
                errors.append(f"Graph edge target {data['target']!r} not in node_ids")


def print_debug_info(result):
    print("\n    [DEBUG INFO]")
    print("    Extracted Entities:")
    for e in result.get("entities", []):
        print(f"      - {e['text']!r} ({e['type']})")
    print("    Resolved Entities:")
    for r in result.get("resolved_entities", []):
        print(f"      - {r['input_text']!r} ({r['input_type']}) -> db_id={r['db_id']!r} [{r['match_status']}] conf={r['confidence']}")
    print("    Relationships:")
    for rel in result.get("relationships", []):
        print(f"      - {rel['subject_label']} -[{rel['predicate']}]-> {rel['object_label']} (meta={rel.get('metadata')})")
    print("    Anomalies:")
    for a in result.get("anomalies", []):
        print(f"      - {a['entity_id']} ({a['entity_name']}): status={a['status']}, severity={a['severity']}, score={a['anomaly_score']}")
        print(f"        reasons: {a.get('reasons')}")
        print(f"        current: {a.get('current_features')}")
    print()


def run_test(tc: dict) -> tuple[bool, list, dict]:
    """Run a single test case. Returns (passed, errors_list, result)."""
    errors = []
    result = {}
    try:
        result = run_pipeline(tc["input_text"])

        check_expected_entities(result, tc.get("expected_entities", []), errors)
        check_min_relationships(result, tc.get("expected_min_relationships", 0), errors)
        check_expected_resolution(result, tc.get("expected_resolution", []), errors)
        check_anomaly(result, tc.get("expected_anomaly"), errors)
        check_historical(result, tc.get("expected_historical"), errors)
        check_new_entity(result, tc.get("expected_new_entity"), errors)
        check_graph(result, errors)

    except Exception as e:
        errors.append(f"Pipeline exception: {e}")
        errors.append(traceback.format_exc())

    return len(errors) == 0, errors, result


def main():
    from backend.data.test_cases import TEST_CASES

    print()
    print("=" * 48)
    print("  SIH-189 DEMO TESTS")
    print("=" * 48)
    print()

    print("-> Bootstrapping: resetting and reseeding database...")
    bootstrap()
    print("-> Database ready.\n")

    passed = 0
    failed = 0
    total = len(TEST_CASES)

    for i, tc in enumerate(TEST_CASES, 1):
        name = tc["name"]
        try:
            ok, errors, result = run_test(tc)
        except Exception as e:
            ok = False
            errors = [f"Unhandled exception in test runner: {e}", traceback.format_exc()]
            result = {}

        if ok:
            print(f"  [PASS] {name}")
            passed += 1
            if DEBUG:
                print_debug_info(result)
        else:
            print(f"  [FAIL] {name}")
            for err in errors:
                print(f"         x {err}")
            if DEBUG or True:
                print_debug_info(result)
            failed += 1

    print()
    print("=" * 48)
    print(f"  {passed}/{total} TESTS PASSED", end="")
    if failed:
        print(f"  ({failed} FAILED)")
    else:
        print()
    print("=" * 48)
    print()

    if failed > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
