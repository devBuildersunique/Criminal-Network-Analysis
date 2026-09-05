import { useState, useEffect } from "react";
import { getEntity } from "../api";

const NODE_TYPE_ICON = {
  PERSON: "👤", VEHICLE: "🚗", LOCATION: "📍",
  PHONE: "📞", CASE: "📂", ORGANIZATION: "🏢",
};

export default function EntityDetailModal({ node, onClose }) {
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!node) { setDetails(null); return; }
    // Only fetch person details
    if (node.node_type === "PERSON" && node.id?.startsWith("P")) {
      setLoading(true);
      getEntity(node.id)
        .then(setDetails)
        .catch(() => setDetails(null))
        .finally(() => setLoading(false));
    }
  }, [node]);

  if (!node) return null;

  return (
    <div
      style={{
        position: "fixed", inset: 0, background: "rgba(0,0,0,0.65)",
        backdropFilter: "blur(4px)", zIndex: 200,
        display: "flex", alignItems: "center", justifyContent: "center",
        padding: "1rem",
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: "var(--bg-card)", border: "1px solid var(--border-light)",
          borderRadius: "var(--radius-xl)", padding: "1.75rem",
          minWidth: "360px", maxWidth: "520px", width: "100%",
          boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.25rem" }}>
          <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
            <div style={{
              width: 48, height: 48, borderRadius: "50%",
              background: `var(--bg-surface)`,
              border: "2px solid var(--border-light)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "1.4rem",
            }}>
              {NODE_TYPE_ICON[node.node_type] || "●"}
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: "1.05rem" }}>{node.label}</div>
              <div style={{ fontSize: "0.72rem", color: "var(--accent-cyan)", fontFamily: "JetBrains Mono, monospace", marginTop: 2 }}>
                {node.id} · {node.node_type}
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "var(--bg-hover)", border: "1px solid var(--border)",
              borderRadius: "var(--radius-sm)", color: "var(--text-secondary)",
              width: 30, height: 30, cursor: "pointer", fontSize: "1rem",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}
          >✕</button>
        </div>

        {loading && (
          <div style={{ textAlign: "center", padding: "1.5rem", color: "var(--text-muted)" }}>
            <span className="spinner" />
          </div>
        )}

        {!loading && details && (
          <>
            {/* Person details */}
            {details.person && (
              <div style={{ marginBottom: "1rem" }}>
                <div style={{ fontSize: "0.72rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-muted)", marginBottom: "0.5rem" }}>
                  Profile
                </div>
                {[
                  ["Name", details.person.name],
                  ["Age", details.person.age],
                  ["Address", details.person.address],
                  ["Aliases", details.person.aliases],
                ].map(([label, value]) => (
                  value ? (
                    <div className="stat-row" key={label}>
                      <span className="stat-label">{label}</span>
                      <span className="stat-value" style={{ fontSize: "0.82rem" }}>{value}</span>
                    </div>
                  ) : null
                ))}
              </div>
            )}

            {/* Cases */}
            {details.cases?.length > 0 && (
              <div style={{ marginBottom: "1rem" }}>
                <div style={{ fontSize: "0.72rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-muted)", marginBottom: "0.5rem" }}>
                  Case History ({details.cases.length})
                </div>
                {details.cases.map((c, i) => (
                  <div className="stat-row" key={i}>
                    <span style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "0.75rem", color: "#f87171" }}>{c.id}</span>
                    <span className="stat-label" style={{ flex: 1, marginLeft: "0.5rem" }}>{c.title}</span>
                    <span style={{ fontSize: "0.68rem", color: "var(--text-muted)" }}>{c.role}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Activity summary */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
              {[
                ["CDR Records", details.cdr_count],
                ["Transactions", details.transaction_count],
              ].map(([label, val]) => (
                <div key={label} style={{
                  background: "var(--bg-surface)", borderRadius: "var(--radius-sm)",
                  padding: "0.6rem 0.8rem", border: "1px solid var(--border)",
                }}>
                  <div style={{ fontSize: "0.68rem", color: "var(--text-muted)" }}>{label}</div>
                  <div style={{ fontWeight: 700, fontSize: "1.1rem", marginTop: "0.2rem" }}>{val}</div>
                </div>
              ))}
            </div>
          </>
        )}

        {!loading && !details && (
          <div style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginTop: "0.5rem" }}>
            <div style={{ marginBottom: "0.5rem" }}>
              <strong>Type:</strong> {node.node_type}
            </div>
            <div style={{ color: "var(--text-muted)", fontSize: "0.78rem" }}>
              Detailed view is available for PERSON entities stored in the database.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
