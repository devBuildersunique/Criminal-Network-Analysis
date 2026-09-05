"""
graph_analysis.py
Graph algorithms applied to the NetworkX DiGraph:
  - Degree Centrality
  - Betweenness Centrality
  - BFS Neighbors (depth 1-2)
  - Shortest Path
  - Community Detection (greedy modularity)
"""

import networkx as nx
from typing import Dict, List, Optional

try:
    from networkx.algorithms.community import greedy_modularity_communities
    COMMUNITY_AVAILABLE = True
except ImportError:
    COMMUNITY_AVAILABLE = False


def analyze_graph(G: nx.DiGraph) -> Dict:
    """
    Run all graph analyses and return a structured result dict.
    """
    if G.number_of_nodes() == 0:
        return _empty_result()

    # Work on undirected version for centrality (more meaningful for small graphs)
    UG = G.to_undirected()

    # ── Degree Centrality ──────────────────────────────────────────────────────
    degree_centrality = nx.degree_centrality(UG)
    degree_centrality = {k: round(v, 4) for k, v in degree_centrality.items()}

    # ── Betweenness Centrality ─────────────────────────────────────────────────
    betweenness_centrality = nx.betweenness_centrality(UG)
    betweenness_centrality = {k: round(v, 4) for k, v in betweenness_centrality.items()}

    # ── Most Connected Entity ──────────────────────────────────────────────────
    if degree_centrality:
        top_node = max(degree_centrality, key=degree_centrality.get)
        most_connected = {
            "entity_id": top_node,
            "label": G.nodes[top_node].get("label", top_node) if top_node in G else top_node,
            "degree": UG.degree(top_node),
            "centrality_score": degree_centrality[top_node],
        }
    else:
        most_connected = None

    # ── Bridge / High Betweenness Entities ────────────────────────────────────
    if betweenness_centrality:
        avg_bc = sum(betweenness_centrality.values()) / len(betweenness_centrality)
        bridges = [
            {
                "entity_id": node,
                "label": G.nodes[node].get("label", node) if node in G else node,
                "betweenness_score": score,
            }
            for node, score in sorted(
                betweenness_centrality.items(), key=lambda x: -x[1]
            )
            if score > avg_bc and score > 0
        ][:3]  # top 3 bridges
    else:
        bridges = []

    # ── BFS Neighbors (depth 1 and 2) ─────────────────────────────────────────
    bfs_neighbors: Dict[str, List[str]] = {}
    for node in list(G.nodes())[:5]:  # limit to first 5 for performance
        depth1 = list(UG.neighbors(node))
        depth2 = set()
        for n1 in depth1:
            depth2.update(UG.neighbors(n1))
        depth2.discard(node)
        depth2 -= set(depth1)
        bfs_neighbors[node] = {
            "depth_1": depth1,
            "depth_2": list(depth2),
        }

    # ── Community Detection ────────────────────────────────────────────────────
    communities = []
    if COMMUNITY_AVAILABLE and UG.number_of_edges() >= 2:
        try:
            raw_communities = list(greedy_modularity_communities(UG))
            communities = [list(c) for c in raw_communities]
        except Exception:
            communities = []

    # ── Raw degree counts per node ─────────────────────────────────────────────
    node_degrees = {
        node: {
            "in": G.in_degree(node),
            "out": G.out_degree(node),
            "total": G.degree(node),
        }
        for node in G.nodes()
    }

    return {
        "degree_centrality": degree_centrality,
        "betweenness_centrality": betweenness_centrality,
        "most_connected": most_connected,
        "bridge_entities": bridges,
        "communities": communities,
        "bfs_neighbors": bfs_neighbors,
        "node_degrees": node_degrees,
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
    }


def shortest_path(G: nx.DiGraph, source: str, target: str) -> Optional[List[str]]:
    """Return the shortest path between two entities (undirected)."""
    UG = G.to_undirected()
    try:
        return nx.shortest_path(UG, source=source, target=target)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None


def _empty_result() -> Dict:
    return {
        "degree_centrality": {},
        "betweenness_centrality": {},
        "most_connected": None,
        "bridge_entities": [],
        "communities": [],
        "bfs_neighbors": {},
        "node_degrees": {},
        "num_nodes": 0,
        "num_edges": 0,
    }
