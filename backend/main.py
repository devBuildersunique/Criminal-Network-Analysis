"""
main.py — FastAPI application for the Criminal Network Analysis System.
Prototype using synthetic investigative data.
"""

import sys
import os

# Ensure project root is on sys.path so submodule imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import backend.database as db
from backend.models import CaseRequest, AnalysisResponse
from backend.nlp.entity_extractor import extract_entities
from backend.nlp.entity_resolver import resolve_entities
from backend.nlp.relationship_extractor import extract_relationships
from backend.graph.graph_builder import build_graph, graph_to_cytoscape
from backend.graph.graph_analysis import analyze_graph
from backend.anomaly.isolation_forest import run_anomaly_detection_all

# ─── App Setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Criminal Network Analysis System",
    description="AI-Powered Criminal Network Analysis — SIH 2024 Prototype (synthetic data only)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure DB is seeded at startup
db.ensure_seeded()

# ─── Helpers ───────────────────────────────────────────────────────────────────

def _compute_priority_score(
    subj_id: str,
    obj_id: str,
    subj_label: str,
    obj_label: str,
    relationships: list,
    historical_cases: list,
    anomalies: list,
    graph_analysis: dict,
) -> dict:
    """Compute investigation priority between two entities."""
    score = 0.0
    reasons = []

    # Relationship strength: count edges between the two
    direct_rels = [
        r for r in relationships
        if (r["subject_id"] == subj_id and r["object_id"] == obj_id)
        or (r["subject_id"] == obj_id and r["object_id"] == subj_id)
    ]
    if direct_rels:
        rel_score = min(len(direct_rels) * 0.2, 0.4)
        score += rel_score
        predicates = list({r["predicate"] for r in direct_rels})
        reasons.append(f"Direct connections: {', '.join(predicates)}")

    # Call frequency bonus
    for rel in direct_rels:
        freq = rel.get("metadata", {}).get("frequency")
        if freq and freq > 10:
            score += 0.15
            reasons.append(f"High call frequency: {freq} contacts")
            break

    # Financial transfer bonus
    has_money_transfer = any(r["predicate"] == "TRANSFERRED_MONEY" for r in direct_rels)
    if has_money_transfer:
        score += 0.2
        reasons.append("Large financial transfer detected")

    # Shared historical cases
    subj_cases = {hc["case_id"] for hc in historical_cases if subj_id in hc.get("entities_involved", [])}
    obj_cases = {hc["case_id"] for hc in historical_cases if obj_id in hc.get("entities_involved", [])}
    shared = subj_cases & obj_cases
    if shared:
        score += min(len(shared) * 0.15, 0.3)
        reasons.append(f"Shared historical cases: {', '.join(shared)}")

    # Anomaly bonus
    subj_anomalies = [a for a in anomalies if a["entity_id"] == subj_id and a["status"] == "ANOMALY"]
    if subj_anomalies:
        severity = subj_anomalies[0].get("severity", "LOW")
        boost = {"HIGH": 0.25, "MEDIUM": 0.15, "LOW": 0.05}.get(severity, 0)
        score += boost
        reasons.append(f"Communication anomaly: {severity} severity for {subj_label}")

    # Graph centrality bonus
    deg_centrality = graph_analysis.get("degree_centrality", {})
    if subj_id in deg_centrality and deg_centrality[subj_id] > 0.4:
        score += 0.1
        reasons.append(f"{subj_label} is highly connected in the network")

    score = round(min(score, 1.0), 3)
    if score >= 0.6:
        priority = "HIGH"
    elif score >= 0.35:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return {
        "subject_id": subj_id,
        "subject_label": subj_label,
        "object_id": obj_id,
        "object_label": obj_label,
        "priority": priority,
        "priority_score": score,
        "reasons": reasons,
    }


def _get_historical_cases(resolved_entities: list) -> list:
    """Fetch and structure historical case connections for all resolved persons."""
    person_ids = [
        e["db_id"] for e in resolved_entities
        if e["input_type"] == "PERSON" and e["db_id"]
    ]

    seen_cases = {}
    for pid in person_ids:
        cases = db.get_cases_for_entity(pid)
        for case in cases:
            cid = case["id"]
            if cid not in seen_cases:
                seen_cases[cid] = {
                    "case_id": cid,
                    "case_title": case.get("title", ""),
                    "case_status": case.get("status", ""),
                    "case_date": case.get("date", ""),
                    "entities_involved": [],
                    "shared_with_current": [],
                }
            seen_cases[cid]["entities_involved"].append(pid)

    # Mark cases shared between multiple current-statement persons
    for cid, hc in seen_cases.items():
        involved = hc["entities_involved"]
        if len(involved) > 1:
            hc["shared_with_current"] = involved

    return list(seen_cases.values())


