const TYPE_BADGE = {
  PERSON:       "badge-person",
  LOCATION:     "badge-location",
  PHONE:        "badge-phone",
  VEHICLE:      "badge-vehicle",
  CASE:         "badge-case",
  MONEY:        "badge-money",
  DATE:         "badge-date",
  ORGANIZATION: "badge-org",
};

const TYPE_ICON = {
  PERSON: "👤", LOCATION: "📍", PHONE: "📞",
  VEHICLE: "🚗", CASE: "📂", MONEY: "💰",
  DATE: "📅", ORGANIZATION: "🏢",
};

export default function EntitiesPanel({ entities, resolvedEntities }) {
  if (!entities?.length) return null;

  const matchClass = (status) => {
    if (status === "AUTO_MATCH")    return "badge-auto";
    if (status === "POSSIBLE_MATCH") return "badge-possible";
    return "badge-new";
  };

  const matchLabel = (status) => {
    if (status === "AUTO_MATCH")    return "✓ Auto-matched";
    if (status === "POSSIBLE_MATCH") return "~ Possible match";
    return "? New entity";
  };

  return (
    <div className="grid-2" style={{ marginTop: "1.25rem" }}>
      {/* Extracted Entities */}
      <div className="card">
        <div className="card-title">
          <span className="dot" style={{ background: "#06b6d4" }} />
          Extracted Entities ({entities.length})
        </div>
        <div className="entity-grid">
          {entities.map((e, i) => (
            <div className="entity-chip" key={i}>
              <span>{TYPE_ICON[e.type] || "•"}</span>
              <span className="entity-text">{e.text}</span>
              <span className={`badge ${TYPE_BADGE[e.type] || "badge-date"}`}>{e.type}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Resolved Entities */}
      <div className="card">
        <div className="card-title">
          <span className="dot" style={{ background: "#10b981" }} />
          Entity Resolution ({resolvedEntities?.length ?? 0})
        </div>
        <div className="scroll-box">
          <table className="res-table">
            <thead>
              <tr>
                <th>Input</th>
                <th>Matched DB Record</th>
                <th>Status</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {resolvedEntities?.map((r, i) => (
                <tr key={i}>
                  <td>
                    <span style={{ fontWeight: 500 }}>{r.input_text}</span>
                    <span style={{ marginLeft: 6 }} className={`badge ${TYPE_BADGE[r.input_type] || ""}`}>{r.input_type}</span>
                  </td>
                  <td style={{ color: r.db_id ? "var(--text-primary)" : "var(--text-muted)" }}>
                    {r.db_id ? (
                      <>
                        <span style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "0.72rem", color: "var(--accent-cyan)", marginRight: 6 }}>{r.db_id}</span>
                        {r.db_name}
                      </>
                    ) : "—"}
                  </td>
                  <td>
                    <span className={`badge ${matchClass(r.match_status)}`}>{matchLabel(r.match_status)}</span>
                  </td>
                  <td>
                    <div className="conf-bar-wrap">
                      <div className="conf-bar-bg">
                        <div
                          className="conf-bar-fill"
                          style={{ width: `${(r.confidence * 100).toFixed(0)}%` }}
                        />
                      </div>
                      <span className="conf-label">{(r.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
