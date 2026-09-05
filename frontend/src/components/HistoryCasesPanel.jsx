export default function HistoryCasesPanel({ historicalCases, relationships, graphAnalysis, priorityConnections }) {
  const hasContent =
    historicalCases?.length ||
    relationships?.length ||
    priorityConnections?.length;

  if (!hasContent) return null;

  return (
    <div className="stack" style={{ marginTop: "1.25rem" }}>
      {/* Historical Cases */}
      {historicalCases?.length > 0 && (
        <div className="card">
          <div className="card-title">
            <span className="dot" style={{ background: "#ef4444" }} />
            Historical & Cross-Case Connections ({historicalCases.length})
          </div>
          <div className="scroll-box stack" style={{ gap: "0.5rem" }}>
            {historicalCases.map((hc, i) => (
              <div className="hist-case" key={i}>
                <span className="hist-case-id">{hc.case_id}</span>
                <span className="hist-case-title">{hc.case_title}</span>
                <span className={`badge badge-${hc.case_status === "Active" ? "high" : "date"}`}>
                  {hc.case_status}
                </span>
                <span style={{ fontSize: "0.72rem", fontFamily: "JetBrains Mono, monospace", color: "var(--text-muted)" }}>
                  {hc.case_date}
                </span>
                {hc.shared_with_current?.length > 1 && (
                  <span className="hist-shared">
                    🔗 Shared by {hc.entities_involved.join(", ")}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Relationships */}
      {relationships?.length > 0 && (
        <div className="card">
          <div className="card-title">
            <span className="dot" style={{ background: "#8b5cf6" }} />
            Extracted Relationships ({relationships.length})
          </div>
          <div className="scroll-box stack" style={{ gap: "0.4rem" }}>
            {relationships.map((r, i) => (
              <div className="rel-item" key={i}>
                <span className="rel-subject">{r.subject_label}</span>
                <span className="rel-arrow">→</span>
                <span className="rel-predicate">{r.predicate}</span>
                <span className="rel-arrow">→</span>
                <span className="rel-object">{r.object_label}</span>
                {r.metadata?.frequency && (
                  <span style={{ marginLeft: "auto", fontSize: "0.72rem", color: "var(--text-muted)" }}>
                    ×{r.metadata.frequency} times
                  </span>
                )}
                {r.metadata?.amount && (
                  <span style={{ marginLeft: "auto", fontSize: "0.72rem", color: "#6ee7b7" }}>
                    ₹{r.metadata.amount?.toLocaleString()}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Graph Analysis Summary */}
      {graphAnalysis && (
        <div className="card">
          <div className="card-title">
            <span className="dot" style={{ background: "#06b6d4" }} />
            Graph Analysis Results
          </div>
          <div className="grid-2">
            <div>
              <div style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-muted)", marginBottom: "0.6rem" }}>
                Network Stats
              </div>
              <div className="stat-row">
                <span className="stat-label">Nodes</span>
                <span className="stat-value">{graphAnalysis.num_nodes ?? "—"}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Edges</span>
                <span className="stat-value">{graphAnalysis.num_edges ?? "—"}</span>
              </div>
              {graphAnalysis.most_connected && (
                <div className="stat-row">
                  <span className="stat-label">Most connected</span>
                  <span className="stat-value">{graphAnalysis.most_connected.label} (deg {graphAnalysis.most_connected.degree})</span>
                </div>
              )}
              {graphAnalysis.communities?.length > 0 && (
                <div className="stat-row">
                  <span className="stat-label">Communities</span>
                  <span className="stat-value">{graphAnalysis.communities.length}</span>
                </div>
              )}
            </div>

            <div>
              <div style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-muted)", marginBottom: "0.6rem" }}>
                Key Bridge Entities
              </div>
              {graphAnalysis.bridge_entities?.length > 0 ? (
                graphAnalysis.bridge_entities.map((b, i) => (
                  <div className="stat-row" key={i}>
                    <span className="stat-label">{b.label || b.entity_id}</span>
                    <span className="stat-value" style={{ color: "#f87171" }}>
                      BC: {b.betweenness_score?.toFixed(3)}
                    </span>
                  </div>
                ))
              ) : (
                <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>No bridge entities found</div>
              )}

              <div style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-muted)", margin: "0.75rem 0 0.5rem" }}>
                Top Degree Centrality
              </div>
              {Object.entries(graphAnalysis.degree_centrality || {})
                .sort((a, b) => b[1] - a[1])
                .slice(0, 3)
                .map(([id, score]) => (
                  <div className="stat-row" key={id}>
                    <span className="stat-label">{id}</span>
                    <span className="stat-value">{(score * 100).toFixed(1)}%</span>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}

      {/* Priority Connections */}
      {priorityConnections?.length > 0 && (
        <div className="card">
          <div className="card-title">
            <span className="dot" style={{ background: "#f59e0b" }} />
            Investigation Priority Score
          </div>
          <div className="stack">
            {priorityConnections.map((pc, i) => (
              <div key={i} className={`priority-card priority-${pc.priority}`}>
                <div className="priority-header">
                  <div className="priority-entities">
                    {pc.subject_label} ↔ {pc.object_label}
                  </div>
                  <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                    <span className={`badge badge-${pc.priority === "HIGH" ? "high" : pc.priority === "MEDIUM" ? "medium" : "low"}`}>
                      {pc.priority} PRIORITY
                    </span>
                    <span style={{ fontSize: "0.72rem", fontFamily: "JetBrains Mono, monospace", color: "var(--text-muted)" }}>
                      Score: {(pc.priority_score * 100).toFixed(0)}
                    </span>
                  </div>
                </div>
                <div className="priority-reasons">
                  {pc.reasons?.map((r, j) => (
                    <span key={j} className="priority-reason-chip">{r}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: "0.75rem", fontSize: "0.72rem", color: "var(--text-muted)", fontStyle: "italic" }}>
            * Investigation Priority Score is based on network connections, communication patterns, shared cases, and behavioral anomalies.
            It is NOT a probability of guilt or criminality.
          </div>
        </div>
      )}
    </div>
  );
}
