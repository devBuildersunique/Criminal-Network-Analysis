"""
Test the live API for:
1. Communication-anomaly case (Rahul 45 times during the day...)
2. Multi-source demo case (full demo with Ravi Singh etc.)
"""
import urllib.request, json, sys

def post(text):
    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        "http://localhost:8000/analyze-case",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

def check_health():
    with urllib.request.urlopen("http://localhost:8000/health", timeout=5) as r:
        return json.loads(r.read())

print("=== GET /health ===")
h = check_health()
print("status=%s database=%s nlp=%s anomaly_model=%s" % (
    h.get("status"), h.get("database"), h.get("nlp"), h.get("anomaly_model")))
assert h["status"] == "ok", "Health check failed!"
print("PASS: health OK")
print()

# ── Test 1: Communication-anomaly input ──────────────────────────────────────
TEST1 = (
    "Rahul Sharma contacted Amit Kumar 45 times during the day "
    "and contacted 15 new phone numbers during the night."
)
print("=== POST /analyze-case (communication-anomaly) ===")
print("Input:", TEST1)
r1 = post(TEST1)

persons = [e for e in r1["entities"] if e["type"] == "PERSON"]
dates   = [e for e in r1["entities"] if e["type"] == "DATE"]
noise   = [e for e in dates if e["text"].lower() in ("the day", "the night")]

print("\nExtracted entities:")
for e in r1["entities"]:
    print("  [%-12s] %r" % (e["type"], e["text"]))

print("\nResolved persons:")
for r in r1["resolved_entities"]:
    if r["input_type"] == "PERSON" and r["db_id"]:
        print("  %r -> %s [%s]" % (r["input_text"], r["db_id"], r["match_status"]))

print("\nRelationships (%d):" % len(r1["relationships"]))
for rel in r1["relationships"]:
    print("  %s --[%s]--> %s" % (rel["subject_label"], rel["predicate"], rel["object_label"]))

print("\nAnomalies:")
for a in r1["anomalies"]:
    print("  %s (%s): %s / %s  score=%.4f" % (
        a["entity_id"], a["entity_name"], a["status"], a["severity"], a["anomaly_score"]
    ))
    for reason in a.get("reasons", []):
        print("    - %s" % reason)

print()
p001 = next((a for a in r1["anomalies"] if a["entity_id"] == "P001"), None)
p002 = next((a for a in r1["anomalies"] if a["entity_id"] == "P002"), None)
assert not noise,              "FAIL: DATE noise present: %s" % [e["text"] for e in noise]
assert p001 and p001["status"] == "ANOMALY", "FAIL: P001 not ANOMALY"
print("PASS: No DATE noise ('the day'/'the night')")
print("PASS: P001 (Rahul) is ANOMALY/%s" % p001["severity"])
if p002:
    print("INFO: P002 (Amit) is %s/%s" % (p002["status"], p002["severity"]))
print("PASS: graph_nodes=%d, graph_edges=%d (no 500 error)" % (
    len(r1["graph_nodes"]), len(r1["graph_edges"])
))
print()

# ── Test 2: Full multi-source demo ───────────────────────────────────────────
TEST2 = (
    "Rahul Sharma met Amit Kumar in Delhi on 25 August. "
    "Rahul contacted Amit 42 times in two days using phone 9876543210. "
    "Rahul transferred Rs 850000 to Amit. "
    "Rahul used vehicle DL01AB1234. "
    "Rahul was previously mentioned in Case C102 with Ravi Singh."
)
print("=== POST /analyze-case (full demo) ===")
r2 = post(TEST2)

persons2 = [e for e in r2["entities"] if e["type"] == "PERSON"]
print("Persons extracted: %s" % [e["text"] for e in persons2])
print("Relationships: %d" % len(r2["relationships"]))
print("Historical cases: %d" % len(r2["historical_cases"]))
print("Anomalies: %s" % [(a["entity_id"], a["status"], a["severity"]) for a in r2["anomalies"]])
print("Graph: %d nodes, %d edges" % (len(r2["graph_nodes"]), len(r2["graph_edges"])))

ravi_ok = any("Ravi" in e["text"] for e in persons2)
rels_ok  = len(r2["relationships"]) >= 5
hist_ok  = len(r2["historical_cases"]) >= 1
graph_ok = len(r2["graph_nodes"]) >= 7

assert ravi_ok,  "FAIL: Ravi Singh not extracted"
assert rels_ok,  "FAIL: Too few relationships: %d" % len(r2["relationships"])
assert hist_ok,  "FAIL: No historical cases"
assert graph_ok, "FAIL: Too few graph nodes"

print()
print("PASS: Ravi Singh extracted and resolved")
print("PASS: %d relationships" % len(r2["relationships"]))
print("PASS: %d historical cases" % len(r2["historical_cases"]))
print("PASS: Graph renders (%d nodes, %d edges)" % (len(r2["graph_nodes"]), len(r2["graph_edges"])))
print()
print("ALL API CHECKS PASSED")