# ─── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/analyze-case", response_model=dict)
async def analyze_case(request: CaseRequest):
    """
    Main pipeline endpoint:
      1. NLP entity extraction
      2. Entity resolution
      3. Relationship extraction
      4. Graph construction
      5. Graph analysis
      6. Historical case lookup
      7. Anomaly detection
      8. Priority scoring
    """
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Case text cannot be empty.")

    # 1. Extract entities
    entities = extract_entities(text)

    # 2. Resolve entities
    resolved = resolve_entities(entities)

    # 3. Extract relationships
    relationships = extract_relationships(text, resolved)

    # 4. Build graph
    G = build_graph(resolved, relationships)
    nodes, edges = graph_to_cytoscape(G)

    # 5. Graph analysis
    graph_analysis = analyze_graph(G)

    # 6. Historical cases
    historical_cases = _get_historical_cases(resolved)

    # 7. Anomaly detection for all resolved persons
    person_ids = list({
        e["db_id"] for e in resolved
        if e["input_type"] == "PERSON" and e["db_id"]
    })
    anomalies = run_anomaly_detection_all(person_ids)

    # 8. Priority connections — compute for all person pairs
    priority_connections = []
    for i, subj in enumerate(person_ids):
        for j, obj in enumerate(person_ids):
            if i < j:
                subj_label = next(
                    (e["db_name"] for e in resolved if e["db_id"] == subj), subj
                )
                obj_label = next(
                    (e["db_name"] for e in resolved if e["db_id"] == obj), obj
                )
                pconn = _compute_priority_score(
                    subj, obj, subj_label, obj_label,
                    relationships, historical_cases, anomalies, graph_analysis
                )
                priority_connections.append(pconn)

    priority_connections.sort(key=lambda x: -x["priority_score"])

    return {
        "case_text": text,
        "entities": entities,
        "resolved_entities": resolved,
        "relationships": relationships,
        "historical_cases": historical_cases,
        "graph_analysis": graph_analysis,
        "anomalies": anomalies,
        "priority_connections": priority_connections,
        "graph_nodes": nodes,
        "graph_edges": edges,
    }


@app.get("/entity/{entity_id}")
async def get_entity(entity_id: str):
    """Get full details for a specific entity."""
    person = db.get_person(entity_id)
    if not person:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found.")
    cases = db.get_cases_for_entity(entity_id)
    cdr = db.get_cdr_for_entity(entity_id)
    txns = db.get_transactions_for_entity(entity_id)
    return {
        "person": person,
        "cases": cases,
        "cdr_count": len(cdr),
        "transaction_count": len(txns),
    }


@app.get("/entity/{entity_id}/history")
async def get_entity_history(entity_id: str):
    """Get historical case involvement for an entity."""
    cases = db.get_cases_for_entity(entity_id)
    if cases is None:
        raise HTTPException(status_code=404, detail="Entity not found.")
    return {"entity_id": entity_id, "cases": cases}


@app.get("/entity/{entity_id}/network")
async def get_entity_network(entity_id: str):
    """Get 1-hop neighbors of an entity from the DB."""
    cdr = db.get_cdr_for_entity(entity_id)
    contacts = set()
    for r in cdr:
        other = r["callee_id"] if r["caller_id"] == entity_id else r["caller_id"]
        contacts.add(other)
    people = [db.get_person(pid) for pid in contacts if db.get_person(pid)]
    return {"entity_id": entity_id, "network": people}


@app.post("/anomaly-detection")
async def anomaly_detection_endpoint(body: dict):
    """Standalone anomaly detection for a given entity_id."""
    entity_id = body.get("entity_id")
    if not entity_id:
        raise HTTPException(status_code=400, detail="entity_id required.")
    result = run_anomaly_detection_all([entity_id])
    return result[0] if result else {}


@app.get("/health")
async def health():
    """Check status of all system components."""
    status = {
        "status": "ok",
        "database": "ok",
        "nlp": "ok",
        "anomaly_model": "ok",
    }

    # Check database
    try:
        conn = db.get_connection()
        conn.execute("SELECT COUNT(*) FROM people").fetchone()
        conn.close()
    except Exception as e:
        status["database"] = f"error: {e}"
        status["status"] = "degraded"

    # Check NLP (spaCy model)
    try:
        from backend.nlp.entity_extractor import extract_entities
        result = extract_entities("Test sentence with Rahul Sharma.")
        if not isinstance(result, list):
            raise ValueError("Unexpected return type from extract_entities")
    except Exception as e:
        status["nlp"] = f"error: {e}"
        status["status"] = "degraded"

    # Check anomaly model
    try:
        from backend.anomaly.isolation_forest import _get_model
        model = _get_model()
        if model is None:
            raise ValueError("Model returned None")
        status["anomaly_model"] = "ok"
    except Exception as e:
        status["anomaly_model"] = f"error: {e}"
        status["status"] = "degraded"

    return status


@app.get("/demo-text")
async def demo_text():
    return {
        "text": (
            "Rahul Sharma met Amit Kumar in Delhi on 25 August. "
            "Rahul contacted Amit 42 times in two days using phone 9876543210. "
            "Rahul transferred Rs 850000 to Amit. "
            "Rahul used vehicle DL01AB1234. "
            "Rahul was previously mentioned in Case C102 with Ravi Singh."
        )
    }
