"""
models.py — Pydantic request/response models for the FastAPI application.
"""

from pydantic import BaseModel
from typing import Any, Optional


class CaseRequest(BaseModel):
    text: str


class ExtractedEntity(BaseModel):
    text: str
    type: str          # PERSON, PHONE, VEHICLE, LOCATION, CASE, MONEY, DATE, ORG
    start: Optional[int] = None
    end: Optional[int] = None
    confidence: float = 1.0


class ResolvedEntity(BaseModel):
    input_text: str
    input_type: str
    db_id: Optional[str] = None
    db_name: Optional[str] = None
    confidence: float = 0.0
    match_status: str  # "AUTO_MATCH" | "POSSIBLE_MATCH" | "NEW_ENTITY"
    db_record: Optional[dict] = None


class Relationship(BaseModel):
    subject_id: str
    subject_label: str
    predicate: str
    object_id: str
    object_label: str
    metadata: dict = {}


class HistoricalCase(BaseModel):
    case_id: str
    case_title: str
    case_status: str
    case_date: str
    entities_involved: list[str]
    shared_with_current: list[str]


class GraphAnalysis(BaseModel):
    degree_centrality: dict[str, float]
    betweenness_centrality: dict[str, float]
    most_connected: Optional[dict] = None
    bridge_entities: list[dict] = []
    communities: list[list[str]] = []
    bfs_neighbors: dict[str, list[str]] = {}


class AnomalyResult(BaseModel):
    entity_id: str
    entity_name: str
    status: str           # "ANOMALY" | "NORMAL" | "UNKNOWN"
    anomaly_score: float  # raw IsolationForest score (negative = more anomalous)
    severity: str         # "HIGH" | "MEDIUM" | "LOW" | "NORMAL"
    reasons: list[str]
    current_features: dict
    baseline_features: dict


class PriorityConnection(BaseModel):
    subject_id: str
    subject_label: str
    object_id: str
    object_label: str
    priority: str          # "HIGH" | "MEDIUM" | "LOW"
    priority_score: float
    reasons: list[str]


class AnalysisResponse(BaseModel):
    case_text: str
    entities: list[ExtractedEntity]
    resolved_entities: list[ResolvedEntity]
    relationships: list[Relationship]
    historical_cases: list[HistoricalCase]
    graph_analysis: GraphAnalysis
    anomalies: list[AnomalyResult]
    priority_connections: list[PriorityConnection]
    graph_nodes: list[dict]
    graph_edges: list[dict]
