"""
graph_builder.py
Builds a NetworkX DiGraph from resolved entities and relationships.
Also loads the historical graph from the DB (case-entity links, CDR, transactions).
"""

import networkx as nx
from typing import List, Dict

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import backend.database as db


# ─── Node type → color mapping (used by frontend) ─────────────────────────────
NODE_COLORS = {
    "PERSON": "#6366f1",       # indigo
    "VEHICLE": "#f59e0b",      # amber
    "LOCATION": "#10b981",     # emerald
    "PHONE": "#3b82f6",        # blue
    "CASE": "#ef4444",         # red
    "ORGANIZATION": "#8b5cf6", # violet
}


def build_graph(
    resolved_entities: List[Dict],
    relationships: List[Dict],
) -> nx.DiGraph:
    """
    Build a directed graph from:
    1. Current resolved entities (from the case statement)
    2. Extracted relationships
    3. Historical DB data (case-entity links, CDR, transactions)
    """
    G = nx.DiGraph()

    # ── Add nodes from resolved entities ──────────────────────────────────────
    for ent in resolved_entities:
        if not ent["db_id"]:
            # Unresolved entity — add as a new node
            node_id = f"NEW_{ent['input_type']}_{ent['input_text'][:10]}"
            G.add_node(
                node_id,
                label=ent["input_text"],
                node_type=ent["input_type"],
                resolved=False,
                color=NODE_COLORS.get(ent["input_type"], "#94a3b8"),
            )
        else:
            G.add_node(
                ent["db_id"],
                label=ent["db_name"] or ent["input_text"],
                node_type=ent["input_type"],
                resolved=True,
                color=NODE_COLORS.get(ent["input_type"], "#94a3b8"),
                db_record=ent.get("db_record"),
            )

    # ── Add edges from extracted relationships ─────────────────────────────────
    for rel in relationships:
        subj = rel["subject_id"]
        obj = rel["object_id"]
        pred = rel["predicate"]
        meta = rel.get("metadata", {})

        # Ensure nodes exist
        if subj not in G:
            G.add_node(subj, label=rel["subject_label"], node_type="PERSON",
                       color=NODE_COLORS["PERSON"])
        if obj not in G:
            G.add_node(obj, label=rel["object_label"], node_type="UNKNOWN",
                       color="#94a3b8")

        # Strip None-valued metadata keys before spreading onto the edge.
        # None values shadow defaults in later .get(key, default) calls,
        # causing e.g. G[u][v].get("frequency", 0) to return None instead of 0.
        clean_meta = {k: v for k, v in meta.items() if v is not None}
        G.add_edge(subj, obj, predicate=pred, **clean_meta)

    # ── Enrich with historical DB data ────────────────────────────────────────
    _add_historical_data(G, resolved_entities)

    return G


def _add_historical_data(G: nx.DiGraph, resolved_entities: List[Dict]):
    """Add case-entity links and CDR/transaction edges from the DB."""
    person_ids = [
        e["db_id"] for e in resolved_entities
        if e["input_type"] == "PERSON" and e["db_id"]
    ]

    for pid in person_ids:
        # Case links
        cases = db.get_cases_for_entity(pid)
        for case in cases:
            cid = case["id"]
            if cid not in G:
                G.add_node(cid, label=f"Case {cid}", node_type="CASE",
                           color=NODE_COLORS["CASE"], title=case.get("title", ""))
            if not G.has_edge(pid, cid):
                G.add_edge(pid, cid, predicate="INVOLVED_IN",
                           role=case.get("role", ""), record_source="historical_db")

        # CDR edges
        cdrs = db.get_cdr_for_entity(pid)
        for cdr in cdrs:
            other = cdr["callee_id"] if cdr["caller_id"] == pid else cdr["caller_id"]
            if other in G or other in person_ids:
                if other not in G:
                    person = db.get_person(other)
                    if person:
                        G.add_node(other, label=person["name"], node_type="PERSON",
                                   color=NODE_COLORS["PERSON"])
                if G.has_edge(pid, other) and G[pid][other].get("predicate") == "CALLED":
                    # None-safe increment: the edge may have frequency=None if it was
                    # created from relationship metadata that had no numeric frequency.
                    current_freq = G[pid][other].get("frequency")
                    G[pid][other]["frequency"] = int(current_freq or 0) + 1
                elif not G.has_edge(pid, other):
                    G.add_edge(pid, other, predicate="CALLED", frequency=1,
                               record_source="CDR_db")

        # Transaction edges
        txns = db.get_transactions_for_entity(pid)
        for txn in txns:
            other = txn["receiver_id"] if txn["sender_id"] == pid else txn["sender_id"]
            if other not in G:
                person = db.get_person(other)
                if person:
                    G.add_node(other, label=person["name"], node_type="PERSON",
                               color=NODE_COLORS["PERSON"])
            if other in G and not G.has_edge(pid, other):
                G.add_edge(pid, other, predicate="TRANSFERRED_MONEY",
                           amount=txn.get("amount"), record_source="transaction_db")


def graph_to_cytoscape(G: nx.DiGraph) -> tuple[list, list]:
    """Convert NetworkX graph to Cytoscape.js nodes + edges format."""
    nodes = []
    for node_id, data in G.nodes(data=True):
        nodes.append({
            "data": {
                "id": str(node_id),
                "label": data.get("label", str(node_id)),
                "node_type": data.get("node_type", "UNKNOWN"),
                "color": data.get("color", "#94a3b8"),
                "resolved": data.get("resolved", True),
            }
        })

    edges = []
    # Keys reserved by Cytoscape that must NOT be overridden by metadata
    RESERVED = {"id", "source", "target", "label", "predicate"}
    for u, v, data in G.edges(data=True):
        extra = {k: v2 for k, v2 in data.items() if k not in RESERVED}
        edges.append({
            "data": {
                "id": f"{u}__{v}",
                "source": str(u),
                "target": str(v),
                "predicate": data.get("predicate", "RELATED_TO"),
                "label": data.get("predicate", ""),
                **extra,
            }
        })

    return nodes, edges
