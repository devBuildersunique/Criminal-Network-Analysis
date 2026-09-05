import { useState, useEffect } from "react";
import "./index.css";
import CaseInput from "./components/CaseInput";
import EntitiesPanel from "./components/EntitiesPanel";
import NetworkGraph from "./components/NetworkGraph";
import AnomalyPanel from "./components/AnomalyPanel";
import HistoryCasesPanel from "./components/HistoryCasesPanel";
import EntityDetailModal from "./components/EntityDetailModal";
import { checkHealth } from "./api";

export default function App() {
  const [result, setResult]         = useState(null);
  const [loading, setLoading]       = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [health, setHealth]         = useState(null);   // null = unknown

  // Poll health on mount and every 15 s
  useEffect(() => {
    const poll = async () => {
      const h = await checkHealth();
      setHealth(h);
    };
    poll();
    const id = setInterval(poll, 15000);
    return () => clearInterval(id);
  }, []);

  const statusDot = (val) => {
    if (val === undefined || val === null) return "⬤ ";
    if (val === "ok") return <span style={{ color: "#4ade80" }}>⬤ </span>;
    return <span style={{ color: "#f87171" }}>⬤ </span>;
  };

  const statusText = (val) => {
    if (val === undefined || val === null) return "Checking…";
    if (val === "ok") return "Ready";
    return "Error";
  };

  return (
    <div className="app-shell">
      {/* Header */}
      <header className="app-header">
        <div className="logo-icon">🔍</div>
        <div>
          <h1>Criminal Network Analysis System</h1>
          <div className="subtitle">SIH 2024 · Ministry of Home Affairs · NCRB</div>
        </div>
        <span className="prototype-badge">⚠ Prototype — Synthetic Data Only</span>
      </header>

      <main className="app-main">
        {/* System Status Bar */}
        <div style={{
          display: "flex", flexWrap: "wrap", gap: "1.25rem",
          padding: "0.6rem 1rem",
          background: "var(--bg-card)",
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--border)",
          fontSize: "0.75rem",
          color: "var(--text-secondary)",
          marginBottom: "1rem",
          alignItems: "center",
        }}>
          <span style={{ fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", fontSize: "0.68rem" }}>
            System Status
          </span>
          {[
            ["Backend",       health?.status],
            ["Database",      health?.database],
            ["NLP",           health?.nlp],
            ["Anomaly Model", health?.anomaly_model],
          ].map(([label, val]) => (
            <span key={label} style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
              {statusDot(health === null ? null : val)}
              <span>{label}:</span>
              <span style={{
                color: health === null ? "var(--text-muted)"
                  : val === "ok" ? "#4ade80" : "#f87171",
                fontFamily: "JetBrains Mono, monospace",
              }}>
                {health === null ? "—" : statusText(val)}
              </span>
            </span>
          ))}
        </div>

        {/* Case Input */}
        <CaseInput onResult={setResult} onLoading={setLoading} health={health} />

        {/* Loading indicator */}
        {loading && (
          <div style={{
            display: "flex", alignItems: "center", gap: "1rem",
            padding: "1.25rem", marginTop: "1.25rem",
            background: "var(--bg-card)", borderRadius: "var(--radius-lg)",
            border: "1px solid var(--border)",
          }}>
            <span className="spinner" />
            <span style={{ color: "var(--text-secondary)" }}>
              Running NLP pipeline → Entity resolution → Graph analysis → Anomaly detection...
            </span>
          </div>
        )}

        {result && !loading && (
          <>
            {/* Pipeline summary banner */}
            <div style={{
              marginTop: "1.25rem",
              padding: "0.75rem 1.25rem",
              background: "rgba(99,102,241,0.08)",
              border: "1px solid rgba(99,102,241,0.2)",
              borderRadius: "var(--radius-md)",
              display: "flex", flexWrap: "wrap", gap: "1.5rem",
              fontSize: "0.8rem", color: "var(--text-secondary)",
            }}>
              {[
                ["Entities extracted", result.entities?.length],
                ["Resolved",          result.resolved_entities?.filter(e => e.db_id).length],
                ["Relationships",     result.relationships?.length],
                ["Graph nodes",       result.graph_nodes?.length],
                ["Historical cases",  result.historical_cases?.length],
                ["Anomalies",         result.anomalies?.filter(a => a.status === "ANOMALY").length],
              ].map(([label, val]) => (
                <span key={label}>
                  <strong style={{ color: "var(--text-primary)" }}>{val ?? 0}</strong> {label}
                </span>
              ))}
            </div>

            {/* 1. Extracted Entities & Entity Resolution */}
            <EntitiesPanel
              entities={result.entities}
              resolvedEntities={result.resolved_entities}
            />

            {/* 2. Relationship Graph */}
            <div style={{ marginTop: "1.25rem" }}>
              <NetworkGraph
                nodes={result.graph_nodes}
                edges={result.graph_edges}
                onNodeClick={setSelectedNode}
              />
            </div>

            {/* 3. Anomaly Alerts */}
            <AnomalyPanel anomalies={result.anomalies} />

            {/* 4. Historical Cases, Relationships, Graph Analysis, Investigation Priority */}
            <HistoryCasesPanel
              historicalCases={result.historical_cases}
              relationships={result.relationships}
              graphAnalysis={result.graph_analysis}
              priorityConnections={result.priority_connections}
            />
          </>
        )}

        {/* Footer */}
        <div style={{
          marginTop: "2rem", paddingTop: "1rem",
          borderTop: "1px solid var(--border)",
          fontSize: "0.72rem", color: "var(--text-muted)",
          textAlign: "center",
        }}>
          SIH 2024 — Problem Statement 26189 · All data is synthetic and for demonstration only ·
          NLP: spaCy en_core_web_sm + Regex · Entity Resolution: RapidFuzz ·
          Graph: NetworkX + Cytoscape.js · Anomaly Detection: scikit-learn IsolationForest (random_state=42)
        </div>
      </main>

      {/* Entity Detail Modal */}
      {selectedNode && (
        <EntityDetailModal node={selectedNode} onClose={() => setSelectedNode(null)} />
      )}
    </div>
  );
}
