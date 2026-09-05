export default function AnomalyPanel({ anomalies }) {
  if (!anomalies?.length) return null;

  const severityClass = (severity) => {
    if (severity === "HIGH")   return "anomaly-high";
    if (severity === "MEDIUM") return "anomaly-medium";
    return "anomaly-normal";
  };

  return (
    <div className="card" style={{ marginTop: "1.25rem" }}>
      <div className="card-title">
        <span className="dot" style={{ background: "#ef4444" }} />
        Anomaly Detection — IsolationForest Results
      </div>

      <div className="stack">
        {anomalies.map((a, i) => (
          <div key={i} className={`anomaly-card ${severityClass(a.severity)}`}>
            <div className="anomaly-header">
              <div>
                <span className="anomaly-name">{a.entity_name}</span>
                <span style={{ marginLeft: "0.5rem", fontSize: "0.72rem", fontFamily: "JetBrains Mono, monospace", color: "var(--text-muted)" }}>
                  {a.entity_id}
                </span>
              </div>
              <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                <span className={`badge badge-${a.severity === "HIGH" ? "high" : a.severity === "MEDIUM" ? "medium" : "low"}`}>
                  {a.status}
                </span>
                {a.status === "ANOMALY" && (
                  <span className={`badge badge-${a.severity === "HIGH" ? "high" : "medium"}`}>
                    {a.severity} severity
                  </span>
                )}
              </div>
            </div>

            {/* Current vs Baseline key stats */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "0.5rem", marginBottom: "0.75rem" }}>
              {[
                ["Calls/day", a.current_features?.calls_per_day, a.baseline_features?.calls_per_day],
                ["Night calls", a.current_features?.night_calls, a.baseline_features?.night_calls],
                ["New contacts", a.current_features?.new_contacts, a.baseline_features?.new_contacts],
                ["Txn amount", a.current_features?.transaction_amount ? `₹${a.current_features.transaction_amount.toLocaleString()}` : "0", a.baseline_features?.transaction_amount ? `₹${a.baseline_features.transaction_amount.toLocaleString()}` : "0"],
              ].map(([label, cur, base]) => (
                <div key={label} style={{
                  background: "rgba(0,0,0,0.25)", borderRadius: "var(--radius-sm)",
                  padding: "0.45rem 0.6rem",
                }}>
                  <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", marginBottom: "0.2rem" }}>{label}</div>
                  <div style={{ display: "flex", gap: "0.4rem", alignItems: "baseline" }}>
                    <span style={{ fontSize: "0.92rem", fontWeight: 700 }}>{cur ?? "—"}</span>
                    {base !== undefined && (
                      <span style={{ fontSize: "0.68rem", color: "var(--text-muted)" }}>
                        (base: {base})
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Score */}
            <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", marginBottom: "0.5rem" }}>
              IsolationForest score: <span style={{ fontFamily: "JetBrains Mono, monospace", color: "var(--text-secondary)" }}>{a.anomaly_score}</span>
              {" "}(more negative = more anomalous)
            </div>

            {/* Reasons */}
            {a.reasons?.length > 0 && (
              <>
                <div style={{ fontSize: "0.72rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-muted)", marginBottom: "0.4rem" }}>
                  Why flagged:
                </div>
                <ul className="anomaly-reasons">
                  {a.reasons.map((r, j) => <li key={j}>{r}</li>)}
                </ul>
              </>
            )}

            {a.status === "ANOMALY" && (
              <div style={{
                marginTop: "0.75rem", fontSize: "0.72rem",
                padding: "0.45rem 0.65rem",
                background: "rgba(245,158,11,0.08)",
                border: "1px solid rgba(245,158,11,0.2)",
                borderRadius: "var(--radius-sm)",
                color: "#fbbf24",
              }}>
                ⚠ This entity shows unusual behavioural patterns compared to historical baseline.
                This is NOT an indication of guilt — it flags activity warranting investigation.
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
